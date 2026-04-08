from src.parser.ast import *
from .symbol_table import SymbolTable, SymbolInfo, SymbolKind
from .type_system import PrimitiveType, StructType, FunctionType, Type
from .errors import SemanticError

class SemanticAnalyzer:
    def __init__(self):
        self.sym_table = SymbolTable()
        self.errors = []
        self.current_function = None   # SymbolInfo текущей функции
        self.in_loop = False           # для break/continue (если будут)

    def analyze(self, program: ProgramNode):
        # Проход 1: регистрация глобальных объявлений (функции, структуры)
        self._register_declarations(program)
        # Проход 2: проверка тел функций и глобальных переменных
        self._check_bodies(program)
        return self.errors

    def _register_declarations(self, node: ASTNode):
        if isinstance(node, ProgramNode):
            for decl in node.declarations:
                self._register_declarations(decl)
        elif isinstance(node, FunctionDeclNode):
            # Создаём тип функции
            param_types = [self._type_from_str(p.param_type) for p in node.parameters]
            ret_type = self._type_from_str(node.return_type)
            func_type = FunctionType(param_types, ret_type)
            # Проверка дубликата
            existing = self.sym_table.lookup(node.name)
            if existing:
                self._error(f"Duplicate function '{node.name}'", node.line, node.column, 'duplicate')
                return
            # Создаём символ функции
            func_sym = SymbolInfo(
                name=node.name,
                kind=SymbolKind.FUNCTION,
                type=func_type,
                line=node.line,
                column=node.column,
                parameters=[]  # заполним позже
            )
            self.sym_table.insert(func_sym)
            node.symbol = func_sym
            # Запоминаем параметры (пока без типов, только имена)
            # Реальные параметры будут добавлены при входе в тело
        elif isinstance(node, StructDeclNode):
            # Регистрация структуры
            existing = self.sym_table.lookup(node.name)
            if existing:
                self._error(f"Duplicate struct '{node.name}'", node.line, node.column, 'duplicate')
                return
            # Сначала вычислим поля
            fields = {}
            for field in node.fields:
                field_type = self._type_from_str(field.var_type)
                if field.name in fields:
                    self._error(f"Duplicate field '{field.name}' in struct '{node.name}'",
                                field.line, field.column, 'duplicate')
                else:
                    fields[field.name] = field_type
            struct_type = StructType(node.name, fields)
            struct_sym = SymbolInfo(
                name=node.name,
                kind=SymbolKind.STRUCT,
                type=struct_type,
                line=node.line,
                column=node.column,
                fields=fields
            )
            self.sym_table.insert(struct_sym)
            node.symbol = struct_sym
        elif isinstance(node, VarDeclStmtNode):
            # Глобальная переменная
            var_type = self._type_from_str(node.var_type)
            existing = self.sym_table.lookup(node.name)
            if existing:
                self._error(f"Duplicate global variable '{node.name}'", node.line, node.column, 'duplicate')
                return
            var_sym = SymbolInfo(
                name=node.name,
                kind=SymbolKind.VARIABLE,
                type=var_type,
                line=node.line,
                column=node.column
            )
            self.sym_table.insert(var_sym)
            node.symbol = var_sym
            # Если есть инициализатор, проверим позже во втором проходе
        # Другие узлы не имеют объявлений на глобальном уровне

    def _check_bodies(self, node: ASTNode):
        if isinstance(node, ProgramNode):
            for decl in node.declarations:
                self._check_bodies(decl)
        elif isinstance(node, FunctionDeclNode):
            # Вход в функцию: новая область видимости
            self.sym_table.enter_scope(f"function {node.name}")
            # Добавляем параметры как символы
            param_syms = []
            for param in node.parameters:
                param_type = self._type_from_str(param.param_type)
                param_sym = SymbolInfo(
                    name=param.name,
                    kind=SymbolKind.PARAMETER,
                    type=param_type,
                    line=param.line,
                    column=param.column
                )
                if not self.sym_table.insert(param_sym):
                    self._error(f"Duplicate parameter '{param.name}'", param.line, param.column, 'duplicate')
                param_syms.append(param_sym)
                param.symbol = param_sym
            # Сохраняем параметры в символе функции
            node.symbol.parameters = param_syms
            # Запоминаем текущую функцию
            old_func = self.current_function
            self.current_function = node.symbol
            # Проверяем тело
            self._check_bodies(node.body)
            # Выход из функции
            self.sym_table.exit_scope()
            self.current_function = old_func
        elif isinstance(node, BlockStmtNode):
            self.sym_table.enter_scope("block")
            for stmt in node.statements:
                self._check_bodies(stmt)
            self.sym_table.exit_scope()
        elif isinstance(node, VarDeclStmtNode):
            # Локальная переменная
            var_type = self._type_from_str(node.var_type)
            existing = self.sym_table.lookup_local(node.name)
            if existing:
                self._error(f"Duplicate variable '{node.name}' in same scope", node.line, node.column, 'duplicate')
                return
            var_sym = SymbolInfo(
                name=node.name,
                kind=SymbolKind.VARIABLE,
                type=var_type,
                line=node.line,
                column=node.column
            )
            self.sym_table.insert(var_sym)
            node.symbol = var_sym
            if node.initializer:
                init_type = self._check_expression(node.initializer)
                if init_type and not var_type.is_convertible_to(init_type):
                    self._error(f"Type mismatch: cannot assign {init_type} to {var_type}",
                                node.initializer.line, node.initializer.column, 'type_mismatch')
        elif isinstance(node, ExprStmtNode):
            self._check_expression(node.expression)
        elif isinstance(node, IfStmtNode):
            cond_type = self._check_expression(node.condition)
            if cond_type and not (isinstance(cond_type, PrimitiveType) and cond_type.name == 'bool'):
                self._error(f"If condition must be bool, got {cond_type}",
                            node.condition.line, node.condition.column, 'type_mismatch')
            self._check_bodies(node.then_branch)
            if node.else_branch:
                self._check_bodies(node.else_branch)
        elif isinstance(node, WhileStmtNode):
            cond_type = self._check_expression(node.condition)
            if cond_type and not (isinstance(cond_type, PrimitiveType) and cond_type.name == 'bool'):
                self._error(f"While condition must be bool, got {cond_type}",
                            node.condition.line, node.condition.column, 'type_mismatch')
            old_loop = self.in_loop
            self.in_loop = True
            self._check_bodies(node.body)
            self.in_loop = old_loop
        elif isinstance(node, ForStmtNode):
            # For: init может быть VarDeclStmtNode или ExprStmtNode
            if node.init:
                self._check_bodies(node.init)
            if node.condition:
                cond_type = self._check_expression(node.condition)
                if cond_type and not (isinstance(cond_type, PrimitiveType) and cond_type.name == 'bool'):
                    self._error(f"For condition must be bool, got {cond_type}",
                                node.condition.line, node.condition.column, 'type_mismatch')
            if node.update:
                self._check_expression(node.update)
            old_loop = self.in_loop
            self.in_loop = True
            self._check_bodies(node.body)
            self.in_loop = old_loop
        elif isinstance(node, ReturnStmtNode):
            if self.current_function is None:
                self._error("Return statement outside function", node.line, node.column, 'invalid')
                return
            ret_type = self.current_function.type.return_type
            if node.value:
                val_type = self._check_expression(node.value)
                if val_type and not val_type.is_convertible_to(ret_type):
                    self._error(f"Return type mismatch: expected {ret_type}, got {val_type}",
                                node.value.line, node.value.column, 'type_mismatch')
            else:
                # Пустой return: допустим только для void
                if not (isinstance(ret_type, PrimitiveType) and ret_type.name == 'void'):
                    self._error(f"Non-void function must return a value",
                                node.line, node.column, 'type_mismatch')
        elif isinstance(node, AssignmentExprNode):
            # Проверка присваивания
            target_type = self._check_expression(node.target)
            value_type = self._check_expression(node.value)
            if target_type and value_type:
                if not value_type.is_convertible_to(target_type):
                    self._error(f"Cannot assign {value_type} to {target_type}",
                                node.line, node.column, 'type_mismatch')
            node.type = target_type   # тип выражения присваивания = тип левой части
        # ... другие узлы

    def _check_expression(self, expr: ExpressionNode) -> Optional[Type]:
        if isinstance(expr, LiteralExprNode):
            # Определяем тип литерала
            if isinstance(expr.value, int):
                expr.type = PrimitiveType('int')
            elif isinstance(expr.value, float):
                expr.type = PrimitiveType('float')
            elif isinstance(expr.value, str):
                expr.type = PrimitiveType('string')
            elif isinstance(expr.value, bool):
                expr.type = PrimitiveType('bool')
            else:
                expr.type = None
            return expr.type
        elif isinstance(expr, IdentifierExprNode):
            sym = self.sym_table.lookup(expr.name)
            if sym is None:
                self._error(f"Undeclared variable '{expr.name}'", expr.line, expr.column, 'undeclared')
                expr.type = None
            else:
                expr.type = sym.type
                expr.symbol = sym
            return expr.type
        elif isinstance(expr, BinaryExprNode):
            left_type = self._check_expression(expr.left)
            right_type = self._check_expression(expr.right)
            if left_type is None or right_type is None:
                expr.type = None
                return None
            op = expr.op
            # Правила для арифметики
            if op in ('+', '-', '*', '/', '%'):
                # int+int -> int, int+float -> float, float+float -> float
                if isinstance(left_type, PrimitiveType) and isinstance(right_type, PrimitiveType):
                    if left_type.name == 'int' and right_type.name == 'int':
                        expr.type = PrimitiveType('int')
                    else:
                        expr.type = PrimitiveType('float')
                else:
                    self._error(f"Arithmetic operator {op} requires numeric types, got {left_type} and {right_type}",
                                expr.line, expr.column, 'type_mismatch')
                    expr.type = None
            elif op in ('==', '!=', '<', '<=', '>', '>='):
                # Сравнение: типы должны быть совместимы, результат bool
                if left_type.is_convertible_to(right_type) or right_type.is_convertible_to(left_type):
                    expr.type = PrimitiveType('bool')
                else:
                    self._error(f"Cannot compare {left_type} and {right_type} with {op}",
                                expr.line, expr.column, 'type_mismatch')
                    expr.type = None
            elif op == '&&' or op == '||':
                if (isinstance(left_type, PrimitiveType) and left_type.name == 'bool' and
                    isinstance(right_type, PrimitiveType) and right_type.name == 'bool'):
                    expr.type = PrimitiveType('bool')
                else:
                    self._error(f"Logical operator {op} requires bool, got {left_type} and {right_type}",
                                expr.line, expr.column, 'type_mismatch')
                    expr.type = None
            else:
                expr.type = None
            return expr.type
        elif isinstance(expr, UnaryExprNode):
            operand_type = self._check_expression(expr.operand)
            if operand_type is None:
                expr.type = None
                return None
            if expr.op == '-':
                if isinstance(operand_type, PrimitiveType) and operand_type.name in ('int', 'float'):
                    expr.type = operand_type
                else:
                    self._error(f"Unary minus requires numeric type, got {operand_type}",
                                expr.line, expr.column, 'type_mismatch')
                    expr.type = None
            elif expr.op == '!':
                if isinstance(operand_type, PrimitiveType) and operand_type.name == 'bool':
                    expr.type = PrimitiveType('bool')
                else:
                    self._error(f"Logical not requires bool, got {operand_type}",
                                expr.line, expr.column, 'type_mismatch')
                    expr.type = None
            else:
                expr.type = None
            return expr.type
        elif isinstance(expr, CallExprNode):
            # Проверка вызова функции
            callee_type = self._check_expression(expr.callee)
            if callee_type is None:
                expr.type = None
                return None
            if not isinstance(callee_type, FunctionType):
                self._error(f"Can only call functions, got {callee_type}",
                            expr.line, expr.column, 'type_mismatch')
                expr.type = None
                return None
            # Проверка аргументов
            arg_types = [self._check_expression(arg) for arg in expr.arguments]
            expected_types = callee_type.param_types
            if len(arg_types) != len(expected_types):
                self._error(f"Function expects {len(expected_types)} arguments, got {len(arg_types)}",
                            expr.line, expr.column, 'argument_count')
                expr.type = callee_type.return_type
                return expr.type
            for i, (arg_t, exp_t) in enumerate(zip(arg_types, expected_types)):
                if arg_t and not arg_t.is_convertible_to(exp_t):
                    self._error(f"Argument {i+1} type mismatch: expected {exp_t}, got {arg_t}",
                                expr.arguments[i].line, expr.arguments[i].column, 'argument_type')
            expr.type = callee_type.return_type
            return expr.type
        # Добавить обработку AssignmentExprNode
        elif isinstance(expr, AssignmentExprNode):
            # Уже обработано в _check_bodies, но для целостности:
            self._check_expression(expr.target)
            self._check_expression(expr.value)
            expr.type = expr.target.type if expr.target.type else None
            return expr.type
        else:
            return None

    def _type_from_str(self, type_str: str) -> Type:
        if type_str in ('int', 'float', 'bool', 'void', 'string'):
            return PrimitiveType(type_str)
        else:
            # Возможно, это имя структуры (будет найдено при регистрации)
            # Пока создадим заглушку, но лучше искать в таблице символов
            sym = self.sym_table.lookup(type_str)
            if sym and sym.kind == SymbolKind.STRUCT:
                return sym.type
            else:
                # Если структура не объявлена, вернём примитив? Лучше ошибку позже
                return PrimitiveType(type_str)  # временно

    def _error(self, message: str, line: int, column: int, category: str):
        self.errors.append(SemanticError(message, line, column, category))