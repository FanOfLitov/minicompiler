
from typing import List, Optional, Callable, Set
from src.lexer.token_types import Token, TokenType
from .ast_nodes import (
    ExpressionNode, StatementNode, DeclarationNode,
    ProgramNode, FunctionDeclNode, StructDeclNode, ParamNode,
    BlockStmtNode, VarDeclStmtNode, ExprStmtNode,
    IfStmtNode, WhileStmtNode, ForStmtNode, ReturnStmtNode,
    LiteralExprNode, IdentifierExprNode, BinaryExprNode,
    UnaryExprNode, CallExprNode, AssignmentExprNode,
)

class ParseError(Exception):
    def __init__(self, message: str, token: Token) -> None:
        super().__init__(message)
        self.token   = token
        self.message = message


class ParserDiagnostic:
    def __init__(self, message: str, line: int, column: int) -> None:
        self.message = message
        self.line    = line
        self.column  = column

    def __str__(self) -> str:
        return f"parse error at {self.line}:{self.column}: {self.message}"


_TYPE_KEYWORDS: Set[TokenType] = {
    TokenType.KW_INT, TokenType.KW_FLOAT,
    TokenType.KW_BOOL, TokenType.KW_VOID,
    TokenType.IDENTIFIER,
}

_ASSIGN_OPS: Set[TokenType] = {
    TokenType.ASSIGN, TokenType.PLUS_ASSIGN,
    TokenType.MINUS_ASSIGN, TokenType.STAR_ASSIGN,
    TokenType.SLASH_ASSIGN,
}


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self._tokens:  List[Token]           = tokens
        self._pos:     int                   = 0
        self.errors:   List[ParserDiagnostic] = []

    def parse(self) -> Optional[ProgramNode]:
        try:
            return self._parse_program()
        except ParseError as e:
            self._record_error(e.message, e.token)
            return None

    def _parse_program(self) -> ProgramNode:
        decls: List[DeclarationNode] = []
        while not self._is_at_end():
            try:
                decls.append(self._parse_declaration())
            except ParseError as e:
                self._record_error(e.message, e.token)
                self._synchronize_declaration()
        return ProgramNode(declarations=decls, line=1, column=1)

    def _parse_declaration(self) -> DeclarationNode:
        if self._check(TokenType.KW_FN):
            return self._parse_function_decl()
        if self._check(TokenType.KW_STRUCT):
            return self._parse_struct_decl()
        return self._parse_var_decl()

    def _parse_function_decl(self) -> FunctionDeclNode:
        tok = self._consume(TokenType.KW_FN, "expected 'fn'")
        name_tok = self._consume(TokenType.IDENTIFIER, "expected function name")
        self._consume(TokenType.LPAREN, "expected '('")

        params: List[ParamNode] = []
        if not self._check(TokenType.RPAREN):
            params = self._parse_params()

        self._consume(TokenType.RPAREN, "expected ')'")

        ret_type = "void"
        if self._match(TokenType.ARROW):
            ret_type = self._parse_type()

        body = self._parse_block()
        return FunctionDeclNode(
            return_type=ret_type,
            name=name_tok.lexeme,
            params=params,
            body=body,
            line=tok.line,
            column=tok.column,
        )

    def _parse_struct_decl(self) -> StructDeclNode:
        tok = self._consume(TokenType.KW_STRUCT, "expected 'struct'")
        name_tok = self._consume(TokenType.IDENTIFIER, "expected struct name")
        self._consume(TokenType.LBRACE, "expected '{'")

        fields: List[VarDeclStmtNode] = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            fields.append(self._parse_var_decl())

        self._consume(TokenType.RBRACE, "expected '}'")
        return StructDeclNode(
            name=name_tok.lexeme,
            fields=fields,
            line=tok.line,
            column=tok.column,
        )

    def _parse_params(self) -> List[ParamNode]:
        params: List[ParamNode] = [self._parse_single_param()]
        while self._match(TokenType.COMMA):
            params.append(self._parse_single_param())
        return params

    def _parse_single_param(self) -> ParamNode:
        type_tok = self._peek()
        ptype    = self._parse_type()
        name_tok = self._consume(TokenType.IDENTIFIER, "expected parameter name")
        return ParamNode(param_type=ptype, name=name_tok.lexeme,
                         line=type_tok.line, column=type_tok.column)

    def _parse_type(self) -> str:
        tok = self._peek()
        if tok.type in _TYPE_KEYWORDS:
            self._advance()
            return tok.lexeme
        raise ParseError(f"expected type, got {tok.lexeme!r}", tok)

    def _parse_statement(self) -> StatementNode:
        if self._check(TokenType.LBRACE):
            return self._parse_block()
        if self._check(TokenType.KW_IF):
            return self._parse_if()
        if self._check(TokenType.KW_WHILE):
            return self._parse_while()
        if self._check(TokenType.KW_FOR):
            return self._parse_for()
        if self._check(TokenType.KW_RETURN):
            return self._parse_return()
        if self._is_type_start():
            return self._parse_var_decl()
        return self._parse_expr_stmt()

    def _parse_block(self) -> BlockStmtNode:
        tok = self._consume(TokenType.LBRACE, "expected '{'")
        stmts: List[StatementNode] = []

        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            try:
                stmts.append(self._parse_statement())
            except ParseError as e:
                self._record_error(e.message, e.token)
                self._synchronize_statement()

        self._consume(TokenType.RBRACE, "expected '}'")
        return BlockStmtNode(statements=stmts, line=tok.line, column=tok.column)

    def _parse_if(self) -> IfStmtNode:
        tok = self._consume(TokenType.KW_IF, "expected 'if'")
        self._consume(TokenType.LPAREN, "expected '('")
        cond = self._parse_expression()
        self._consume(TokenType.RPAREN, "expected ')'")
        then_branch = self._parse_statement()

        else_branch: Optional[StatementNode] = None
        if self._match(TokenType.KW_ELSE):
            else_branch = self._parse_statement()

        return IfStmtNode(condition=cond, then_branch=then_branch,
                          else_branch=else_branch, line=tok.line, column=tok.column)

    def _parse_while(self) -> WhileStmtNode:
        tok = self._consume(TokenType.KW_WHILE, "expected 'while'")
        self._consume(TokenType.LPAREN, "expected '('")
        cond = self._parse_expression()
        self._consume(TokenType.RPAREN, "expected ')'")
        body = self._parse_statement()
        return WhileStmtNode(condition=cond, body=body, line=tok.line, column=tok.column)

    def _parse_for(self) -> ForStmtNode:
        tok = self._consume(TokenType.KW_FOR, "expected 'for'")
        self._consume(TokenType.LPAREN, "expected '('")

        init: Optional[StatementNode] = None
        if not self._check(TokenType.SEMICOLON):
            if self._is_type_start():
                init = self._parse_var_decl()
            else:
                init = self._parse_expr_stmt()
        else:
            self._advance()

        condition: Optional[ExpressionNode] = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "expected ';'")

        update: Optional[ExpressionNode] = None
        if not self._check(TokenType.RPAREN):
            update = self._parse_expression()
        self._consume(TokenType.RPAREN, "expected ')'")

        body = self._parse_statement()
        return ForStmtNode(init=init, condition=condition,
                           update=update, body=body, line=tok.line, column=tok.column)

    def _parse_return(self) -> ReturnStmtNode:
        tok = self._consume(TokenType.KW_RETURN, "expected 'return'")
        value: Optional[ExpressionNode] = None
        if not self._check(TokenType.SEMICOLON):
            value = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "expected ';'")
        return ReturnStmtNode(value=value, line=tok.line, column=tok.column)

    def _parse_var_decl(self) -> VarDeclStmtNode:
        type_tok = self._peek()
        vtype    = self._parse_type()
        name_tok = self._consume(TokenType.IDENTIFIER, "expected variable name")
        init: Optional[ExpressionNode] = None
        if self._match(TokenType.ASSIGN):
            init = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "expected ';'")
        return VarDeclStmtNode(
            var_type=vtype,
            name=name_tok.lexeme,
            initializer=init,
            line=type_tok.line,
            column=type_tok.column,
        )

    def _parse_expr_stmt(self) -> ExprStmtNode:
        tok  = self._peek()
        expr = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "expected ';'")
        return ExprStmtNode(expression=expr, line=tok.line, column=tok.column)

    def _parse_expression(self) -> ExpressionNode:
        return self._parse_assignment()

    def _parse_assignment(self) -> ExpressionNode:
        expr = self._parse_logical_or()
        if self._peek().type in _ASSIGN_OPS:
            op_tok = self._advance()
            if not isinstance(expr, IdentifierExprNode):
                raise ParseError("invalid assignment target", op_tok)
            value = self._parse_assignment()
            return AssignmentExprNode(
                target=expr.name,
                operator=op_tok.lexeme,
                value=value,
                line=op_tok.line,
                column=op_tok.column,
            )
        return expr

    def _parse_logical_or(self) -> ExpressionNode:
        return self._parse_left_assoc(self._parse_logical_and, {TokenType.PIPE_PIPE})

    def _parse_logical_and(self) -> ExpressionNode:
        return self._parse_left_assoc(self._parse_equality, {TokenType.AMP_AMP})

    def _parse_equality(self) -> ExpressionNode:
        return self._parse_left_assoc(self._parse_relational, {TokenType.EQ_EQ, TokenType.BANG_EQ})

    def _parse_relational(self) -> ExpressionNode:
        return self._parse_left_assoc(
            self._parse_additive,
            {TokenType.LT, TokenType.LT_EQ, TokenType.GT, TokenType.GT_EQ}
        )

    def _parse_additive(self) -> ExpressionNode:
        return self._parse_left_assoc(self._parse_multiplicative, {TokenType.PLUS, TokenType.MINUS})

    def _parse_multiplicative(self) -> ExpressionNode:
        return self._parse_left_assoc(
            self._parse_unary,
            {TokenType.STAR, TokenType.SLASH, TokenType.PERCENT}
        )

    def _parse_left_assoc(
        self,
        next_rule: Callable[[], ExpressionNode],
        ops: Set[TokenType],
    ) -> ExpressionNode:
        left = next_rule()
        while self._peek().type in ops:
            op_tok = self._advance()
            right  = next_rule()
            left   = BinaryExprNode(
                left=left, operator=op_tok.lexeme, right=right,
                line=op_tok.line, column=op_tok.column,
            )
        return left

    def _parse_unary(self) -> ExpressionNode:
        if self._peek().type in {TokenType.MINUS, TokenType.BANG}:
            op_tok  = self._advance()
            operand = self._parse_unary()
            return UnaryExprNode(
                operator=op_tok.lexeme,
                operand=operand,
                line=op_tok.line,
                column=op_tok.column,
            )
        return self._parse_primary()

    def _parse_primary(self) -> ExpressionNode:
        tok = self._peek()

        if tok.type == TokenType.INT_LITERAL:
            self._advance()
            return LiteralExprNode(value=tok.literal, kind='int', line=tok.line, column=tok.column)
        if tok.type == TokenType.FLOAT_LITERAL:
            self._advance()
            return LiteralExprNode(value=tok.literal, kind='float', line=tok.line, column=tok.column)
        if tok.type == TokenType.BOOL_LITERAL:
            self._advance()
            return LiteralExprNode(value=tok.literal, kind='bool', line=tok.line, column=tok.column)
        if tok.type == TokenType.STRING_LITERAL:
            self._advance()
            return LiteralExprNode(value=tok.literal, kind='string', line=tok.line, column=tok.column)
        if tok.type == TokenType.KW_NULL:
            self._advance()
            return LiteralExprNode(value=None, kind='null', line=tok.line, column=tok.column)

        if tok.type == TokenType.IDENTIFIER:
            self._advance()
            if self._check(TokenType.LPAREN):
                return self._parse_call(tok)
            return IdentifierExprNode(name=tok.lexeme, line=tok.line, column=tok.column)

        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "expected ')'")
            return expr

        raise ParseError(f"unexpected token {tok.lexeme!r}", tok)

    def _parse_call(self, name_tok: Token) -> CallExprNode:
        self._consume(TokenType.LPAREN, "expected '('")
        args: List[ExpressionNode] = []
        if not self._check(TokenType.RPAREN):
            args.append(self._parse_expression())
            while self._match(TokenType.COMMA):
                args.append(self._parse_expression())
        self._consume(TokenType.RPAREN, "expected ')'")
        return CallExprNode(callee=name_tok.lexeme, arguments=args,
                            line=name_tok.line, column=name_tok.column)

    def _peek(self) -> Token:
        return self._tokens[self._pos]

    def _peek_next(self) -> Token:
        idx = min(self._pos + 1, len(self._tokens) - 1)
        return self._tokens[idx]

    def _advance(self) -> Token:
        tok = self._tokens[self._pos]
        if not self._is_at_end():
            self._pos += 1
        return tok

    def _is_at_end(self) -> bool:
        return self._tokens[self._pos].type == TokenType.EOF

    def _check(self, ttype: TokenType) -> bool:
        return not self._is_at_end() and self._peek().type == ttype

    def _match(self, *types: TokenType) -> bool:
        for ttype in types:
            if self._check(ttype):
                self._advance()
                return True
        return False

    def _consume(self, ttype: TokenType, message: str) -> Token:
        if self._check(ttype):
            return self._advance()
        tok = self._peek()
        raise ParseError(f"{message}; got {tok.lexeme!r}", tok)

    def _is_type_start(self) -> bool:
        if self._peek().type not in _TYPE_KEYWORDS:
            return False
        return self._peek_next().type == TokenType.IDENTIFIER

    def _record_error(self, message: str, token: Token) -> None:
        self.errors.append(ParserDiagnostic(message, token.line, token.column))

    def _synchronize_statement(self) -> None:
        while not self._is_at_end():
            if self._peek().type == TokenType.SEMICOLON:
                self._advance()
                return
            if self._peek().type in {
                TokenType.KW_IF, TokenType.KW_WHILE, TokenType.KW_FOR,
                TokenType.KW_RETURN, TokenType.KW_FN, TokenType.KW_STRUCT,
                TokenType.RBRACE,
            }:
                return
            self._advance()

    def _synchronize_statement(self) -> None:
        while not self._is_at_end():
            if self._peek().type == TokenType.SEMICOLON:
                self._advance()
                return
            if self._peek().type in {
                TokenType.KW_IF, TokenType.KW_WHILE, TokenType.KW_FOR,
                TokenType.KW_RETURN, TokenType.KW_FN, TokenType.KW_STRUCT,
                TokenType.KW_INT, TokenType.KW_FLOAT, TokenType.KW_BOOL,  # Добавлено для лучшего восстановления
                TokenType.RBRACE,
            }:
                return
            self._advance()

    def _synchronize_declaration(self) -> None:
        while not self._is_at_end():
            if self._peek().type in {TokenType.KW_FN, TokenType.KW_STRUCT}:
                return
            self._advance()