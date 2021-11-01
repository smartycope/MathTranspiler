try:
    from Cope import *
except ImportError:
    pass
# from EasyRegex import *

import sympy as sym
import numpy as np
import math
# from math import degrees, radians
# from numpy import deg2rad, rad2deg
# from sympy.mpmath import radians, degrees
from sympy import abc
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
from sympy.solvers.inequalities import *
from sympy.core.sympify import SympifyError
from sympy.solvers.ode.systems import dsolve_system
from random import randint, uniform
from typing import Iterable

def addCustomFuncs(self):
    self._addCustomFunc('Get Continuous at',             'out = isContinuousAt(expr=expr, symbol=curSymbol, at=S.Reals)')
    self._addCustomFunc('Get Equation of Tangent Line',  'out = getTanSlopeEquation(expr=expr, symbol=curSymbol, symbolVal=curValue)')
    self._addCustomFunc('Get Equation of Normal Line',   'out = getNormalSlopeEquation(expr=expr, symbol=curSymbol, symbolVal=curValue)')
    self._addCustomFunc('Find Average Rate of Change over Interval', 'out = getAvgRateOfChange(func=func, interval=Interval(-oo, oo))')
    self._addCustomFunc('Intermediate Value Theorem',    'out = leastPossibleVal(func=func, interval=Interval(-oo, oo))')
    self._addCustomFunc('Solve as Implicit Derivative',  'out = idiff(eq=expr, y=y, x=x, n=1)', 'eq is the equation. Must equal 0 (use -, not Eq() or =)', 'n is the order of the derivative')
    self._addCustomFunc('Get left/right at time',        'print(leftOrRight(func=func, timeVal=curSymbol))')
    self._addCustomFunc('Get times at veolcity',         'out = timesAtHeight(expr=expr, timeVar=curSymbol, height=0)')
    self._addCustomFunc('Get Velocity at height',        'out = velocityAtHeight(expr=expr, timeVar=curSymbol, height=0)')
    self._addCustomFunc('Get acceleration at time',      'out = accAtTime(expr=expr, timeVar=curSymbol, time=curValue)')
    self._addCustomFunc('Is speeding up at time',        'print(isSpeedingUpAtTime(expr=expr, timeVar=curSymbol, time=curValue))')
    self._addCustomFunc('Get Critical Points',           'out = getCriticalPoints(expr=expr, var=curSymbol, order=1)')
    self._addCustomFunc('Get Critical Points over Interval', 'out = getCriticalPointsOverInterval(expr=expr, var=curSymbol, interval=Interval(-oo, oo), order=1)')
    self._addCustomFunc('Get Min and Max over Interval', 'print(minMaxOverInterval(expr=expr, var=curSymbol, interval=Interval(-oo, oo)))')
    self._addCustomFunc('Solve Related Rate',            "out = solveRelatedRate(equation=expr, changeExpr=, solveVar=curSymbol)", "changeExpr is the amount its changing", "equation must be an Eq() statement of type Eq(<stuff>, <stuff involving solveVar>)")
    self._addCustomFunc('Solve Related Rate',            "# Put one of these in the box, then fill the variables with what you know (rate of change of volume is Derivative(v,t), current value, ect.)",
                                                         'For a Triangle, with the base changing: Eq(Derivative(volume(time), time), (1/2)*Derivative(base(time), time)*height)',
                                                         'Cube, with the side changing: Eq(Derivative(volume(time), time), Derivative(side(time), time)**3)',
                                                         'Rectangle, with any side changing: Eq(Derivative(volume(time), time), Derivative(side(time), time)*width*height)'
                                                         'Cylinder = V=pi*h*r^2',
                                                         'Cone: (1/3)*pi*(r^2)*h')
    self._addCustomFunc('Deg to Rad',                     'out = degrees(expr)')
    self._addCustomFunc('Rad to Deg',                     'out = radians(expr)')
    self._addCustomFunc('Get Quadrant of Angle',          'out = getQuadrant(angle=expr, isRadians=True)')
    self._addCustomFunc('Get Reference Angle',            'out = getReferenceAngle(angle=expr, isRadians=True)')
    self._addCustomFunc('Get Coterminal Angle',           'out = getCoterminalAngleOverInterval(angle=expr, interval=Interval(0, 2*pi), isRadians=True)')
    self._addCustomFunc('Get all Derivatives equal to 0', 'out = getAllDiffsAt0(expr=expr, interval=Interval(-oo, oo), solveVar=curSymbol)')
    self._addCustomFunc('Find Local Extrema',             'print(findLocalExtrema(expr=expr, solveVar=curSymbol))')
    self._addCustomFunc('Find Local Extrema using Derivative', 'print(findLocalExtremaOverIntervalUsingDerivative(expr=expr, solveVar=curSymbol, interval=Interval(-oo, oo), order=1))')
    self._addCustomFunc('Find Absolute Extrema',          'print(findAbsExtremaOverInterval(expr=expr, solveVar=curSymbol, interval=Interval(-oo, oo)))')
    self._addCustomFunc('Get Time when Instant Velocity equals Average Velocity', 'out = getWhenDiffEqualToAverageChange(expr=expr, solveVar=curSymbol)')
    self._addCustomFunc('Mean Value Theorem',             'out = meanValueTheorem(expr=expr, solveVar=curSymbol, interval=Interval(-oo, oo))')
    self._addCustomFunc('Mean Value Theorem -- Raw',      'c = Symbol("c")\n'
                                                          'interval = Interval(, )\n'
                                                          'f = Function("f")\n'
                                                          'equ = Eq(Derivative(f(c)), (f(interval.end) - f(interval.start)) / (interval.end - interval.start))\n'
                                                          '# equ = equ.subs(f(interval.start), )\n'
                                                          '# equ = equ.subs(f(interval.end), )\n'
                                                          'out = equ.simplify()')
    # self._addCustomFunc('', '')

def _addCustomFunc(self, name, code, *comments):
    self.menuCustomFunctions.addAction(name, lambda: self.runCustomFuncInCode(code, *comments))



seperate = lambda: print('--------------------------------')

degrees = lambda x: (x * (pi / 180)).simplify()
radians = lambda x: (x * (180 / pi)).simplify()
printVar = lambda name, var: print(f'{name}: {var}')

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

# def getAvgRateOfChange2(expr, solveVar, interval):
#     seperate()
#     print('f(b):', func(interval.end))
#     print('f(a):', func(interval.start))
#     print('b - a:', interval.end - interval.start)
#     return ((expr.subs(solveVar, interval.start) - expr.subs(solveVar, interval.end)) / (interval.end - interval.start)).simplify()

def isWithinInterval(val, interval):
    return isBetween(val, interval.start, interval.end, not interval.left_open, not interval.right_open)

def constrainToInterval(iterable, interval):
    return [i for i in ensureIterable(iterable) if isWithinInterval(i, interval)]


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


# def solveRelatedRate(equation, solveVar, changing):
#     equation = equation.subs(solveVar, Derivative(solveVar))
#     print('just the var derived', equation)
#     equation = equation.subs(equation.lhs, )
#     print('Derived Equation:', equation)
#     try:
#         return solveset(equation, solveVar).simplify()
#     except:
#         return solveset(equation, solveVar)


def solveRelatedRate(equation, changingVar, isIncreasing, getAtVar, getAtValue, solveVar):
    return solveset(Eq(equation.lhs.diff(), equation.rhs.diff()), Derivative(solveVar))


def getCriticalPoints(expr, var, order=1):
    return solveset(Eq(expr.diff(), 0), var).simplify()
    # return solveset(Derivative(expr, (var, order)), var, domain=S.Reals).simplify()


def getCriticalIntervals(expr, var, overInterval=Interval(-oo, oo)):
    criticalPoints = getCriticalPoints(expr, var)
    criticalPoints = [overInterval.start] + sorted(list(criticalPoints)) + [overInterval.end]

    intervals = []
    for i in range(len(criticalPoints) - 1):
        intervals.append(Interval(criticalPoints[i], criticalPoints[i+1]))
    return intervals


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


def getQuadrant(angle, isRadians=True):
    if not isRadians:
        angle = angle * (pi / 180)
    if isBetween(angle, 0, pi/2, True):
        return 1
    elif isBetween(angle, pi/2, pi, True):
        return 2
    elif isBetween(angle, pi, (2*pi)/2, True):
        return 3
    elif isBetween(angle, (2*pi)/2, 2*pi, True):
        return 4
    else:
        return None


def getReferenceAngle(angle, isRadians=True):
    if not isRadians:
        angle = angle * (pi / 180)
    quad = getQuadrant(angle)
    if quad == 1:
        return angle
    elif quad == 2:
        return (pi/2) - angle
    elif quad == 3:
        return angle - (pi/2)
    elif quad == 4:
        return (2*pi) - angle
    else:
        return EmptySet


def getCoterminalAngleOverInterval(angle, interval, isRadians=True):
    testAngle = angle
    limit = 20
    while not interval.start <= testAngle and not testAngle.end <= interval.end and testAngle != angle:
        limit -= 1
        if limit <= 0:
            while not interval.start <= testAngle and not testAngle.end <= interval.end and testAngle != angle:
                limit += 1
                if limit >= 40:
                    return EmptySet
                testAngle -= (2*pi) if isRadians else 360
        testAngle += (2*pi) if isRadians else 360
    return testAngle


def getContinuousOrGetDifferentiableOrSomething(expr, var, interval):
    return expr.subs(var, interval.start) == expr.subs(var, interval.end)


def getAllDiffsAt0(expr, interval, solveVar):
    if getContinuousOrGetDifferentiableOrSomething(expr, solveVar, interval):
        return solveset(Eq(expr, 0), solveVar)
    else:
        return EmptySet


def meanValueTheorem(expr, solveVar, interval):
    alg  = getAvgRateOfChange(Lambda(solveVar, expr), interval)
    calc = expr.diff()
    printVar('Calculus  Slope', calc)
    printVar('Algebraic Slope', alg)
    return ensureNotIterable(constrainToInterval(solveset(Eq(calc, alg), solveVar), interval), EmptySet)


def rollesTheorem(expr, solveVar, interval):
    return constrainToInterval(solveset(Eq(expr.diff(), getAvgRateOfChange(Lambda(solveVar, expr), interval)), solveVar), interval)


def defangInf(inf, easy=True):
    if inf == oo:
        return 1000 if easy else 2147483640
    if inf == -oo:
        return -1000 if easy else -2147483640
    else:
        return inf


def getTestingValues(intervals):
    return [uniform(defangInf(i.start), defangInf(i.end)) for i in intervals]


def findLocalExtrema(expr, solveVar):
    printVar('Critival Points', getCriticalPoints(expr, solveVar))

    D = expr.diff()
    intervals = getCriticalIntervals(expr, solveVar)
    printVar('Intervals', intervals)

    exampleVals = getTestingValues(intervals)
    printVar('Testing values', exampleVals)
    path = [D.subs(solveVar, i) > 0 for i in exampleVals]
    printVar('Path of the Derivative', path)

    extrema = []
    for i in range(len(path) - 1):
        if path[i] != path[i+1]:
            extrema.append(('Maximum' if path[i] else 'Minimum', intervals[i].end))
    printVar('Extrema', extrema)

    regAns = [expr.subs(solveVar, i[1]) for i in extrema]
    printVar('Associated answers', regAns)

    rtnStr = ''
    for i in range(len(extrema)):
        rtnStr += f'Relative {extrema[i][0]} = {regAns[i]} at {solveVar} = {extrema[i][1]}\n'

    return rtnStr if len(rtnStr) else EmptySet

@todo
def findAbsExtremaOverInterval(expr, solveVar, interval):
    printVar('Critival Points', getCriticalPoints(expr, solveVar))

    D = expr.diff()
    intervals = getCriticalIntervals(expr, solveVar, interval)
    printVar('Intervals', intervals)

    exampleVals = getTestingValues(intervals)
    printVar('Testing values', exampleVals)
    path = [D.subs(solveVar, i) > 0 for i in exampleVals]
    printVar('Path of the Derivative', path)

    extrema = []
    for i in range(len(path) - 1):
        if path[i] != path[i+1]:
            extrema.append(('Maximum' if path[i] else 'Minimum', intervals[i].end))
    printVar('Extrema', extrema)

    regAns = [expr.subs(solveVar, i[1]) for i in extrema]
    printVar('Associated answers', regAns)

    rtnStr = ''
    for i in range(len(extrema)):
        rtnStr += f'Relative {extrema[i][0]}: y = {regAns[i]}, {solveVar} = {extrema[i][1]}\n'

    return rtnStr if len(rtnStr) else EmptySet


def findLocalExtremaOverIntervalUsingDerivative(expr, solveVar, interval, order=1):
    # printVar('Critival Points', getCriticalPoints(expr, solveVar))
    D = expr.diff((solveVar, order))
    printVar('Derivative', D)
    # return ensureNotIterable(constrainToInterval(solveset(Eq(D, 0), solveVar), interval), EmptySet)

    # criticalPoints = constrainToInterval(solve(Eq(D, 0), solveVar), interval)debug
    criticalPoints = solveset(Eq(D, 0), solveVar, domain=interval)
    printVar('Points where y is 0', criticalPoints)
    criticalPoints = [-oo] + sorted(list(criticalPoints)) + [oo]

    intervals = []
    for i in range(len(criticalPoints) - 1):
        intervals.append(Interval(criticalPoints[i], criticalPoints[i+1]))

    printVar("Intervals", intervals)
    exampleVals = getTestingValues(intervals)
    printVar('Testing values', exampleVals)
    path = [(D.subs(solveVar, i) > 0).simplify() for i in exampleVals]
    printVar('Path of the Derivative', path)

    extrema = []
    for i in range(len(path) - 1):
        if path[i] != path[i+1]:
            try:
                extrema.append(('Maximum' if path[i] else 'Minimum', intervals[i].end))
            except TypeError:
                extrema.append((str(path[i]), intervals[i].end))
    printVar('Extrema', extrema)

    regAns = [expr.subs(solveVar, i[1]) for i in extrema]
    printVar('Associated answers', regAns)

    rtnStr = ''
    for i in range(len(extrema)):
        rtnStr += f'Relative {extrema[i][0]}: y = {regAns[i]}, {solveVar} = {extrema[i][1]}\n'

    return rtnStr if len(rtnStr) else EmptySet


def assumePositive(expr):
    # if isinstance(expr, Iterable):
    for i in expr:
        if i < 0:
            del i
    return expr
    # else:
        # return abs(expr)


def getWhenDiffEqualToAverageChange(expr, solveVar):
    timeTill0 = solveset(Eq(expr, 0), solveVar)
    printVar('Time till 0', list(timeTill0))
    if timeTill0 is EmptySet:
        return EmtpySet
    vAvgs = [getAvgRateOfChange(Lambda(solveVar, expr), Interval(0, i)) for i in list(timeTill0)]
    return [solveset(Eq(expr.diff(), i), solveVar) for i in vAvgs]


if False:
    expr = parse_expr(' x**(1*1/3) - 8*x**(5/3) ')
    curSymbol = Symbol('x')
    solveVar = curSymbol
    interval = Interval(-oo, oo)


    #solve_univariate_inequality
    # z = Symbol('z', real=True)
    # z = Function('z')
    t = Symbol('t')
    # x, y = (4, 0)
    x, y = symbols('x y')
    x=1
    y = Function('y')

    eqs = [
        Eq(y(x), x**3 - 8),
        Eq(Derivative(x, t), -6),
    ]
    # out = dsolve(eqs, y, t), t=t)
    # out = dsolve(Eq(y(x), x**3 - 8), y(x))
    # out = reduce_inequalities([
    #         Eq(Derivative(z, t), Derivative(cbrt(x**3 + y**2), t)),
    #         Eq(Derivative(x, t), 2),
    #         Eq(Derivative(y, t), 1),
    #         Gt(z, 0),
    #         # (Derivative(x, t), 2, '=='),
    #         # (Derivative(y, t) - 1, '=='),
    #         # (z, '>'),
    #         # (z**3 - x**3 + y**2, '=='),
    #     ], Derivative(z, t))
    #     # ], z)

    # out = solve(Eq(Derivative(z, t), Derivative(cbrt(x**3 + y**2), t)), Derivative(z, t))
    # out = solve(Eq(Derivative(z, t), Derivative(cbrt(x**3 + y**2), t)).subs(Derivative(x, t), 2).subs(Derivative(y, t), 1), Derivative(z, t))
    # out = findLocalExtremaOverIntervalUsingDerivative(expr, solveVar, interval, order=1)

    # print(getWhenDiffEqualToAverageChange(expr, curSymbol))

    # b, h, a = symbols('b h a')
    # solveRelatedRate(Eq(a, (1/2)*b*h), b, False, h, 12, a)
    # print(isWithinInterval(6, Interval.Lopen(6, 10)))
    # print(isWithinInterval(6, Interval.Ropen(6, 10)))
    # print(isWithinInterval(6, Interval.open(6, 10)))
    # print(isWithinInterval(6, Interval(6, 10)))

    # print(meanValueTheorem(expr, curSymbol, Interval(-8, -2)))

    print(out)
    print(out.simplify())