sourcecode = """
{

# macros that translate directly to builtin commands (but know the amount of arguments)
!putchar(c){c .putchar}
!add(a b){a b .add}
!mult(a b){a b .mult}
!div(a b){a b .div}
!mod(a b){a b .mod}
!bitand(a b){a b .bitand}
!bitor(a b){a b .bitor}
!shiftup(a b){a b .shiftup}
!exit(code){code .exit}
!jump(to){to .jump}
!jumpifz(condition to){condition to .jumpifz}
!setstack(to){to .setstack}
!not(a){a .not}
!moveto(value ptr){value ptr .moveto}
!memmove(amount src dest){amount src dest .memmove}


# macros that almost translate directly to builtins
!minus(val){val .neg}
!isnegative(a){a .negative}
!deref (ptr) {ptr .movefrom}
!setref(ptr value){
	ptr
	value
	.swap
	.moveto
}
!dup2 {
	.dup
	.dup
	.drop
	.drop
	.drop
	.dup
	.undrop
	.swap
	.undrop
}
!jumpif(condition to) jumpifz(not(condition) to)

# other macros
!dupsecond {
	.swap
	.dup
	.drop
	.swap
	.undrop
}
!printint(val){
	val
	putchar(40)
	putint({ })
	putchar(41)
}
!dowhile (body condition)(:whilestart) {
	:whilestart
	body
	jumpifz(not(condition) whilestart)
}
!if(condition body)(:ifend) {
	jumpifz(condition ifend)
	body
	:ifend
}
!and(a b) (:end){
	a
	jumpifz(.dup end)
	.drop
	b
	:end
}
!or(a b) {
	a
	jumpif(.dup end)
	.drop
	b
	:end
}
!ifelse(condition ifbody elsebody)(:elsepart :ifend) {
	jumpifz(condition elsepart)
	ifbody
	jump(ifend)
	:elsepart
	elsebody
	:ifend
}
!while (condition body) {
	if(condition {
		dowhile (body condition)
	})
}
!sub(a b){
	add(a minus(b))
}
!lt (left right){
	isnegative(sub(left right))
}
!gt(left right){
	left
	right
	.swap
	isnegative(sub({ } { }))
}
!leq(left right){
	not(gt(left right))
}
!geq(left right){
	not(lt(left right))
}
!neq(a b){
	sub(a b)
}
!eq (a b){
	not(sub(a b))
}
!varptr(id) {
	add(deref(@funcmem) id)
}
!setvar(id value){
	setref(varptr(id) value)
}
!getvar(id){
	deref(varptr(id))
}

!addto (pos val){
	setref(pos add(deref(.dup) val))
}
!calls(fun)(:returnpos){
	returnpos
	jump(fun)
	:returnpos
}
!call(fun args){
	args
	calls(fun)
}
!function(label nargs nvars body){
	label
	# remember old stack location
	deref(@funcmem)
	
	# remember current stack location
	.getstack
	@funcmem
	.moveto
	
	# remember argument number
	nargs
	# remember number of local variables
	nvars
	
	# reserve space for local variables
	.dup
	.getstack
	.add
	.setstack
	.drop
	# execute function body
	body
	
	returns
}
!endfunc{
	# store old stack and old mem location location in temporary globals
	setref(@memtmp getvar(-1))
	setref(@calltmp getvar(-2))
	.getstack
	minus(add(add(deref(@funcmem) getvar(1)) 2))
	.add
	@returntmp
	.moveto
	
	# move return values to top of regular stack
	# source location start
	.getstack
	minus(deref(@returntmp))
	.add
	# amount of return values
	deref(@returntmp)
	.swap
	# destination location start
	sub(deref(@funcmem) add(getvar(0) 2))
	# remember destination location for later (because getvar(0) might get overwritten)
	.dup
	@funcmem
	.moveto
	# actually move the return values
	.memmove
	
	# move stack to end of return values
	setstack(add(deref(@funcmem) deref(@returntmp)))
	
	# recall old stack location
	setref(@funcmem deref(@memtmp))
}
!returns {
	endfunc
	# return to previous position
	jump(deref(@calltmp))
}
!return(val){
	val
	returns
}
!tailcalls(fun){
	endfunc
	deref(@calltmp)
	jump(fun)
}
!tailcall(fun val){
	val
	tailcalls(fun)
}
!print(string)(:stringstart :stringend){
	stringstart
	while( neq(.dup stringend) {
		putchar(deref(.dup))
		add({ } 1)
	})
	jump(stringend)
	:stringstart
	string
	:stringend
	.drop
}
!println(string){
	print(string)
	putchar(10)
}
!putint(val){
	val
	0
	.swap
	while(.dup {
		add(mod(.dup 10) 48)
		.swap
		div({ } 10)
	})
	.drop
	while(.dup {
		.putchar
	})
	.drop
}
!printmem(ptr size){
	ptr
	size
	dup2
	.add
	.swap
	.drop
	.swap
	while(neq(dup2 { }) {
		putchar(deref(.dup))
		add({ } 1)
	})
	.drop
	.drop
}
!mallocnew(amount) {
	add(2 deref(@heapend))
	add(amount 2)
	moveto(.dup deref(@heapend))
	arrset(deref(@heapend) 1 1)
	moveto(add({ } deref(@heapend)) @heapend)
}


!arrset(arr index val){
	setref(add(arr index) val)
}
!arrget(arr index){
	deref(add(arr index))
}

# actual code part

# some initializer metadata
[
0
@codestart # initial location of the code pointer
@codeend # initial location of the stack pointer
]

# place where the code starts executing
:codestart
addto(@heapstart 4096) # reserve 4096 words space for the stack
setref(@heapend deref(@heapstart))

# end with as exit code the return value from main
exit(call(@main { }))

function(:malloc 1 2 {
	!amount -3
	!heapptr 2
	!next 3
	setvar(heapptr deref(@heapstart))
	while(neq(getvar(heapptr) deref(@heapend)) { # loop over all chunks
		if(not(arrget(heapptr 1)) { # chunk is free
			setvar(next add(heapptr deref(heapptr)))
			# if the next chunks are free too, merge them into this one
			while(and(neq(next @heapend) not(arrget(next 1))) {
				setref(heapptr add(deref(heapptr) deref(next)))
				setvar(next add(heapptr deref(heapptr)))
			})
			if(leq(amount add(deref(heapptr) 2)) {
				# enough free space found!
				# claim this block
				arrset(heapptr 1 1)
				if(gt(sub(deref(heapptr) amount) 4) {
					# still a significant free space behind this block
					# add a new free chunk
					arrset(heapptr amount sub(deref(heapptr) amount))
					arrset(heapptr add(amount 1) 1)
					setref(heapptr amount)
				})
				return(add(heapptr 2))
			})
		})
		setvar(heapptr add(getvar(heapptr) deref(getvar(heapptr))))
	})
	# no free chunk found that's large enough; allocate some new memory
	mallocnew(getvar(amount))
})
!malloc(amount) call(@malloc amount)
!free(ptr) {arrset(ptr -1 0)}
function(:realloc 2 2 {
	!ptr -4
	!amount -3
	!new 2
	!oldamount 3
	setvar(new getvar(ptr))
	setvar(oldamount arrget(getvar(ptr) -2))
	if(gt(getvar(amount) add(getvar(oldamount) -2)) {
		setvar(new malloc(getvar(amount)))
		memmove(getvar(oldamount) getvar(ptr) getvar(new))
		free(getvar(ptr))
	})
	getvar(new)
})
!realloc(ptr amount) call(@realloc {ptr amount})



!vecnew{
	malloc(3)
	setref(.dup 0)
	arrset(.dup 1 8)
	arrset(.dup 2 malloc(8))
	
}

function(:vecgrow 1 0 {
	!vec -3
	arrset(getvar(vec) 1 mult(arrget(getvar(vec) 1) 2))
	arrset(getvar(vec) 2 realloc(arrget(getvar(vec) 2) arrget(getvar(vec) 1)))
})

function(:vecappend 2 0 {
	!vec -4
	!val -3
	if(eq(deref(getvar(vec)) arrget(getvar(vec) 1)) {
		call(@vecgrow getvar(vec))
	})
	arrset(arrget(getvar(vec) 2) deref(getvar(vec)) getvar(val))
	addto(getvar(vec) 1)
})
!vecappend(vec val){call(@vecappend {vec val})}

!printstr(vecstr){
	vecstr
	.dup
	arrget({ } 2)
	.swap
	.movefrom
	printmem({ } { })
}




function(:readinput 0 4 {
	!text 2
	!char 3
	setvar(text vecnew())
	setvar(char .getchar)
	while(not(isnegative(getvar(char))){
		vecappend(getvar(text) getvar(char))
		setvar(char .getchar)
	})
	getvar(text) # return a linked list of letters
})


function(:tokenize 1 4 {
	!letters -3
	!char 2
	!tokens 3
	!token 4
	!last_token 5
	setvar(tokens 0)
	while(getvar(letters) {
		setvar(char deref(getvar(letters)))
		setvar(letters arrget(getvar(letters) 1))
		putchar(getvar(char))
		#setvar(token malloc(4))
		#if(not(getvar(tokens)) {
			#setvar(tokens getvar(token))
		#}
	})
	0
})

function (:main 0 2 {
	!input 2
	!tokens 3
	setvar(input call(@readinput { }))
	#call(@readinput { })
	#input
	#.moveto
	printstr(getvar(input))
	print("\n")
	#setvar(tokens call(@tokenize getvar(input)))
	0
})
# some extra space of memory
# this is used for global constants and variables
[0]
:heapstart # pointer to the first address that is used for heap memory
[@codeend]
:heapend # pointer to the first address that is not part of the used heap
[@codeend]
:funcmem # pointer to the location of the function arguments and local variables
[0]
:calltmp # hold the previous call frame when the stack is being manipulated
[0]
:memtmp # hold the previous funcmem location when the stack is being manipulateds
[0]
:returntmp # hold the amount of return values during a return
[0]
# the stack begins here
:codeend
[0]
}
"""
