import re
from enum import Enum

class EasyRegex:
    r""" EasyRegex! A Class for making regular expressions syntax easier.

        Note: This class does NOT actually do any regular expression processing.
              That's for the re module to do. All this class does is generate a
              regex command which is available on calling str() (the method or
              the cast), or compile(), which compiles it into the re module for
              you.

        Usage:
            EasyRegex().match("Foo{").ifProceededBy(EasyRegex().word().match("}")))
            ->
            "Foo\{(?=\w+\})"

            To start any regex command, call the default constructor, or if you
                already know some regex syntax, call the constructor with a base command.
            Then just chain method calls in the order you wish to construct the command,
                ending with .str(), .compile(), or nothing (it automatically casts to a
                string).
            Global flags such as caseInsensitive() and matchMultiLine() are available,
                and can be used at any point in the chain. However, they do not work with the
                python re module, so don't use them.
            Assertions ifProceededBy(), ifPreceededBy(), and their inverts are available.
                Note that any method that takes a statement can take a brand new chain as a
                parameter.
            You do still have to escape the \ character (i.e. \\), however all other
                characters you do not have to escape, that's automatically handled for you.
            Different flavors are available with alternate syntaxes. They're defined in the
                EasyRegex.Flavor enum. Available are Genertic, Python, and Perl (Perl is not
                implemented)
    """

    class Flavor(Enum):
        GENERIC = 0
        PYTHON = 1
        PERL = 2


    def __init__(self, expr=''):
        self.regexpr = expr
        self.flavor = EasyRegex.Flavor.PYTHON
        self.globalFlags = ""
        # self.passive = False

# Magic Functions
    def __str__(self):
        # return '(' + ('?:' if self.passive else '') + self.regexpr + self.globalFlags + ')'
        return self.regexpr + self.globalFlags

    def __repr__(self):
        return 'RegexGroup("' + str(self) + '")'

    def __add__(self, thing):
        return thing + str(self)

    def __iadd__(self, thing):
        thing += str(self)

# Non-Regex functions
    def compile(self):
        return re.compile(str(self))

    def str(self):
        return str(self)

    def debug(self):
        try:
            from Cope import debug
        except ImportError:
            print(f"Compiled EasyRegex String = {self.regexpr}")
        else:
            debug(self.regexpr, name='Compiled EasyRegex String')
        return self

    def debugStr(self):
        return self.debug().str()

    def _correctInput(self, i):
        # If it's another chain, we've already corrected the input
        if type(i) is EasyRegex:
            return str(i)
        # i = re.sub(r'\\', r'\\', i)
        # i = re.sub(r'\((?<!\\)', r'\(', i)
        i = re.sub(r'(?<!\\)\)', r'\)', i)
        i = re.sub(r'(?<!\\)\(', r'\(', i)
        i = re.sub(r'(?<!\\)\[', r'\[', i)
        i = re.sub(r'(?<!\\)\]', r'\]', i)
        i = re.sub(r'(?<!\\)\{', r'\{', i)
        i = re.sub(r'(?<!\\)\}', r'\}', i)
        i = re.sub(r'(?<!\\)\+', r'\+', i)
        i = re.sub(r'(?<!\\)\*', r'\*', i)
        i = re.sub(r'(?<!\\)\$', r'\$', i)
        i = re.sub(r'(?<!\\)\@', r'\@', i)
        i = re.sub(r'(?<!\\)\^', r'\^', i)
        i = re.sub(r'(?<!\\)\:', r'\:', i)
        i = re.sub(r'(?<!\\)\=', r'\=', i)
        i = re.sub(r'(?<!\\)\-', r'\-', i)
        i = re.sub(r'(?<!\\)\/', r'\/', i)
        # i = re.sub(r'(?<!\\)\<', r'\<', i)
        # i = re.sub(r'(?<!\\)\>', r'\>', i)
        # i = re.sub(r'(?<!/)/', r'//', i)
        return i

# Flavor Setters
    def usePythonFlavor(self):
        self.flavor = self.Flavor.PYTHON

    def useGenericFlavor(self):
        self.flavor = self.Flavor.GENERIC

    def usePerlFlavor(self):
        self.flavor = self.Flavor.PERL

    def setFlavor(self, flavor):
        self.flavor = flavor

# Positional
    def wordStartsWith(self, group):
        group = self._correctInput(group)
        self.regexpr = group + r'\<' + self.regexpr
        return self

    def wordEndsWith(self, group):
        group = self._correctInput(group)
        self.regexpr += r'\>' + group
        return self

    def startsWith(self, group):
        group = self._correctInput(group)
        self.regexpr = group + r'\A' + self.regexpr
        return self

    def endsWith(self, group):
        group = self._correctInput(group)
        self.regexpr += r'\Z' + group
        return self

    def ifAtBeginning(self):
        self.regexpr = r'^' + self.regexpr
        return self

    def ifAtEnd(self):
        self.regexpr += r'$'
        return self

# Matching
    def match(self, group):
        group = self._correctInput(group)
        self.regexpr += group
        return self

    def add(self, group):
        group = self._correctInput(group)
        self.regexpr += group
        return self

    def isExactly(self, group):
        group = self._correctInput(group)
        self.regexpr += "^" + group + '$'
        return self

# Amounts
    def matchMax(self, group=''):
        group = self._correctInput(group)
        self.regexpr += ('' if not len(group) else '(' + group + ')') + r'+'
        return self

    def matchNum(self, num, group=''):
        group = self._correctInput(group)
        self.regexpr += ('' if not len(group) else '(' + group + ')') + '{' + str(num) + '}'
        return self

    def matchRange(self, min, max, group=''):
        group = self._correctInput(group)
        self.regexpr += ('' if not len(group) else '(' + group + ')') + '{' + str(min) + ',' + str(max) + '}'
        return self

    def matchMoreThan(self, min, group=''):
        group = self._correctInput(group)
        self.regexpr += ('' if not len(group) else '(' + group + ')') + '{' + str(min - 1) + ',}'
        return self

    def matchAtLeast(self, min, group=''):
        group = self._correctInput(group)
        self.regexpr += ('' if not len(group) else '(' + group + ')') + '{' + str(min) + ',}'
        return self

# Single Characters
    def whitespace(self):
        self.regexpr += r'\s'
        return self

    def whitechunk(self):
        self.regexpr += r'\s+'
        return self

    def digit(self):
        self.regexpr += r'\d'
        return self

    def number(self):
        self.regexpr += r'\d+'
        return self

    def word(self):
        self.regexpr += r'\w+'
        return self

    def wordChar(self):
        self.regexpr += r'\w'
        return self

    def hexDigit(self):
        self.regexpr += r'\x'
        return self

    def octDigit(self):
        self.regexpr += r'\O'
        return self

    def anything(self):
        self.regexpr += r'.'
        return self

# Explicit Characters
    def spaceOrTab(self):
        self.regexpr += r'[ \t]'
        return self

    def newLine(self):
        self.regexpr += r'\n'
        return self

    def carriageReturn(self):
        self.regexpr += r'\r'
        return self

    def tab(self):
        self.regexpr += r'\t'
        return self

    def space(self):
        self.regexpr += r' '
        return self

    def quote(self):
        self.regexpr += '(\'|")'
        return self

    def verticalTab(self):
        self.regexpr += r'\v'
        return self

    def formFeed(self):
        self.regexpr += r'\f'
        return self

# Not Chuncks
    def notWhitespace(self):
        self.regexpr += r'\S'
        return self

    def notDigit(self):
        self.regexpr += r'\D'
        return self

    def notWord(self):
        self.regexpr += r'\W'
        return self

# Optionals
    def optional(self, group=''):
        group = self._correctInput(group)
        self.regexpr += ('' if not len(group) else '(' + group + ')') + r'?'
        return self

    def multiOptional(self, group=''):
        group = self._correctInput(group)
        self.regexpr += ('' if not len(group) else '(' + group + ')') + r'*'
        return self

    def either(self, group, or_group):
        group = self._correctInput(group)
        or_group = self._correctInput(or_group)
        self.regexpr += rf'({group}|{or_group})'
        return self

    def anyOf(self, *groups):
        self.regexpr += r'['
        for i in groups:
            i = self._correctInput(i)
            self.regexpr += i
        self.regexpr += r']'
        return self

    def anyExcept(self, *groups):
        self.regexpr += r'[^'
        for i in groups:
            i = self._correctInput(i)
            self.regexpr += i
        self.regexpr += r']'
        return self

    def anyBetween(self, group, and_group):
        group = self._correctInput(group)
        and_group = self._correctInput(and_group)
        self.regexpr += r'[' + group + '-' + and_group + r']'
        return self

# Sets
    def anyUppercase(self):
        self.regexpr += r' [A-Z]'
        return self

    def anyLowercase(self):
        self.regexpr += r' [a-z]'
        return self

    def anyLetter(self):
        self.regexpr += r'[A-Za-z]'
        return self

    def anyAlphaNum(self):
        self.regexpr += r'[A-Za-z0-9]'
        return self

    def anyDigit(self):
        self.regexpr += r'[0-9]'
        return self

    def anyHexDigit(self):
        self.regexpr += r'[0-9a-f]'
        return self

    def anyOctDigit(self):
        self.regexpr += r'[0-7]'
        return self

    def anyPunctuation(self):
        self.regexpr += r'[:punct:]'
        return self

    def anyBlank(self):
        self.regexpr += r'[ \t\r\n\v\f]'
        return self

    def anyControllers(self):
        self.regexpr += r'[\x00-\x1F\x7F]'
        return self

    def anyPrinted(self):
        self.regexpr += r'[\x21-\x7E]'
        return self

    def anyPrintedAndSpace(self):
        self.regexpr += r'[\x20-\x7E]'
        return self

    def anyAlphaNum_(self):
        self.regexpr += r'[A-Za-z0-9_]'
        return self

# Numbers
    def octalNum(self, num):
        self.regexpr += '\\' + num
        return self

    def hexNum(self, num):
        self.regexpr += r'\x' + num
        return self

# Global Flags
    def matchGlobally(self):
        self.globalFlags += r'//g'
        return self

    def caseSensitive(self):
        return self

    def caseInsensitive(self):
        self.globalFlags += r'//i'
        return self

    # def caseInsensitive(self):
        # self.globalFlags += r'//i'
        # self.regexpr = re.sub(r'[A-Za-z]', , self.regexpr)
        # return self

    def matchMultiLine(self):
        self.globalFlags += r'//m'
        return self

    def treatAsSingleLine(self):
        self.globalFlags += r'//s'
        return self

    def greedy(self):
        return self

    def notGreedy(self):
        self.globalFlags += r'//U'
        return self

# Conditionals
    def ifProceededBy(self, condition_group):
        condition_group = self._correctInput(condition_group)
        self.regexpr = self.regexpr + fr'(?={condition_group})'
        return self

    def ifNotProceededBy(self, condition_group):
        condition_group = self._correctInput(condition_group)
        self.regexpr = self.regexpr + fr'(?!{condition_group})'
        return self

    def ifPrecededBy(self, condition_group):
        condition_group = self._correctInput(condition_group)
        self.regexpr = fr'(?<={condition_group})' + self.regexpr

        return self

    def ifNotPrecededBy(self, condition_group):
        condition_group = self._correctInput(condition_group)
        self.regexpr = fr'(?<!{condition_group})' + self.regexpr
        return self


ere = EasyRegex


# Python flavor:
r'''
    "."      Matches any character except a newline.
    "^"      Matches the start of the string.
    "$"      Matches the end of the string or just before the newline at
             the end of the string.
    "*"      Matches 0 or more (greedy) repetitions of the preceding RE.
             Greedy means that it will match as many repetitions as possible.
    "+"      Matches 1 or more (greedy) repetitions of the preceding RE.
    "?"      Matches 0 or 1 (greedy) of the preceding RE.
    *?,+?,?? Non-greedy versions of the previous three special characters.
    {m,n}    Matches from m to n repetitions of the preceding RE.
    {m,n}?   Non-greedy version of the above.
    "\\"     Either escapes special characters or signals a special sequence.
    []       Indicates a set of characters.
             A "^" as the first character indicates a complementing set.
    "|"      A|B, creates an RE that will match either A or B.
    (...)    Matches the RE inside the parentheses.
             The contents can be retrieved or matched later in the string.
    (?aiLmsux) The letters set the corresponding flags defined below.
    (?:...)  Non-grouping version of regular parentheses.
    (?P name ...) The substring matched by the group is accessible by name.
    (?P=name)     Matches the text matched earlier by the group named name.
    (?#...)  A comment; ignored.
    (?=...)  Matches if ... matches next, but doesn't consume the string.
    (?!...)  Matches if ... doesn't match next.
    (? =...) Matches if preceded by ... (must be fixed length).
    (? !...) Matches if not preceded by ... (must be fixed length).
    (?(id/name)yes|no) Matches yes pattern if the group with id/name matched,
                       the (optional) no pattern otherwise.
The special sequences consist of "\" and a character from the list below. If the ordinary character is not on the list, then the resulting RE will match the second character.

    \number  Matches the contents of the group of the same number.
    \A       Matches only at the start of the string.
    \Z       Matches only at the end of the string.
    \b       Matches the empty string, but only at the start or end of a word.
    \B       Matches the empty string, but not at the start or end of a word.
    \d       Matches any decimal digit; equivalent to the set [0-9] in
             bytes patterns or string patterns with the ASCII flag.
             In string patterns without the ASCII flag, it will match the whole
             range of Unicode digits.
    \D       Matches any non-digit character; equivalent to [^\d].
    \s       Matches any whitespace character; equivalent to [ \t\n\r\f\v] in
             bytes patterns or string patterns with the ASCII flag.
             In string patterns without the ASCII flag, it will match the whole
             range of Unicode whitespace characters.
    \S       Matches any non-whitespace character; equivalent to [^\s].
    \w       Matches any alphanumeric character; equivalent to [a-zA-Z0-9_]
             in bytes patterns or string patterns with the ASCII flag.
             In string patterns without the ASCII flag, it will match the
             range of Unicode alphanumeric characters (letters plus digits
             plus underscore).
             With LOCALE, it will match the set [0-9_] plus characters defined
             as letters for the current locale.
    \W       Matches the complement of \w.
    \\       Matches a literal backslash.
'''


# Generic syntax:
r'''
    Anchors
    ^	Start of string or line
    \A	Start of string
    $	End of string or line
    \Z	End of string
    \b	Word boundary
    \B	Not word boundary
    \<	Start of word
    \>	End of word
    Character Classes
    \c	Control character
    \s	Whitespace [ \t\r\n\v\f]
    \S	Not Whitespace [^ \t\r\n\v\f]
    \d	Digit [0-9]
    \D	Not digit [^0-9]
    \w	Word [A-Za-z0-9_]
    \W	Not Word [^A-Za-z0-9_]
    \x	Hexadecimal digit [A-Fa-f0-9]
    \O	Octal Digit [0-7]
    POSIX Classes
    [:upper:]	Uppercase letters [A-Z]
    [:lower:]	Lowercase letters [a-z]
    [:alpha:]	All letters [A-Za-z]
    [:alnum:]	Digits and letters [A-Za-z0-9]
    [:digit:]	Digits [0-9]
    [:xdigit:]	Hexadecimal digits [0-9a-f]
    [:punct:]	Punctuation
    [:blank:]	Space and tab [ \t]
    [:space:]	Blank characters [ \t\r\n\v\f]
    [:cntrl:]	Control characters [\x00-\x1F\x7F]
    [:graph:]	Printed characters [\x21-\x7E]
    [:print:]	Printed characters and spaces [\x20-\x7E]
    [:word:]	Digits, letters and underscore [A-Za-z0-9_]
    Pattern Modifiers
    //g	Global Match (all occurrences)
    //i	Case-insensitive
    //m	Multiple line
    //s	Treat string as single line
    //x	Allow comments and whitespace
    //e	Evaluate replacement
    //U	Ungreedy pattern
    Escape Sequences
    \	Escape following character
    \Q	Begin literal sequence
    \E	End literal sequence
    Quantifiers
    *	0 or more
    +	1 or more
    ?	0 or 1 (optional)
    {3}	Exactly 3
    {3,}	3 or more
    {2,5}	2, 3, 4 or 5
    Groups and Ranges
    .	Any character except newline (\n)
    (a|b)	a or b
    (...)	Group
    (?:...)	Passive (non-capturing) group
    [abc]	Single character (a or b or c)
    [^abc]	Single character (not a or b or c)
    [a-q]	Single character range (a or b ... or q)
    [A-Z]	Single character range (A or B ... or Z)
    [0-9]	Single digit from 0 to 9
    Assertions
    ?=	Lookahead assertion
    ?!	Negative lookahead
    ?<=	Lookbehind assertion
    ?!= / ?<!	Negative lookbehind
    ?>	Once-only Subexpression
    ?()	Condition [if then]
    ?()|	Condition [if then else]
    ?#	Comment
    Special Characters
    \n	New line
    \r	Carriage return
    \t	Tab
    \v	Vertical tab
    \f	Form feed
    \ooo	Octal character ooo
    \xhh	Hex character hh
    String Replacement
    $n	n-th non-passive group
    $2	"xyz" in /^(abc(xyz))$/
    $1	"xyz" in /^(?:abc)(xyz)$/
    $`	Before matched string
    $'	After matched string
    $+	Last matched string
    $&	Entire matched string
'''


def invertRegex(regex):
    for re, to in self.thingsToMatch.items():
        regex = re.sub(re, to, regex)

    return regex


r'''
    wordStartsWith:
    group + r'\<' + self.regexpr

    wordEndsWith:
    r'\>' + group

    startsWith:
    group + r'\A' + self.regexpr

    endsWith:
    r'\Z' + group

    match:
    group

    isExactly:
    "^" + group + '$'

    optional:
    ('' if not len(group) else '(' + group + ')') + r'?'

    multiOptional:
    ('' if not len(group) else '(' + group + ')') + r'*'

    matchMax:
    ('' if not len(group) else '(' + group + ')') + r'+'

    matchNum num,:
    ('' if not len(group) else '(' + group + ')') + '{' + str(num) + '}'

    matchRange min, max,:
    ('' if not len(group) else '(' + group + ')') + '{' + str(min) + ',' + str(max) + '}'

    matchMoreThan min,:
    ('' if not len(group) else '(' + group + ')') + '{' + str(min - 1) + ',}'

    matchAtLeast min,:
    ('' if not len(group) else '(' + group + ')') + '{' + str(min) + ',}'

    whitespace:
    r'\s'

    whitechunk:
    r'\s+'

    digit:
    r'\d'

    number:
    r'\d+'

    word:
    r'\w+'

    wordChar:
    r'\w'

    notWhitespace:
    r'\S'

    notDigit:
    r'\D'

    notWord:
    r'\W'

    hexDigit:
    r'\x'

    octDigit:
    r'\O'

    anything:
    r'.'

    either:
    rf'({group}|{or_group})'

    anyOf *:
    r'['

    for i in:
        i
    r']'

    anyExcept *:
    r'[^'

    for i in:
        i
    r']'

    anyBetween:
    r'[' + group + '-' + and_group + r']'

    anyUppercase:
    r' [A-Z]'

    anyLowercase:
    r' [a-z]'

    anyLetter:
    r'[A-Za-z]'

    anyAlphaNum:
    r'[A-Za-z0-9]'

    anyDigit:
    r'[0-9]'

    anyHexDigit:
    r'[0-9a-f]'

    anyOctDigit:
    r'[0-7]'

    anyPunctuation:

    r'[:punct:]'

    spaceOrTab:
    r'[ \t]'

    anyBlank:
    r'[ \t\r\n\v\f]'

    anyControllers:
    r'[\x00-\x1F\x7F]'

    anyPrinted:
    r'[\x21-\x7E]'

    anyPrintedAndSpace:
    r'[\x20-\x7E]'

    anyAlphaNum_:
    r'[A-Za-z0-9_]'

    newLine:
    r'\n'

    carriageReturn:
    r'\r'

    tab:
    r'\t'

    space:
    r' '

    quote:
    '(\'|")'

    verticalTab:
    r'\v'

    formFeed:
    r'\f'

    octalNum num):
    '\\' + num

    hexNum num):
    r'\x' + num

    add:
    group

    ifAtBeginning:
    r'^' + self.regexpr

    ifAtEnd:
    r'$'

    ifProceededBy condition_:
    self.regexpr + fr'(?={condition_group})'

    ifNotProceededBy condition_:
    self.regexpr + fr'(?!{condition_group})'

    ifPrecededBy condition_:
    fr'(?<={condition_group})'

    ifNotPrecededBy condition_:
    fr'(?<!{condition_group})'
'''

testRegex = None
testString = None


# testRegex = \
# ere().anything().matchMax().ifPrecededBy(ere().match('limit(')).ifProceededBy(ere().match(',').anything().matchMax().match(','))

# testString = \
# 'limit(x + 6, x, oo)'

if testRegex:
    print(testRegex.str())
    if testString:
        print(re.search(testRegex.str(), testString))