
# Temat

The temat language is intented to be a very minimal language, but with a macro system that can make it very expressive.

An identifier refers to a string that consists of a letter or underscore followed by zero or more letters, underscores and/or digits

## Comments

A comment starts with a `#` character and goes on to the end of a line

## Builtin commands

Temat 'builtin' commands translate directly to tebat commands.
Builtins start with a dot character (`.`) followed by the name of the command in lowercase letters.
See [tebat_specification.md](tebat_specification.md) for a list of available commmands

## Number literals

A number literal is a sequence of digits.
This is translated into a tebat PUSH command, followed by the value of this number.
The number is a 32 bit integer.
The number can have a minus (`-`) as prefix.
There must be no space between the minus and the digits
The values `-1` and `4294967295` are equivalent.

### Character literal

A character literal is also a number literal.
A character literal either consists of a single quote character (`'`) followed by a backslash (`\\`) followed by another character, or it consists of a single quote followed by any other character.
In the form without the backslash it just pushes the ascii index of the character.
In the form with the backslash followed by `n`, `r` and `t` it will escape those characters to linefeed, carriage return and tab respectively.
If the backslash is followed by any other character then the ascii code of that character is just pushed.
Examples: `'A` is equivalent to `65` and `'\A`. `'\\` is equivalent to `92`. `\n` is equivalent to `10`

## Label

A label is an address of some code that can be referenced from other places in the code.
A label starts with a `:` character and is followed by an identifier.

## Reference

A reference is like a number literal, but it refers to a label and at the end of compilation it will be replaced with the memory location of the label it refers to.
A reference starts with a `@` character and is followed by an identifier.
This identifier must match the identifier for a label.

Just like with a number literal this value is pushed on the stack.

## Raw block

A raw block starts with a `[` character, ends with a `]` character and may only contain number literals, labels and references.
For a number literal or reference the value will not be pushed in the stack, but it will be included verbatim as a word in the source code.
It is up to the programmer to jump over this word to make sure that it is not executed as an instruction instead.

## String literal

A string literal is a sort of raw block that consists only of characters.
A string literal starts and ends with a `"`.
Within a string literal the same escape codes as in a character literal apply.
Escaped `"` characters do not end a string literal.
Just like with a raw block the resulting words are placed verbatim into the source code and it is up to the programmer to prevent executing these words as instructions.

## Block

A block allows writing multiple or zero statements in a location where one statement is expected.
A block starts with `{` and ends with `}`.
Blocks can be nested.

## Macro definition

A macro definition creates a new macro.
A macro definition starts with a `!` character, followed by the macro name (an identifier), optionally followed by an argument list between parentheses, optionally followed by a label list between parentheses, followed by a statement.
The following are all equivalent valid macros:

	!nop .noop
	!nop() .noop
	!nop()() .noop
	!nop {.noop}
	!nop(){.noop}
	!nop()(){.noop}

If an argument list is present then each element of that list must be an identifier.
If a label list is present then each element of that list must be an identifier prefixed with `:`.
The body consists of one statement, but this can be made into multiple (or zero) statements using a block statement.

When calling a macro, an identifier in the macro body that is the same as the macro argument will be replaced with the code that is given for that macro argument.

If a macro body contains a label that is in also in the label list then the name will be mangled so it is unique to that macro invocation.
The identifier with the name of that label will be replaced with a reference to that mangled label.

Macro definitions within a macro body are only valid within the scope of that macro body.

Examples:

	!jumpifz(condition to){condition to .jumpifz}
	
	!not(a){a .not}
	
	!dowhile (body condition)(:whilestart) {
		:whilestart
		body
		jumpifz(not(condition) whilestart)
	}


## Macro call

A macro call calls a defined macro
A macro call starts with an identifier, optionally followed by an argument list between parentheses.
An identifier by itself could either be a macro call, a macro argument or a reference to a mangled macro label.
Macro arguments are evaluated before the substitution is performed.
Macro definitions within the arguments of a macro call are only valid within that argument.

