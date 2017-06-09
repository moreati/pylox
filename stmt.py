from expr import Expr


__all__ = [
    "StmtVisitor",
    "Stmt",
    "Expression",
    "Print",
    "Var",
]


class StmtVisitor:
    def visitExpressionStmt(stmt): raise NotImplementedError
    def visitPrintStmt(stmt): raise NotImplementedError


class Stmt:
    def accept(visitor: StmtVisitor):
        raise NotImplementedError


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
