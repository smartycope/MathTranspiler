#!/usr/bin/env python3
""" Cope.py
A bunch of generic functions and classes useful in multiple projects
"""
__version__ = '3.1.0'
__author__ = 'Copeland Carter'
__email__ = 'smartycope@gmail.com'
__license__ = 'GPL 3.0'
__copyright__ = '(c) 2021, Copeland Carter'


import atexit
import math
import re
from ctypes import pointer, py_object
from inspect import stack
from os.path import basename, dirname, join
# from Point import Pointf, Pointi, Point
from random import randint
from time import process_time
from typing import Any, Callable, Iterable, Optional, Union

try:
    from varname import (ImproperUseError, VarnameRetrievingError, argname, nameof)
except ImportError:
    Warning("Can't to import Cope.py (for debugging). Try installing varname via pip (pip install varname --user).")
    varnameImported = False
else:
    varnameImported = True

# This is because I write a lot of C/C++ code
true, false = True, False

_debugCount = 0

# Override the debug parameters and display the file/function for each debug call
#   (useful for finding debug calls you left laying around and forgot about)
DISPLAY_FILE = False
DISPLAY_PATH = False
DISPLAY_FUNC = False
DISPLAY_LINK = False
HIDE_TODO    = False
# FORCE_TODO_LINK = False

# Default color constants
DEFAULT_COLOR = (204, 204, 204)
ALERT_COLOR =   (220, 0, 0)
WARN_COLOR =    (150, 30, 30)

#* A set of distinct characters for debugging
_colors = [(43, 142, 213), (19, 178, 118), (163, 61, 148), (255, 170, 0), (255, 170, 255), (170, 0, 255)]

# Default colors for debugging -- None for using the previously set color
NOTE_CALL_COLOR =     (211, 130, 0)
EMPTY_COLOR =         NOTE_CALL_COLOR
CONTEXT_COLOR =       None
COUNT_COLOR =         (34, 111, 157)
DEFAULT_DEBUG_COLOR = (34, 179, 99)
TODO_COLOR            = (128, 64, 64)
STACK_TRACE_COLOR     = (159, 148, 211)

#* Convenience commonly used paths. ROOT can be set by the setRoot() function
DIR  = dirname(__file__)
ROOT = dirname(DIR) if basename(DIR) in ('src', 'source') else DIR

VERBOSE = False

#* Setters for the gloabals
def displayAllFiles(to=True):
    global DISPLAY_FILE
    DISPLAY_FILE = to

def displayAllPaths(to=True):
    global DISPLAY_PATH
    DISPLAY_PATH = to

def displayAllFuncs(to=True):
    global DISPLAY_FUNC
    DISPLAY_FUNC = to

def displayAllLinks(to=True):
    global DISPLAY_LINK
    DISPLAY_LINK = to

def hideAllTodos(to=True):
    global HIDE_TODO
    HIDE_TODO = to

def setRoot(path):
    global ROOT
    ROOT = path

def setVerbose(to=True):
    global VERBOSE
    VERBOSE = to

def verbose():
    global VERBOSE
    return VERBOSE


# This is bad practice, try to avoid using these
def ref(obj):
    return pointer(py_object(obj))

def deref(ptr):
    return ptr.contents.value


def resetColor():
    print('\033[0m',  end='')
    print('\033[39m', end='')
    print('\033[49m', end='')
    # print('', end='')


def parseColorParams(r, g=None, b=None, a=None, bg=False) -> "((r, g, b), background)":
    """ Parses given color parameters and returns a tuple of equalized
        3-4 item tuple of color data, and a bool for background.
        Can take 3-4 tuple/list of color data, or r, g, and b as induvidual parameters,
        and a single int (0-5) representing a preset unique color id.
        a and bg are always available as optional or positional parameters.

        Note: Seperate color specifications for foreground and background are not currently
        supported. bg is just a bool.
    """
    #* We've been given a list of values
    if type(r) in (tuple, list):
        if len(r) not in (3, 4):
            raise SyntaxError(f'Incorrect number ({len(r)}) of color parameters given')
        else:
            return (tuple(r), (False if g is None else g) if not bg else bg)

    #* We've been given a single basic value
    elif type(r) is int and b is None:
        return (_colors[r] + ((a,) if a is not None else ()), (False if g is None else g) if not bg else bg)

    #* We've been given 3 seperate parameters
    elif type(r) is int and g is not None and b is not None:
        if type(a) is int:
            return ((r, g, b, a), bg)
        elif type(a) is bool or a is None:
            return ((r, g, b), bool(a) if not bg else bg)

    #* We've been given None
    elif r is None:
        return (DEFAULT_COLOR, bg)

    #* We're not sure how to interpret the parameters given
    else:
        raise SyntaxError(f'Incorrect color parameters {tuple(type(i) for i in (r, g, b, a, bg))} given')


class coloredOutput:
    """ A class to be used with the 'with' command to print colors.
        Resets after it's done.
        @Parameters:
            Takes either a 3 or 4 list/tuple of color arguements, 3 seperate
            color arguements, or 1 color id between 0-5 representing a distinct
            color. Set the curColor parameter (must be a 3 or 4 item list/tuple)
            to have the terminal reset to that color instead of white.
        https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
    """
    def __init__(self, r, g=None, b=None, foreground=True, curColor=DEFAULT_COLOR):
        color, bg = parseColorParams(r, g, b, bg=foreground)
        self.fg = bg
        self.r, self.g, self.b = color
        self.doneColor = curColor

    def __enter__(self):
        try:
            if self.fg:
                print(f'\033[38;2;{self.r};{self.g};{self.b}m', end='')
            else:
                print(f'\033[48;2;{self.r};{self.g};{self.b}m', end='')
        except:
            self.reset()

    def __exit__(self, *args):
        self.reset()

    def reset(self):
        print(f'\033[38;2;{self.doneColor[0]};{self.doneColor[1]};{self.doneColor[2]}m', end='')


#* These are all helper functions for debug
def _debugGetMetaData(calls=1):
    """ Gets the meta data of the line you're calling this function from.
        Calls is for how many function calls to look back from.
    """
    try:
        s = stack()[calls]
        return s
    except IndexError:
        return None

def _debugGetLink(calls=0, full=False, customMetaData=None):
    if customMetaData is not None:
        d = customMetaData
    else:
        d = _getMetaData(calls+2)

    _printLink(d.filename, d.lineno, d.function if full else None)

# TODO This doesn't quite work properly
def _debugGetListStr(v: Union[tuple, list, set, dict], limitToLine: bool=True, minItems: int=2, maxItems: int=10,
                color: int=0) -> str:
    """ "Cast" a tuple, list, set or dict to a string, automatically shorten
        it if it's long, and display how long it is.

        Params:
            limitToLine: if True, limit the length of list to a single line
            minItems: show at least this many items in the list
            maxItems: show at most this many items in the list
            color: a simple int color

        Note:
            If limitToLine is True, it will overrule maxItems, but *not* minItems
    """
    if type(v) in (tuple, list, set) and len(v) > minItems:
        from copy import deepcopy
        from os import get_terminal_size
        if type(v) is set:
            v = tuple(v)

        ellipsis = f', \033[0m...\033[{_colors[color]}m '
        length = f'(len={len(v)})'

        if limitToLine:
            firstHalf  = str(v[0:round(minItems/2)])[:-1]
            secondHalf = str(v[-round(minItems/2)-1:-1])[1:]
            prevFirstHalf = firstHalf
            prevSecondHalf = secondHalf
            index = 0

            # The 46 is a fugde factor. I don't know why it needs to be there, but it works.
            while (6 + 54 + len(length) + len(firstHalf) + len(secondHalf)) < get_terminal_size().columns:
                index += 1
                firstHalf  = str(v[0:round((minItems+index)/2)])[:-1]
                secondHalf = str(v[-round((minItems+index)/2)-1:-1])[1:]
                prevFirstHalf = firstHalf
                prevSecondHalf = secondHalf
                if index > KILL_IT:
                    break

            firstHalf = prevFirstHalf
            secondHalf = prevSecondHalf

        else:
            firstHalf  = str(v[0:round(maxItems/2)])[:-1]
            secondHalf = str(v[-round(maxItems/2)-1:-1])[1:]

        return firstHalf + ellipsis + secondHalf + length

    else:
        return str(v) + f'(len={len(v)})'

def _debugGetTypename(var):
    if type(var) in (tuple, list, set):
        returnMe = type(var).__name__
        while type(var) in (tuple, list, set):
            try:
                var = var[0]
            except (KeyError, IndexError, TypeError):
                returnMe += '('
                break
            returnMe += '(' + type(var).__name__

        cnt = 0
        for i in returnMe:
            if i == '(':
                cnt += 1
        return returnMe + (')'*cnt)
    else:
        return type(var).__name__

def _debugPrintLink(filename, lineNum, function=None):
    """ Print a VSCodium clickable file and line number
        If function is specified, a full python error message style line is printed
    """
    try:
        _printColor(40, 43, 46)
        if function is None: #    \|/  Oddly enough, this double quote is nessicary
            print('\t', filename, '", line ', lineNum, '\033[0m', sep='')
        else:
            print('\tFile "', filename, '", line ', lineNum, ', in ', function, sep='')

        _resetColor()
    finally:
        _resetColor()
    _resetColor()
    print('\033[0m', end='')

def _printDebugCount(leftAdjust=2, color: int=COUNT_COLOR):
    global _debugCount
    _debugCount += 1
    with coloredOutput(color):
        print(f'{str(_debugCount)+":":<{leftAdjust+2}}', end='')

def _debugGetVarName(var, full=True, calls=1):
    try:
        return argname('var', frame=calls+1)
    # It's a *likely* string literal
    except ImproperUseError as e:
        if type(var) is str:
            return None
        else:
            try:
                return nameof(var, frame=calls+1)
            except Exception as e:
                if VERBOSE:
                    raise e
                else:
                    return '?'
    except VarnameRetrievingError as e:
        if VERBOSE:
            raise e
        else:
            return '?'

def _debugGetAdjustedFilename(filename):
    return filename[len(ROOT)+1:]

def _debugGetContext(metadata, useVscodeStyle, showFunc, showFile, showPath):
    #* Set the stuff in the [] (the "context")
    if metadata is not None:
        if useVscodeStyle:
            s = f'["{metadata.filename if showPath else _debugGetAdjustedFilename(metadata.filename)}", line {metadata.lineno}'
            if showFunc:
                if metadata.function.startswith('<'):
                    s += ', in Global Scope'
                else:
                    s += f', in {metadata.function}()'
            s += '] '
            return s
        else:
            context = str(metadata.lineno)
            if showFunc:
                if metadata.function.startswith('<'):
                    context = 'Global Scope' + context
                else:
                    context = metadata.function + '()->' + context

            if showFile:
                context = (metadata.filename if showPath else basename(metadata.filename)) + '->' + context

            return f'[{context}] '
    else:
        return ' '

def _debugPrintStackTrace(calls, useVscodeStyle, showFunc, showFile, showPath):
    for i in reversed(stack()[3:]):
        print('\t', _debugGetContext(i, useVscodeStyle, showFunc, showFile, showPath))

def _debugBeingUsedAsDecorator(funcName, metadata=None, calls=1):
    """ Return 1 if being used as a function decorator, 2 if as a class decorator, and 0 if neither. """
    if metadata is None:
        metadata = _debugGetMetaData(calls+1)

    if funcName not in metadata.code_context[0]:
        if 'def ' in metadata.code_context[0]:
            return 1
        if 'class ' in metadata.code_context[0]:
            return 2

    return False

# A unique dummy class for the var parameter
class _None: pass

# TODO: somehow round any float to a given length, including those printed in iterables
# TODO make it so if the first is a variable you can't get (or just any variable), and the
#   second is a string literal, set the string literal as the name of the first variable
def debug(var=_None,                # The variable to debug
          name: str=None,           # Don't try to get the name, use this one instead
          color=_None,              # A number (0-5), a 3 item tuple/list, or None
          showFunc: bool=True,      # Expressly show what function we're called from
          showFile: bool=True,      # Expressly show what file we're called from
          showPath: bool=False,     # Show just the file name, or the full filepath
          useRepr: bool=False,      # Whether we should print the repr of var instead of str
          calls: int=1,             # Add extra calls
          background: bool=False,   # Whether the color parameter applies to the forground or the background
          limitToLine: bool=True,   # When printing iterables, whether we should only print items to the end of the line
          minItems: int=4,          # Minimum number of items to print when printing iterables (overrides limitToLine)
          maxItems: int=10,         # Maximum number of items to print when printing iterables, use None or negative to specify no limit
          stackTrace: bool=False,   # Print a stack trace
          raiseError: bool=False,   # If var is an error type, raise it
          clr=_None,                 # Alias of color
          _repr: bool=False,        # Alias of useRepr
          trace: bool=False,        # Alias of stackTrace
          bg: bool=False,           # Alias of background
          throwError: bool=False,   # Alias of raiseError
          throw: bool=False         # Alias of raiseError
    ) -> "var":
    """ Print variable names and values for easy debugging.

        Usage:
            debug()          -> Prints a standard message to just tell you that it's getting called
            debug('msg')     -> Prints the string along with metadata
            debug(var)       -> Prints the variable name, type, and value
            foo = debug(bar) -> Prints the variable name, type, and value, and returns the variable
            @debug           -> Use as a decorator to make note of when the function is called

        Args:
            var: The variable or variables to print
            name: Manully specify the name of the variable
            color: A number between 0-5, or 3 or 4 tuple/list of color data to print the debug message as
            showFunc: Ensure that the function the current call is called from is shown
            showFile: Ensure that the file the current call is called from is shown
            showPath: Show the full path of the current file, isntead of it's relative path
            useRepr: Use __repr__() instead of __str__() on the given variable
            limitToLine: If var is a list/tuple/dict/set, only show as many items as will fit on one terminal line, overriden by minItems
            minItems: If var is a list/tuple/dict/set, don't truncate more than this many items
            maxItems: If var is a list/tuple/dict/set, don't show more than this many items
            stackTrace: Prints a neat stack trace of the current call
            calls: If you're passing in a return from a function, say calls=2
            background: Changes the background color instead of the forground color
            clr: Alias of color
            _repr: Alias of useRepr
            trace: Alias of stackTrace
            bg: Alias of background
    """
    stackTrace = stackTrace or trace
    useRepr = useRepr or _repr
    background = background or bg
    throwError = throw or throwError or raiseError
    useColor = (DEFAULT_DEBUG_COLOR if clr is _None else clr) if color is _None else color

    if maxItems < 0 or maxItems is None:
        maxItems = 1000000

    if isinstance(var, Warning):
        useColor = WARN_COLOR
    elif isinstance(var, Exception):
        useColor = ALERT_COLOR

    # +1 call because we don't want to get this line, but the one before it
    metadata = _debugGetMetaData(calls+1)

    #* First see if we're being called as a decorator
    if callable(var) and _debugBeingUsedAsDecorator('debug', metadata):
        def wrap(*args, **kwargs):
            # +1 call because we don't want to get this line, but the one before it
            metadata = _debugGetMetaData(2)

            _printDebugCount()

            if stackTrace:
                with coloredOutput(STACK_TRACE_COLOR):
                    _debugPrintStackTrace(2, True, showFunc, showFile, showPath)


            with coloredOutput(NOTE_CALL_COLOR):
                print(_debugGetContext(metadata, True, showFunc or DISPLAY_FUNC, showFile or DISPLAY_FILE, showPath or DISPLAY_PATH), end='')
                print(f'{var.__name__}() called!')

            return var(*args, **kwargs)

        return wrap

    _printDebugCount()

    if stackTrace:
        with coloredOutput(STACK_TRACE_COLOR):
            _debugPrintStackTrace(calls+1, True, showFunc, showFile, showPath)

    #* Only print the "HERE! HERE!" message
    if var is _None:
        with coloredOutput(useColor if color is not _None else EMPTY_COLOR, not background):
            print(_debugGetContext(metadata, True, showFunc or DISPLAY_FUNC, showFile or DISPLAY_FILE, showPath or DISPLAY_PATH), end='')
            if not metadata.function.startswith('<'):
                print(f'{metadata.function}() called ', end='')
            print('HERE!')
        return

    #* Print the standard line
    with coloredOutput(useColor, not background):
        print(_debugGetContext(metadata, True,
                               showFunc or DISPLAY_FUNC,
                               showFile or DISPLAY_FILE,
                               showPath or DISPLAY_PATH), end='')

        #* Seperate the variables into a tuple of (typeStr, varString)
        varType = _debugGetTypename(var)
        if useRepr:
            varVal = repr(var)
        else:
            if type(var) in (tuple, list, set, dict):
                varVal  = _debugGetListStr(var, limitToLine, minItems, maxItems, color=color)
            else:
                varVal  = str(var)

        #* Actually get the name
        varName = _debugGetVarName(var, calls=calls) if name is None else name
        # It's a string literal
        if varName is None:
            print(var)
            return

        print(f'{varType} {varName} = {varVal}')

    if isinstance(var, Exception) and throwError:
        raise var

    # Does the same this as debugged used to
    return var


def todo(featureName=None, enabled=True, blocking=True, showFunc=True, showFile=True, showPath=False):
    """ Leave reminders for yourself to finish parts of your code.
        Can be manually turned on or off with hideAllTodos(bool).
        Can also be used as a decorator (function, or class) to print a reminder
        and also throw a NotImplemented error on being called/constructed.
    """
    metadata = _debugGetMetaData(2)
    situation = _debugBeingUsedAsDecorator('todo', metadata)
    # def decorator(*decoratorArgs, **decoratorKwArgs):
    #     def wrap(func):
    #         def innerWrap(*funcArgs, **funcKwArgs):
    #             return func(*funcArgs, **funcKwArgs)
    #         return innerWrap
    #     return wrap

    def printTodo(disableFunc):
        if not HIDE_TODO and enabled:
            _printDebugCount()
            with coloredOutput(TODO_COLOR):
                print(_debugGetContext(metadata, True,
                                      (showFunc or DISPLAY_FUNC) and not disableFunc,
                                       showFile or DISPLAY_FILE,
                                       showPath or DISPLAY_PATH), end='')
                # This is coincidental, but it works
                print(f'TODO: {featureName.__name__ if disableFunc else featureName}')

    # Being used as a function decorator
    if situation == 1:
        def wrap(func):
            def innerWrap(*funcArgs, **funcKwArgs):
                printTodo(True)
                if blocking:
                    raise NotImplementedError()
                return featureName(*funcArgs, **funcKwArgs)
            return innerWrap
        return wrap

    elif situation == 2:
        def wrap(clas):
            def raiseErr(*_, **kw_):
                raise NotImplementedError()
            printTodo(True)
            if blocking:
                featureName.__init__ = raiseErr
        return featureName
    else:
        printTodo(False)


def reprise(obj, *args, **kwargs):
    """ Sets the __repr__ function to the __str__ function of a class.
        Useful for custom classes with overloaded string functions
    """
    obj.__repr__ = obj.__str__
    return obj

# TODO Finish this
# def checkImport(lib, package=None):
    # module = __import__(mname, {}, {}, (cls,))

# TODO Make this use piping and return the command output
def runCmd(args):
    """ Run a command and terminate if it fails. """

    try:
        ec = subprocess.call(' '.join(args), shell=True)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
        ec = 1

    if ec:
        sys.exit(ec)


def percent(percentage):
    ''' Usage:
        if (percent(50)):
            <code that has a 50% chance of running>
    '''
    return randint(1, 100) < percentage


def randbool():
    """ Returns, randomly, either True or False """
    return bool(randint(0, 1))


def closeEnough(a, b, tolerance):
    """ Returns True if a is within tolerance range of b """
    return a <= b + tolerance and a >= b - tolerance


def findClosestPoint(target, comparatorList):
    """ Finds the closest point in the list to what it's given"""
    finalDist = 1000000

    for i in comparatorList:
        current = getDist(target, i)
        if current < finalDist:
            finalDist = current

    return finalDist


def findClosestXPoint(target, comparatorList, offsetIndex = 0):
    """ I've forgotten what *exactly* this does. I think it finds the point in a list of
        points who's x point is closest to the target
    """
    finalDist = 1000000
    result = 0

    # for i in range(len(comparatorList) - offsetIndex):
    for current in comparatorList:
        # current = comparatorList[i + offsetIndex]
        currentDist = abs(target.x - current.x)
        if currentDist < finalDist:
            result = current
            finalDist = currentDist

    return result


def getPointsAlongLine(p1, p2):
    """ I don't remember what this does. """
    p1 = Pointi(p1)
    p2 = Pointi(p2)

    returnMe = []

    dx = p2.x - p1.x
    dy = p2.y - p1.y

    for x in range(p1.x, p2.x):
        y = p1.y + dy * (x - p1.x) / dx
        returnMe.append(Pointf(x, y))

    return returnMe


def rotatePoint(p, angle, pivotPoint, radians = False):
    """ This rotates one point around another point a certain amount, and returns it's new position """
    if not radians:
        angle = math.radians(angle)
    # p -= pivotPoint
    # tmp = pygame.math.Vector2(p.data()).normalize().rotate(amount)
    # return Pointf(tmp.x, tmp.y) + pivotPoint

    dx = p.x - pivotPoint.x
    dy = p.y - pivotPoint.y
    newX = dx * math.cos(angle) - dy * math.sin(angle) + pivotPoint.x
    newY = dx * math.sin(angle) + dy * math.cos(angle) + pivotPoint.y

    return Pointf(newX, newY)


def getMidPoint(p1, p2):
    """ Returns the halfway point between 2 given points """
    assert type(p1) == type(p2)
    # return Pointf((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
    return p1._initCopy((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)

timingData = {}
def timeFunc(func, accuracy=5):
    """ A function decorator that prints how long it takes for a function to run """
    def wrap(*params, **kwparams):
        global timingData

        t = process_time()

        returns = func(*params, **kwparams)

        t2 = process_time()

        elapsed_time = round(t2 - t, accuracy)
        name = func.__name__

        try:
            timingData[name] += (elapsed_time,)
        except KeyError:
            timingData[name] = (elapsed_time,)

        _printDebugCount()
        # print(name, ' ' * (10 - len(name)), 'took', elapsed_time if elapsed_time >= 0.00001 else 0.00000, '\ttime to run.')
        print(f'{name:<12} took {elapsed_time:.{accuracy}f} seconds to run.')
        #  ' ' * (15 - len(name)),
        return returns
    return wrap

def _printTimingData(accuracy=5):
    """ I realized *after* I wrote this that this is a essentially profiler. Oops. """
    global timingData
    if len(timingData):
        print()

        maxName = len(max(timingData.keys(), key=len))
        maxNum  = len(str(len(max(timingData.values(), key=lambda x: len(str(len(x)))))))
        for name, times in reversed(sorted(timingData.items(), key=lambda x: sum(x[1]))):
            print(f'{name:<{maxName}} was called {len(times):<{maxNum}} times taking {sum(times)/len(times):.{accuracy}f} seconds on average for a total of {sum(times):.{accuracy}f} seconds.')
atexit.register(_printTimingData)


class getTime:
    """ A class to use with a with statement like so:
        with getTime('sleep'):
            time.sleep(10)
        It will then print how long the enclosed code took to run.
    """
    def __init__(self, name, accuracy=5):
        self.name = name
        self.accuracy = accuracy

    def __enter__(self):
        self.t = process_time()

    def __exit__(self, *args):
        # args is completely useless, not sure why it's there.
        t2 = process_time()
        elapsed_time = round(t2 - self.t, self.accuracy)
        print(self.name, ' ' * (15 - len(self.name)), 'took', f'{elapsed_time:.{self.accuracy}f}', '\ttime to run.')


@todo
class LoopingList(list):
    """ It's a list, that, get this, loops!
    """
    def __getitem__(self, index):
        if index > self.__len__():
            return super().__getitem__(index % self.__len__())
        else:
            return super().__getitem__(index)


class FunctionCall:
    """ A helpful class that represents an as-yet uncalled function call with parameters """
    def __init__(self, func=lambda: None, args=(), kwargs={}):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def call(self, *args, override_args=False, **kwargs):
        return self.__call__(*args, override_args, **kwargs)

    def __call__(self, *args, override_args=False, **kwargs):
        """ If you specify parameters and don't explicitly set override_args to True,
            then the given parameters are ignored and the previously set parameters are used.
        """
        if override_args:
            return self.func(*args, **kwargs)
        else:
            return self.func(*self.args, **self.kwargs)


class Signal:
    """ A custom Signal implementation. Connect with the connect() function """
    def __init__(self):
        self.funcs = []

    def connect(self, func, *args, **kwargs):
        self.funcs.append(FunctionCall(func, args, kwargs))

    def __call__(self, *args, override_args=False, **kwargs):
        """ If you specify parameters and don't explicitly set override_args to True,
            then the given parameters are ignored and the previously set parameters are used.
            WARNING: If override_args is set to True, the given parameters will be passed into
            every function given with connect().
        """
        # rtns = ()
        for f in self.funcs:
            f(*args, override_args=override_args, **kwargs)

        # return rtns[0] if len(rtns) <= 1 else rtns


def absdeg(angle):
    """ If an angle (in degrees) is not within 360, then this cuts it down to within 0-360 """
    angle = angle % 360.0
    if angle < 0:
        angle += 360
    return angle


def absrad(angle):
    """ If an angle (in radians) is not within 2Pi, then this cuts it down to within 0-2Pi """
    angle = angle % math.tau
    if angle < 0:
        angle += math.tau
    return angle


def center(string):
    """ Centers a string for printing in the terminal """
    from os import get_terminal_size
    for _ in range(int((get_terminal_size().columns - len(string)) / 2)): string = ' ' + string
    return string


def isPowerOf2(x):
    """ Returns true if x is a power of 2 """
    return (x != 0) and ((x & (x - 1)) == 0)


def isBetween(val, start, end, beginInclusive=False, endInclusive=False):
    """ Returns true if val is between start and end """
    return (val >= start if beginInclusive else val > start) and \
           (val <= end   if endInclusive   else val < end)


def collidePoint(topLeft: 'Point', size: Union[tuple, list, 'Size'], target, inclusive=True):
    """ Returns true if target is within the rectangle given by topLeft and size """
    return isBetween(target.x, topLeft.x, size[0], beginInclusive=inclusive, endInclusive=inclusive) and \
           isBetween(target.y, topLeft.y, size[1], beginInclusive=inclusive, endInclusive=inclusive)


def insertChar(string, index, char):
    """ Returns the string with char inserted into string at index. Freaking python string are immutable. """
    return string[:index] + char + string[index+1:]


def constrain(val, low, high):
    """ Constrains val to be within low and high """
    return min(high, max(low, val))


def rgbToHex(rgb):
    """ Translates an rgb tuple of int to a tkinter friendly color code """
    return f'#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}'


def darken(rgb, amount):
    """ Returns the given color, but darkened. Make amount negative to lighten """
    return tuple([constrain(i+amount, 0, 255) for i in rgb])


def lighten(rgb, amount):
    """ Returns the given color, but darkened. Make amount negative to darken """
    return tuple([constrain(i-amount, 0, 255) for i in rgb])


def ensureIterable(obj, useList=False):
    if not isinstance(obj, Iterable):
        return [obj, ] if useList else (obj, )
    else:
        return obj

# Returns the index of the first object in a list in which key returns true to.
# Example: getIndexWith([ [5, 3], [2, 3], [7, 3] ], lambda x: x[0] + x[1] == 10) -> 2
# If none are found, returns None
def getIndexWith(obj, key):
    for cnt, i in enumerate(obj):
        if key(i):
            return cnt
    return None




'''
def tlOriginToCenterOrigin(p: Point, width, height):
    return Pointf(p.x - (width / 2), p.y - (height / 2))
'''

'''
def clampPoint(p: Point, width, height):
    return p._initCopy(p.x / (width / 2), p.y / (height / 2))
'''


def clampColor(*rgba):
    """ Clamp a 0-255 color to a float between 1 and 0.
        Helpful for openGL commands.
    """
    if len(rgba) == 1 and type(rgba[0]) in (tuple, list):
        return tuple(c / 255 for c in rgba[0])
    else:
        return tuple(c / 255 for c in rgba)


def invertColor(*rgba):
    """ Inverts a color
    """
    if len(rgba) == 1 and type(rgba[0]) in (tuple, list):
        return tuple(255 - c for c in rgba[0])
    else:
        return tuple(255 - c for c in rgba)

'''
def toOpenGLCoord(p: Point, width, height):
    return Pointf((p.x - (width / 2)) / (width / 2), (p.y - (height / 2)) / (height / 2))
'''
'''
def toTLCoord(p: Point, width, height):
    return Pointi((p.x * (width / 2)) + (width / 2), (p.y * (height / 2)) + (height / 2))
'''

def translate(value, fromStart, fromEnd, toStart, toEnd):
    return ((abs(value - fromStart) / abs(fromEnd - fromStart)) * abs(toEnd - toStart)) + toStart


def frange(start, stop, skip=1.0, accuracy=10000000000000000):
    return [x / accuracy for x in range(int(start*accuracy), int(stop*accuracy), int(skip*accuracy))]


# def getDist(a: 'Point', b: 'Point'):
    # return math.sqrt(((b.x - a.x)**2) + ((b.y - a.y)**2))


def getDist(ax, ay, bx, by):
    return math.sqrt(((bx - ax)**2) + ((by - ay)**2))


def deg2rad(a):
    return a * math.PI / 180.0

def normalize2rad(a):
    while a < 0: a += math.tau
    while a >= math.tau: a -= math.tau
    return a

def normalize2deg(a):
    while a < 0: a += 360
    while a >= 360: a -= 360
    return a


#* API Specific functions

#* Tkinter (ttk specifically)

# import tkinter as tk
# import tkinter.ttk as ttk
# from contextlib import redirect_stdout
# import ttkthemes

def stylenameElementOptions(stylename):
    '''Function to expose the options of every element associated to a widget
       stylename.'''
    with open('tmp.del', 'a') as f:
        with redirect_stdout(f):
            print('\n-----------------------------------------------------------------------------\n')
            try:
                # Get widget elements
                style = ttk.Style()
                layout = str(style.layout(stylename))
                print('Stylename = {}'.format(stylename))
                print('Layout    = {}'.format(layout))
                elements=[]
                for n, x in enumerate(layout):
                    if x=='(':
                        element=""
                        for y in layout[n+2:]:
                            if y != ',':
                                element=element+str(y)
                            else:
                                elements.append(element[:-1])
                                break
                print('\nElement(s) = {}\n'.format(elements))
                # Get options of widget elements
                for element in elements:
                    print('{0:30} options: {1}'.format(
                        element, style.element_options(element)))
            except tk.TclError:
                print('_tkinter.TclError: "{0}" in function'
                    'widget_elements_options({0}) is not a regonised stylename.'
                    .format(stylename))


# for i in ['TButton', 'TCheckbutton', 'TCombobox', 'TEntry', 'TFrame', 'TLabel', 'TLabelFrame', 'TMenubutton', 'TNotebook', 'TPanedwindow', 'Horizontal.TProgressbar', 'Vertical.TProgressbar', 'TRadiobutton', 'Horizontal.TScale', 'Vertical.TScale', 'Horizontal.TScrollbar', 'Vertical.TScrollbar', 'TSeparator', 'TSizegrip', 'Treeview', 'TSpinbox']:
#     stylenameElementOptions('test.' + i)

# stylenameElementOptions('me.TButton')




#* Pygame






'''
from Point import *
import os, math
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import time

class Pointer:
    def __init__(self, val):
        self.value = val

    def get(self):


def loadAsset(dir, name, extension='png'):
    return loadImage(dir + name + '.' + extension)


def getGroundPoints(groundPoints):
    returnMe = []
    for i in range(len(groundPoints) - 1):
        returnMe += getPointsAlongLine(groundPoints[i], groundPoints[i + 1])

    return returnMe


def portableFilename(filename):
    return os.path.join(*filename.split('/'))


def loadImage(filename):
    # if pygame.image.get_extended():
    filename = '/' + portableFilename(DATA + '/' + filename)

    image = pygame.image.load(filename)
    # self.image = self.image.convert()
    image = image.convert_alpha()
    # else:
    #     assert(not f"Cannot support the file extension {}")
    return image


def drawAllGroundPoints(surface, gp):
    for i in gp:
        pygame.gfxdraw.pixel(surface, *i.datai(), [255, 0, 0])


def rotateSurface(surface, angle, pivot, offset):
    """Rotate the surface around the pivot point.

    Args:
        surface (pygame.Surface): The surface that is to be rotated.
        angle (float): Rotate by this angle.
        pivot (tuple, list, pygame.math.Vector2): The pivot point.
        offset (pygame.math.Vector2): This vector is added to the pivot.
    """
    rotated_image = pygame.transform.rotozoom(surface, -angle, 1)  # Rotate the image.
    rotated_offset = offset.rotate(angle)  # Rotate the offset vector.
    # Add the offset vector to the center/pivot point to shift the rect.
    rect = rotated_image.get_rect(center=pivot+rotated_offset)
    return rotated_image, rect  # Return the rotated image and shifted rect.


'''


"""
DECORATOR SYNTAX:

def decorator(*decoratorArgs, **decoratorKwArgs):
    def wrap(functionBeingDecorated):
        def innerWrap(*decoratedArgs, **decoratedKwArgs):
            return functionBeingDecorated(*decoratedArgs, **decoratedKwArgs)
        return innerWrap
    return wrap

COPY version:

def decorator(*decoratorArgs, **decoratorKwArgs):
    def wrap(func):
        def innerWrap(*funcArgs, **funcKwArgs):
            return func(*funcArgs, **funcKwArgs)
        return innerWrap
    return wrap


"""










#* TESTING

#* parseColorParams tests
if False:
    # setVerbose(True)
    # debug(parseColorParams((5, 5, 5)) )
    # debug(parseColorParams((5, 5, 5), True) )
    # debug(parseColorParams((5, 5, 5, 6)) )
    # debug(parseColorParams((5, 5, 5, 6), True) )
    # debug(parseColorParams([5, 5, 5, 6]) )
    # debug(parseColorParams(5, 5, 5) )
    # debug(parseColorParams(5, 5, 5, True) )
    # debug(parseColorParams(5, 5, 5, 6) )
    # debug(parseColorParams(5, 5, 5, bg=True) )
    # debug(parseColorParams(5, 5, 5, 6, True) )
    # debug(parseColorParams(3) )
    # debug(parseColorParams(3, bg=True)
    # debug(parseColorParams((3,)) ) # Succeeded
    # debug(parseColorParams(3, a=6) )
    # debug(parseColorParams(3, a=6, bg=True) )
    # debug(parseColorParams(None) )
    # debug(parseColorParams(None, bg=True) )
    pass

#* debug tests
if False:
    # setVerbose(True)
    a = 6
    s = 'test'
    j = None
    def testFunc():
        print('testFunc called')

    debug(a)
    debug(a, 'apple')

    debug('test3')
    debug(s)

    debug(j)
    debug()

    debug(testFunc)

    foo = debug(a)
    debug(foo)

    debug(parseColorParams((5, 5, 5)) )

    debug(SyntaxError('Not an error'))
    debug(SyntaxError('Not an error'), raiseError=True)
    debug(UserWarning('Not a warning'))
    debug(UserWarning('Not a warning'), raiseError=True)

    @debug
    def testFunc2():
        print('testFunc2 (decorator test) called')

    testFunc2()

    debug(None)

#* todo tests
if False:
    todo('testing todo')
    todo('testing todo 2', False)

    @todo
    def unfinishedFunc():
        print("this func is unfin")

    try:
        unfinishedFunc()
    except NotImplementedError:
        print("func decorator test worked!")
    else:
        print("func decorator test failed.")

    @todo(blocking=False)
    def unfinishedFunc2():
        print("this non Blocking func is unfin")

    unfinishedFunc2()

    @todo
    class unfinishedClass:
        def __init__(self):
            print('this class is unfin')

    try:
        x = unfinishedClass()
    except NotImplementedError:
        print("class decorator test worked!")
    else:
        print("class decorator test failed.")

#* Decorator Testing
if False:
    def decorator(*decoratorArgs, **decoratorKwArgs):
        def wrap(functionBeingDecorated):
            def innerWrap(*decoratedArgs, **decoratedKwArgs):
                debug(decoratorArgs)
                debug(decoratorKwArgs)
                debug(functionBeingDecorated)
                debug(decoratedArgs)
                debug(decoratedKwArgs)
                return functionBeingDecorated(*decoratedArgs, **decoratedKwArgs)
            return innerWrap
        return wrap

    @decorator("decoratorArg1", "decoratorArg2", decoratorKwArg="decoratorKwValue")
    def testFunc(funcArg1, funcArg2, funcKwArg='funcKwArg'):
        debug(funcArg1)
        debug(funcArg2)
        debug(funcKwArg)

    testFunc("calledArg1", 'calledArg2', funcKwArg='calledKwArg')
