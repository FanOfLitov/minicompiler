"""
Explicit, manually crafted unit tests for the MiniCompiler Parser.
Compatible with Python 3.8+.
"""
import pytest
from typing import List, Tuple
from src.lexer.scanner import Scanner
from src.parser.parser import Parser, ParserDiagnostic
from src.parser.ast_nodes import (
    ProgramNode, FunctionDeclNode, StructDeclNode,
    BlockStmtNode, VarDeclStmtNode, IfStmtNode,
    WhileStmtNode, ForStmtNode, ReturnStmtNode, ExprStmtNode,
    LiteralExprNode, IdentifierExprNode, BinaryExprNode,
    UnaryExprNode, CallExprNode, AssignmentExprNode,
)


def parse_source(source: str) -> Tuple[ProgramNode, List[ParserDiagnostic]]:
    scanner = Scanner(source)
    tokens = scanner.scan_all()
    parser = Parser(tokens)
    program = parser.parse()
    return program, parser.errors


def parse_assert_ok(source: str) -> ProgramNode:
    program, errors = parse_source(source)
    assert program is not None, f"Parser returned None. Errors: {[str(e) for e in errors]}"
    assert len(errors) == 0, f"Expected no parse errors, but got: {[str(e) for e in errors]}"
    return program


# ══════════════════════════════════════════════════════════════════════════════
#  Top-Level Declarations Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestParserDeclarations:
    def test_empty_program(self):
        prog = parse_assert_ok("")
        assert isinstance(prog, ProgramNode)
        assert len(prog.declarations) == 0

    def test_function_no_params_void(self):
        prog = parse_assert_ok("fn main() { }")
        assert len(prog.declarations) == 1
        fn = prog.declarations[0]
        assert isinstance(fn, FunctionDeclNode)
        assert fn.name == "main"
        assert fn.return_type == "void"
        assert len(fn.params) == 0
        assert isinstance(fn.body, BlockStmtNode)
        assert len(fn.body.statements) == 0

    def test_function_with_params_and_return_type(self):
        prog = parse_assert_ok("fn add(int a, float b) -> float { }")
        fn = prog.declarations[0]
        assert isinstance(fn, FunctionDeclNode)
        assert fn.name == "add"
        assert fn.return_type == "float"
        assert len(fn.params) == 2
        assert fn.params[0].name == "a"
        assert fn.params[0].param_type == "int"
        assert fn.params[1].name == "b"
        assert fn.params[1].param_type == "float"

    def test_struct_declaration(self):
        prog = parse_assert_ok("struct Vector { int x; int y; }")
        st = prog.declarations[0]
        assert isinstance(st, StructDeclNode)
        assert st.name == "Vector"
        assert len(st.fields) == 2
        assert st.fields[0].name == "x"
        assert st.fields[0].var_type == "int"
        assert st.fields[1].name == "y"
        assert st.fields[1].var_type == "int"


# ══════════════════════════════════════════════════════════════════════════════
#  Statement Nodes Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestParserStatements:
    def test_variable_declaration_stmt(self):
        prog = parse_assert_ok("fn test() { int x = 42; }")
        fn = prog.declarations[0]
        stmt = fn.body.statements[0]
        assert isinstance(stmt, VarDeclStmtNode)
        assert stmt.var_type == "int"
        assert stmt.name == "x"
        assert isinstance(stmt.initializer, LiteralExprNode)
        assert stmt.initializer.value == 42

    def test_if_else_statement(self):
        prog = parse_assert_ok("fn test() { if (true) { return 1; } else { return 0; } }")
        fn = prog.declarations[0]
        stmt = fn.body.statements[0]
        assert isinstance(stmt, IfStmtNode)
        assert isinstance(stmt.condition, LiteralExprNode)
        assert stmt.condition.value is True
        assert isinstance(stmt.then_branch, BlockStmtNode)
        assert isinstance(stmt.else_branch, BlockStmtNode)

    def test_while_statement(self):
        prog = parse_assert_ok("fn test() { while (false) { } }")
        fn = prog.declarations[0]
        stmt = fn.body.statements[0]
        assert isinstance(stmt, WhileStmtNode)
        assert isinstance(stmt.condition, LiteralExprNode)
        assert stmt.condition.value is False
        assert isinstance(stmt.body, BlockStmtNode)

    def test_for_statement(self):
        prog = parse_assert_ok("fn test() { for (int i = 0; i < 5; i += 1) { } }")
        fn = prog.declarations[0]
        stmt = fn.body.statements[0]
        assert isinstance(stmt, ForStmtNode)
        assert isinstance(stmt.init, VarDeclStmtNode)
        assert isinstance(stmt.condition, BinaryExprNode)
        assert isinstance(stmt.update, AssignmentExprNode)
        assert isinstance(stmt.body, BlockStmtNode)


# ══════════════════════════════════════════════════════════════════════════════
#  Expressions (Operator Precedence & Associativity)
# ══════════════════════════════════════════════════════════════════════════════

class TestParserExpressions:
    def test_primary_literals(self):
        prog = parse_assert_ok("fn test() { float f = 3.14; string s = \"hello\"; bool b = null; }")
        stmts = prog.declarations[0].body.statements
        assert stmts[0].initializer.value == 3.14
        assert stmts[1].initializer.value == "hello"
        assert stmts[2].initializer.value is None

    def test_operator_precedence_mul_over_add(self):
        # x = 1 + 2 * 3; => x = 1 + (2 * 3);
        prog = parse_assert_ok("fn test() { int x = 1 + 2 * 3; }")
        stmt = prog.declarations[0].body.statements[0]
        expr = stmt.initializer
        assert isinstance(expr, BinaryExprNode)
        assert expr.operator == "+"
        assert isinstance(expr.left, LiteralExprNode)
        assert expr.left.value == 1
        assert isinstance(expr.right, BinaryExprNode)
        assert expr.right.operator == "*"

    def test_operator_associativity_left(self):
        # x = 10 - 5 - 2; => (10 - 5) - 2;
        prog = parse_assert_ok("fn test() { int x = 10 - 5 - 2; }")
        stmt = prog.declarations[0].body.statements[0]
        expr = stmt.initializer
        assert isinstance(expr, BinaryExprNode)
        assert expr.operator == "-"
        assert isinstance(expr.left, BinaryExprNode)
        assert expr.left.operator == "-"
        assert expr.right.value == 2

    def test_unary_operators(self):
        prog = parse_assert_ok("fn test() { bool x = !false; }")
        stmt = prog.declarations[0].body.statements[0]
        expr = stmt.initializer
        assert isinstance(expr, UnaryExprNode)
        assert expr.operator == "!"
        assert isinstance(expr.operand, LiteralExprNode)
        assert expr.operand.value is False

    def test_function_call(self):
        prog = parse_assert_ok("fn test() { foo(1, x); }")
        stmt = prog.declarations[0].body.statements[0]
        assert isinstance(stmt, ExprStmtNode)
        call = stmt.expression
        assert isinstance(call, CallExprNode)
        assert call.callee == "foo"
        assert len(call.arguments) == 2
        assert isinstance(call.arguments[0], LiteralExprNode)
        assert isinstance(call.arguments[1], IdentifierExprNode)


# ══════════════════════════════════════════════════════════════════════════════
#  Syntax Error Recovery Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestParseErrors:
    def test_missing_semicolon(self):
        program, errors = parse_source("fn test() { int x = 42 }")
        assert len(errors) == 1
        assert "expected ';'" in errors[0].message

    def test_mismatched_brackets(self):
        program, errors = parse_source("fn test() { foo(1; }")
        assert len(errors) >= 1

    def test_recovery_finds_multiple_errors(self):
        # С введением точек синхронизации типов парсер теперь корректно изолирует
        # обе ошибки и находит ровно две проблемы.
        program, errors = parse_source("fn test() { int x = 1 int y = 2 }")
        assert len(errors) == 2
        assert "expected ';'" in errors[0].message
        assert "expected ';'" in errors[1].message