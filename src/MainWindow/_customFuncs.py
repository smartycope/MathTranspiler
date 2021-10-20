from Cope import *
from EasyRegex import *

from sympy import abc
import sympy as sym
from sympy.solvers.solveset import invert_real, invert_complex
from sympy.abc import *
from sympy import *
from sympy.calculus.util import continuous_domain, function_range
from sympy.core.function import AppliedUndef, UndefinedFunction
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import (convert_xor, implicit_multiplication,
                                        implicit_multiplication_application,
                                        lambda_notation, parse_expr,
                                        standard_transformations)
from sympy.plotting import plot
from sympy.printing.latex import latex
from sympy.printing.mathematica import mathematica_code
from sympy.printing.mathml import mathml
from sympy.printing.preview import preview
from sympy.printing.pycode import pycode
from sympy.sets.conditionset import ConditionSet
from sympy.solvers.inequalities import solve_rational_inequalities

def addCustomFuncs(self):
    self._addCustomFunc('Get Continuous at',             'out = isContinuousAt(expr=expr, symbol=curSymbol, at=S.Reals)')
    self._addCustomFunc('Get Equation of Tangent Line',  'out = getTanSlopeEquation(expr=expr, symbol=curSymbol, symbolVal=curValue)')
    self._addCustomFunc('Get Equation of Normal Line',   'out = getNormalSlopeEquation(expr=expr, symbol=curSymbol, symbolVal=curValue)')
    self._addCustomFunc('Find Average Rate of Change over Interval', 'out = getAvgRateOfChange(func=func, interval=Interval(from, to))')
    self._addCustomFunc('Intermediate Value Theorem',    'out = leastPossibleVal(func=func, interval=Interval(from, to))')
    self._addCustomFunc('Solve as Implicit Derivative',  'out = idiff(eq=expr, y=y, x=x, n=1)', 'eq is the equation. Must equal 0 (use -, not Eq() or =)', 'n is the order of the derivative')
    self._addCustomFunc('Get left/right at time',        'print(leftOrRight(func=func, timeVal=curSymbol))')
    self._addCustomFunc('Get times at veolcity',         'out = timesAtHeight(expr=expr, timeVar=curSymbol, height=0)')
    self._addCustomFunc('Get Velocity at height',        'out = velocityAtHeight(expr=expr, timeVar=curSymbol, height=0)')
    self._addCustomFunc('Get acceleration at time',      'out = accAtTime(expr=expr, timeVar=curSymbol, time=curValue)')
    self._addCustomFunc('Is speeding up at time',        'print(isSpeedingUpAtTime(expr=expr, timeVar=curSymbol, time=curValue))')
    self._addCustomFunc('Get Critical Points',           'out = getCriticalPoints(expr=expr, var=curSymbol, order=1)')
    self._addCustomFunc('Get Critical Points over Interval', 'out = getCriticalPointsOverInterval(expr=expr, var=curSymbol, interval=Interval(from, to), order=1)')
    self._addCustomFunc('Get Min and Max over Interval', 'print(minMaxOverInterval(expr=expr, var=curSymbol, interval=Interval(from, to)))')
    # self._addCustomFunc('', '')

def _addCustomFunc(self, name, code, *comments):
    self.menuTools.addAction(name, lambda: self.runCustomFuncInCode(code, *comments))



seperate = lambda: print('--------------------------------')

def isContinuousAt(expr, symbol, at):
    # function f(x) is continuous at a point x=a if and only if:
    # f(a) is defined
    # lim(x→a, f(x)) exists
    # lim(x→a, f(x))=f(a)

    return continuous_domain(expr, symbol, at)

    '''
    expr = expr
    expr.subs(symbol, x)
    print(f'Result of f({x}) = {expr}')

    if not (expr):
        reason = 'Expression does not exist'
        cont = False
    # elif type(expr) is not Function:
    #     return False
    elif not expr:
        reason = f'expression is not defined at {x}'
        cont = False
    elif Limit(expr, symbol, x, '-') != Limit(expr, symbol, x, '+'):
        reason = f'limit at {x} does not exist'
        cont = False
    else:
        cont = True
        print(f"Expression is {'' if cont else 'not '}continuous at {x}" + (f':\n{reason}' if cont else ''))
    '''
    # return expr(x) == expr(a)


def getTanSlopeEquation(expr, symbol, symbolVal):
    seperate()
    # y = mx+b
    # The slope of the tangent line is just the derivative
    simp = Derivative(expr, symbol).simplify()
    slope = simp.subs(symbol, symbolVal)
    point = (symbolVal, expr.subs(symbol, symbolVal))
    print('derivative:', simp, '\tslope:', slope, '\tpoint:', point)
    return Eq(y, solve(Eq(y - point[1], slope * (x - point[0])), y)[0])


def getNormalSlopeEquation(expr, symbol, symbolVal):
    seperate()
    # y = mx+b
    # The slope of the tangent line is just the derivative
    simp = Derivative(expr, symbol).simplify()
    slope = simp.subs(symbol, symbolVal)
    slope = (1 / slope) * -1
    point = (symbolVal, expr.subs(symbol, symbolVal))
    print('derivative:', simp, '\tslope:', slope, '\tpoint:', point)
    return Eq(y, solve(Eq(y - point[1], slope * (x - point[0])), y)[0])


def getAvgRateOfChange(func, interval):
    seperate()
    print('f(b):', func(interval.end))
    print('f(a):', func(interval.start))
    print('b - a:', interval.end - interval.start)
    return ((func(interval.end) - func(interval.start)) / ((interval.end - interval.start))).simplify()


def leastPossibleVal(func, interval):
    seperate()
    isPositive = func(interval.start) > 0
    print(f'f({interval.start}) is', 'positive' if isPositive else 'negative')
    i = interval.start
    while True:
        print(f'f({i}):', func(i).simplify())
        if (func(i) > 0) != isPositive:
            break
        else:
            if isPositive:
                i += 1
            else:
                i -= 1
    return i


def leftOrRight(func, timeVal):
    return 'Right' if func(timeVal) > 0 else 'Left'


def timesAtHeight(expr, timeVar, height):
    if height == 0:
        expr = expr.diff(timeVar)

    return solveset(Eq(expr, height), timeVar)


def velocityAtHeight(expr, timeVar, height):
    diff = expr.diff(timeVar)
    ans = []

    heights = ensureIterable(solveset(Eq(expr, height), timeVar))
    print('Derivative:', diff)
    print('Heights:', heights)
    for i in heights:
        ans.append(diff.subs(timeVar, i))

    return ans


def accAtTime(expr, timeVar, time):
    diff = expr.diff(timeVar, 2)
    ans = []

    heights = ensureIterable(solveset(expr, timeVar))
    print('Derivative:', diff)
    print('Heights:', heights)
    for i in heights:
        ans.append(diff.subs(timeVar, i))

    return ans


def isSpeedingUpAtTime(expr, timeVar, time):
    diff1 = expr.diff(timeVar, 1).subs(timeVar, time)
    diff2 = expr.diff(timeVar, 2).subs(timeVar, time)
    print('First Derivative:', diff1)
    print('Second Derivative:', diff2)
    return (diff1 > 0) == (diff2 > 0)

# "solveRelatedRate(equation=expr, changeExpr=, solveVar=curVar)", "changeExpr is the amount its changing", "equation must be an Eq() statement of type Eq(<stuff>, <stuff involving solveVar>)"
def solveRelatedRate(equation, changeExpr, solveVar):
    equation = equation.subs(solveVar, solveVar.diff())
    # equation.lhs.diff()
    equation = equation.subs(equation.lhs, changeExpr)
    return solve(equation, solveVar)


def getCriticalPoints(expr, var, order=1):
    return solveset(Derivative(expr, (var, order)), var, domain=S.Reals).simplify()


def getCriticalPointsOverInterval(expr, var, interval, order=1):
    #* THIS SHOULD WORK DANG IT
    # return [i for i in ensureIterable(solveset(expr.diff(var, order), var)) if isBetween(i, interval.start, interval.end)]
    try:
        a, b = solveset(Derivative(expr, (var, order)), var, domain=interval)
    except:
        a = solveset(Derivative(expr, (var, order)), var, domain=interval)
        b = None
    ans = []
    if isBetween(a, interval.start, interval.end):
        ans.append(a)
    if isBetween(b, interval.start, interval.end):
        ans.append(b)
    return ans




def minMaxOverInterval(expr, var, interval):
    start = expr.subs(var, interval.start)
    end = expr.subs(var, interval.end)
    print('Start:', start)
    print('End:', end)
    # diff = expr.diff(var)
    crit = getCriticalPoints(expr, var)
    print('Critical Points:', crit)
    evalPoints = solvedEvalPoints = []

    for i in crit:
        i = i.simplify()
        if isBetween(i, interval.start, interval.end, True, True):
            evalPoints.append(i)
    print('Critical Points between the interval:', evalPoints)

    #* This for loop does work and i have NO idea why
    # for k in evalPoints:
        # print('running:', k)
        # solvedEvalPoints.append(expr.subs(var, k))
    solvedEvalPoints.append(expr.subs(var, evalPoints[0]))
    solvedEvalPoints.append(expr.subs(var, evalPoints[1]))

    print('Those points plugged into the expression give you:', solvedEvalPoints)

    solvedEvalPoints += [start, end]
    for i in crit:
        try:
            solvedEvalPoints.remove(i)
        except:
            pass
    print('All the points are:', solvedEvalPoints)
    return f'Min: {min(solvedEvalPoints).simplify()} at {var} = {min(crit)}, Max: {max(solvedEvalPoints).simplify()} at {var} = {max(crit)}'


"""
1a = 8x + 5e^x - 3/x
1b = 7*5^(7x - 2)*log(5)
2a = -8x/(16x^4 + 1)
-x/2x^4+32^8
2b = 3*(4*2^(6x)*(3x - 1)*log(2)^2 - 4)  /  (8*(3x - 1)*log(2))
"""




todo('add auto-uncondition or un-finiteset an answer with only one entry in sanatize solution/sanitize output')
todo('autoconvert to lambda (func and implicitly in varsetter) smartly, ie via a private function and get the atoms first instead of assuming x')
todo('update code box tooltip')
todo('auto sanatize == to Eq(), = to -, and -> to Lambda()')