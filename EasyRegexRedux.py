import re
from enum import Enum, auto
# import Cope
from Cope import debug, debugged

# This is *not* generalized. For a general version, use the one in Cope.py
class FunctionCall:
    def __init__(self, func=lambda: None, args=()):
        self.func = func
        self.args = args

    def __call__(self, cur):
        return self.func(cur, *self.args)

class RegexFlavor(Enum):
    GENERIC = 0
    PYTHON = 1
    PERL = 2

# This is literally here so the user feels good. You get the same result just surrounding it in parenthesis
# def EasyRegex(elements):
    # return elements

class EasyRegexElement:
    def __init__(self, part):
        self.funcList = []
        self.flavor = None

        # If we're given an element, then we're starting the chain
        if type(part) is EasyRegexElement:
            self.funcList += part.funcList
            # Reset the child chain's head element (the one all the others in the chain dumped their crap onto)
            # to it's original state so we can use it again
            part.funcList = part.funcList[0]
        elif callable(part):
            self.funcList.append(FunctionCall(part))
        elif type(part) is str:
            self.funcList.append(FunctionCall(lambda cur: cur + part))
        else:
            raise TypeError(f"Invalid type {type(part)} passed to EasyRegexElement constructor")

# Magic Functions
    def __str__(self):
        return self._compile()

    def __repr__(self):
        return 'EasyRegex("' + str(self) + '")'

    def __add__(self, thing):
        if type(thing) is str:
            self.funcList.append(FunctionCall(lambda cur: cur + thing))
        elif type(thing) is EasyRegexElement:
            self.funcList += thing.funcList
        return self

    def __iadd__(self, thing):
        tmp = self + thing
        return tmp

    def __not__(self):
        NotImplementedError('The not operator is not currently implemented')

    def __call__(self, *args):
        # if len(self.funcList) > 1:
            # debug(self.funcList)
            # raise SyntaxError("Do not try to call EasyRegex chains; only use them as functions!")
        args = list(args)
        for cnt, i in enumerate(args):
            args[cnt] = self._sanitizeInput(i)
        self.funcList[-1].args = args
        return self

# Non-Regex functions
    def _compile(self):
        regex = r''
        for func in self.funcList:
            regex = func(regex)
        return regex

    def _sanitizeInput(self, i):
        # If it's another chain, compile it
        i = str(i)

        # r'\<', r'\>', r'//'
        for part in (r'\)', r'\(', r'\[', r'\]', r'\{', r'\}', r'\+', r'\*', r'\$', r'\@', r'\^', r'\:', r'\=', r'\-', r'\/'):
            i = re.sub(r'(?<!\\)\)', part, i)

        return i

    def compile(self):
        return re.compile(str(self))

    def str(self):
        return str(self)

    def debug(self):
        try:
            from Cope import debug
        except ImportError:
            print(f"Compiled EasyRegex String = {self}")
        else:
            debug(self, name='Compiled EasyRegex String')

    def debugStr(self):
        return self.debug().str()

# Flavor Setters
    def usePythonFlavor(self):
        self.flavor = RegexFlavor.PYTHON

    def useGenericFlavor(self):
        self.flavor = RegexFlavor.GENERIC

    def usePerlFlavor(self):
        self.flavor = RegexFlavor.PERL

    def setFlavor(self, flavor):
        self.flavor = flavor


EasyRegex = EasyRegexElement


# Positional
wordStartsWith = EasyRegexElement(lambda cur, input: input + r'\<' + cur)
wordEndsWith =   EasyRegexElement(lambda cur, input: cur + r'\>' + input)
startsWith =     EasyRegexElement(lambda cur, input: input + r'\A' + cur)
endsWith =       EasyRegexElement(lambda cur, input: cur + r'\Z' + input)
ifAtBeginning =  EasyRegexElement(lambda cur: r'^' + cur)
ifAtEnd =        EasyRegexElement(r'$')

# Matching
match =     EasyRegexElement(lambda cur, input: cur + input)
isExactly = EasyRegexElement(lambda cur, input: "^" + input + '$')
add = match

# Amounts
matchMax =      EasyRegexElement(lambda cur, input='':           cur + ('' if not len(input) else '(' + input + ')') + r'+')
matchNum =      EasyRegexElement(lambda cur, num, input='':      cur + ('' if not len(input) else '(' + input + ')') + '{' + str(num) + '}')
matchRange =    EasyRegexElement(lambda cur, min, max, input='': cur + ('' if not len(input) else '(' + input + ')') + '{' + str(min) + ',' + str(max) + '}')
matchMoreThan = EasyRegexElement(lambda cur, min, input='':      cur + ('' if not len(input) else '(' + input + ')') + '{' + str(min - 1) + ',}')
matchAtLeast =  EasyRegexElement(lambda cur, min, input='':      cur + ('' if not len(input) else '(' + input + ')') + '{' + str(min) + ',}')

# Single Characters
whitespace = EasyRegexElement(r'\s')
whitechunk = EasyRegexElement(r'\s+')
digit      = EasyRegexElement(r'\d')
number     = EasyRegexElement(r'\d+')
word       = EasyRegexElement(r'\w+')
wordChar   = EasyRegexElement(r'\w')
hexDigit   = EasyRegexElement(r'\x')
octDigit   = EasyRegexElement(r'\O')
anything   = EasyRegexElement(r'.')
chunk      = EasyRegexElement(r'.+')
stuff      = chunk

# Explicit Characters
spaceOrTab     = EasyRegexElement(r'[ \t]')
newLine        = EasyRegexElement(r'\n')
carriageReturn = EasyRegexElement(r'\r')
tab            = EasyRegexElement(r'\t')
space          = EasyRegexElement(r' ')
quote          = EasyRegexElement(r'(\'|")')
verticalTab    = EasyRegexElement(r'\v')
formFeed       = EasyRegexElement(r'\f')

# Not Chuncks
notWhitespace = EasyRegexElement(r'\S')
notDigit      = EasyRegexElement(r'\D')
notWord       = EasyRegexElement(r'\W')

# Optionals
optional = EasyRegexElement(lambda cur, input='': cur + ('' if not len(input) else '(' + input + ')') + r'?')
multiOptional = EasyRegexElement(lambda cur, input='': cur + ('' if not len(input) else '(' + input + ')') + r'*')
either = EasyRegexElement(lambda cur, input, or_input: cur + rf'({input}|{or_input})')

def _anyOfFunc(cur, *inputs):
    cur += r'['
    for i in inputs:
        cur += i
    cur += r']'
    return cur
anyOf = EasyRegexElement(_anyOfFunc)

def _anyExceptFunc(cur, *inputs):
    cur += r'[^'
    for i in inputs:
        cur += i
    cur += r']'
    return cur
anyExcept = EasyRegexElement(_anyExceptFunc)
anyBetween = EasyRegexElement(lambda cur, input, and_input: cur + r'[' + input + '-' + and_input + r']')

# Sets
anyUppercase       = EasyRegexElement(r' [A-Z]')
anyLowercase       = EasyRegexElement(r' [a-z]')
anyLetter          = EasyRegexElement(r'[A-Za-z]')
anyAlphaNum        = EasyRegexElement(r'[A-Za-z0-9]')
anyDigit           = EasyRegexElement(r'[0-9]')
anyHexDigit        = EasyRegexElement(r'[0-9a-f]')
anyOctDigit        = EasyRegexElement(r'[0-7]')
anyPunctuation     = EasyRegexElement(r'[:punct:]')
anyBlank           = EasyRegexElement(r'[ \t\r\n\v\f]')
anyControllers     = EasyRegexElement(r'[\x00-\x1F\x7F]')
anyPrinted         = EasyRegexElement(r'[\x21-\x7E]')
anyPrintedAndSpace = EasyRegexElement(r'[\x20-\x7E]')
anyAlphaNum_       = EasyRegexElement(r'[A-Za-z0-9_]')

# Numbers
octalNum = EasyRegexElement(lambda cur, num: cur + r'\\' + num)
hexNum =   EasyRegexElement(lambda cur, num: cur + r'\x' + num)

# Conditionals
ifProceededBy =    EasyRegexElement(lambda cur, condition: cur + fr'(?={condition})')
ifNotProceededBy = EasyRegexElement(lambda cur, condition: cur + fr'(?!{condition})')
ifFollowedBy =     ifProceededBy
ifNotFollowedBy =  ifNotProceededBy
ifPrecededBy =     EasyRegexElement(lambda cur, condition: fr'(?<={condition})' + cur)
ifNotPrecededBy =  EasyRegexElement(lambda cur, condition: fr'(?<!{condition})' + cur)

# TODO Implement Flavors (and rename them dialects)
# Global Flags -- I don't think these will work
matchGlobally     = EasyRegexElement(r'//g')
caseInsensitive   = EasyRegexElement(r'//i')
matchMultiLine    = EasyRegexElement(r'//m')
treatAsSingleLine = EasyRegexElement(r'//s')
notGreedy         = EasyRegexElement(r'//U')






optionalParams = EasyRegex(multiOptional(match(',') + r'\s+' + chunk))

testRegex = \
EasyRegex(anything +
matchMax +
match('test(') +
ifFollowedBy(
                                                    match('ing') +
                                                    multiOptional(match(',') + r'\s+' + chunk)
                                                 ) +
                                                 add(')')).debug()

testString = \
'Testing test(ing, ?) + test-ing!'
#        |   |  if  |

if testRegex:
    print(testRegex.str())
    if testString:
        print(re.search(testRegex.str(), testString))