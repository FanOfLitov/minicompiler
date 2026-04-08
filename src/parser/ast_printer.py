# src/parser/ast_printer.py
import sys
from typing import TextIO, Optional
from src.parser.ast import *


class ASTPrinter:
    def __init__(self, indent: int = 2):
        self.indent = indent

    def print_text(self, node: ASTNode, file: TextIO = sys.stdout):
        self._print_node(node, 0, file)

    def _print_node(self, node: ASTNode, level: int, file: TextIO):
        indent = " " * (level * self.indent)
        if isinstance(node, ProgramNode):
            print(f"{indent}Program [line {node.line}]:", file=file)
            for decl in node.declarations:
                self._print_node(decl, level + 1, file)
        elif isinstance(node, FunctionDeclNode):
            print(f"{indent}FunctionDecl: {node.name} -> {node.return_type} [line {node.line}]:", file=file)
            print(f"{indent}  Parameters:", file=file)
            for param in node.parameters:
                self._print_node(param, level + 2, file)
            print(f"{indent}  Body:", file=file)
            self._print_node(node.body, level + 2, file)
        elif isinstance(node, ParamNode):
            print(f"{indent}{node.param_type} {node.name}", file=file)
        elif isinstance(node, StructDeclNode):
            print(f"{indent}StructDecl: {node.name} [line {node.line}]:", file=file)
            for field in node.fields:
                self._print_node(field, level + 1, file)
        elif isinstance(node, VarDeclStmtNode):
            init_str = ""
            if node.initializer:
                init_str = f" = {self._expr_to_string(node.initializer)}"
            print(f"{indent}VarDecl: {node.var_type} {node.name}{init_str} [line {node.line}]", file=file)
        elif isinstance(node, BlockStmtNode):
            print(f"{indent}Block [line {node.line}]:", file=file)
            for stmt in node.statements:
                self._print_node(stmt, level + 1, file)
        elif isinstance(node, ExprStmtNode):
            print(f"{indent}ExprStmt: {self._expr_to_string(node.expression)} [line {node.line}]", file=file)
        elif isinstance(node, IfStmtNode):
            print(f"{indent}IfStmt [line {node.line}]:", file=file)
            print(f"{indent}  Condition: {self._expr_to_string(node.condition)}", file=file)
            print(f"{indent}  Then:", file=file)
            self._print_node(node.then_branch, level + 2, file)
            if node.else_branch:
                print(f"{indent}  Else:", file=file)
                self._print_node(node.else_branch, level + 2, file)
        elif isinstance(node, WhileStmtNode):
            print(f"{indent}WhileStmt [line {node.line}]:", file=file)
            print(f"{indent}  Condition: {self._expr_to_string(node.condition)}", file=file)
            print(f"{indent}  Body:", file=file)
            self._print_node(node.body, level + 2, file)
        elif isinstance(node, ForStmtNode):
            print(f"{indent}ForStmt [line {node.line}]:", file=file)
            print(f"{indent}  Init: {self._stmt_to_string(node.init)}", file=file)
            print(f"{indent}  Condition: {self._expr_to_string(node.condition)}", file=file)
            print(f"{indent}  Update: {self._expr_to_string(node.update)}", file=file)
            print(f"{indent}  Body:", file=file)
            self._print_node(node.body, level + 2, file)
        elif isinstance(node, ReturnStmtNode):
            value_str = self._expr_to_string(node.value) if node.value else ""
            print(f"{indent}Return: {value_str} [line {node.line}]", file=file)
        elif isinstance(node, LiteralExprNode):
            # Usually printed as part of expression, but if called separately, print value
            print(f"{indent}Literal: {node.value} [line {node.line}]", file=file)
        elif isinstance(node, IdentifierExprNode):
            print(f"{indent}Identifier: {node.name} [line {node.line}]", file=file)
        elif isinstance(node, BinaryExprNode):
            # Should not be called directly; expressions are printed inline
            print(f"{indent}Binary: {self._expr_to_string(node)}", file=file)
        elif isinstance(node, UnaryExprNode):
            print(f"{indent}Unary: {self._expr_to_string(node)}", file=file)
        elif isinstance(node, CallExprNode):
            print(f"{indent}Call: {self._expr_to_string(node)}", file=file)
        elif isinstance(node, AssignmentExprNode):
            print(f"{indent}Assignment: {self._expr_to_string(node)}", file=file)
        else:
            print(f"{indent}{node.__class__.__name__}", file=file)

    def _expr_to_string(self, expr: Optional[ExpressionNode]) -> str:
        if expr is None:
            return ""
        if isinstance(expr, LiteralExprNode):
            return str(expr.value)
        if isinstance(expr, IdentifierExprNode):
            return expr.name
        if isinstance(expr, BinaryExprNode):
            return f"({self._expr_to_string(expr.left)} {expr.op} {self._expr_to_string(expr.right)})"
        if isinstance(expr, UnaryExprNode):
            return f"{expr.op}{self._expr_to_string(expr.operand)}"
        if isinstance(expr, CallExprNode):
            args = ", ".join(self._expr_to_string(a) for a in expr.arguments)
            return f"{expr.callee.name}({args})"
        if isinstance(expr, AssignmentExprNode):
            return f"{self._expr_to_string(expr.target)} {expr.op} {self._expr_to_string(expr.value)}"
        return "?"

    def _stmt_to_string(self, stmt: Optional[StatementNode]) -> str:
        if stmt is None:
            return ""
        if isinstance(stmt, ExprStmtNode):
            return self._expr_to_string(stmt.expression)
        if isinstance(stmt, VarDeclStmtNode):
            init = f" = {self._expr_to_string(stmt.initializer)}" if stmt.initializer else ""
            return f"{stmt.var_type} {stmt.name}{init}"
        return "?"


class ASTDotPrinter:

    def __init__(self):
        self.node_counter = 0

    def _next_id(self):
        self.node_counter += 1
        return f"node{self.node_counter}"

    def print_dot(self, node: ASTNode, file: TextIO = sys.stdout):
        print("digraph AST {", file=file)
        print("  node [shape=box];", file=file)
        self._print_node(node, file)
        print("}", file=file)

    def _print_node(self, node: ASTNode, file: TextIO, parent_id: Optional[str] = None):
        node_id = self._next_id()
        label = self._node_label(node)
        print(f'  {node_id} [label="{label}"];', file=file)
        if parent_id:
            print(f"  {parent_id} -> {node_id};", file=file)

        # Recurse to children
        if isinstance(node, ProgramNode):
            for decl in node.declarations:
                self._print_node(decl, file, node_id)
        elif isinstance(node, FunctionDeclNode):
            for param in node.parameters:
                self._print_node(param, file, node_id)
            self._print_node(node.body, file, node_id)
        elif isinstance(node, ParamNode):
            pass  # leaf
        elif isinstance(node, StructDeclNode):
            for field in node.fields:
                self._print_node(field, file, node_id)
        elif isinstance(node, VarDeclStmtNode):
            if node.initializer:
                self._print_node(node.initializer, file, node_id)
        elif isinstance(node, BlockStmtNode):
            for stmt in node.statements:
                self._print_node(stmt, file, node_id)
        elif isinstance(node, ExprStmtNode):
            self._print_node(node.expression, file, node_id)
        elif isinstance(node, IfStmtNode):
            self._print_node(node.condition, file, node_id)
            self._print_node(node.then_branch, file, node_id)
            if node.else_branch:
                self._print_node(node.else_branch, file, node_id)
        elif isinstance(node, WhileStmtNode):
            self._print_node(node.condition, file, node_id)
            self._print_node(node.body, file, node_id)
        elif isinstance(node, ForStmtNode):
            if node.init:
                self._print_node(node.init, file, node_id)
            if node.condition:
                self._print_node(node.condition, file, node_id)
            if node.update:
                self._print_node(node.update, file, node_id)
            self._print_node(node.body, file, node_id)
        elif isinstance(node, ReturnStmtNode):
            if node.value:
                self._print_node(node.value, file, node_id)
        elif isinstance(node, BinaryExprNode):
            self._print_node(node.left, file, node_id)
            self._print_node(node.right, file, node_id)
        elif isinstance(node, UnaryExprNode):
            self._print_node(node.operand, file, node_id)
        elif isinstance(node, CallExprNode):
            for arg in node.arguments:
                self._print_node(arg, file, node_id)
        elif isinstance(node, AssignmentExprNode):
            self._print_node(node.target, file, node_id)
            self._print_node(node.value, file, node_id)
        # Literal and Identifier are leaf nodes

    def _node_label(self, node: ASTNode) -> str:
        if isinstance(node, ProgramNode):
            return "Program"
        if isinstance(node, FunctionDeclNode):
            return f"Function\\n{node.name} -> {node.return_type}"
        if isinstance(node, ParamNode):
            return f"Param\\n{node.param_type} {node.name}"
        if isinstance(node, StructDeclNode):
            return f"Struct\\n{node.name}"
        if isinstance(node, VarDeclStmtNode):
            init = " = ..." if node.initializer else ""
            return f"VarDecl\\n{node.var_type} {node.name}{init}"
        if isinstance(node, BlockStmtNode):
            return "Block"
        if isinstance(node, ExprStmtNode):
            return "ExprStmt"
        if isinstance(node, IfStmtNode):
            return "If"
        if isinstance(node, WhileStmtNode):
            return "While"
        if isinstance(node, ForStmtNode):
            return "For"
        if isinstance(node, ReturnStmtNode):
            return "Return"
        if isinstance(node, LiteralExprNode):
            return f"Literal\\n{node.value}"
        if isinstance(node, IdentifierExprNode):
            return f"Identifier\\n{node.name}"
        if isinstance(node, BinaryExprNode):
            return f"Binary\\n{node.op}"
        if isinstance(node, UnaryExprNode):
            return f"Unary\\n{node.op}"
        if isinstance(node, CallExprNode):
            return f"Call\\n{node.callee.name}"
        if isinstance(node, AssignmentExprNode):
            return f"Assign\\n{node.op}"
        return node.__class__.__name__