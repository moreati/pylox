## Pylox

An interpreter for Lox from [Crafting Interpreters] by [Bob Nystrom].
Pylox is incomplete and not intended to be useful, even as a reference.
It is *learning in progress*. I'm merely translating Java snippets to Python
3.x as I read through the book.

### Differences to jlox

## Lox

[Lox] is a high-level programming language created as a teaching aid.
It has a C-like syntax, dynamic typing, automatic memory management, first
class functions, closures, and class-based object orientation.

The standand library contains a single function: `clock()`. Code examples
tend to be breakfast themed.

Crafting Interpreters includes 2 implementations of Lox: [jlox] & [clox].
Readers have also implmented various other [lox implementations].

[bob nystrom]: http://stuffwithstuff.com/
[clox]: https://github.com/munificent/craftinginterpreters/tree/master/c
[crafting interpreters]: http://craftinginterpreters.com/
[jlox]: https://github.com/munificent/craftinginterpreters/tree/master/java/com/craftinginterpreters
[lox]: http://craftinginterpreters.com/the-lox-language.html
[lox implementations]: https://github.com/munificent/craftinginterpreters/wiki/Lox-implementations
