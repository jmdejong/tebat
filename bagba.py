#!/usr/bin/env python3

import base64
import sys
import parser
import run
#import compileself
#import examplecode


def main():
	
	#code = [
		#0,
		#4,
		#128,
		#0,
		#Commands.NOOP,
		#Commands.PUSH,
		#32,
		#Commands.DUP,
		#Commands.PUTCHAR,
		#Commands.PUSH,
		#1,
		#Commands.ADD,
		#Commands.DUP,
		#Commands.PUSH,
		#7,
		#Commands.SWAP,
		#Commands.PUSH,
		#126,
		#Commands.NEG,
		#Commands.ADD,
		#Commands.NOT,
		#Commands.JUMPIFZ,
		#Commands.PUSH,
		#10,
		#Commands.PUTCHAR,
		#Commands.PUSH,
		#0,
		#Commands.EXIT
	#]
	
	with open("compileself.tidk") as f:
		sourcecode = f.read()
	#sourcecode = examplecode.sourcecode
	code = parser.compile_code(sourcecode)
	codebytes = b"".join(command.to_bytes(4, "little") for command in code)
	with open("compileself.bidk", "wb") as fo:
		fo.write(codebytes)
	
	#print([run.command_code_to_str.get(c, c) for c in code])
	run.run(code)




if __name__ == "__main__":
	main()
	

