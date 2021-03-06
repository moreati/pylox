from typing import List

from expr import *
from stmt import *
from tokens import Token, TokenType as tt


class RuntimeError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message

    def report(self):
        return f'{self.message}\n[line {self.token.line}]'


def truthy(value):
    """Return the truthiness of a value, according to Lox semantics.

    Lox follows Ruby's rule: false & nil are falsey, anything else is truthy. 
    """
    if value is None or value is False: return False
    return True


def floaty(value):
    """Return value if it is a float, otherwise raise a Python TypeError.

    Lox has one number type (float). There's no way to convert between types.

    This function should only be called only after checkNumberOperand().
    It is only backstop, hence why it can raises a Python specific exception.
    """
    if type(value) == float: return value
    raise TypeError


def stringy(value):
    """Return value if it is a str, otherwise raise a Python TypeError.

    Lox has one string type (str). There's no way to convert between types.

    This function should only be called only after checkNumberOperand().
    It is only backstop, hence why it can raises a Python specific exception.
    """
    if type(value) == str: return value
    raise TypeError


class Environment:
    def __init__(self, enclosing=None):
        self.enclosing = enclosing
        self.values = {}

    def define(self, name: str, value):
        self.values[name] = value

    def assign(self, name: Token, value):
        if name.lexeme in self.values:
            self.values[name] = value
        elif self.enclosing is not None:
            self.enclosing.assign(name, value)
        else:
            raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get(self, name: Token):
        try:
            return self.values[name.lexeme]
        except KeyError:
            if self.enclosing is not None:
                return self.enclosing.get(name)
            raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")


class Interpreter:
    def __init__(self):
        self.environment = Environment()
        self.errors = []

    def interpret(self, statements: list):
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError as error:
            self.errors.append(error)

    def visitLiteralExpr(self, expr: Literal):
        return expr.value

    def visitUnaryExpr(self, expr: Unary):
        right = self.evaluate(expr.right)

        type = expr.operator.type
        if type == tt.MINUS:
            self.checkNumberOperand(expr.operator, right)
            return -floaty(right)

        if type == tt.BANG:
            return not truthy(right)

        # Unreachable
        raise Exception('you dun goofed.')

    def visitVariableExpr(self, expr: Variable):
        return self.environment.get(expr.name)

    def vistGroupingExpr(self, expr: Grouping):
        return self.evaluate(expr)

    def visitBinaryExpr(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        type = expr.operator.type
        if type == tt.BANG_EQUAL:       return left != right
        if type == tt.EQUAL_EQUAL:      return left == right
        if type == tt.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return floaty(left) + floaty(right)
            elif isinstance(left, str) and isinstance(right, str):
                return stringy(left) + stringy(right)
            raise RuntimeError(expr.operator,
                               'Operands must be two numbers or two strings.')

        self.checkNumberOperands(expr.operator, left, right)
        if  type == tt.GREATER:         return floaty(left) >  floaty(right)
        elif type == tt.GREATER_EQUAL:  return floaty(left) >= floaty(right)
        elif type == tt.LESS:           return floaty(left) <  floaty(right)
        elif type == tt.LESS_EQUAL:     return floaty(left) <= floaty(right)
        elif type == tt.MINUS:          return floaty(left) -  floaty(right)
        elif type == tt.SLASH:          return floaty(left) /  floaty(right)
        elif type == tt.STAR:           return floaty(left) *  floaty(right)

        # Unreachable
        raise Exception('I dun goofed.')

    def checkNumberOperand(self, operator: Token, operand):
        if isinstance(operand, float): return
        raise RuntimeError(operator, 'Operand must be a number.')

    def checkNumberOperands(self, operator: Token, left, right):
        if isinstance(left, float) and isinstance(right, float): return
        raise RuntimeError(operator, 'Operands must be a numbers.')

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def execute(self, stmt: Stmt):
        stmt.accept(self)

    def executeBlock(self, statements: List[Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visitBlockStmt(self, stmt: Block):
        self.executeBlock(stmt.statements, Environment(self.environment))

    def visitExpressionStmt(self, stmt: Expression):
        self.evaluate(stmt.expression)
        return None

    def visitPrintStmt(self, stmt: Print):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visitVarStmt(self, stmt: Var):
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        else:
            value = None
        self.environment.define(stmt.name.lexeme, value)

    def visitAssignExpr(self, expr: Assign):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def stringify(self, value):
        if value is None:
            return 'nil'
        text = str(value)
        if isinstance(value, float) and text.endswith('.0'):
            return text[:-2]
        if isinstance(value, bool):
            return text.lower()
        return text
