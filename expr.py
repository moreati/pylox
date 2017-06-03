from pylox import Token


class Visitor:
    def visitBinaryExpr(expr): raise NotImplementedError
    def visitGroupingExpr(expr): raise NotImplementedError
    def visitLiteralExpr(expr): raise NotImplementedError
    def visitUnaryExpr(expr): raise NotImplementedError


class Expr:
    def accept(visitor: Visitor):
        raise NotImplementedError


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: Visitor):
        return visitor.visitBinaryExpr(self)


class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: Visitor):
        return visitor.visitGroupingExpr(self)


class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor: Visitor):
        return visitor.visitLiteralExpr(self)


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor: Visitor):
        return visitor.visitUnaryExpr(self)
