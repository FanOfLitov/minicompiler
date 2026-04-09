# src/parser/parser.py
from typing import List, Optional
from src.lexer.token import Token, TokenType
from src.parser.ast import *

class ParseError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.errors = []

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens) or self.peek().type == TokenType.END_OF_FILE

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def match(self, *types: TokenType) -> bool:
        if self.check(*types):
            self.advance()
            return True
        return False

    def check(self, *types: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type in types

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        raise ParseError(self.peek(), message)

    def synchronize(self):
        # Синхронизация после ошибки: пропускаем до точки синхронизации (; или })
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            if self.peek().type == TokenType.RBRACE:
                return
            self.advance()

    # ---------- Грамматика ----------
    def parse(self) -> ProgramNode:
        declarations = []
        while not self.is_at_end():
            try:
                decl = self.declaration()
                declarations.append(decl)
            except ParseError as e:
                self.errors.append((e.token, e.message))
                self.synchronize()
        return ProgramNode(declarations)

    def declaration(self) -> DeclarationNode:
        if self.match(TokenType.KW_FN):
            return self.function_decl()
        if self.match(TokenType.KW_STRUCT):
            return self.struct_decl()

        return self.var_decl()

    def function_decl(self) -> FunctionDeclNode:
        # fn name ( params ) [-> type] block
        line = self.previous().line
        column = self.previous().column
        name_token = self.consume(TokenType.IDENTIFIER, "Expected function name")
        name = name_token.lexeme
        self.consume(TokenType.LPAREN, "Expected '(' after function name")
        parameters = []
        if not self.check(TokenType.RPAREN):
            parameters = self.parameters()
        self.consume(TokenType.RPAREN, "Expected ')' after parameters")
        return_type = "void"
        if self.match(TokenType.MINUS, TokenType.GT):  # "->"
            return_type = self.type_name()
        body = self.block()
        return FunctionDeclNode(return_type, name, parameters, body, line, column)

    def parameters(self) -> List[ParamNode]:
        params = []
        first = True
        while not self.check(TokenType.RPAREN):
            if not first:
                self.consume(TokenType.COMMA, "Expected ',' between parameters")
            param_type = self.type_name()
            param_name = self.consume(TokenType.IDENTIFIER, "Expected parameter name")
            params.append(ParamNode(param_type, param_name.lexeme,
                                    line=param_name.line, column=param_name.column))
            first = False
        return params

    def type_name(self) -> str:
        # Пока поддерживаем базовые типы и идентификаторы (для структур)
        if self.match(TokenType.KW_INT):
            return "int"
        if self.match(TokenType.KW_FLOAT):
            return "float"
        if self.match(TokenType.KW_BOOL):
            return "bool"
        if self.match(TokenType.KW_VOID):
            return "void"
        if self.check(TokenType.IDENTIFIER):
            token = self.advance()
            return token.lexeme
        raise ParseError(self.peek(), f"Expected type, got {self.peek().type}")

    def struct_decl(self) -> StructDeclNode:
        # struct Name { varDecls }
        line = self.previous().line
        column = self.previous().column
        name_token = self.consume(TokenType.IDENTIFIER, "Expected struct name")
        name = name_token.lexeme
        self.consume(TokenType.LBRACE, "Expected '{' after struct name")
        fields = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            # var_decl внутри структуры
            var_decl = self.var_decl()
            fields.append(var_decl)
        self.consume(TokenType.RBRACE, "Expected '}' after struct fields")
        return StructDeclNode(name, fields, line, column)

    def var_decl(self) -> VarDeclStmtNode:
        # type name [ = expr ] ;
        var_type = self.type_name()
        name_token = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        name = name_token.lexeme
        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        return VarDeclStmtNode(var_type, name, initializer,
                               line=name_token.line, column=name_token.column)

    def statement(self) -> StatementNode:
        if self.match(TokenType.LBRACE):
            return self.block()
        if self.match(TokenType.KW_IF):
            return self.if_stmt()
        if self.match(TokenType.KW_WHILE):
            return self.while_stmt()
        if self.match(TokenType.KW_FOR):
            return self.for_stmt()
        if self.match(TokenType.KW_RETURN):
            return self.return_stmt()

        if self.check(TokenType.KW_INT, TokenType.KW_FLOAT, TokenType.KW_BOOL, TokenType.IDENTIFIER):

           return self.var_decl()
        # В противном случае это выражение-оператор
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression")
        return ExprStmtNode(expr, line=expr.line, column=expr.column)

    def block(self) -> BlockStmtNode:
        # { statements }
        line = self.previous().line
        column = self.previous().column
        statements = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            stmt = self.statement()
            statements.append(stmt)
        self.consume(TokenType.RBRACE, "Expected '}' after block")
        return BlockStmtNode(statements, line, column)

    def if_stmt(self) -> IfStmtNode:
        line = self.previous().line
        column = self.previous().column
        self.consume(TokenType.LPAREN, "Expected '(' after 'if'")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Expected ')' after condition")
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.KW_ELSE):
            else_branch = self.statement()
        return IfStmtNode(condition, then_branch, else_branch, line, column)

    def while_stmt(self) -> WhileStmtNode:
        line = self.previous().line
        column = self.previous().column
        self.consume(TokenType.LPAREN, "Expected '(' after 'while'")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Expected ')' after condition")
        body = self.statement()
        return WhileStmtNode(condition, body, line, column)

    def for_stmt(self) -> ForStmtNode:
        line = self.previous().line
        column = self.previous().column
        self.consume(TokenType.LPAREN, "Expected '(' after 'for'")
        # init
        init = None
        if not self.check(TokenType.SEMICOLON):
            if self.check(TokenType.KW_INT, TokenType.KW_FLOAT, TokenType.KW_BOOL, TokenType.IDENTIFIER):
                               init = self.expression_statement()  # expression followed by semicolon
            else:
                init = self.expression_statement()
        else:
            # пропускаем точку с запятой
            self.consume(TokenType.SEMICOLON, "Expected ';' after for init")
        # condition
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after for condition")
        # update
        update = None
        if not self.check(TokenType.RPAREN):
            update = self.expression()
        self.consume(TokenType.RPAREN, "Expected ')' after for update")
        body = self.statement()
        return ForStmtNode(init, condition, update, body, line, column)

    def expression_statement(self) -> StatementNode:
        # парсит выражение и следующую точку с запятой, возвращает ExprStmtNode
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression")
        return ExprStmtNode(expr)

    def return_stmt(self) -> ReturnStmtNode:
        line = self.previous().line
        column = self.previous().column
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after return")
        return ReturnStmtNode(value, line, column)

    def expression(self) -> ExpressionNode:
        return self.assignment()

    def assignment(self) -> ExpressionNode:
        # left = assignment | logical_or
        left = self.logical_or()
        if self.match(TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
                      TokenType.STAR_ASSIGN, TokenType.SLASH_ASSIGN):
            op = self.previous().lexeme
            right = self.assignment()
            return AssignmentExprNode(left, op, right, line=left.line, column=left.column)
        return left

    def logical_or(self) -> ExpressionNode:
        left = self.logical_and()
        while self.match(TokenType.OR):
            op = self.previous().lexeme
            right = self.logical_and()
            left = BinaryExprNode(left, op, right, line=left.line, column=left.column)
        return left

    def logical_and(self) -> ExpressionNode:
        left = self.equality()
        while self.match(TokenType.AND):
            op = self.previous().lexeme
            right = self.equality()
            left = BinaryExprNode(left, op, right, line=left.line, column=left.column)
        return left

    def equality(self) -> ExpressionNode:
        left = self.relational()
        while self.match(TokenType.EQ, TokenType.NE):
            op = self.previous().lexeme
            right = self.relational()
            left = BinaryExprNode(left, op, right, line=left.line, column=left.column)
        return left

    def relational(self) -> ExpressionNode:
        left = self.additive()
        while self.match(TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE):
            op = self.previous().lexeme
            right = self.additive()
            left = BinaryExprNode(left, op, right, line=left.line, column=left.column)
        return left

    def additive(self) -> ExpressionNode:
        left = self.multiplicative()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.previous().lexeme
            right = self.multiplicative()
            left = BinaryExprNode(left, op, right, line=left.line, column=left.column)
        return left

    def multiplicative(self) -> ExpressionNode:
        left = self.unary()
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.previous().lexeme
            right = self.unary()
            left = BinaryExprNode(left, op, right, line=left.line, column=left.column)
        return left

    def unary(self) -> ExpressionNode:
        if self.match(TokenType.MINUS, TokenType.NOT):
            op = self.previous().lexeme
            right = self.unary()
            return UnaryExprNode(op, right, line=self.previous().line, column=self.previous().column)
        return self.primary()

    def primary(self) -> ExpressionNode:
        if self.match(TokenType.INT_LITERAL):
            token = self.previous()
            return LiteralExprNode(token.literal, token.line, token.column)
        if self.match(TokenType.FLOAT_LITERAL):
            token = self.previous()
            return LiteralExprNode(token.literal, token.line, token.column)
        if self.match(TokenType.STRING_LITERAL):
            token = self.previous()
            return LiteralExprNode(token.literal, token.line, token.column)
        if self.match(TokenType.KW_TRUE, TokenType.KW_FALSE):
            token = self.previous()
            value = True if token.type == TokenType.KW_TRUE else False
            return LiteralExprNode(value, token.line, token.column)
        if self.match(TokenType.IDENTIFIER):
            token = self.previous()
            if self.match(TokenType.LPAREN):
                return self.finish_call(token)
            return IdentifierExprNode(token.lexeme, token.line, token.column)
        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        raise ParseError(self.peek(), f"Unexpected token in primary: {self.peek().type}")

    def finish_call(self, callee_token: Token) -> CallExprNode:
        # callee_token is the identifier token
        callee = IdentifierExprNode(callee_token.lexeme, callee_token.line, callee_token.column)
        arguments = []
        if not self.check(TokenType.RPAREN):
            arguments = self.arguments()
        self.consume(TokenType.RPAREN, "Expected ')' after function call")
        return CallExprNode(callee, arguments, line=callee_token.line, column=callee_token.column)

    def arguments(self) -> List[ExpressionNode]:
        args = []
        first = True
        while not self.check(TokenType.RPAREN):
            if not first:
                self.consume(TokenType.COMMA, "Expected ',' between arguments")
            arg = self.expression()
            args.append(arg)
            first = False
        return args