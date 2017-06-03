#!/usr/bin/env python3

import sys 

from expr import *
from pylox import Token, TokenType

class AstPrinter:
    def print(self, expr: Expr):
        return expr.accept(self)

    def visitBinaryExpr(self, expr: Binary):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visitGroupingExpr(self, expr: Grouping):
        return self.parenthesize('group', expr.expression)

    def visitLiteralExpr(self, expr: Literal):
        return str(expr.value)

    def visitUnaryExpr(self, expr: Unary):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name, *exprs):
        fragments = []
        fragments.append('(')
        fragments.append(name)
        for expr in exprs:
            fragments.append(' ')
            fragments.append(expr.accept(self))
        fragments.append(')')

        return ''.join(fragments)


def main(argv):
    expression = Binary(
        Unary(
            Token(TokenType.MINUS, '-', None, 1),
            Literal(123)
        ),
        Token(TokenType.STAR, '*', None, 1),
        Grouping(
            Literal(45.67)
        )
    )
    print(AstPrinter().print(expression))


if __name__ == '__main__':
    main(sys.argv)
