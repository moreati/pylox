#!/usr/bin/env python3.6

import os
import sys


def write_ast(output_dir: str, base_name: str, imports: dict, types: list):
    path = os.path.join(output_dir, base_name.lower() + '.py')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(''.join(define_ast(base_name, imports, types)))


def define_ast(base_name: str, imports: dict, types: list):
    for module, members in imports.items():
        yield f'from {module} import {members}\n'

    yield '\n\n'
    yield '__all__ = [\n'
    yield f'    "{base_name}Visitor",\n'
    yield f'    "{base_name}",\n'
    for type in types:
        class_name = type.split(':', maxsplit=1)[0].strip()
        yield f'    "{class_name}",\n'
    yield ']\n'

    yield '\n\n'
    yield from define_visitor(base_name, types)

    yield '\n\n'
    yield f'class {base_name}:\n'
    # The base accept() method.
    yield f'    def accept(visitor: {base_name}Visitor):\n'
    yield '        raise NotImplementedError\n'

    # The AST classes.
    for type in types:
        yield '\n\n'
        class_name = type.split(':', maxsplit=1)[0].strip()
        fields_sig = type.split(':', maxsplit=1)[1].strip()
        yield from define_type(base_name, class_name, fields_sig)


def define_visitor(base_name: str, types: list):
    yield f'class {base_name}Visitor:\n'

    for type in types:
        type_name = type.split(':', maxsplit=1)[0].strip()
        yield f'    def visit{type_name}{base_name}({base_name.lower()}): '
        yield f'raise NotImplementedError\n'


def define_type(base_name: str, class_name: str, fields_sig: str):
    yield f'class {class_name}({base_name}):\n'

    # Initialiser.
    yield f'    def __init__(self, {fields_sig}):\n'

    # Store parameters in fields.
    fields = fields_sig.split(', ')
    for field in fields:
        name = field.split(': ')[0]
        yield f'        self.{name} = {name}\n'

    yield f'\n'
    yield f'    def accept(self, visitor: {base_name}Visitor):\n'
    yield f'        return visitor.visit{class_name}{base_name}(self)\n'


def main(argv):
    prog = argv.pop(0)
    if len(argv) != 1:
        print(f'Usage: {prog} <output directory>', file=sys.stderr)
        sys.exit(1)

    output_dir = argv[0]

    write_ast(output_dir, 'Expr', {'tokens': 'Token'}, [
        'Assign   : name: Token, value: Expr',
        'Binary   : left: Expr, operator: Token, right: Expr',
        'Grouping : expression: Expr',
        'Literal  : value',
        'Unary    : operator: Token, right: Expr',
        'Variable : name: Token',
    ])

    write_ast(output_dir, 'Stmt', {'tokens': 'Token', 'expr': 'Expr'}, [
        'Expression : expression: Expr',
        'Print      : expression: Expr',
        'Var        : name: Token, initializer: Expr',
    ])
if __name__ == '__main__':
    main(sys.argv)
