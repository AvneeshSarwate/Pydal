# A simple Recursive Descent Parser. Grammar in Backus-Naur Form as follows - 
#
# <expression>  ::= <symbol> [(<mult> <number>)] | <paren-block> [(<mult> <number>)] | <expression> [(<expression>)]...  
# 
# <paren_block> ::= "[" <expression>  ["," <expression>]... "]" | "{" <expression> ["," <expression>] "}" 
# 
# <mult>        ::= "*" | "x"
#
# <symbol>      ::= [a-zA-Z0-9][a-zA-Z0-9]*(:[0-9][0-9]*){0,1}
#
# additional features - NOT SUPPORTED YET, even though "x" is in the parser
#   - "x": "new step repeat" - i.e a bx3 c -> a b b b c, whereas a b*3 c -> a [b b b] c
#   - <pat1, pat2, ...> - plays the "next" pattern every time around
#   - (pat1, pat2, ...) - plays a random pattern from the set every time around


#nodeTypes determine how their children are aggregated

#isDelimiter - whether a token is a paren, number, or mult-operator or comma 

import re
import itertools
import string 
import PydalAssembler as nodes


delimiters = ["]", "[", "{", "}", "<", ">" "*", "x", ",", ")", "("]

def tokenize(inputStr):
    p = "([" + "".join(delimiters) + "])"
    dirtyTokens = map(str.split, re.split(p, inputStr))
    tokens = list(itertools.chain.from_iterable(dirtyTokens))
    #print " ".join(tokens)
    return tokens

def allIn(test, ref):
    vals = [t in ref for t in test]
    return reduce(lambda a, b: a and b, vals)

def isMult(s):
    return s in ("*", "x")
def isNumber(s):
    return allIn(s, string.digits)
def isOpenParen(s):
    return s in ("{", "[", "(", "<")
def isEndParen(s):
    return s in ("}", "]", ")", ">")
def isComma(s):
    return s == ","
#TODO: more conditions required to determine valid symbol 
def isPydalSymbol(s): 
    return allIn(s, string.letters+string.digits+":"+"~") and s[0] != ":" and s[-1] != ":"
def isSampleSymbol(s):
    return re.match('^[a-g][a-g]:[0-9](\.[0-9]+)?_[0-9](\.[0-9]+)?$', s) or s == "~"
def isMaxSymbol(s):
    return re.match('^[a-d]:[0-9](\.[0-9]+)?(_[0-9](\.[0-9]+)?)?$', s) or s == "~"
def isArpeggiatorSymbol(s):
    return s.isdigit() or s == "~"
def isChordSeqSymbol(s):
    return re.match('^[a-h][a-h]$', s) or s == "~"
def isBallState(s):
    return s in 'abcdefghijk~' and len(s) == 1
def isFuncTrigger(s):
    return s in 'abcdefghijklmnopqrs~' and len(s) == 1


symbolMatchers = {}
symbolMatchers['pydal'] = isPydalSymbol
symbolMatchers['sample'] = isSampleSymbol
symbolMatchers['arp'] = isArpeggiatorSymbol
symbolMatchers['max'] = isMaxSymbol
symbolMatchers['chord'] = isChordSeqSymbol
symbolMatchers['ballState'] = isBallState
symbolMatchers['funcTrigger'] = isFuncTrigger


# you can define what types of strings you use as tokens, they can
# be anything, provided it doesn't contain any of the reserved characters
# listed in the 'delimiters' variable above
def parse(inputStr, symbolKey = 'pydal'):
    tokens = tokenize(inputStr)
    symbolMatcher = symbolMatchers[symbolKey]
    node = parseExpression(tokens, 0, symbolMatcher)[0]
    node.type = symbolKey
    return node



# through all the parse* functions
# ind should always point to the next token to be read
# TODO: make sure this is enforced

def parseMult(tokenList, ind, node):
    if isNumber(tokenList[ind+1]):
        return nodes.MultNode(node, tokenList[ind+1]), ind+2
    else:
        raise StopIteration("number must follow muliplication operator")


def parseSymbol(tokenList, ind):
    symbolNode = nodes.SymbolNode(tokenList[ind:ind+1])
    if ind+1 < len(tokenList) and isMult(tokenList[ind+1]):
        return parseMult(tokenList, ind+1, symbolNode)
    else:
        return nodes.SymbolNode(tokenList[ind:ind+1]), ind+1 



def parseParenBlock(tokenList, ind, isSymbol, parseDebug = False):
    startInd = ind
    openParen = tokenList[ind]
    if openParen == "[":
        node = nodes.SquareBracketNode([])
    elif openParen == "{":
        node = nodes.CurlyBracketNode([])
    elif openParen == "(":
        node = nodes.ParenBracketNode([])
    elif openParen == "<":
        node = nodes.AngleBracketNode([])
    ind += 1

    while not isEndParen(tokenList[ind]):
        expNode, newInd = parseExpression(tokenList, ind, isSymbol)
        node.children.append(expNode)
        if isComma(tokenList[newInd]):
            newInd += 1
        ind = newInd

    if (
            (openParen == "[" and tokenList[ind] == "]") or 
            (openParen == "{" and tokenList[ind] == "}") or
            (openParen == "(" and tokenList[ind] == ")") or
            (openParen == "<" and tokenList[ind] == ">")
       ):
        if ind+1 < len(tokenList) and isMult(tokenList[ind+1]):
            return parseMult(tokenList, ind+1, node)
        else:
            return node, ind+1
    else:
        raise StopIteration("paren at index " + str(startInd) + "must be closed")



def parseExpression(tokenList, ind, isSymbol):
    
    node = nodes.ExpressionNode([])

    #at start of loop, [new]ind is always the index to read next 
    while ind < len(tokenList) and not isComma(tokenList[ind]) and not isEndParen(tokenList[ind]): #check this
        newInd = .5

        if isSymbol(tokenList[ind]):
            symbolOrMultNode, newInd = parseSymbol(tokenList, ind)
            node.children.append(symbolOrMultNode)

        elif isOpenParen(tokenList[ind]):
            parenOrMultNode, newInd = parseParenBlock(tokenList, ind, isSymbol)
            node.children.append(parenOrMultNode)
        else:
            raise StopIteration("can only start expressions with symbols or open paren: ") 

        ind = newInd

    return node, ind

def printLevels(node):
    lists = [[],[]]

    a = lambda x: x%2
    b = lambda x: (a(x)+1)%2

    i = 0

    lists[a(i)].append(node)
    while not all([n.leaf for n in lists[a(i)]]):
        lists[b(i)] = []
        print "  -  ".join(map(str, lists[a(i)]))
        for n in lists[a(i)]:
            if n.leaf:
                lists[b(i)].append(n)
            else:
                lists[b(i)].extend([c for c in n.children])
        i += 1

    print "  -  ".join(map(str, lists[a(i)]))


def test(testStr):
    print "TEST CASE:", testStr
    node = parse(testStr)
    printLevels(node)
    print "--------------------"
    renderedNode = node.render(1.0)
    for t in renderedNode:
        print t[0], ":", t[1]
    print "\n\n----------------------------------------------------------------"
    print "----------------------------------------------------------------\n\n"

cases = [
    "a a a",
    "a { a a}",
    "[a c]*2",
    "a {a a, b b } ",
    "a {a a, b b* 2 } ",
    "a {[a a]*3, b b* 2 } ",
    "{a c, d {d a}*3} b [a, g]",
    "{lt lt:2, {hc hc:2, ho sn:2 sn:3*2} {bottle bottle bottle, [bin:2 bin] bin:1} bd}"
    ]

statefulCases = ["{a b, c d e, f g h i}"]

