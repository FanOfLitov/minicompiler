"""
AST pretty-printer and Graphviz DOT generator.
"""
from __future__ import annotations

import json
from typing import Any, List

from .ast_nodes import (
    ASTVisitor, ASTNode,
    ProgramNode, FunctionDeclNode, StructDeclNode, ParamNode,
    BlockStmtNode, VarDeclStmtNode, ExprStmtNode,
    IfStmtNode, WhileStmtNode, ForStmtNode, ReturnStmtNode,
    LiteralExprNode, IdentifierExprNode, BinaryExprNode,
    UnaryExprNode, CallExprNode, AssignmentExprNode,
)


# ══════════════════════════════════════════════════════════════════════════════
#  Text pretty-printer
# ══════════════════════════════════════════════════════════════════════════════

class TextPrinter(ASTVisitor):
    """Produces an indented text representation of the AST."""

    def __init__(self) -> None:
        self._lines: list[str] = []
        self._depth: int = 0

    def print(self, node: ASTNode) -> str:
        self._lines.clear()
        self._depth = 0
        node.accept(self)
        return '\n'.join(self._lines)

    # ── helpers ────────────────────────────────────────────────────────────
    def _w(self, text: str) -> None:
        self._lines.append("  " * self._depth + text)

    def _loc(self, node: ASTNode) -> str:
        return f"[{node.line}:{node.column}]"

    def _type_ann(self, node: ASTNode) -> str:
        if node.resolved_type:
            return f" : {node.resolved_type}"
        return ""

    # ── Program & declarations ─────────────────────────────────────────────
    def visit_program(self, node: ProgramNode) -> None:
        self._w(f"Program {self._loc(node)}")
        self._depth += 1
        for decl in node.declarations:
            decl.accept(self)
        self._depth -= 1

    def visit_function_decl(self, node: FunctionDeclNode) -> None:
        params = ", ".join(f"{p.param_type} {p.name}" for p in node.params)
        self._w(f"FunctionDecl: {node.name}({params}) -> {node.return_type}"
                f" {self._loc(node)}")
        self._depth += 1
        node.body.accept(self)
        self._depth -= 1

    def visit_struct_decl(self, node: StructDeclNode) -> None:
        self._w(f"StructDecl: {node.name} {self._loc(node)}")
        self._depth += 1
        for f in node.fields:
            f.accept(self)
        self._depth -= 1

    def visit_param(self, node: ParamNode) -> None:
        self._w(f"Param: {node.param_type} {node.name} {self._loc(node)}")

    # ── Statements ─────────────────────────────────────────────────────────
    def visit_block_stmt(self, node: BlockStmtNode) -> None:
        self._w(f"Block {self._loc(node)}")
        self._depth += 1
        for s in node.statements:
            s.accept(self)
        self._depth -= 1

    def visit_var_decl_stmt(self, node: VarDeclStmtNode) -> None:
        init = ""
        if node.initializer:
            init = " = <expr>"
        self._w(f"VarDecl: {node.var_type} {node.name}{init}"
                f"{self._type_ann(node)} {self._loc(node)}")
        if node.initializer:
            self._depth += 1
            node.initializer.accept(self)
            self._depth -= 1

    def visit_expr_stmt(self, node: ExprStmtNode) -> None:
        self._w(f"ExprStmt {self._loc(node)}")
        self._depth += 1
        node.expression.accept(self)
        self._depth -= 1

    def visit_if_stmt(self, node: IfStmtNode) -> None:
        self._w(f"If {self._loc(node)}")
        self._depth += 1
        self._w("Condition:")
        self._depth += 1
        node.condition.accept(self)
        self._depth -= 1
        self._w("Then:")
        self._depth += 1
        node.then_branch.accept(self)
        self._depth -= 1
        if node.else_branch:
            self._w("Else:")
            self._depth += 1
            node.else_branch.accept(self)
            self._depth -= 1
        self._depth -= 1

    def visit_while_stmt(self, node: WhileStmtNode) -> None:
        self._w(f"While {self._loc(node)}")
        self._depth += 1
        self._w("Condition:")
        self._depth += 1
        node.condition.accept(self)
        self._depth -= 1
        self._w("Body:")
        self._depth += 1
        node.body.accept(self)
        self._depth -= 1
        self._depth -= 1

    def visit_for_stmt(self, node: ForStmtNode) -> None:
        self._w(f"For {self._loc(node)}")
        self._depth += 1
        if node.init:
            self._w("Init:")
            self._depth += 1
            node.init.accept(self)
            self._depth -= 1
        if node.condition:
            self._w("Condition:")
            self._depth += 1
            node.condition.accept(self)
            self._depth -= 1
        if node.update:
            self._w("Update:")
            self._depth += 1
            node.update.accept(self)
            self._depth -= 1
        self._w("Body:")
        self._depth += 1
        node.body.accept(self)
        self._depth -= 1
        self._depth -= 1

    def visit_return_stmt(self, node: ReturnStmtNode) -> None:
        self._w(f"Return{self._type_ann(node)} {self._loc(node)}")
        if node.value:
            self._depth += 1
            node.value.accept(self)
            self._depth -= 1

    # ── Expressions ────────────────────────────────────────────────────────
    def visit_literal_expr(self, node: LiteralExprNode) -> None:
        self._w(f"Literal({node.kind}): {node.value!r}"
                f"{self._type_ann(node)} {self._loc(node)}")

    def visit_identifier_expr(self, node: IdentifierExprNode) -> None:
        self._w(f"Identifier: {node.name}{self._type_ann(node)}"
                f" {self._loc(node)}")

    def visit_binary_expr(self, node: BinaryExprNode) -> None:
        self._w(f"Binary: {node.operator!r}{self._type_ann(node)}"
                f" {self._loc(node)}")
        self._depth += 1
        node.left.accept(self)
        node.right.accept(self)
        self._depth -= 1

    def visit_unary_expr(self, node: UnaryExprNode) -> None:
        self._w(f"Unary: {node.operator!r}{self._type_ann(node)}"
                f" {self._loc(node)}")
        self._depth += 1
        node.operand.accept(self)
        self._depth -= 1

    def visit_call_expr(self, node: CallExprNode) -> None:
        self._w(f"Call: {node.callee}(){self._type_ann(node)}"
                f" {self._loc(node)}")
        self._depth += 1
        for arg in node.arguments:
            arg.accept(self)
        self._depth -= 1

    def visit_assignment_expr(self, node: AssignmentExprNode) -> None:
        self._w(f"Assignment: {node.target} {node.operator}"
                f"{self._type_ann(node)} {self._loc(node)}")
        self._depth += 1
        node.value.accept(self)
        self._depth -= 1


# ══════════════════════════════════════════════════════════════════════════════
#  Graphviz DOT generator
# ══════════════════════════════════════════════════════════════════════════════

class DotPrinter(ASTVisitor):
    """Generates a Graphviz DOT file from the AST."""

    # Node colours per category
    _COLOURS = {
        "program":     "#AED6F1",
        "declaration": "#A9DFBF",
        "statement":   "#FAD7A0",
        "expression":  "#F9E79F",
        "param":       "#D7BDE2",
    }

    def __init__(self) -> None:
        self._nodes: list[str] = []
        self._edges: list[str] = []
        self._counter: int = 0

    def generate(self, root: ASTNode) -> str:
        self._nodes.clear()
        self._edges.clear()
        self._counter = 0
        root.accept(self)
        lines = ["digraph AST {",
                 '  node [shape=box fontname="Courier"];']
        lines.extend(self._nodes)
        lines.extend(self._edges)
        lines.append("}")
        return '\n'.join(lines)

    def _new_id(self) -> str:
        self._counter += 1
        return f"n{self._counter}"

    def _node(self, label: str, category: str) -> str:
        nid    = self._new_id()
        colour = self._COLOURS.get(category, "#FFFFFF")
        safe   = label.replace('"', '\\"')
        self._nodes.append(
            f'  {nid} [label="{safe}" style=filled fillcolor="{colour}"];'
        )
        return nid

    def _edge(self, parent: str, child: str, label: str = "") -> None:
        lbl = f' [label="{label}"]' if label else ""
        self._edges.append(f"  {parent} -> {child}{lbl};")

    # All visitor methods share the same pattern: create node, recurse,
    # add edges.  Only a representative subset is shown for brevity.

    def visit_program(self, node: ProgramNode) -> str:
        nid = self._node("Program", "program")
        for decl in node.declarations:
            child = decl.accept(self)
            self._edge(nid, child)
        return nid

    def visit_function_decl(self, node: FunctionDeclNode) -> str:
        label = f"fn {node.name}\\n-> {node.return_type}"
        nid   = self._node(label, "declaration")
        for p in node.params:
            child = p.accept(self)
            self._edge(nid, child, "param")
        body = node.body.accept(self)
        self._edge(nid, body, "body")
        return nid

    def visit_struct_decl(self, node: StructDeclNode) -> str:
        nid = self._node(f"struct {node.name}", "declaration")
        for f in node.fields:
            child = f.accept(self)
            self._edge(nid, child, "field")
        return nid

    def visit_param(self, node: ParamNode) -> str:
        return self._node(f"param\\n{node.param_type} {node.name}", "param")

    def visit_block_stmt(self, node: BlockStmtNode) -> str:
        nid = self._node("Block", "statement")
        for s in node.statements:
            child = s.accept(self)
            self._edge(nid, child)
        return nid

    def visit_var_decl_stmt(self, node: VarDeclStmtNode) -> str:
        nid = self._node(f"VarDecl\\n{node.var_type} {node.name}", "statement")
        if node.initializer:
            child = node.initializer.accept(self)
            self._edge(nid, child, "init")
        return nid

    def visit_expr_stmt(self, node: ExprStmtNode) -> str:
        nid   = self._node("ExprStmt", "statement")
        child = node.expression.accept(self)
        self._edge(nid, child)
        return nid

    def visit_if_stmt(self, node: IfStmtNode) -> str:
        nid  = self._node("If", "statement")
        cond = node.condition.accept(self)
        self._edge(nid, cond, "cond")
        then = node.then_branch.accept(self)
        self._edge(nid, then, "then")
        if node.else_branch:
            else_ = node.else_branch.accept(self)
            self._edge(nid, else_, "else")
        return nid

    def visit_while_stmt(self, node: WhileStmtNode) -> str:
        nid  = self._node("While", "statement")
        cond = node.condition.accept(self)
        self._edge(nid, cond, "cond")
        body = node.body.accept(self)
        self._edge(nid, body, "body")
        return nid

    def visit_for_stmt(self, node: ForStmtNode) -> str:
        nid = self._node("For", "statement")
        if node.init:
            c = node.init.accept(self)
            self._edge(nid, c, "init")
        if node.condition:
            c = node.condition.accept(self)
            self._edge(nid, c, "cond")
        if node.update:
            c = node.update.accept(self)
            self._edge(nid, c, "update")
        body = node.body.accept(self)
        self._edge(nid, body, "body")
        return nid

    def visit_return_stmt(self, node: ReturnStmtNode) -> str:
        nid = self._node("Return", "statement")
        if node.value:
            child = node.value.accept(self)
            self._edge(nid, child, "value")
        return nid

    def visit_literal_expr(self, node: LiteralExprNode) -> str:
        return self._node(f"Literal\\n{node.kind}: {node.value!r}", "expression")

    def visit_identifier_expr(self, node: IdentifierExprNode) -> str:
        return self._node(f"Identifier\\n{node.name}", "expression")

    def visit_binary_expr(self, node: BinaryExprNode) -> str:
        nid   = self._node(f"Binary\\n{node.operator}", "expression")
        left  = node.left.accept(self)
        right = node.right.accept(self)
        self._edge(nid, left,  "left")
        self._edge(nid, right, "right")
        return nid

    def visit_unary_expr(self, node: UnaryExprNode) -> str:
        nid     = self._node(f"Unary\\n{node.operator}", "expression")
        operand = node.operand.accept(self)
        self._edge(nid, operand)
        return nid

    def visit_call_expr(self, node: CallExprNode) -> str:
        nid = self._node(f"Call\\n{node.callee}()", "expression")
        for i, arg in enumerate(node.arguments):
            child = arg.accept(self)
            self._edge(nid, child, f"arg{i}")
        return nid

    def visit_assignment_expr(self, node: AssignmentExprNode) -> str:
        nid   = self._node(f"Assign\\n{node.target} {node.operator}", "expression")
        child = node.value.accept(self)
        self._edge(nid, child, "value")
        return nid


# ══════════════════════════════════════════════════════════════════════════════
#  JSON serialiser
# ══════════════════════════════════════════════════════════════════════════════

class JsonPrinter(ASTVisitor):
    """Serialises the AST to a JSON-compatible dict tree."""

    def serialise(self, node: ASTNode) -> str:
        data = node.accept(self)
        return json.dumps(data, indent=2, default=str)

    def _loc(self, node: ASTNode) -> dict:
        return {"line": node.line, "column": node.column}

    def visit_program(self, node: ProgramNode) -> dict:
        return {
            "node": "Program",
            **self._loc(node),
            "declarations": [d.accept(self) for d in node.declarations],
        }

    def visit_function_decl(self, node: FunctionDeclNode) -> dict:
        return {
            "node": "FunctionDecl",
            **self._loc(node),
            "name": node.name,
            "return_type": node.return_type,
            "params": [p.accept(self) for p in node.params],
            "body": node.body.accept(self),
        }

    def visit_struct_decl(self, node: StructDeclNode) -> dict:
        return {
            "node": "StructDecl",
            **self._loc(node),
            "name": node.name,
            "fields": [f.accept(self) for f in node.fields],
        }

    def visit_param(self, node: ParamNode) -> dict:
        return {"node": "Param", **self._loc(node),
                "type": node.param_type, "name": node.name}

    def visit_block_stmt(self, node: BlockStmtNode) -> dict:
        return {"node": "Block", **self._loc(node),
                "statements": [s.accept(self) for s in node.statements]}

    def visit_var_decl_stmt(self, node: VarDeclStmtNode) -> dict:
        return {
            "node": "VarDecl", **self._loc(node),
            "type": node.var_type, "name": node.name,
            "initializer": node.initializer.accept(self) if node.initializer else None,
        }

    def visit_expr_stmt(self, node: ExprStmtNode) -> dict:
        return {"node": "ExprStmt", **self._loc(node),
                "expression": node.expression.accept(self)}

    def visit_if_stmt(self, node: IfStmtNode) -> dict:
        return {
            "node": "If", **self._loc(node),
            "condition":   node.condition.accept(self),
            "then_branch": node.then_branch.accept(self),
            "else_branch": node.else_branch.accept(self) if node.else_branch else None,
        }

    def visit_while_stmt(self, node: WhileStmtNode) -> dict:
        return {"node": "While", **self._loc(node),
                "condition": node.condition.accept(self),
                "body":      node.body.accept(self)}

    def visit_for_stmt(self, node: ForStmtNode) -> dict:
        return {
            "node": "For", **self._loc(node),
            "init":      node.init.accept(self) if node.init else None,
            "condition": node.condition.accept(self) if node.condition else None,
            "update":    node.update.accept(self) if node.update else None,
            "body":      node.body.accept(self),
        }

    def visit_return_stmt(self, node: ReturnStmtNode) -> dict:
        return {"node": "Return", **self._loc(node),
                "value": node.value.accept(self) if node.value else None}

    def visit_literal_expr(self, node: LiteralExprNode) -> dict:
        return {"node": "Literal", **self._loc(node),
                "kind": node.kind, "value": node.value,
                "type": node.resolved_type}

    def visit_identifier_expr(self, node: IdentifierExprNode) -> dict:
        return {"node": "Identifier", **self._loc(node),
                "name": node.name, "type": node.resolved_type}

    def visit_binary_expr(self, node: BinaryExprNode) -> dict:
        return {"node": "Binary", **self._loc(node),
                "operator": node.operator,
                "left":  node.left.accept(self),
                "right": node.right.accept(self),
                "type":  node.resolved_type}

    def visit_unary_expr(self, node: UnaryExprNode) -> dict:
        return {"node": "Unary", **self._loc(node),
                "operator": node.operator,
                "operand":  node.operand.accept(self),
                "type":     node.resolved_type}

    def visit_call_expr(self, node: CallExprNode) -> dict:
        return {"node": "Call", **self._loc(node),
                "callee": node.callee,
                "arguments": [a.accept(self) for a in node.arguments],
                "type": node.resolved_type}

    def visit_assignment_expr(self, node: AssignmentExprNode) -> dict:
        return {"node": "Assignment", **self._loc(node),
                "target": node.target, "operator": node.operator,
                "value": node.value.accept(self),
                "type":  node.resolved_type}