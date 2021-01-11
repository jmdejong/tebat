
from run import Commands

class ParseError(Exception):
	def __init__(self, message, line=None):
		self.message = message
		self.line = line
	
	def __repr__(self):
		if self.line is None:
			return "ParseError(\"{}\")".format(self.message)
		else:
			return "ParseError(\"{}\", {})".format(self.message, str(self.line))

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
		if ch == "#":
			while len(letters) and letters.pop(0) != "\n":
				pass
			linenum += 1
		elif ch.isdecimal() or ch == "-":
			tokenl.append(ch)
			while len(letters) and letters[0].isdecimal():
				tokenl.append(letters.pop(0))
		elif ch.isalpha():
			tokenl.append(ch)
			while len(letters) and letters[0].isalpha():
				tokenl.append(letters.pop(0))
		elif ch in "(){}[]":
			tokenl.append(ch)
		elif ch in ":@":
			tokenl.append(ch)
			if len(letters) == 0:
				raise ParseError("line ended unexpectedly")
			while len(letters) and letters[0].isalnum():
				tokenl.append(letters.pop(0))
		elif ch in "!.":
			tokenl.append(ch)
			if len(letters) == 0:
				raise ParseError("line parsing ended unexpectedly")
			while len(letters) and letters[0].isalpha():
				tokenl.append(letters.pop(0))
		elif ch == '"':
			tokenl = [ch]
			while True:
				if len(letters) == 0:
					raise ParseError("unterminated string")
				c = letters.pop(0)
				if c == "\n":
					linenum += 1
				if c == '"':
					break
				elif c == "\\":
					n = letters.pop(0)
					if n == "n":
						tokenl.append("\n")
					elif n == "t":
						tokenl.append("\t")
					else:
						tokenl.append(n)
				else:
					tokenl.append(c)
		else:
			raise ParseError("Unknown token character: '{}'".format(ch))
		if len(tokenl):
			tokens.append(("".join(tokenl), linenum))
	return tokens



class Node:
	pass

class BuiltinNode(Node):
	def __init__(self, name):
		self.name = name

class CallNode(Node):
	def __init__(self, name, args):
		self.name = name
		self.args = args

class NumberNode(Node):
	def __init__(self, val):
		self.val = val

class BlockNode(Node):
	def __init__(self, code):
		self.code = code

class LabelNode(Node):
	def __init__(self, name):
		self.name = name

class ReferenceNode(Node):
	def __init__(self, name):
		self.name = name

class MacroDefNode(Node):
	def __init__(self, name, args, body, labels):
		self.name = name
		self.args = args
		self.body = body
		self.labels = labels

class CodeNode(Node):
	def __init__(self, code):
		self.code = code


def isnum(token):
	return token.isdecimal() or token != "" and token[0] == "-" and token[1:].isdecimal()

def parse_command(tokens):
	(token, linenum) = tokens.pop(0)
	
	if token.isalpha():
		args = []
		if tokens[0][0] == "(":
			tokens.pop(0)
			while True:
				if len(tokens) == 0:
					raise ParseError("no matching close tag for call arguments", linenum)
				if tokens[0][0] == ")":
					tokens.pop(0)
					break
				args.append(parse_command(tokens))
		return CallNode(token, args)
	elif token[0] == "!":
		name = token[1:]
		if len(tokens) == 0:
			raise ParseError("macro has no body")
		args = []
		if tokens[0][0] == "(":
			tokens.pop(0)
			while True:
				if len(tokens) == 0:
					raise ParseError("no matching close tag for macro arguments")
				t, _line = tokens.pop(0)
				if t == ")":
					break
				args.append(t)
		if len(tokens) == 0:
			raise ParseError("macro has no body")
		labels = []
		if tokens[0][0] == "(":
			tokens.pop(0)
			while True:
				if len(tokens) == 0:
					raise ParseError("no matching close tag for macro labels")
				t, _line = tokens.pop(0)
				if t == ")":
					break
				if t[0] != ":":
					raise ParseError("non label in labels field")
				labels.append(t[1:])
		if len(tokens) == 0:
			raise ParseError("macro has no body")
		body = parse_command(tokens)
		return MacroDefNode(name, args, body, labels)
	elif token[0] == ".":
		return BuiltinNode(token[1:])
	elif token[0] == "$":
		return MacroArgumentNode(token[1:])
	elif token[0] == ":":
		return LabelNode(token[1:])
	elif token[0] == "@":
		return ReferenceNode(token[1:])
	elif isnum(token):
		return NumberNode(int(token))
	elif token == "{":
		code = []
		while True:
			if len(tokens) == 0:
				raise ParseError("No matching close tag for a code block")
			if tokens[0][0] == "}":
				tokens.pop(0)
				break
			code.append(parse_command(tokens))
		return BlockNode(code)
	elif token[0] == "\"":
		return CodeNode([ord(c) for c in token[1:]])
	elif token == "[":
		code = []
		while True:
			if len(tokens) == 0:
				raise ParseError("No matching close tag for a raw block")
			if tokens[0][0] == "]":
				tokens.pop(0)
				break
			node = parse_command(tokens)
			if isinstance(node, NumberNode):
				code.append(node.val % (2**32))
			elif isinstance(node, ReferenceNode):
				code.append(Reference(node.name))
			else:
				raise ParseError("Raw blocks may only contain numbers and references")
		return CodeNode(code)
	else:
		raise ParseError("Invalid start of a command: '{}'".format(token, tokens), linenum)



class Label:
	def __init__(self, name):
		self.name = name
		#self.scope = scope

class Reference:
	def __init__(self, name):
		self.name = name
		#self.scope = scope

class Substitution:
	def __init__(self, body, args=None, labels=None):
		self.body = body
		self.args = args if args is not None else []
		self.labels = labels if labels is not None else []

scopeid = 1


def compile_tree(node, substitutions, scope):
	code = []
	if isinstance(node, BuiltinNode):
		comm = Commands.__dict__.get(node.name.upper())
		if comm == None:
			raise Exception("Unknown builtin command {}".format(node.name))
		code.append(comm)
	if isinstance(node, CodeNode):
		code.extend(node.code)
	elif isinstance(node, BlockNode):
		for command in node.code:
			code.extend(compile_tree(command, substitutions, scope))
	elif isinstance(node, MacroDefNode):
		substitutions[node.name] = Substitution(node.body, node.args, node.labels)
	elif isinstance(node, CallNode):
		sub = substitutions.get(node.name)
		if sub == None:
			raise Exception("Unknown call '{}'".format(node.name))
		if len(sub.args) != len(node.args):
			raise Exception("macro definition of {} has {} arguments, but call has {} arguments".format(node.name, sub.args, node.args))
		s = substitutions.copy()
		s.update({argname: Substitution(CodeNode(compile_tree(argbody, substitutions, scope))) for argname, argbody in zip(sub.args, node.args)})
		global scopeid
		scopeid += 1
		s.update({labelname: Substitution(CodeNode([Commands.PUSH, Reference(labelname+":"+str(scopeid))])) for labelname in sub.labels})
		code.extend(compile_tree(sub.body, s, scopeid))
	elif isinstance(node, NumberNode):
		code.append(Commands.PUSH)
		code.append(node.val % (2**32))
	elif isinstance(node, LabelNode):
		name = node.name
		if scope != 0:
			name += ":" + str(scope)
		code.append(Label(name))
	elif isinstance(node, ReferenceNode):
		code.append(Commands.PUSH)
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
		else:
			code.append(item)
	return code

def compile_code(text):
	tokens = tokenize(text)
	tree = parse_command(tokens)
	unlinkedcode = compile_tree(tree, {}, 0)
	code = link(unlinkedcode)
	return code
	


