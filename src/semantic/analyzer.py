"""
Semantic analyser: traverses the AST, populates the symbol table,
performs type checking, and decorates expression nodes with their types.
"""
from __future__ import annotations

from typing import Optional, Dict, List
from src.parser.ast_nodes import (
    ASTVisitor, ASTNode,
    ProgramNode, FunctionDeclNode, StructDeclNode, ParamNode,
    BlockStmtNode, VarDeclStmtNode, ExprStmtNode,
    IfStmtNode, WhileStmtNode, ForStmtNode, ReturnStmtNode,
    LiteralExprNode, IdentifierExprNode, BinaryExprNode,
    UnaryExprNode, CallExprNode, AssignmentExprNode,
)
from .symbol_table import SymbolTable, Symbol, SymbolKind
from .type_system import (
    Type, INT, FLOAT, BOOL, STRING, VOID, NULL,
    IntType, FloatType, BoolType, VoidType, StructType, FunctionType,
    BUILTIN_TYPES, resolve_type,
    binary_result_type, unary_result_type,
)
from .errors import ErrorReporter


class SemanticAnalyzer(ASTVisitor):
    """
    Single-pass semantic analyser implemented as an AST visitor.

    After calling analyze():
      - self.symbol_table  – fully populated
      - self.errors        – list of SemanticError
      - Every ExpressionNode.resolved_type is set to a type string
        (or 'error' on failure).
    """

    def __init__(self, filename: str = "<unknown>",
                 source: str = "") -> None:
        self.symbol_table = SymbolTable()
        self._reporter = ErrorReporter(filename, source)
        self._struct_registry: Dict[str, StructType] = {}
        self._current_function: Optional[FunctionDeclNode] = None
        self._current_return_type: Optional[Type] = None
        self._loop_depth: int = 0

    # ── Public API ─────────────────────────────────────────────────────────

    def analyze(self, ast: ProgramNode) -> bool:
        """
        Run semantic analysis.
        Returns True if no errors were found.
        """
        ast.accept(self)
        return not self._reporter.has_errors

    @property
    def errors(self):
        return self._reporter.errors

    @property
    def has_errors(self) -> bool:
        return self._reporter.has_errors

    def format_errors(self) -> str:
        return self._reporter.format_all()

    def summary(self) -> str:
        return self._reporter.summary()

    # ── Helpers ────────────────────────────────────────────────────────────

    def _err(self, msg: str, node: ASTNode, hint: str = "") -> None:
        ctx = ""
        if self._current_function:
            ctx = f"in function '{self._current_function.name}'"
        self._reporter.error(msg, node.line, node.column,
                             context=ctx, hint=hint)

    def _resolve_type(self, name: str, node: ASTNode) -> Type:
        t = resolve_type(name, self._struct_registry)
        if t is None:
            self._err(f"unknown type '{name}'", node)
            return VOID  # sentinel
        return t

    def _set_expr_type(self, node: ASTNode, t: Type) -> Type:
        """Annotate an expression node with its resolved type."""
        node.resolved_type = str(t)
        return t

    def _error_type(self, node: ASTNode) -> Type:
        node.resolved_type = "error"
        return VOID  # continue analysis with a safe sentinel

    def _lookup_value_type(self, name: str, node: ASTNode) -> Optional[Type]:
        """Resolve variables and simple struct fields like p.x."""
        parts = name.split('.')
        sym = self.symbol_table.lookup(parts[0])
        if sym is None:
            self._err(f"undeclared variable '{parts[0]}'", node)
            return None

        current_type = sym.type
        for field in parts[1:]:
            if not isinstance(current_type, StructType):
                self._err(f"'{'.'.join(parts[:-1])}' is not a struct", node)
                return None
            if field not in current_type.fields:
                self._err(f"struct '{current_type.name}' has no field '{field}'", node)
                return None
            current_type = current_type.fields[field]
        return current_type

    def _lookup_assign_symbol_and_type(self, name: str, node: ASTNode):
        """Return (base symbol, final target type) for x or p.x."""
        parts = name.split('.')
        sym = self.symbol_table.lookup(parts[0])
        if sym is None:
            self._err(f"assignment to undeclared variable '{parts[0]}'", node)
            return None, None
        if sym.kind not in {SymbolKind.VARIABLE, SymbolKind.PARAMETER}:
            self._err(f"'{parts[0]}' is not assignable (it is a {sym.kind})", node)
            return sym, None

        current_type = sym.type
        for field in parts[1:]:
            if not isinstance(current_type, StructType):
                self._err(f"'{'.'.join(parts[:-1])}' is not a struct", node)
                return sym, None
            if field not in current_type.fields:
                self._err(f"struct '{current_type.name}' has no field '{field}'", node)
                return sym, None
            current_type = current_type.fields[field]
        return sym, current_type

    # ══════════════════════════════════════════════════════════════════════
    #  Visitor implementations
    # ══════════════════════════════════════════════════════════════════════

    # ── Program ────────────────────────────────────────────────────────────

    def visit_program(self, node: ProgramNode) -> None:
        # Pass 1: register all struct types so functions can use them
        for decl in node.declarations:
            if isinstance(decl, StructDeclNode):
                self._register_struct(decl)

        # Pass 2: register all function signatures (forward references)
        for decl in node.declarations:
            if isinstance(decl, FunctionDeclNode):
                self._register_function_signature(decl)

        # Pass 3: fully analyse every declaration
        for decl in node.declarations:
            decl.accept(self)

    # ── Declarations ───────────────────────────────────────────────────────

    def _register_struct(self, node: StructDeclNode) -> None:
        if node.name in self._struct_registry:
            self._err(f"duplicate struct declaration '{node.name}'", node)
            return
        st = StructType(name=node.name)
        self._struct_registry[node.name] = st
        sym = Symbol(name=node.name, kind=SymbolKind.STRUCT,
                     type=st, decl_line=node.line, decl_column=node.column)
        self.symbol_table.define(sym)

    def _register_function_signature(self, node: FunctionDeclNode) -> None:
        param_types = [self._resolve_type(p.param_type, p)
                       for p in node.params]
        ret_type = self._resolve_type(node.return_type, node)
        fn_type = FunctionType(param_types=param_types,
                               return_type=ret_type)
        sym = Symbol(name=node.name, kind=SymbolKind.FUNCTION,
                     type=fn_type,
                     decl_line=node.line, decl_column=node.column)
        if not self.symbol_table.define(sym):
            self._err(f"duplicate function declaration '{node.name}'", node)

    def visit_struct_decl(self, node: StructDeclNode) -> None:
        st = self._struct_registry.get(node.name)
        if st is None:
            return  # error already reported in pass 1

        seen_fields: set[str] = set()
        for field_node in node.fields:
            if field_node.name in seen_fields:
                self._err(
                    f"duplicate field '{field_node.name}' "
                    f"in struct '{node.name}'",
                    field_node,
                )
            else:
                seen_fields.add(field_node.name)
                ftype = self._resolve_type(field_node.var_type, field_node)
                st.fields[field_node.name] = ftype

    def visit_function_decl(self, node: FunctionDeclNode) -> None:
        fn_sym = self.symbol_table.lookup_global(node.name)
        if fn_sym is None:
            return  # fatal duplicate – skip body

        ret_type = (fn_sym.type.return_type
                    if isinstance(fn_sym.type, FunctionType) else VOID)

        self._current_function = node
        self._current_return_type = ret_type

        self.symbol_table.enter_scope(f"fn:{node.name}")

        # Define parameters
        for param in node.params:
            ptype = self._resolve_type(param.param_type, param)
            sym = Symbol(name=param.name, kind=SymbolKind.PARAMETER,
                         type=ptype,
                         decl_line=param.line, decl_column=param.column,
                         is_initialized=True)
            if not self.symbol_table.define(sym):
                self._err(f"duplicate parameter '{param.name}'", param)

        # Analyse body
        node.body.accept(self)

        self.symbol_table.exit_scope()
        self._current_function = None
        self._current_return_type = None

    def visit_param(self, node: ParamNode) -> None:
        pass  # handled inside visit_function_decl

    # ── Statements ─────────────────────────────────────────────────────────

    def visit_block_stmt(self, node: BlockStmtNode) -> None:
        self.symbol_table.enter_scope("block")
        for stmt in node.statements:
            stmt.accept(self)
        self.symbol_table.exit_scope()

    def visit_var_decl_stmt(self, node: VarDeclStmtNode) -> None:
        vtype = self._resolve_type(node.var_type, node)

        # Check for duplicate in current scope
        existing = self.symbol_table.lookup_local(node.name)
        if existing is not None:
            self._err(
                f"variable '{node.name}' already declared in this scope",
                node,
                hint=(f"previously declared at "
                      f"{existing.decl_line}:{existing.decl_column}"),
            )

        initialized = False
        if node.initializer is not None:
            init_type = node.initializer.accept(self)
            if init_type is not None and not vtype.is_assignable_from(init_type):
                self._err(
                    f"type mismatch in initializer of '{node.name}': "
                    f"expected {vtype}, got {init_type}",
                    node.initializer,
                )
            initialized = True

        sym = Symbol(
            name=node.name, kind=SymbolKind.VARIABLE,
            type=vtype, decl_line=node.line, decl_column=node.column,
            is_initialized=initialized,
        )
        self.symbol_table.define(sym)
        node.resolved_type = str(vtype)

    def visit_expr_stmt(self, node: ExprStmtNode) -> None:
        node.expression.accept(self)

    def visit_if_stmt(self, node: IfStmtNode) -> None:
        cond_type = node.condition.accept(self)
        if cond_type is not None and not isinstance(cond_type, BoolType):
            self._err(
                f"condition in 'if' must be bool, got {cond_type}",
                node.condition,
            )
        node.then_branch.accept(self)
        if node.else_branch:
            node.else_branch.accept(self)

    def visit_while_stmt(self, node: WhileStmtNode) -> None:
        cond_type = node.condition.accept(self)
        if cond_type is not None and not isinstance(cond_type, BoolType):
            self._err(
                f"condition in 'while' must be bool, got {cond_type}",
                node.condition,
            )
        self._loop_depth += 1
        node.body.accept(self)
        self._loop_depth -= 1

    def visit_for_stmt(self, node: ForStmtNode) -> None:
        self.symbol_table.enter_scope("for")
        if node.init:
            node.init.accept(self)
        if node.condition:
            cond_type = node.condition.accept(self)
            if cond_type is not None and not isinstance(cond_type, BoolType):
                self._err(
                    f"condition in 'for' must be bool, got {cond_type}",
                    node.condition,
                )
        if node.update:
            node.update.accept(self)
        self._loop_depth += 1
        node.body.accept(self)
        self._loop_depth -= 1
        self.symbol_table.exit_scope()

    def visit_return_stmt(self, node: ReturnStmtNode) -> None:
        if self._current_return_type is None:
            self._err("'return' statement outside of a function", node)
            return

        if node.value is None:
            # bare return
            if not isinstance(self._current_return_type, VoidType):
                self._err(
                    f"function '{self._current_function.name}' must return "
                    f"{self._current_return_type}, not void",
                    node,
                )
            return

        ret_type = node.value.accept(self)
        if ret_type is None:
            return

        expected = self._current_return_type
        if not expected.is_assignable_from(ret_type):
            self._err(
                f"return type mismatch in '{self._current_function.name}': "
                f"expected {expected}, got {ret_type}",
                node,
                hint=f"function declared at "
                     f"{self._current_function.line}:"
                     f"{self._current_function.column}",
            )

    # ── Expressions ────────────────────────────────────────────────────────

    def visit_literal_expr(self, node: LiteralExprNode) -> Type:
        mapping = {
            'int': INT,
            'float': FLOAT,
            'bool': BOOL,
            'string': STRING,
            'null': NULL,
        }
        t = mapping.get(node.kind, VOID)
        return self._set_expr_type(node, t)

    def visit_identifier_expr(self, node: IdentifierExprNode) -> Type:
        t = self._lookup_value_type(node.name, node)
        if t is None:
            return self._error_type(node)

        # Use-before-initialization check only for plain variables.
        if '.' not in node.name:
            sym = self.symbol_table.lookup(node.name)
            if sym and sym.kind == SymbolKind.VARIABLE and not sym.is_initialized:
                self._err(f"variable '{node.name}' may be used before initialization", node)

        return self._set_expr_type(node, t)

    def visit_binary_expr(self, node: BinaryExprNode) -> Type:
        left_type = node.left.accept(self)
        right_type = node.right.accept(self)

        if left_type is None or right_type is None:
            return self._error_type(node)

        result = binary_result_type(node.operator, left_type, right_type)
        if result is None:
            self._err(
                f"operator '{node.operator}' cannot be applied to "
                f"{left_type} and {right_type}",
                node,
            )
            return self._error_type(node)

        return self._set_expr_type(node, result)

    def visit_unary_expr(self, node: UnaryExprNode) -> Type:
        operand_type = node.operand.accept(self)
        if operand_type is None:
            return self._error_type(node)

        result = unary_result_type(node.operator, operand_type)
        if result is None:
            self._err(
                f"unary operator '{node.operator}' cannot be applied "
                f"to {operand_type}",
                node,
            )
            return self._error_type(node)

        return self._set_expr_type(node, result)

    def visit_call_expr(self, node: CallExprNode) -> Type:
        sym = self.symbol_table.lookup(node.callee)
        if sym is None:
            self._err(f"call to undeclared function '{node.callee}'", node)
            return self._error_type(node)

        if not isinstance(sym.type, FunctionType):
            self._err(
                f"'{node.callee}' is not a function "
                f"(declared as {sym.kind})",
                node,
            )
            return self._error_type(node)

        fn_type = sym.type

        # Argument count
        expected_n = len(fn_type.param_types)
        actual_n = len(node.arguments)
        if expected_n != actual_n:
            self._err(
                f"wrong number of arguments to '{node.callee}': "
                f"expected {expected_n}, got {actual_n}",
                node,
                hint=f"function signature: {node.callee}{fn_type}",
            )
            # Still type-check as many args as we can

        for i, arg in enumerate(node.arguments):
            arg_type = arg.accept(self)
            if i < expected_n and arg_type is not None:
                expected_type = fn_type.param_types[i]
                if not expected_type.is_assignable_from(arg_type):
                    self._err(
                        f"argument {i + 1} to '{node.callee}': "
                        f"expected {expected_type}, got {arg_type}",
                        arg,
                    )

        return self._set_expr_type(node, fn_type.return_type)

    def visit_assignment_expr(self, node: AssignmentExprNode) -> Type:
        target_type = self._resolve_assignment_target_type(node.target, node)
        value_type = node.value.accept(self)

        if value_type is None:
            return self._error_type(node)


        if not target_type.is_assignable_from(value_type):

            self._err(
                f"type mismatch in assignment to '{node.target}': "
                f"expected {target_type}, got {value_type}",
                node,
            )
            return self._error_type(node)

        return self._set_expr_type(node, target_type)

        sym.is_initialized = True
        return self._set_expr_type(node, sym.type)

        sym.is_initialized = True
        return self._set_expr_type(node, target_type)

    def _resolve_assignment_target_type(self, target: str, node: ASTNode) -> Type:
        if "." not in target:
            sym = self.symbol_table.lookup(target)
            if sym is None:
                self._err(f"undeclared variable '{target}'", node)
                return VOID
            sym.is_initialized = True
            return sym.type

        base_name, field_name = target.split(".", 1)
        sym = self.symbol_table.lookup(base_name)

        if sym is None:
            self._err(f"undeclared variable '{base_name}'", node)
            return VOID

        if not isinstance(sym.type, StructType):
            self._err(f"'{base_name}' is not a struct", node)
            return VOID

        if field_name not in sym.type.fields:
            self._err(
                f"struct '{sym.type.name}' has no field '{field_name}'",
                node,
            )
            return VOID

        sym.is_initialized = True
        return sym.type.fields[field_name]