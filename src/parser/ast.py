# src/parser/ast.py
from abc import ABC, abstractmethod
from typing import List, Optional, Any
from enum import Enum

class ASTNode(ABC):
    def __init__(self, line: int = 0, column: int = 0):
        self.line = line
        self.column = column

    @abstractmethod
    def accept(self, visitor): pass

class ExpressionNode(ASTNode):
    pass

class StatementNode(ASTNode):
    pass

class DeclarationNode(ASTNode):
    pass

# --- Expression nodes ---
class LiteralExprNode(ExpressionNode):
    def __init__(self, value: Any, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal_expr(self)

class IdentifierExprNode(ExpressionNode):
    def __init__(self, name: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name

    def accept(self, visitor):
        return visitor.visit_identifier_expr(self)

class BinaryExprNode(ExpressionNode):
    def __init__(self, left: ExpressionNode, op: str, right: ExpressionNode,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.left = left
        self.op = op
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)

class UnaryExprNode(ExpressionNode):
    def __init__(self, op: str, operand: ExpressionNode,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.op = op
        self.operand = operand

    def accept(self, visitor):
        return visitor.visit_unary_expr(self)

class CallExprNode(ExpressionNode):
    def __init__(self, callee: IdentifierExprNode, arguments: List[ExpressionNode],
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.callee = callee
        self.arguments = arguments

    def accept(self, visitor):
        return visitor.visit_call_expr(self)

class AssignmentExprNode(ExpressionNode):
    def __init__(self, target: ExpressionNode, op: str, value: ExpressionNode,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.target = target
        self.op = op
        self.value = value

    def accept(self, visitor):
        return visitor.visit_assignment_expr(self)

# --- Statement nodes ---
class BlockStmtNode(StatementNode):
    def __init__(self, statements: List[StatementNode], line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)

class ExprStmtNode(StatementNode):
    def __init__(self, expression: ExpressionNode, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expr_stmt(self)

class IfStmtNode(StatementNode):
    def __init__(self, condition: ExpressionNode, then_branch: StatementNode,
                 else_branch: Optional[StatementNode] = None,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor):
        return visitor.visit_if_stmt(self)

class WhileStmtNode(StatementNode):
    def __init__(self, condition: ExpressionNode, body: StatementNode,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visit_while_stmt(self)

class ForStmtNode(StatementNode):
    def __init__(self, init: Optional[StatementNode], condition: Optional[ExpressionNode],
                 update: Optional[ExpressionNode], body: StatementNode,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

    def accept(self, visitor):
        return visitor.visit_for_stmt(self)

class ReturnStmtNode(StatementNode):
    def __init__(self, value: Optional[ExpressionNode] = None, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = value

    def accept(self, visitor):
        return visitor.visit_return_stmt(self)

class VarDeclStmtNode(StatementNode):  # также может быть DeclarationNode, но для простоты как Statement
    def __init__(self, var_type: str, name: str, initializer: Optional[ExpressionNode],
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.var_type = var_type
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit_var_decl_stmt(self)

# --- Declaration nodes ---
class FunctionDeclNode(DeclarationNode):
    def __init__(self, return_type: str, name: str, parameters: List['ParamNode'],
                 body: BlockStmtNode, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.return_type = return_type
        self.name = name
        self.parameters = parameters
        self.body = body

    def accept(self, visitor):
        return visitor.visit_function_decl(self)

class ParamNode(ASTNode):
    def __init__(self, param_type: str, name: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.param_type = param_type
        self.name = name

    def accept(self, visitor):
        return visitor.visit_param(self)

class StructDeclNode(DeclarationNode):
    def __init__(self, name: str, fields: List[VarDeclStmtNode], line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.fields = fields

    def accept(self, visitor):
        return visitor.visit_struct_decl(self)

class ProgramNode(ASTNode):
    def __init__(self, declarations: List[DeclarationNode], line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.declarations = declarations

    def accept(self, visitor):
        return visitor.visit_program(self)

class ASTNode(ABC):
    def __init__(self, line: int = 0, column: int =0):
        self.line = line
        self.column = column
        self.type = None
        self.symbol = None

class IdentifierExprNode(ExpressionNode):
    def __init__(self, name:str, line: int =0, column: int=0):
        super().__init__(line,column)
        self.name = name
        self.symbol = None