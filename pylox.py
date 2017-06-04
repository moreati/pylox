#!/usr/bin/env python3.6

import functools
import sys

from astprinter import AstPrinter
from parser import Parser
from tokens import Token, TokenType, TokenType as tt


class ScanError(Exception):
    def __init__(self, line: int, message: str):
        self.line = line
        self.message = message

    def report(self):
        return f'[line {self.line}] Error: {self.message}'


class Scanner:
    keywords = {
        'and':    tt.AND,
        'class':  tt.CLASS,
        'else':   tt.ELSE,
        'false':  tt.FALSE,
        'for':    tt.FOR,
        'fun':    tt.FUN,
        'if':     tt.IF,
        'nil':    tt.NIL,
        'or':     tt.OR,
        'print':  tt.PRINT,
        'return': tt.RETURN,
        'super':  tt.SUPER,
        'this':   tt.THIS,
        'true':   tt.TRUE,
        'var':    tt.VAR,
        'while':  tt.WHILE,
    }

    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.errors = []

        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(tt.EOF, '', None, self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()
        if   c == '(': self.add_token(tt.LEFT_PAREN)
        elif c == ')': self.add_token(tt.RIGHT_PAREN)
        elif c == '{': self.add_token(tt.LEFT_BRACE)
        elif c == '}': self.add_token(tt.RIGHT_BRACE)
        elif c == ',': self.add_token(tt.COMMA)
        elif c == '.': self.add_token(tt.DOT)
        elif c == '-': self.add_token(tt.MINUS)
        elif c == '+': self.add_token(tt.PLUS)
        elif c == ';': self.add_token(tt.SEMICOLON)
        elif c == '*': self.add_token(tt.STAR)
        elif c == '!':
            if self.match('='): self.add_token(tt.BANG_EQUAL)
            else:               self.add_token(tt.BANG)
        elif c == '=':
            if self.match('='): self.add_token(tt.EQUAL_EQUAL)
            else:               self.add_token(tt.EQUAL)
        elif c == '<':
            if self.match('='): self.add_token(tt.LESS_EQUAL)
            else:               self.add_token(tt.LESS)
        elif c == '>':
            if self.match('='): self.add_token(tt.GREATER_EQUAL)
            else:               self.add_token(tt.GREATER)
        elif c == '/':
            if self.match('/'):
                # A comment goes until the end of the line
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(tt.SLASH)
        elif c in (' ', '\r', '\t'):
            # Ignore whitespace.
            pass
        elif c == '\n': self.line += 1
        elif c == '"': self.string()
        elif self.is_digit(c): self.number()
        elif self.is_alpha(c): self.identifier()
        else:
            self.error('Unexpected character.')

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()

        # Look for fractional part.
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            # Consume the '.'
            self.advance()

            while self.is_digit(self.peek()):
                self.advance()

        self.add_token(tt.NUMBER, float(self.source[self.start:self.current]))

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        # Unterminated string.
        if self.is_at_end():
            self.error('Unterminated string.')
            return

        # The closing ".
        self.advance()

        # Trim the surrounding quotes
        value = self.source[self.start+1 : self.current - 1]
        self.add_token(tt.STRING, value)

    def identifier(self):
        while self.is_alphanumeric(self.peek()):
            self.advance()

        # See if the identifier is a reserved word.
        text = self.source[self.start:self.current]
        type = self.keywords.get(text, tt.IDENTIFIER)
        self.add_token(type)

    def match(self, expected: str):
        if self.is_at_end(): return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self):
        if self.current >= len(self.source):
            return '\0'
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def is_digit(self, c):
        return '0' <= c <= '9'

    def is_alpha(self, c):
        return 'a' <= c <= 'z' or 'A' <= c <= 'Z' or c == '_'

    def is_alphanumeric(self, c):
        return self.is_alpha(c) or self.is_digit(c)

    def is_at_end(self):
        return bool(self.current >= len(self.source))

    def advance(self):
        self.current += 1
        return self.source[self.current-1]

    def add_token(self, type: TokenType, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def error(self, message):
        err = ScanError(self.line, message)
        self.errors.append(err)


def run_file(path: str):
    with open(path, encoding='utf-8') as file:
        errors = run(file.read())
    if errors:
        sys.exit(65)

def run_prompt():
    while True:
        run(input('> '))


def run(source: str):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    expression = parser.parse()

    errors = scanner.errors + parser.errors
    for error in  errors:
        print(error.report(), file=sys.stderr)

    # Stop if there was a syntax error.
    if errors:
        return errors

    print(AstPrinter.print(expression))


def main(argv: list):
    prog = argv.pop(0)
    if len(argv) > 1:
        print(f"Usage: {prog} [script]", file=sys.stderr)
        sys.exit(1)
    elif len(argv) == 1:
        run_file(argv[0])
    else:
        run_prompt()


if __name__ == '__main__':
    main(sys.argv)
