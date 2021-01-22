#!/usr/bin/env python3

from run import Commands
import sys
## make the stacktrace for infinite mutual recursion smaller
#sys.setrecursionlimit(100)

class ParseError(Exception):
	def __init__(self, message, line=None):
		self.message = message
		self.line = line
	
	def __repr__(self):
		if self.line is None:
			return "ParseError(\"{}\")".format(self.message)
		else:
			return "ParseError(\"{}\", {})".format(self.message, str(self.line))

class Token:
	IDENT = "ident"
	NUM = "num"
	MACRODEF = "!"
	LABEL = ":"
	REFERENCE = "@"
	BUILTIN = "."
	STRING = "str"
	def __init__(self, typ, text, linenum):
		self.typ = typ
		self.text = text
		self.linenum = linenum

def tokenize_char(c, letters):
	if c == "\\":
		n = letters.pop(0)
		if n == "n":
			return "\n"
		elif n == "t":
			return "\t"
		elif n == "r":
			return "\r"
		else:
			return n
	else:
		return c


def tokenize(text):
	tokens = []
	linenum = 1
	letters = list(text)
	while len(letters):
		ch = letters.pop(0)
		if ch.isspace():
			if ch == "\n":
				linenum += 1
			continue
		tokenl = []
		typ = None
		if ch == "#":
			while len(letters) and letters.pop(0) != "\n":
				pass
			linenum += 1
			continue
		elif ch.isdecimal() or (ch == "-" and len(letters) and letters[0].isdecimal()):
			tokenl.append(ch)
			while len(letters) and letters[0].isdecimal():
				tokenl.append(letters.pop(0))
			typ = Token.NUM
		elif ch.isalpha() or ch == "_":
			tokenl.append(ch)
			while len(letters) and (letters[0].isalpha() or letters[0].isdecimal() or letters[0] == "_"):
				tokenl.append(letters.pop(0))
			typ = Token.IDENT
		elif ch in "(){[]}!":
			typ = ch
		elif ch in ":@":
			if len(letters) == 0:
				raise ParseError("line ended unexpectedly")
			if not (letters[0].isalpha() or letters[0] == "_"):
				raise ParseError("invalid starting character of label/references", linenum)
			tokenl.append(letters.pop(0))
			while len(letters) and letters[0].isalnum() or letters[0] == "_":
				tokenl.append(letters.pop(0))
			typ = ch
		elif ch == ".":
			if len(letters) == 0:
				raise ParseError("line parsing ended unexpectedly", linenum)
			while len(letters) and letters[0].isalpha():
				tokenl.append(letters.pop(0))
			typ = ch
		elif ch == "'":
			if len(letters) == 0:
				raise ParseError("unterminated string", linenum)
			c = letters.pop(0)
			if c == "\n":
				linenum += 1
			tokenl.extend(list(str(ord(tokenize_char(c, letters)))))
			typ = Token.NUM
		elif ch == '"':
			while True:
				if len(letters) == 0:
					raise ParseError("unterminated string", linenum)
				c = letters.pop(0)
				if c == "\n":
					linenum += 1
				if c == '"':
					break
				tokenl.append(tokenize_char(c, letters))
			typ = Token.STRING
		else:
			raise ParseError("Unknown token character: '{}'".format(ch), linenum)
		if typ is not None:
			tokens.append(Token(typ, "".join(tokenl), linenum))
	return tokens



class Node:
	def __repr__(self):
		return "{}({})".format(
			type(self).__name__,
			", ".join(
				"{}={}".format(key, val)
					for key, val in self.__dict__.items()
					if len(key) != 0 and key[0] != "_"
			)
		)

class BuiltinNode(Node):
	def __init__(self, name, linenum):
		self.name = name
		self.linenum = linenum
class CallNode(Node):
	def __init__(self, name, args, linenum):
		self.name = name
		self.args = args
		self.linenum = linenum
class NumberNode(Node):
	def __init__(self, val, linenum):
		self.val = val
		self.linenum = linenum
class BlockNode(Node):
	def __init__(self, code, linenum):
		self.code = code
		self.linenum = linenum
class LabelNode(Node):
	def __init__(self, name, linenum):
		self.name = name
		self.linenum = linenum
class ReferenceNode(Node):
	def __init__(self, name, linenum):
		self.name = name
		self.linenum = linenum
class MacroDefNode(Node):
	def __init__(self, name, args, body, labels, linenum):
		self.name = name
		self.args = args
		self.body = body
		self.labels = labels
		self.linenum = linenum
class RawNode(Node):
	def __init__(self, code, linenum):
		self.code = code
		self.linenum = linenum


def parse_command(tokens):
	token = tokens.pop(0)
	typ = token.typ
	if typ == Token.IDENT:
		args = []
		if tokens[0].typ == "(":
			tokens.pop(0)
			while True:
				if len(tokens) == 0:
					raise ParseError("no matching close tag for macro call arguments", token.linenum)
				if tokens[0].typ == ")":
					tokens.pop(0)
					break
				args.append(parse_command(tokens))
		return CallNode(token.text, args, token.linenum)
	elif typ == Token.MACRODEF:
		if len(tokens) == 0 or tokens[0].typ != Token.IDENT:
			raise ParseError("macro has no name")
		name = tokens.pop(0).text
		if len(tokens) == 0:
			raise ParseError("macro has no body")
		args = []
		if tokens[0].typ == "(":
			tokens.pop(0)
			while True:
				if len(tokens) == 0:
					raise ParseError("no matching close tag for macro arguments", token.linenum)
				t = tokens.pop(0)
				if t.typ == ")":
					break
				args.append(t.text)
		if len(tokens) == 0:
			raise ParseError("macro has no body")
		labels = []
		if tokens[0].typ == "(":
			tokens.pop(0)
			while True:
				if len(tokens) == 0:
					raise ParseError("no matching close tag for macro labels", token.linenum)
				t = tokens.pop(0)
				if t.typ == ")":
					break
				if t.typ != Token.LABEL:
					raise ParseError("non label in labels field", token.linenum)
				labels.append(t.text)
		if len(tokens) == 0:
			raise ParseError("macro has no body", token.linenum)
		body = parse_command(tokens)
		return MacroDefNode(name, args, body, labels, token.linenum)
	elif typ == Token.BUILTIN:
		return BuiltinNode(token.text, token.linenum)
	elif typ == Token.LABEL:
		return LabelNode(token.text, token.linenum)
	elif typ == Token.REFERENCE:
		return ReferenceNode(token.text, token.linenum)
	elif typ == Token.NUM:
		return NumberNode(int(token.text), token.linenum)
	elif typ == "{":
		code = []
		while True:
			if len(tokens) == 0:
				raise ParseError("No matching close tag for a code block", token.linenum)
			if tokens[0].typ == "}":
				tokens.pop(0)
				break
			code.append(parse_command(tokens))
		return BlockNode(code, token.linenum)
	elif typ == Token.STRING:
		return RawNode([Literal(ord(c)) for c in token.text], token.linenum)
	elif typ == "[":
		code = []
		while True:
			if len(tokens) == 0:
				raise ParseError("No matching close tag for a raw block", token.linenum)
			if tokens[0].typ == "]":
				tokens.pop(0)
				break
			node = parse_command(tokens)
			if isinstance(node, NumberNode):
				code.append(Literal(node.val % (2**32)))
			elif isinstance(node, ReferenceNode):
				code.append(Reference(node.name))
			elif isinstance(node, LabelNode):
				code.append(Label(node.name))
			else:
				raise ParseError("Raw blocks may only contain numbers and references", token.linenum)
		return RawNode(code, token.linenum)
	else:
		raise ParseError("Invalid start of a command: '{}': '{}'".format(token.typ, token.text), token.linenum)



class Label:
	def __init__(self, name):
		self.name = name
class Reference:
	def __init__(self, name):
		self.name = name
class Command:
	def __init__(self, command):
		self.command = command
class Literal:
	def __init__(self, val):
		self.val = val


class Substitution:
	def __init__(self, body, substitutionscope, args=None, labels=None):
		self.body = body
		self.substitutionscope = substitutionscope
		self.args = args if args is not None else []
		self.labels = labels if labels is not None else []
		
	def __repr__(self):
		return "Substitution({}, {}, {})".format(self.body, self.args, self.labels)

scopeid = 1


def compile_tree(node, substitutions, scope):
	code = []
	if isinstance(node, BuiltinNode):
		comm = Commands.__dict__.get(node.name.upper())
		if comm == None:
			raise Exception("Unknown builtin command {} on line {}".format(node.name, node.linenum))
		code.append(Command(comm))
	if isinstance(node, RawNode):
		code.extend(node.code)
	elif isinstance(node, BlockNode):
		for command in node.code:
			code.extend(compile_tree(command, substitutions, scope))
	elif isinstance(node, MacroDefNode):
		substitutions[node.name] = Substitution(node.body, substitutions.copy(), node.args, node.labels)
	elif isinstance(node, CallNode):
		sub = substitutions.get(node.name)
		if sub == None:
			raise Exception("Unknown call '{}' on line {}".format(node.name, node.linenum))
		assert isinstance(sub, Substitution), sub
		if len(sub.args) != len(node.args):
			raise Exception("macro definition of {} has {} as arguments, but call has {} as arguments on line {}".format(node.name, sub.args, node.args, node.linenum))
		bodysubs = sub.substitutionscope.copy()
		bodysubs.update({
			argname: Substitution(RawNode(compile_tree(argbody, substitutions.copy(), scope), argbody.linenum), {}) 
				for argname, argbody in zip(sub.args, node.args)})
		global scopeid
		scopeid += 1
		bodysubs.update({labelname: Substitution(RawNode([Command(Commands.PUSH), Reference(labelname+":"+str(scopeid))], node.linenum), {}) for labelname in sub.labels})
		code.extend(compile_tree(sub.body, bodysubs, scopeid))
	elif isinstance(node, NumberNode):
		code.append(Command(Commands.PUSH))
		code.append(Literal(node.val % (2**32)))
	elif isinstance(node, LabelNode):
		name = node.name
		if scope != 0:
			name += ":" + str(scope)
		code.append(Label(name))
	elif isinstance(node, ReferenceNode):
		code.append(Command(Commands.PUSH))
		code.append(Reference(node.name))
	return code


def link(unlinked):
	refcode = []
	labels = {}
	while len(unlinked):
		item = unlinked.pop(0)
		if isinstance(item, Label):
			labels[item.name] = len(refcode)
		else:
			refcode.append(item)
	code = []
	for item in refcode:
		if isinstance(item, Reference):
			location = labels.get(item.name)
			if location == None:
				raise Exception("Reference {} without a matching label".format(item.name))
			code.append(location)
		elif isinstance(item, Literal):
			code.append(item.val)
		elif isinstance(item, Command):
			code.append(item.command)
		else:
			raise Exception("Unknown code type encountered when linking: {}".format(item))
	return code

def compile_code(text):
	tokens = tokenize(text)
	tree = parse_command(tokens)
	unlinkedcode = compile_tree(tree, {}, 0)
	code = link(unlinkedcode)
	return code
	

def writehex(code, fname):
	codetext = "\n".join(format(c, "08X") for c in code)
	with open(fname, "w") as fo:
		fo.write(codetext)

def main():
	ashex = False
	if len(sys.argv) > 1:
		fname = sys.argv[1]
		if fname == "--hex":
			fname = sys.argv[2]
			ashex = True
		with open(fname) as f:
			sourcecode = f.read()
		outfname = fname.rpartition(".")[0] + ".tebat"
	else:
		sourcecode = sys.stdin.read()
		outfname = "code.tebat"
	code = compile_code(sourcecode)
	if ashex:
		writehex(code, outfname)
	else:
		codebytes = b"".join(command.to_bytes(4, "little") for command in code)
		with open(outfname, "wb") as fo:
			fo.write(codebytes)
	




if __name__ == "__main__":
	main()
