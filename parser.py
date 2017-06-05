from typing import List

from expr import *
from stmt import *
from tokens import Token, TokenType, TokenType as tt


class ParseError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message

    def report(self):
        if self.token.type == tt.EOF:
            return f'[line {self.token.line}] Error at end: {self.message}'
        else:
            where = self.token.lexeme
            return f"[line {self.token.line}] Error at '{where}': {self.message}"


class Parser:
    """
    program     = statement* EOF ;

    statement   = exprStmt
                | printStmt ;

    exprStmt    = expression ";" ;
    printStmt   = "print" expression ";" ;

    expression → equality
    equality   → comparison ( ( "!=" | "==" ) comparison )*
    comparison → term ( ( ">" | ">=" | "<" | "<=" ) term )*
    term       → factor ( ( "-" | "+" ) factor )*
    factor     → unary ( ( "/" | "*" ) unary )*
    unary      → ( "!" | "-" ) unary
               | primary
    primary    → NUMBER | STRING | "false" | "true" | "nil"
               | "(" expression ")"
    """
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.errors = []
        self.current = 0

    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.statement())
        return statements

    def expression(self):
        return self.equality()

    def statement(self):
        if self.match(tt.PRINT): return self.printStatement()
        return self.expressionStatement()

    def printStatement(self):
        value = self.expression()
        self.consume(tt.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def expressionStatement(self):
        expr = self.expression()
        self.consume(tt.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)

    def equality(self):
        expr = self.comparison()
        while self.match(tt.BANG_EQUAL, tt.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(tt.GREATER, tt.GREATER_EQUAL, tt.LESS, tt.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self):
        expr = self.factor()
        while self.match(tt.MINUS, tt.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(tt.SLASH, tt.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self):
        if self.match(tt.BANG, tt.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.primary()

    def primary(self):
        if   self.match(tt.FALSE):  return Literal(False)
        elif self.match(tt.TRUE):   return Literal(True)
        elif self.match(tt.NIL):    return Literal(None)
        elif self.match(tt.NUMBER,
                        tt.STRING): return Literal(self.previous().literal)

        elif self.match(tt.LEFT_PAREN):
            expr = self.expression()
            self.consume(tt.RIGHT_PAREN, "Expect ')' after expression")
            return Grouping(expr)

        raise self.error(self.peek(), 'Expect expression')

    def match(self, *types: List[TokenType]):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def consume(self, type: TokenType, message: str):
        if self.check(type):
            return self.advance()

    def check(self, type: TokenType):
        if self.is_at_end():
            return False
        return self.peek().type == type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == tt.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def error(self, token: Token, message: str):
        err = ParseError(token, message)
        self.errors.append(err)
        return err

    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().type == tt.SEMICOLON:
                return

            if self.peek().type in {
                    tt.CLASS,
                    tt.FUN,
                    tt.VAR,
                    tt.FOR,
                    tt.IF,
                    tt.WHILE,
                    tt.PRINT,
                    tt.RETURN,
                }:
                return

            self.advance()
