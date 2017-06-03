#!/usr/bin/env python3

import enum
import sys


had_error = False


@enum.unique
class TokenType(enum.Enum):
    # Single-character tokens.
    LEFT_PAREN      = 1
    RIGHT_PAREN     = 2
    LEFT_BRACE      = 3
    RIGHT_BRACE     = 4
    COMMA           = 5
    DOT             = 6
    MINUS           = 7
    PLUS            = 8
    SEMICOLON       = 9
    SLASH           = 10
    STAR            = 11

    # One or two character tokens.
    BANG            = 12
    BANG_EQUAL      = 13
    EQUAL           = 14
    EQUAL_EQUAL     = 15
    GREATER         = 16
    GREATER_EQUAL   = 17
    LESS            = 18
    LESS_EQUAL      = 19

    # Literals.
    IDENTIFIER      = 20
    STRING          = 21
    NUMBER          = 22

    # Keywords.
    AND             = 23
    CLASS           = 24
    ELSE            = 25
    FALSE           = 26
    FUN             = 27
    FOR             = 28
    IF              = 29
    NIL             = 30
    OR              = 31
    PRINT           = 32
    RETURN          = 33
    SUPER           = 34
    THIS            = 35
    TRUE            = 36
    VAR             = 37
    WHILE           = 38

    EOF             = 39

tt = TokenType

class Token:
    def __init__(self, type: TokenType, lexeme: str, literal, line: int):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return '%s %s %s' % (self.type, self.lexeme, self.literal)


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
            error(self.line, 'Unexpected character.')

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
            error(self.line, 'Unterminated string.')
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


def run_file(path: str):
    with open(path, encoding='utf-8') as file:
        run(file.read())
    if had_error:
        sys.exit(65)

def run_prompt():
    while True:
        run(input('> '))


def run(source: str):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    for token in tokens:
        print(token)


def error(line: int, message: str):
    report(line, '', message)


def report(line: int, where: str, message: str):
    global had_error

    print('[line %i] Error%s: %s' % (line, where, message), file=sys.stderr)
    had_error = True


def main(argv: list):
    prog = argv.pop(0)
    if len(argv) > 1:
        print("Usage: %s [script]" % prog, file=sys.stderr)
    elif len(argv) == 1:
        run_file(argv[0])
    else:
        run_prompt()


if __name__ == '__main__':
    main(sys.argv)
