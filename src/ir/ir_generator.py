"""
IR Generator for Sprint 4.
Compatible with Python 3.8+.
"""
from __future__ import annotations

from typing import List, Optional

from src.parser.ast_nodes import (
    ASTVisitor,
    ProgramNode, FunctionDeclNode, StructDeclNode, ParamNode,
    BlockStmtNode, VarDeclStmtNode, ExprStmtNode,
    IfStmtNode, WhileStmtNode, ForStmtNode, ReturnStmtNode,
    LiteralExprNode, IdentifierExprNode, BinaryExprNode,
    UnaryExprNode, CallExprNode, AssignmentExprNode,
)

from .basic_block import IRProgram, IRFunction, BasicBlock
from .control_flow import LabelManager
from .ir_instructions import IRInstruction


class IRGenerator(ASTVisitor):
    _BIN_OPS = {
        "+": "ADD",
        "-": "SUB",
        "*": "MUL",
        "/": "DIV",
        "%": "MOD",
        "&&": "AND",
        "||": "OR",
        "==": "CMP_EQ",
        "!=": "CMP_NE",
        "<": "CMP_LT",
        "<=": "CMP_LE",
        ">": "CMP_GT",
        ">=": "CMP_GE",
    }

    _ASSIGN_COMPOUND = {
        "+=": "ADD",
        "-=": "SUB",
        "*=": "MUL",
        "/=": "DIV",
    }

    def __init__(self) -> None:
        self.program = IRProgram()
        self.current_function: Optional[IRFunction] = None
        self.current_block: Optional[BasicBlock] = None
        self.labels = LabelManager()
        self._temp_counter = 0

    def generate(self, ast: ProgramNode) -> IRProgram:
        self.program = IRProgram()
        self.current_function = None
        self.current_block = None
        self.labels = LabelManager()
        self._temp_counter = 0
        ast.accept(self)
        return self.program

    def get_all_ir(self) -> IRProgram:
        return self.program

    def get_function_ir(self, name: str) -> IRFunction:
        return self.program.get_function(name)

    def dump(self) -> str:
        return self.program.dump()

    def _new_temp(self) -> str:
        self._temp_counter += 1
        return f"t{self._temp_counter}"

    def _emit(self, opcode: str, dest: Optional[str] = None,
              args: Optional[List[str]] = None, comment: str = "") -> IRInstruction:
        if self.current_block is None:
            raise RuntimeError("IR emit attempted outside a basic block")
        instr = IRInstruction(opcode=opcode, dest=dest, args=args or [], comment=comment)
        self.current_block.add(instr)
        return instr

    def _start_block(self, label: str) -> BasicBlock:
        if self.current_function is None:
            raise RuntimeError("Cannot create basic block outside a function")
        self.current_block = self.current_function.new_block(label)
        return self.current_block

    def _const_text(self, node: LiteralExprNode) -> str:
        if node.kind == "bool":
            return "true" if bool(node.value) else "false"
        if node.kind == "string":
            return chr(34) + str(node.value).replace(chr(34), "\\\"") + chr(34)
        return str(node.value)

    def visit_program(self, node: ProgramNode) -> None:
        for decl in node.declarations:
            decl.accept(self)

    def visit_struct_decl(self, node: StructDeclNode) -> None:
        return None

    def visit_function_decl(self, node: FunctionDeclNode) -> None:
        params = [f"{p.name}: {p.param_type}" for p in node.params]
        fn = IRFunction(name=node.name, return_type=node.return_type, params=params)
        self.program.add_function(fn)

        prev_fn = self.current_function
        prev_block = self.current_block

        self.current_function = fn
        self._start_block("entry")

        for param in node.params:
            fn.locals[param.name] = param.param_type

        node.body.accept(self)

        if self.current_block is not None:
            if not self.current_block.instructions or self.current_block.instructions[-1].opcode != "RETURN":
                if node.return_type == "void":
                    self._emit("RETURN")

        self.current_function = prev_fn
        self.current_block = prev_block

    def visit_param(self, node: ParamNode) -> None:
        return None

    def visit_block_stmt(self, node: BlockStmtNode) -> None:
        for stmt in node.statements:
            stmt.accept(self)

    def visit_var_decl_stmt(self, node: VarDeclStmtNode) -> None:
        if self.current_function is not None:
            self.current_function.locals[node.name] = node.var_type

        if node.initializer is not None:
            value = node.initializer.accept(self)
            self._emit("STORE", args=[node.name, value], comment=f"{node.name} initialization")
        else:
            self._emit("DECLARE", args=[node.var_type, node.name])

    def visit_expr_stmt(self, node: ExprStmtNode) -> None:
        node.expression.accept(self)

    def visit_if_stmt(self, node: IfStmtNode) -> None:
        cond = node.condition.accept(self)
        else_label = self.labels.new_label("else")
        end_label = self.labels.new_label("endif")

        if node.else_branch is not None:
            self._emit("JUMP_IF_NOT", args=[cond, else_label], comment="if condition false")
        else:
            self._emit("JUMP_IF_NOT", args=[cond, end_label], comment="if condition false")

        node.then_branch.accept(self)
        self._emit("JUMP", args=[end_label])

        if node.else_branch is not None:
            self._start_block(else_label)
            node.else_branch.accept(self)
            self._emit("JUMP", args=[end_label])

        self._start_block(end_label)

    def visit_while_stmt(self, node: WhileStmtNode) -> None:
        header = self.labels.new_label("while")
        body = self.labels.new_label("while_body")
        end = self.labels.new_label("while_end")

        self._emit("JUMP", args=[header])
        self._start_block(header)

        cond = node.condition.accept(self)
        self._emit("JUMP_IF_NOT", args=[cond, end])

        self._start_block(body)
        node.body.accept(self)
        self._emit("JUMP", args=[header])

        self._start_block(end)

    def visit_for_stmt(self, node: ForStmtNode) -> None:
        if node.init is not None:
            node.init.accept(self)

        header = self.labels.new_label("for")
        body = self.labels.new_label("for_body")
        end = self.labels.new_label("for_end")

        self._emit("JUMP", args=[header])
        self._start_block(header)

        if node.condition is not None:
            cond = node.condition.accept(self)
            self._emit("JUMP_IF_NOT", args=[cond, end])

        self._start_block(body)
        node.body.accept(self)

        if node.update is not None:
            node.update.accept(self)

        self._emit("JUMP", args=[header])
        self._start_block(end)

    def visit_return_stmt(self, node: ReturnStmtNode) -> None:
        if node.value is None:
            self._emit("RETURN")
        else:
            value = node.value.accept(self)
            self._emit("RETURN", args=[value])

    def visit_literal_expr(self, node: LiteralExprNode) -> str:
        return self._const_text(node)

    def visit_identifier_expr(self, node: IdentifierExprNode) -> str:
        temp = self._new_temp()
        self._emit("LOAD", dest=temp, args=[node.name])
        return temp

    def visit_binary_expr(self, node: BinaryExprNode) -> str:
        left = node.left.accept(self)
        right = node.right.accept(self)
        temp = self._new_temp()
        opcode = self._BIN_OPS.get(node.operator, f"BINOP_{node.operator}")
        self._emit(opcode, dest=temp, args=[left, right], comment=node.operator)
        return temp

    def visit_unary_expr(self, node: UnaryExprNode) -> str:
        value = node.operand.accept(self)
        temp = self._new_temp()

        if node.operator == "-":
            self._emit("NEG", dest=temp, args=[value])
        elif node.operator == "!":
            self._emit("NOT", dest=temp, args=[value])
        else:
            self._emit(f"UNARY_{node.operator}", dest=temp, args=[value])

        return temp

    def visit_call_expr(self, node: CallExprNode) -> str:
        args = [arg.accept(self) for arg in node.arguments]
        temp = self._new_temp()
        self._emit("CALL", dest=temp, args=[node.callee] + args)
        return temp

    def visit_assignment_expr(self, node: AssignmentExprNode) -> str:
        value = node.value.accept(self)

        if node.operator == "=":
            self._emit("STORE", args=[node.target, value], comment=f"{node.target} =")
            return value

        opcode = self._ASSIGN_COMPOUND.get(node.operator)
        if opcode is None:
            self._emit("STORE", args=[node.target, value], comment=f"{node.target} {node.operator}")
            return value

        old_value = self._new_temp()
        result = self._new_temp()
        self._emit("LOAD", dest=old_value, args=[node.target])
        self._emit(opcode, dest=result, args=[old_value, value], comment=node.operator)
        self._emit("STORE", args=[node.target, result])
        return result
