import logging

#logging my debug print statements into a seperate log file 'test.log'
logging.basicConfig(
    filename="test4_1.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s: %(message)s"
)

#tokenizer was provided by professor
import re
def tokenize(s):
    return re.findall("/?[a-zA-Z][a-zA-Z0-9_]*|[[][a-zA-Z0-9_\s!][a-zA-Z0-9_\s!]*[]]|[-]?[0-9]+|[}{]+|%.*|[^ \t\n]", s)

#print(tokenize("/square {dup mul} def [1 2 3 4] {square} forall add add add 30 eq stack"))

#________________________Convert the token list into a code__________________________
#groupMatching2(it)
#   will place the code array into an empty array of its own
#   and then append the current code array to the array in parse(L) function

def groupMatching2(it):
    res = []
    for c in it:
        if ((c == '}') or (c==']')):
            #at end of code array (nested or unnested)
            return res
        elif ((c=='{') or (c=='[')):
            #if nested code array
            # inner matching parenthesis.
            res.append(groupMatching2(it))
        else:
            if ((str.isdigit(c)) or (c[0] == '-')): #if integer convert to int
                if c[0] == '-':
                    newNum = c.replace('-','')
                    res.append(int(newNum) * -1)
                else:
                    res.append(int(c))
            elif (isArray(c)): #if array
                    res.append(arrayMatching(c))
            else:  
                res.append(c)
    return False


def arrayMatching(s):      
    res = []
    char = 0
    while (char < (len(s) - 1)):
        curNum = ''
        if ((s[char] != '[')):
            while((s[char] != ' ') and (s[char] != ']')):
                curNum += s[char]
                char += 1
        if(curNum != ''):
            if (curNum[0] == '-'):
                newNum = curNum.replace('-','')
                res.append(int(newNum) * -1)
            else:
                res.append(int(curNum))
        char += 1
    return res


def isArray(it):
    if it[0] == '[':
        return True
    else:
        return False

def parse(L):
    res = []
    it = iter(L)
    isFloat = False
    for c in it:
        if ((c=='}') or (c==']')):  #non matching closing paranthesis; return false since there is
                    # a syntax error in the Postscript code.
            return False
        elif ((c=='{') or (c=='[')):
            #if code block
            res.append(groupMatching2(it)) 
        else:
            if ((str.isdigit(c)) or (c[0]=='-') or (c == '.')):
                if c[0] == '-':
                    newNum = c.replace('-','')
                    res.append(int(newNum) * -1)
                elif (isFloat == True):
                    val = (str(res.pop())+'.'+ c)
                    res.append(float(val))
                    isFloat = False
                elif(c == '.'):
                    isFloat = True
                else:
                    res.append(int(c))
            elif (isArray(c)): #if array
                res.append(arrayMatching(c))
            else:
                if c == 'true':
                    res.append(True)
                elif c == 'false':
                    res.append(False)
                else:
                    res.append(c)
    return res



def psIf():
    op1 =  opPop()
    op2 =  opPop()
    if op2:
        interpretSPS(op1,'dynamic')

def psIfelse():
    if(len( opstack) > 2):
        op3 =  opPop() #else block
        op2 =  opPop() #if block
        op1 =  opPop() #boolean
        if op1 == True:
            interpretSPS(op2,'dynamic')
        else:
            interpretSPS(op3, 'dynamic')

def psFor():
    codeBlock =  opPop()
    k =  opPop()
    j =  opPop()
    i =  opPop()
    if j < 0:
        for index in range(i,k-1,j):
            opPush(index)
            interpretSPS(codeBlock,'dynamic')
    else:
        for index in range(i, k+1, j):
            opPush(index)
            interpretSPS(codeBlock,'dynamic')
            
def forall():
    codeBlock =  opPop()
    op1 =  opPop() #array
    for i in op1:
        opPush(i)
        interpretSPS(codeBlock, 'dynamic')

def interpretSPS(tokens,scope):
    psOpDict = {"add":  add, "sub":  sub, "mul":  mul,"div":  div, "eq":  eq, "lt":  lt, "gt":  gt, 
            "length":  length, "get":  get,
            "and": psAnd, "or": psOr, "not": psNot, "if": psIf, "ifelse": psIfelse, "for": psFor, "forall": forall,
            "dup":  dup, "exch":  exch, "pop": pop, "copy": copy, "clear": clear, "stack": stack,
            "dict":  psDict, "begin":  begin, "end":  end, "def":  psDef}
    constants = [int, bool, float] #all constant types in SPS
    if type(tokens) in constants:
         opPush(tokens)
    else:         
        for token in tokens:
            if (type(token) in constants):
                opPush(token)

            if(type(token) is list):
                opPush(token)

            #strings
            elif ((type(token) is str)):
                if (token[0] == '/'): #var name (undefined)
                    opPush(token)

                #if string is a SPS operation call
                elif token in psOpDict:
                    if(token == 'def'):
                        opPush(scope)
                    funcToCall = psOpDict[token]
                    funcToCall()

                else: #var name (maybe defined)
                    if(scope == 'static'):
                        val = lookup(token,scope)
                        if (val != None):#var name (maybe defined)
                            if (type(val) in constants):
                                opPush(val)
                            else: #code block
                                link = getLink(token) #grab the link of where the function was defined
                                dictPush(({},link))
                                interpretSPS(val,scope)
                                dictPop() #pop topmost tuple
                    else:
                        val = lookup(token,scope)
                        if (val != None):#var name (maybe defined)
                            if (type(val) in constants):
                                opPush(val)
                            else: #code block
                                dictPush(({},0))
                                interpretSPS(val,scope)
                                dictPop()
                                

 #__________________________opstack Operations__________________________#
opstack = []

# opPop(): returns the last index of opStack 
def opPop():
    if (len(opstack) > 0):
       return opstack.pop(-1) 
    else:
        logging.debug("Error: opPop    opstack is empty")

logging.debug(opPop()) #log opPop result

#opPush(): push postscript constant onto stack
def opPush(value):
    opstack.append(value) #append value to back of list

 #__________________________dictstack Operations__________________________#
dictstack = []

#dictPop(): pops current dictionary from back of stack
def dictPop():
    if (len(dictstack) > 0):
       return dictstack.pop(-1)
    else: 
        logging.debug("Error: dictPop   dictstack is empty")


#dictPush(d): d is a dict that will be pushed to dictstack
def dictPush(d): 
    dictstack.append(d)


def define(name, value):
    if (len(dictstack) == 0):
        d = ({name:value},0)
        dictPush(d)
    else:
        d = dictPop() #grab topmost dict in dictstacks
        d[0][name] = value #add or overwrite current key name with new value
        dictPush(d)

def getLink(name):
    #lookup looks from the topmost dict and then continues down stack
    # we implemented our stack in reverse (back of list is head of stack)
    index = len(dictstack) - 1
    for d in reversed(dictstack):
        if ('/' + name) in d[0].keys():
            return index #return value paired to key param 'name'
        index -= 1 #subtract 1 from index
    return None

def lookup(name,scope):
    #lookup looks from the topmost dict and then continues down stack
    # we implemented our stack in reverse (back of list is head of stack)
    #static scoping
    if(scope == 'static'):
        try:
            t = dictPop()
            d,link = t
            dictPush(t)
            
            if('/'+name) in dictstack[link][0]:
                return dictstack[link][0]['/'+name]
            elif('/'+name) in d:
                return d['/'+name]

        except:
            index = len(dictstack) - 1
            for d in reversed(dictstack):
                if ('/' + name) in d[0].keys():
                    return d[index]['/'+name]#return value paired to key param 'name'
                index -= 1 #subtract 1 from index
        else:
            index = len(dictstack) - 1
            for d in reversed(dictstack):
                if ('/' + name) in d[0].keys():
                    return d[0]['/'+name]#return value paired to key param 'name'
                index -= 1 #subtract 1 from index
    #dynamic scoping
    else:
        for d in reversed(dictstack):
            if ('/' + name) in d[0].keys():
                return d[0]['/'+name]#return value paired to key param 'name'

    print("Error NAME: /"+name+" is undefined in dictstack")
    return None



 #__________________________Arithmetic Operations__________________________#

#add(): pops two items from opstack and adds them
#    - warning: incase of a variable name (as op1 or op2) is not defined 
#               in dictstack, add will pop both op1,op2 and not add them back to opstack
def add():
    if (len(opstack) > 1):
        op1 = opPop()
        op2 = opPop()

        #if op1 and op2 are ints or floats
        if((type(op1) is int) or (type(op1) is float)
            and ((type(op2) is int) or (type(op2) is float))):
            opPush(op1 + op2)
    else:
        logging.debug("Error: opPop   not enough operands for add")


def sub():
    if (len(opstack) > 1):
        op1 = opPop()
        op2 = opPop()

        #if op1 and op2 are ints or floats
        if ((type(op1) is int) or (type(op1) is float)
                and ((type(op2) is int) or (type(op2) is float))):
            opPush(op2 - op1) #warning: if result type float, result is not rounded
    else:
        print("Error: opPop   not enough operands for sub")
        logging.debug("Error: opPop   not enough operands for sub")


def mul():
    if (len(opstack) > 1):
        op1 = opPop()
        op2 = opPop()

        #if op1 and op2 are ints or floats
        if ((type(op1) is int) or (type(op1) is float)
                and ((type(op2) is int) or (type(op2) is float))):
            opPush(op1 * op2) #warning: if result type float, result is not rounded

    elif(len(opstack) == 1):
        op2 = opPop()
        #if op1 and op2 are ints or floats
        if ((type(op2) is int) or (type(op2) is float)):
            opPush(op2) #warning: if result type float, result is not rounded

    else:
        print("Error: opPop   not enough operands for mul")
        logging.debug("Error: opPop   not enough operands for mul")


def div():
    if (len(opstack) > 1):
        op1 = opPop()
        op2 = opPop()

        #if op1 and op2 are ints or floats
        if ((type(op1) is int) or (type(op1) is float)
                and ((type(op2) is int) or (type(op2) is float))):
            opPush(op2 / op1) #warning: if result type float, result is not rounded
    else:
        print("Error: opPop   not enough operands for div")
        logging.debug("Error: opPop   not enough operands for div")

def eq():
    if (len(opstack) > 1):
        op1 = opPop()
        op2 = opPop()
        opPush(False) #assuming they are not equal
        #if op1 and op2 are ints or floats
        if ((type(op1) is int) or (type(op1) is float)
                and ((type(op2) is int) or (type(op2) is float))):
            if(op1 == op2):
                opPop()
                opPush(True)
    else:
        print("Error: opPop   not enough operands for div")
        logging.debug("Error: opPop   not enough operands for div")

def lt():
    if (len(opstack) > 1):
        op1 = opPop()
        op2 = opPop()
        opPush(False) #assuming op1 is greater than op2
 
        #if op1 and op2 are ints or floats
        if ((type(op1) is int) or (type(op1) is float)
                and ((type(op2) is int) or (type(op2) is float))):
            if(op2 < op1):
                opPop()
                opPush(True)
    else:
        print("Error: opPop   not enough operands for div")
        logging.debug("Error: opPop   not enough operands for div")

def gt():
    if (len(opstack) > 1):
        op1 = opPop()
        op2 = opPop()
        opPush(False) #assuming op1 is greater than op2
        #if op1 and op2 are ints or floats
        if ((type(op1) is int) or (type(op1) is float)
                and ((type(op2) is int) or (type(op2) is float))):
            if(op2 > op1):
                opPop()
                opPush(True)
    else:
        print("Error: opPop   not enough operands for div")
        logging.debug("Error: opPop   not enough operands for div")

 #__________________________Array Operators__________________________#
 # Array operators: define the array operators length, get

def length():
    if (len(opstack) > 0):
        op1 = opPop()
        if(type(op1) is int):
            opPush(1)
        elif(type(op1) is not int):
            opPush(len(op1))
        else:
            opPush(1)
    else:
        print("Error: length failed")


def get():
    if(len(opstack) > 1):
        i = opPop()
        op1 = opPop()
        if(type(op1) is not str):
            opPush(op1[i])
        else:
            print("Error: get param is of type int")
    else:
        print("Error: get failed")


#__________________________Boolean Operators__________________________#
# boolean operators psAnd, psOr, psNot

def psAnd():
    if (len(opstack) > 1):
        op1 = opPop()
        op2 = opPop()
        if((type(op1) is bool) and (type(op2) is bool)):
            if(op1 and op2 == True):
                opPush(True)
            else:
                opPush(False)
        else:
           print("Error: psAnd  operand(s) are not of type bool; lost({},{})".format(op2,op1))
    else:
        print("Error: psAnd   not enough operands")

def psOr():
    if (len(opstack) > 1):
        op1 = opPop()
        op2 = opPop()
        if((type(op1) is bool) and (type(op2) is bool)):
            if(op1 or op2 == True):
                opPush(True)
            else:
                opPush(False)
        else:
            print("Error: psAnd  operand(s) are not of type bool; lost({},{})".format(op2,op1))
    else:
        print("Error: psAnd   not enough operands")

def psNot():
    if (len(opstack) > 0):
        op1 = opPop()
        if(type(op1) is bool):
            opPush(not op1)
        elif(type(op1) is int):
            opPush(-1 * op1)
        else:
            print("Error: psAnd  operand(s) are not of type bool; lost({})".format(op1))
    else:
        print("Error: psAnd   not enough operands")


#__________________________Stack Manipulation and Print Operators__________________________#
#stack manipulation and print operators: dup, exch, pop, copy, clear, copy

def dup():
    if(len(opstack) > 0):
        opPush(opstack[-1])
    else:
        print("Error: dup   not enough items in opstack")

def exch():
    if(len(opstack) > 1):
        op1 = opPop()
        op2 = opPop()
        #push op1 and op2 in reverse order
        opPush(op1)
        opPush(op2)
    else:
        print("Error: exch   not enough items in opstack")

def pop():
    opPop()

def copy():
    i = -2
    if(len(opstack) > 0):
        num2Copy = opPop()
        if(len(opstack) > num2Copy):
            opstack.append(opstack[-1])
            while (abs(i) <= num2Copy):
                opstack.append(opstack[i*2])
                i -= 1
        else:
            print("Error: copy   copy number param > items in opstack; lost({})".format(num2Copy))
    else:
        print("Error: copy   not enough items in opstack")

def clear():
    opstack.clear()

def stack():
    if((len(opstack) > 0) or (len(dictstack) > 0)):
        print("==========opstack=========")
        for i in range(len(opstack)):
            print(opstack[len(opstack) - (i+1)])
        print("=========dictstack========")
        for i in range(len(dictstack)):
            print("----" + str((len(dictstack)) - (i + 1))+ "----" + str(dictstack[i][1]) + "----")
            for key in dictstack[(len(dictstack)) - (i + 1)][0].keys():
                print(key + " " + str(dictstack[(len(dictstack)) - (i + 1)][0][key]))
        print("==========================")
        
    else:
        print("empty")

#__________________________Dictionary Manipulation Operators__________________________#
# dictionary manipulation operators: psDict, begin, end, psDef
# Note: The psDef operator will pop the value and name from the opstack and
# call your my own"define" operator (pass those values as parameters).

def psDict():
    if (len(opstack) > 0):
        if(type(opstack[-1]) is int):
            size = opPop()
            d = {}
            opPush(d)
        else:
            print("Error: psDict   param is not of type int")
    else:
        print("Error: psDict   opstack is empty")

def begin():
    if (len(opstack) > 0):
        if(type(opstack[-1]) is dict):
            d = opPop()
            dictPush(d)
        else:
            print("Error: begin   param is not of type dictionary")
    else:
        print("Error: begin   opstack is empty")

def end():
    if (len(dictstack) > 0):
        dictPop()
    else:
        print("Error: end   dictstack is empty")

def psDef():
    if(len(opstack) > 1):
        scope = opPop()
        val = opPop()
        key = opPop()
        if ((type(key) is str ) and (key[0] == '/')):
            define(key,val)
        else:
            print("Error: psDef   key param is not of correct type; lost({},{})".format(key,val))
            opPush(key)
            opPush(val)
    else:
        print("Error: psDef   not enough items in in opstack")

#scope can be 'static ' or 'dynamic' this will tell 
# ----the interpreterSPS what scoping rule it will use
def interpreter(s,scope):
    l = parse(tokenize(s))
    interpretSPS(l,scope)

input1 = """
 [1 2 3 4 5] dup length exch {dup mul} forall
 add add add add
 exch 0 exch -1 1 {dup mul add} for
 eq stack
"""

input2 = """
 [9 9 8 4 10] {dup 5 lt {pop} if} forall
 stack
"""

input3 = """
/x 4 def
/g { x } def
/f { /x 7 def g /w { x } def /z { x } def w z } def
/h { /x 10 def g /q { x } def /n { x  stack } def q n } def
f
h
"""

input4 = """/x 4 def
/g { x stack } def
/f { /x 7 def g } def
f"""

input5 = """/m 50 def
/n 100 def
/egg1 {/m 25 def n} def
/chic {
 /n 1 def
 /egg2 { n } def
 m n
 egg1
 egg2
 stack } def
n
chic"""

input6 ="""/x 10 def
/A { x } def
/C { /x 40 def A stack } def
/B { /x 30 def /A { x } def C } def
B"""
#Test Cases:
#=============================================
print("\n----------Input 2---------\n")
print("DYNAMIC input2: ")
interpreter(input2,'dynamic')
clear()
print("STATIC input2: ")
interpreter(input2,'static')
print("\n----------Input 3---------\n")
print("DYNAMIC input3: ")
interpreter(input3,'dynamic')
clear()
print("STATIC input3: ")
interpreter(input3,'static')
print("\n----------Input 4---------\n")
print("DYNAMIC input4: ")
interpreter(input4,'dynamic')
clear()
print("STATIC input4: ")
interpreter(input4,'static')
print("\n----------Input 5---------\n")
print("DYNAMIC input5: ")
interpreter(input5,'dynamic')
clear()
print("STATIC input5: ")
interpreter(input5,'static')
print("\n----------Input 6---------\n")
print("DYNAMIC input6: ")
interpreter(input6,'dynamic')
clear()
print("STATIC input6: ")
interpreter(input6,'static')