from expr import Expr


class Visitor:
    def visitExpressionStmt(stmt): raise NotImplementedError
    def visitPrintStmt(stmt): raise NotImplementedError


class Stmt:
    def accept(visitor: Visitor):
        raise NotImplementedError


class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: Visitor):
        return visitor.visitExpressionStmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: Visitor):
        return visitor.visitPrintStmt(self)
