from typing import List
from tokens import Token
from expr import Expr


__all__ = [
    "StmtVisitor",
    "Stmt",
    "Block",
    "Expression",
    "Print",
    "Var",
]


class StmtVisitor:
    def visitBlockStmt(stmt): raise NotImplementedError
    def visitExpressionStmt(stmt): raise NotImplementedError
    def visitPrintStmt(stmt): raise NotImplementedError
    def visitVarStmt(stmt): raise NotImplementedError


class Stmt:
    def accept(visitor: StmtVisitor):
        raise NotImplementedError


class Block(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def accept(self, visitor: StmtVisitor):
        return visitor.visitBlockStmt(self)


class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: StmtVisitor):
        return visitor.visitExpressionStmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: StmtVisitor):
        return visitor.visitPrintStmt(self)


class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: StmtVisitor):
        return visitor.visitVarStmt(self)
