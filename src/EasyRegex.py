#!/usr/bin/env python3
""" EasyRegex
An readable and intuitive way to generate Regular Expressions
"""
__version__ = '2.2.0'
__author__ = 'Copeland Carter'
__email__ = 'smartycope@gmail.com'
__license__ = 'GPL 3.0'
__copyright__ = '(c) 2021, Copeland Carter'

# This is to Regex expressions what CMake is to makefiles
# Explination of how this works:
    # This is version 2. The original version just had an EasyRegex class with a bunch of members that returned self,
    # then you chained together member function calls.
    # This version uses a bunch of constant singletons (of type EasyRegexSingleton) that have the __call__() dunder function
    # overridden to return a seperate class (EasyRegexMember) which override the __add__() and __str__() dunder functions.
    # What happens is you have all the singletons created in this file, specifying lambdas (or strings, for convenience)
    # describing how they interact with the regex expression, and then optional inverted lambdas (get to that in a moment)
    # and seperate dialog lambdas. When those are called later on by the user, (they can be treated like regular functions)
    # they initialize a EasyRegexMember, and give it the function they hold. Then, EasyRegexMembers are chained together with
    # +'s (or <<'s). EasyRegexMembers all have internal ordered lists of functions that get added to when +'ed. If you assign
    # the chain (or chains!) to a varaible or put in ()'s, what you end up with is one EasyRegexMember that has an ordered
    # list of all the functions from all the EasyRegexMembers in that chain. When you then cast that to a string (or call .str()
    # or .compile()), it finally goes through and calls all those functions, which results in the final regex string.
# Status:
# Current limitations include:
    # .inverse() doesn't work well with broken up chains. A large code refactoring would be required. So to get proper
        # inversing on broken up functions, you have to put .inverse() at the end of every chain, before it enters the main chain.
        # This will mess up your end result however, so use only for debugging purpouses.
    # The "not" operator doesn't currently work. Again, another large code refactoring would be required.
    # Everything is kinda just mushed together as generic dialect. Seperating of python and generic dialects would be helpful.
    # The Perl dialect isn't implemented at all. I don't know any perl, but this is meant to be a cross-platform solution.
# Usage:
    # optionalParams = multiOptional(match(',') + whitechunk() + chunk())
    # regex = stuff() + match('test(') + ifFollowedBy(match('ing') + optionalParams)
    # regex.test('Testing test(ing, ?) + test-ing!')


# Python Syntax (source: my python linter):
    # "."      Matches any character except a newline.
    # "^"      Matches the start of the string.
    # "$"      Matches the end of the string or just before the newline at
    #          the end of the string.
    # "*"      Matches 0 or more (greedy) repetitions of the preceding RE.
    #          Greedy means that it will match as many repetitions as possible.
    # "+"      Matches 1 or more (greedy) repetitions of the preceding RE.
    # "?"      Matches 0 or 1 (greedy) of the preceding RE.
    # *?,+?,?? Non-greedy versions of the previous three special characters.
    # {m,n}    Matches from m to n repetitions of the preceding RE.
    # {m,n}?   Non-greedy version of the above.
    # "\\"     Either escapes special characters or signals a special sequence.
    # []       Indicates a set of characters.
    #          A "^" as the first character indicates a complementing set.
    # "|"      A|B, creates an RE that will match either A or B.
    # (...)    Matches the RE inside the parentheses.
    #          The contents can be retrieved or matched later in the string.
    # (?aiLmsux) The letters set the corresponding flags defined below.
    # (?:...)  Non-grouping version of regular parentheses.
    # (?P name ...) The substring matched by the group is accessible by name.
    # (?P=name)     Matches the text matched earlier by the group named name.
    # (?#...)  A comment; ignored.
    # (?=...)  Matches if ... matches next, but doesn't consume the string.
    # (?!...)  Matches if ... doesn't match next.
    # (? =...) Matches if preceded by ... (must be fixed length).
    # (? !...) Matches if not preceded by ... (must be fixed length).
    # (?(id/name)yes|no) Matches yes pattern if the group with id/name matched,
    #                    the (optional) no pattern otherwise.

    # The special sequences consist of "\" and a character from the list below.
    # If the ordinary character is not on the list, then the resulting RE will match the second character.
    # \number  Matches the contents of the group of the same number.
    # \A       Matches only at the start of the string.
    # \Z       Matches only at the end of the string.
    # \b       Matches the empty string, but only at the start or end of a word.
    # \B       Matches the empty string, but not at the start or end of a word.
    # \d       Matches any decimal digit; equivalent to the set [0-9] in
    #          bytes patterns or string patterns with the ASCII flag.
    #          In string patterns without the ASCII flag, it will match the whole
    #          range of Unicode digits.
    # \D       Matches any non-digit character; equivalent to [^\d].
    # \s       Matches any whitespace character; equivalent to [ \t\n\r\f\v] in
    #          bytes patterns or string patterns with the ASCII flag.
    #          In string patterns without the ASCII flag, it will match the whole
    #          range of Unicode whitespace characters.
    # \S       Matches any non-whitespace character; equivalent to [^\s].
    # \w       Matches any alphanumeric character; equivalent to [a-zA-Z0-9_]
    #          in bytes patterns or string patterns with the ASCII flag.
    #          In string patterns without the ASCII flag, it will match the
    #          range of Unicode alphanumeric characters (letters plus digits
    #          plus underscore).
    #          With LOCALE, it will match the set [0-9_] plus characters defined
    #          as letters for the current locale.
    # \W       Matches the complement of \w.
    # \\       Matches a literal backslash.

# [What I'm using as] Generic syntax (source: DuckDuckGo):
    # Anchors
    # ^	Start of string or line
    # \A	Start of string
    # $	End of string or line
    # \Z	End of string
    # \b	Word boundary
    # \B	Not word boundary
    # \<	Start of word
    # \>	End of word
    # Character Classes
    # \c	Control character
    # \s	Whitespace [ \t\r\n\v\f]
    # \S	Not Whitespace [^ \t\r\n\v\f]
    # \d	Digit [0-9]
    # \D	Not digit [^0-9]
    # \w	Word [A-Za-z0-9_]
    # \W	Not Word [^A-Za-z0-9_]
    # \x	Hexadecimal digit [A-Fa-f0-9]
    # \O	Octal Digit [0-7]
    # POSIX Classes
    # [:upper:]	Uppercase letters [A-Z]
    # [:lower:]	Lowercase letters [a-z]
    # [:alpha:]	All letters [A-Za-z]
    # [:alnum:]	Digits and letters [A-Za-z0-9]
    # [:digit:]	Digits [0-9]
    # [:xdigit:]	Hexadecimal digits [0-9a-f]
    # [:punct:]	Punctuation
    # [:blank:]	Space and tab [ \t]
    # [:space:]	Blank characters [ \t\r\n\v\f]
    # [:cntrl:]	Control characters [\x00-\x1F\x7F]
    # [:graph:]	Printed characters [\x21-\x7E]
    # [:print:]	Printed characters and spaces [\x20-\x7E]
    # [:word:]	Digits, letters and underscore [A-Za-z0-9_]
    # Pattern Modifiers
    # //g	Global Match (all occurrences)
    # //i	Case-insensitive
    # //m	Multiple line
    # //s	Treat string as single line
    # //x	Allow comments and whitespace
    # //e	Evaluate replacement
    # //U	Ungreedy pattern
    # Escape Sequences
    # \	Escape following character
    # \Q	Begin literal sequence
    # \E	End literal sequence
    # Quantifiers
    # *	0 or more
    # +	1 or more
    # ?	0 or 1 (optional)
    # {3}	Exactly 3
    # {3,}	3 or more
    # {2,5}	2, 3, 4 or 5
    # Groups and Ranges
    # .	Any character except newline (\n)
    # (a|b)	a or b
    # (...)	Group
    # (?:...)	Passive (non-capturing) group
    # [abc]	Single character (a or b or c)
    # [^abc]	Single character (not a or b or c)
    # [a-q]	Single character range (a or b ... or q)
    # [A-Z]	Single character range (A or B ... or Z)
    # [0-9]	Single digit from 0 to 9
    # Assertions
    # ?=	Lookahead assertion
    # ?!	Negative lookahead
    # ?<=	Lookbehind assertion
    # ?!= / ?<!	Negative lookbehind
    # ?>	Once-only Subexpression
    # ?()	Condition [if then]
    # ?()|	Condition [if then else]
    # ?#	Comment
    # Special Characters
    # \n	New line
    # \r	Carriage return
    # \t	Tab
    # \v	Vertical tab
    # \f	Form feed
    # \ooo	Octal character ooo
    # \xhh	Hex character hh
    # String Replacement
    # $n	n-th non-passive group
    # $2	"xyz" in /^(abc(xyz))$/
    # $1	"xyz" in /^(?:abc)(xyz)$/
    # $`	Before matched string
    # $'	After matched string
    # $+	Last matched string
    # $&	Entire matched string

# I don't know Perl syntax specifically, if you do, and would like to help me, contact me!



import re
from enum import Enum, auto
from random import randint, choice, choices
try:
    from random_word import RandomWords
    _rw = RandomWords()
except ImportError:
    print("Can't import random_word (for the EasyRegex invert function). Try pip install Random-Words.")
    _rw = None


# This and the singletons are the only things in this file that *can* be used directly
class RegexDialect(Enum):
    GENERIC = 0
    PYTHON = 1
    PERL = 2


# This is a helper class that just holds the args and function so we can call them last
class EasyRegexFunctionCall:
    def __init__(self, genericFunc, args=(), invertedFunc=lambda cur, *_: cur, pythonFunc=None, perlFunc=None):
        self.genericFunc  = genericFunc
        self.pythonFunc   = pythonFunc if pythonFunc else self.genericFunc
        self.perlFunc     = perlFunc   if perlFunc   else self.genericFunc

        self.invertedFunc = invertedFunc
        self.args = args

    def __call__(self, cur, dialect=RegexDialect.GENERIC, inverted=False):
        # The inverted function uses the same args as the regular functions
        if inverted:
            return self.invertedFunc(cur, *self.args)

        if dialect == RegexDialect.GENERIC:
            return self.genericFunc(cur, *self.args)
        if dialect == RegexDialect.PYTHON:
            return self.pythonFunc(cur, *self.args)
        if dialect == RegexDialect.PERL:
            return self.perlFunc(cur, *self.args)


# These are mutable parts of the Regex statement, produced by EasyRegexElements. Should not be used directly.
class EasyRegexMember:
    def __init__(self, func:EasyRegexFunctionCall):
        self.funcList = [func]
        self.dialect = RegexDialect.GENERIC

    # Magic Functions
    def __str__(self):
        return self._compile()

    def __repr__(self):
        return 'EasyRegex("' + str(self) + '")'

    def __add__(self, thing):
        if type(thing) is str:
            self.funcList.append(EasyRegexFunctionCall(lambda cur: cur + thing))
        elif type(thing) is EasyRegexMember:
            self.funcList += thing.funcList
        return self

    def __iadd__(self, thing):
        tmp = self + thing
        return tmp

    def __not__(self):
        NotImplementedError('The not operator is not currently implemented')

    # Regular functions
    def _compile(self, inverted=False):
        regex = r''
        for func in self.funcList:
            regex = func(regex, self.dialect, inverted)
        return regex

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
        return self

    def debugStr(self):
        return self.debug().str()

    def test(self, testString):
        """ Tests the current regex expression to see if it's in @param testString.
        """
        print('-----------------------------------')
        print(f"Testing regex expression:\n{self}\nfor matches in:\n{testString}")
        match = re.search(str(self), testString)
        if match:
            print(f'Result: Found. Match = "{match.group()}", Span = {match.span()} ')
        else:
            print('Result: Not Found')
        print('-----------------------------------')

    def unsanitize(self, string):
        for part in EasyRegexSingleton.escapeChars:
            string = re.sub(part, part[1:], string)
        return string

    def inverse(self):
        """ "Inverts" the current Regex expression to give an example of a string it would match.
            Useful for debugging purposes.
        """
        try:
            from Cope import debug
        except ImportError:
            print(f"Inverted Regex = {self.unsanitize(self._compile(True))}")
        else:
            debug(self.unsanitize(self._compile(True)), name='Inverted Regex')
        return self

    def invert(self):
        """ Alias of inverse
        """
        return self.inverse()

    def printInverse(self):
        print(self.inverse())

    # Dialect Setters
    def usePythonDialect(self):
        self.dialect = RegexDialect.PYTHON

    def useGenericDialect(self):
        self.dialect = RegexDialect.GENERIC

    def usePerlDialect(self):
        self.dialect = RegexDialect.PERL

    def setDialect(self, dialect:RegexDialect):
        self.dialect = dialect


# These are constant singletons that do not change. When called, they produce EasyRegexMembers.
# This should not be used directly (except when making singletons)
class EasyRegexSingleton:
    # r'\<', r'\>', r'//'
    escapeChars = (r'\)', r'\(', r'\[', r'\]', r'\{', r'\}', r'\+', r'\*', r'\$', r'\@', r'\^', r'\:', r'\=', r'\-', r'\/')

    def __init__(self, func, invertedFunc=lambda cur, *_: cur, pythonFunc=None, perlFunc=None):
        def parseFuncParam(p):
            if callable(p):
                return p
            elif type(p) is str:
                return lambda cur: cur + p
            elif p is None:
                return None
            else:
                raise TypeError(f"Invalid type {type(p)} passed to EasyRegexSingleton constructor")

        self.func         = parseFuncParam(func)
        self.invertedFunc = parseFuncParam(invertedFunc)
        self.pythonFunc   = parseFuncParam(pythonFunc)
        self.perlFunc     = parseFuncParam(perlFunc)

    def __call__(self, *args):
        args = list(args)
        for cnt, i in enumerate(args):
            args[cnt] = self._sanitizeInput(i)
        return EasyRegexMember(EasyRegexFunctionCall(self.func, args, self.invertedFunc, self.pythonFunc, self.perlFunc))

    def _sanitizeInput(self, i):
        # If it's another chain, compile it
        if type(i) is EasyRegexMember:
            return str(i)
        elif type(i) is str:
            for part in self.escapeChars:
                i = re.sub(r'(?<!\\)' + part, part, i)
            return i
        else:
            raise TypeError(f'Incorrect type {type(i)} given to EasyRegex parameter: Must be string or another EasyRegex chain.')



# Inverting helpers
_alot = 6
_digits = '0123456789'
_letters = 'abcdefghijklmnopqrstuvwxyz'
_letters += _letters.upper()
_punctuation = r''',./;'[]\=-)(*&^%$#@!~`+{}|:"<>?'''
_whitespace = ' \t'
_everything = _digits + _letters + _punctuation + _whitespace + '_'

_proceedOpen = '   <if followed by> { '
_notProceedOpen = '   <if not followed by> { '
_preceedOpen = '   <if preceeded by> { '
_notPreceedOpen = '    <if not preceeded by> { '
_optionalClose = ' }   '

def _defaultInvert(s):
    return lambda cur: cur + s

def _randWord():
    if _rw:
        return _rw.get_random_word()
    else:
        return ''.join(choices(_letters + '_', k=randint(1, _alot)))

def _prevThing(cur):
    try:
        return re.search(r'(\\?\w+)\Z', cur).group()
    except AttributeError:
        return ''

#* All the singletons
# Positional
# wordStartsWith = EasyRegexSingleton(lambda cur, input: input + r'\<' + cur,
#                                     lambda cur, input: input + cur)
# wordEndsWith   = EasyRegexSingleton(lambda cur, input: cur   + r'\>' + input,
#                                     lambda cur, input: cur   + r'\>' + input)
startsWith     = EasyRegexSingleton(lambda cur, input: input + r'\A' + cur,
                                    lambda cur, input: input + cur)
endsWith       = EasyRegexSingleton(lambda cur, input: cur   + r'\z' + input,
                                    lambda cur, input: input + cur)
# ifAtBeginning  = EasyRegexSingleton(lambda cur: r'^' + cur,
#                                     lambda cur: r'^' + cur)
# ifAtEnd        = EasyRegexSingleton(r'$',
#                                     r'$')

# Matching
match     = EasyRegexSingleton(lambda cur, input: cur + input,
                               lambda cur, input: cur + input)
isExactly = EasyRegexSingleton(lambda cur, input: "^" + input + '$',
                               lambda cur, input: input)
add       = match
# Not sure how to implement these, I don't have enough experience with Regex
# \b       Matches the empty string, but only at the start or end of a word.
# \B       Matches the empty string, but not at the start or end of a word.

# Amounts
matchMax      = EasyRegexSingleton(lambda cur,      input='':      cur + ('' if not len(input) else r'(' + input + r')') + r'+',
                                   lambda cur,      input='':      cur + ((_prevThing(cur) if not len(input) else input) * randint(0, _alot)))
matchNum      = EasyRegexSingleton(lambda cur, num, input='':      cur + ('' if not len(input) else r'(' + input + r')') + r'{' + str(num) + r'}',
                                   lambda cur, num, input='':      cur + ((_prevThing(cur) if not len(input) else input) * num))
matchRange    = EasyRegexSingleton(lambda cur, min, max, input='': cur + ('' if not len(input) else r'(' + input + r')') + r'{' + str(min) + r',' + str(max) + r'}',
                                   lambda cur, min, max, input='': cur + ((_prevThing(cur) if not len(input) else input) * randint(min, max)))
matchMoreThan = EasyRegexSingleton(lambda cur, min, input='':      cur + ('' if not len(input) else r'(' + input + r')') + r'{' + str(min - 1) + r',}',
                                   lambda cur, min, input='':      cur + ((_prevThing(cur) if not len(input) else input) * randint(min - 1, _alot + min - 1)))
matchAtLeast  = EasyRegexSingleton(lambda cur, min, input='':      cur + ('' if not len(input) else r'(' + input + r')') + r'{' + str(min) + r',}',
                                   lambda cur, min, input='':      cur + ((_prevThing(cur) if not len(input) else input) * randint(min, _alot + min)))

# Single Characters
whitespace = EasyRegexSingleton(r'\s',  _defaultInvert(_whitespace))
whitechunk = EasyRegexSingleton(r'\s+', _defaultInvert(_whitespace * randint(1, _alot)))
digit      = EasyRegexSingleton(r'\d',  _defaultInvert(choice(_digits)))
number     = EasyRegexSingleton(r'\d+', _defaultInvert(''.join(choices(_digits, k=randint(1, _alot)))))
word       = EasyRegexSingleton(r'\w+', _defaultInvert(_randWord()))
wordChar   = EasyRegexSingleton(r'\w',  _defaultInvert(choice(_letters + '_')))
hexDigit   = EasyRegexSingleton(r'\x',  _defaultInvert(choice(_digits + 'ABCDEF')))
octDigit   = EasyRegexSingleton(r'\O',  _defaultInvert(choice(_digits[:8])))
anything   = EasyRegexSingleton(r'.',   _defaultInvert(choice(_everything)))
chunk      = EasyRegexSingleton(r'.+',  _defaultInvert(''.join(choices(_everything, k=randint(1, _alot)))))
stuff      = chunk

# Explicit Characters
spaceOrTab     = EasyRegexSingleton(r'[ \t]',  _defaultInvert(' \t'))
newLine        = EasyRegexSingleton(r'\n',     _defaultInvert('\n'))
carriageReturn = EasyRegexSingleton(r'\r',     _defaultInvert('\r'))
tab            = EasyRegexSingleton(r'\t',     _defaultInvert('\t'))
space          = EasyRegexSingleton(r' ',      _defaultInvert(' '))
quote          = EasyRegexSingleton(r'(\'|")', _defaultInvert(choice('\'"')))
verticalTab    = EasyRegexSingleton(r'\v',     _defaultInvert('\v'))
formFeed       = EasyRegexSingleton(r'\f',     _defaultInvert('\f'))

# Not Chuncks
notWhitespace = EasyRegexSingleton(r'\S', _defaultInvert(choice(_digits  + _letters     + _punctuation + '_')))
notDigit      = EasyRegexSingleton(r'\D', _defaultInvert(choice(_letters + _whitespace  + _punctuation + '_')))
notWord       = EasyRegexSingleton(r'\W', _defaultInvert(choice(_digits  + _punctuation + _whitespace)))

# Optionals
optional      = EasyRegexSingleton(lambda cur, input='': cur + ('' if not len(input) else r'(' + input + r')') + r'?',
                                   lambda cur, input='': cur + (_prevThing(cur) if not len(input) else input) * randint(0, 1))
multiOptional = EasyRegexSingleton(lambda cur, input='': cur + ('' if not len(input) else r'(' + input + r')') + r'*',
                                   lambda cur, input='': cur + (_prevThing(cur) if not len(input) else input) * randint(0, 3))
either        = EasyRegexSingleton(lambda cur, input, or_input: cur + rf'({input}|{or_input})',
                                   lambda cur, input, or_input: cur + input if randint(0, 1) else or_input)
anyBetween    = EasyRegexSingleton(lambda cur, input, and_input: cur + r'[' + input + r'-' + and_input + r']')

def _anyOfFunc(cur, *inputs):
    cur += r'['
    for i in inputs:
        cur += i
    cur += r']'
    return cur
anyOf = EasyRegexSingleton(_anyOfFunc, lambda cur, *inputs: choice(inputs))

def _anyExceptFunc(cur, *inputs):
    cur += r'[^'
    for i in inputs:
        cur += i
    cur += r']'
    return cur

def _anyExceptInvertedFunc(cur, *inputs):
    for i in inputs:
        _everything.replace(i, '')
    return cur + _everything
anyExcept  = EasyRegexSingleton(_anyExceptFunc, _anyExceptInvertedFunc)

# Sets
anyUppercase       = EasyRegexSingleton(r' [A-Z]',      _defaultInvert(choice(_letters.upper())))
anyLowercase       = EasyRegexSingleton(r' [a-z]',      _defaultInvert(choice(_letters.lower())))
anyLetter          = EasyRegexSingleton(r'[A-Za-z]',    _defaultInvert(choice(_letters)))
anyAlphaNum        = EasyRegexSingleton(r'[A-Za-z0-9]', _defaultInvert(choice(_letters + _digits)))
anyDigit           = EasyRegexSingleton(r'[0-9]',       _defaultInvert(choice(_digits)))
anyHexDigit        = EasyRegexSingleton(r'[0-9a-fA-F]', _defaultInvert(choice(_digits + "ABCDEF")))
anyOctDigit        = EasyRegexSingleton(r'[0-7]',       _defaultInvert(choice(_digits[:8])))
anyPunctuation     = EasyRegexSingleton(r'[:punct:]',   _defaultInvert(choice(_punctuation)))
anyBlank           = EasyRegexSingleton(r'[ \t\r\n\v\f]', _defaultInvert(choice(_whitespace)))
anyControllers     = EasyRegexSingleton(r'[\x00-\x1F\x7F]')
anyPrinted         = EasyRegexSingleton(r'[\x21-\x7E]', _defaultInvert(choice(_everything.replace(' ', ''))))
anyPrintedAndSpace = EasyRegexSingleton(r'[\x20-\x7E]', _defaultInvert(choice(_everything)))
anyAlphaNum_       = EasyRegexSingleton(r'[A-Za-z0-9_]', _defaultInvert(choice(_letters + _digits + '_')))

# Numbers
octalNum = EasyRegexSingleton(lambda cur, num: cur + r'\\' + num, lambda cur, num: cur + oct(num))
hexNum   = EasyRegexSingleton(lambda cur, num: cur + r'\x' + num, lambda cur, num: cur + hex(num))

# Conditionals
ifProceededBy    = EasyRegexSingleton(lambda cur, condition: cur + fr'(?={condition})',
                                      lambda cur, condition: cur + _proceedOpen + condition + _optionalClose)
ifNotProceededBy = EasyRegexSingleton(lambda cur, condition: cur + fr'(?!{condition})',
                                      lambda cur, condition: cur + _notProceedOpen + condition + _optionalClose)
ifPrecededBy     = EasyRegexSingleton(lambda cur, condition: fr'(?<={condition})' + cur,
                                      lambda cur, condition: _preceedOpen + condition + _optionalClose + cur)
ifNotPrecededBy  = EasyRegexSingleton(lambda cur, condition: fr'(?<!{condition})' + cur,
                                      lambda cur, condition: _notPreceedOpen + condition + _optionalClose + cur)
ifFollowedBy     = ifProceededBy
ifNotFollowedBy  = ifNotProceededBy

# Groups
# I don't understand these.
# (?aiLmsux) The letters set the corresponding flags defined below.
# \number  Matches the contents of the group of the same number.
group          = EasyRegexSingleton(lambda cur, chain: f'{cur}({chain})',
                                    lambda cur, chain: cur + chain)
# I don't think this inverse is correct
notGroup       = EasyRegexSingleton(lambda cur, chain: f'{cur}(?:{chain})',
                                    lambda cur, chain: cur + chain)

namedGroup     = EasyRegexSingleton(lambda cur, name, chain: f'{cur}(?P {name} {chain})')
referenceGroup = EasyRegexSingleton(lambda cur, name:        f'{cur}(?P={name})')


# TODO Implement Dialects
# Global Flags -- I don't think these will work
matchGlobally     = EasyRegexSingleton(r'//g')
caseInsensitive   = EasyRegexSingleton(r'//i')
matchMultiLine    = EasyRegexSingleton(r'//m')
treatAsSingleLine = EasyRegexSingleton(r'//s')
notGreedy         = EasyRegexSingleton(r'//U')
