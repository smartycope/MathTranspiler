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
from sympy.logic.boolalg import Boolean
from sympy.physics.vector.vector import *
from random import randint, uniform
from typing import Iterable

seperate = lambda enabled=True: print('--------------------------------') if enabled else None

degrees = lambda x: (x * (180 / pi)).simplify()
radians = lambda x: (x * (pi / 180)).simplify()
printVar = lambda name, var, enabled=True: print(f'{name.title()}: {var}') if enabled else None
isPositive = isPos = lambda x: x > 0
isNegative = isNeg = lambda x: x < 0


@confidence(40)
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


def getFunctionBetweenPoints(a, b):
    slope, offset = symbols('slope, offset')
    equ1 = Eq(a[1], offset*a[0] + slope)
    equ2 = Eq(b[1], offset*b[0] + slope)
    solvedSlope = debug(ensureNotIterable(solve(equ1, slope)))
    solvedOffset = debug(ensureNotIterable(equ2.subs(solvedSlope, slope), offset))
    return Eq(Symbol('y'), solvedOffset * Symbol('x') + solvedSlope)


@confidence(80)
def getTanSlopeEquation(expr, symbol, symbolVal):
    seperate()
    # y = mx+b
    # The slope of the tangent line is just the derivative
    simp = Derivative(expr, symbol).simplify()
    slope = simp.subs(symbol, symbolVal)
    point = (symbolVal, expr.subs(symbol, symbolVal))
    print('derivative:', simp, '\tslope:', slope, '\tpoint:', point)
    return Eq(y, solve(Eq(y - point[1], slope * (x - point[0])), y)[0])


@confidence(80)
def getTanSlope(expr, symbol, symbolVal):
    seperate()
    # y = mx+b
    # The slope of the tangent line is just the derivative
    simp = Derivative(expr, symbol).simplify()
    slope = simp.subs(symbol, symbolVal)
    return slope

@confidence(45)
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


def getLinearSlopeFrom2Points(a, b):
    return (b[1] - a[1]) / (b[0] - a[0])


def slopeIntercept(slope, b):
    return Eq(Symbol('y'), slope * Symbol('x') + b)


@confidence(60)
def getAvgRateOfChange(func, interval):
    seperate()
    print('f(b):', func(interval.end))
    print('f(a):', func(interval.start))
    print('b - a:', interval.end - interval.start)
    return ((func(interval.end) - func(interval.start)) / ((interval.end - interval.start))).simplify()


# def getAvgRateOfChange2(expr, solveVar, interval):
    # seperate()
    # print('f(b):', func(interval.end))
    # print('f(a):', func(interval.start))
    # print('b - a:', interval.end - interval.start)
    # return ((expr.subs(solveVar, interval.start) - expr.subs(solveVar, interval.end)) / (interval.end - interval.start)).simplify()


@confidence(80)
def isWithinInterval(val, interval):
    return isBetween(val, interval.start, interval.end, not interval.left_open, not interval.right_open)


@confidence(75)
def constrainToInterval(iterable, interval):
    return [i for i in ensureIterable(iterable) if isWithinInterval(i, interval)]


@confidence(55)
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


@confidence(99)
def leftOrRight(func, timeVal):
    return 'Right' if func(timeVal) > 0 else 'Left'


@confidence(40)
def timesAtHeight(expr, timeVar, height):
    if height == 0:
        expr = expr.diff(timeVar)

    return solveset(Eq(expr, height), timeVar)


@confidence(40)
def velocityAtHeight(expr, timeVar, height):
    seperate()
    diff = expr.diff(timeVar)
    ans = []

    heights = ensureIterable(solveset(Eq(expr, height), timeVar))
    print('Derivative:', diff)
    print('Heights:', heights)
    for i in heights:
        ans.append(diff.subs(timeVar, i))

    return ans


@confidence(30)
def accAtTime(expr, timeVar, time):
    seperate()
    diff = expr.diff(timeVar, 2)
    ans = []

    heights = ensureIterable(solveset(expr, timeVar))
    print('Derivative:', diff)
    print('Heights:', heights)
    for i in heights:
        ans.append(diff.subs(timeVar, i))

    return ans


@confidence(30)
def isSpeedingUpAtTime(expr, timeVar, time):
    seperate()
    diff1 = expr.diff(timeVar, 1).subs(timeVar, time)
    diff2 = expr.diff(timeVar, 2).subs(timeVar, time)
    print('First Derivative:', diff1)
    print('Second Derivative:', diff2)
    return (diff1 > 0) == (diff2 > 0)


# def solveRelatedRate(equation, solveVar, changing):
    # equation = equation.subs(solveVar, Derivative(solveVar))
    # print('just the var derived', equation)
    # equation = equation.subs(equation.lhs, )
    # print('Derived Equation:', equation)
    # try:
    #     return solveset(equation, solveVar).simplify()
    # except:
    #     return solveset(equation, solveVar)


@confidence(5)
def solveRelatedRate(equation, changingVar, isIncreasing, getAtVar, getAtValue, solveVar):
    return solveset(Eq(equation.lhs.diff(), equation.rhs.diff()), Derivative(solveVar))


@confidence(90)
def getCriticalPoints(expr, var, interval=Interval(-oo, oo), order=1) -> 'iterable':
    return ensureIterable(solveset(Eq(expr.diff(var, order), 0), var, domain=interval).simplify())
    # return solveset(Derivative(expr, (var, order)), var, domain=S.Reals).simplify()


@confidence(80)
def getCriticalIntervals(expr, var, overInterval=Interval(-oo, oo)):
    criticalPoints = getCriticalPoints(expr, var)
    criticalPoints = [overInterval.start] + sorted(list(criticalPoints)) + [overInterval.end]

    intervals = []
    for i in range(len(criticalPoints) - 1):
        intervals.append(Interval(criticalPoints[i], criticalPoints[i+1]))
    return intervals

@depricated
@confidence(49)
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


@confidence('sorta')
def minMaxOverInterval(expr, var, interval):
    seperate()
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


@confidence(60)
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


@confidence('sorta')
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


@confidence('fairly')
def getCoterminalAngleOverInterval(angle, interval, isRadians=True):
    answers = []
    i = 2*pi if isRadians else 360
    while True:
        testAngle = (angle + i).simplify()
        if isWithinInterval(testAngle, interval):
            answers.append(testAngle)

        testAngle = (angle - i).simplify()
        if isWithinInterval(testAngle, interval):
            answers.append(testAngle)

        i += 2*pi if isRadians else 360
        if not isWithinInterval(i, interval):
            break

    return ensureNotIterable(answers)


    # return EmptySet
    # testAngle = angle
    # limit = 20
    # while not interval.start <= testAngle and not testAngle.end <= interval.end and testAngle != angle:
    #     limit -= 1
    #     if limit <= 0:
    #         break
    #     else:
    #         testAngle += (2*pi) if isRadians else 360
    #         if isWithinInterval(testAngle, interval):
    #             return testAngle

    # testAngle = angle
    # limit = 20
    # while not interval.start <= testAngle and not testAngle.end <= interval.end and testAngle != angle:
    #     limit -= 1
    #     if limit <= 0:
    #         break
    #     else:
    #         testAngle -= (2*pi) if isRadians else 360
    #         if isWithinInterval(testAngle, interval):
    #             return testAngle

    # return EmptySet


@confidence('fairly')
def getContinuousOrGetDifferentiableOrSomething(expr, var, interval):
    return expr.subs(var, interval.start) == expr.subs(var, interval.end)


@confidence('somewhat')
def getAllDiffsAt0(expr, interval, solveVar):
    if getContinuousOrGetDifferentiableOrSomething(expr, solveVar, interval):
        return solveset(Eq(expr, 0), solveVar)
    else:
        return EmptySet


@confidence(50)
def meanValueTheorem(expr, solveVar, interval):
    seperate()
    alg  = getAvgRateOfChange(Lambda(solveVar, expr), interval)
    calc = expr.diff()
    printVar('Calculus  Slope', calc)
    printVar('Algebraic Slope', alg)
    return ensureNotIterable(constrainToInterval(solveset(Eq(calc, alg), solveVar), interval), EmptySet)


@confidence(55)
def rollesTheorem(expr, solveVar, interval):
    return constrainToInterval(solveset(Eq(expr.diff(), getAvgRateOfChange(Lambda(solveVar, expr), interval)), solveVar), interval)


@confidence(78)
def defangInf(inf, easy=True):
    if inf == oo:
        return 100000 if easy else 2147483640
    if inf == -oo:
        return -100000 if easy else -2147483640
    else:
        return inf


@confidence(85)
def getTestingValues(intervals):
    return [uniform(defangInf(i.start), defangInf(i.end)) for i in intervals]


@confidence(60)
def getIntervalsFromPoints(points, addInf=True):
    if addInf:
        points = [-oo] + sorted(list(points)) + [oo]

    intervals = []
    for i in range(len(points) - 1):
        add = Interval.open(points[i], points[i+1])
        if type(add) is Interval:
            intervals.append(add)
    return intervals

    printVar("Intervals", intervals)


@confidence(50)
def findLocalExtrema(expr, solveVar):
    seperate()
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


@confidence(30)
def findAbsExtremaOverInterval(expr, solveVar, interval):
    todo('Finish the function')
    seperate()
    printVar('Critival Points', getCriticalPoints(expr, solveVar))

    D = expr.diff()
    intervals = getCriticalIntervals(expr, solveVar, interval)
    printVar('Intervals', intervals)

    exampleVals = getTestingValues(intervals)
    printVar('Testing values', exampleVals)
    path = [isPositive(D.subs(solveVar, i)) for i in exampleVals]
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


@confidence(75)
def findLocalExtremaOverIntervalUsingDerivative(expr, solveVar, interval, order=1, extrema='Both'):
    both = extrema.lower() == 'both'
    max = extrema.lower() in ('max', 'maximum')
    min = extrema.lower() in ('min', 'minimum')
    if extrema.lower() not in ('both', 'max', 'maximum', 'min', 'minimum'):
        raise TypeError("Invalid extrema parameter. Must be one of (both, max, maximum, min, minimum)")

    seperate(both)
    # printVar('Critival Points', getCriticalPoints(expr, solveVar))
    D = expr.diff((solveVar, order))
    printVar('Derivative', D, both)
    # return ensureNotIterable(constrainToInterval(solveset(Eq(D, 0), solveVar), interval), EmptySet)

    # criticalPoints = constrainToInterval(solve(Eq(D, 0), solveVar), interval)debug
    criticalPoints = solveset(Eq(D, 0), solveVar, domain=interval)
    printVar('Points where y is 0', criticalPoints, both)
    criticalPoints = [-oo] + sorted(list(criticalPoints)) + [oo]

    intervals = []
    for i in range(len(criticalPoints) - 1):
        intervals.append(Interval(criticalPoints[i], criticalPoints[i+1]))

    printVar("Intervals", intervals, both)
    exampleVals = getTestingValues(intervals)
    printVar('Testing values', exampleVals, both)
    path = [(D.subs(solveVar, i) > 0).simplify() for i in exampleVals]
    printVar('Path of the Derivative', path, both)

    extrema = []
    for i in range(len(path) - 1):
        if path[i] != path[i+1]:
            try:
                extrema.append(('Maximum' if path[i] else 'Minimum', intervals[i].end))
            except TypeError:
                extrema.append((str(path[i]), intervals[i].end))
    printVar('Extrema', extrema, both)

    regAns = [expr.subs(solveVar, i[1]) for i in extrema]
    printVar('Associated answers', regAns, both)

    if both:
        rtnStr = ''
        for i in range(len(extrema)):
            rtnStr += f'Relative {extrema[i][0]}: f({solveVar}) = {regAns[i].simplify()}, {solveVar} = {extrema[i][1].simplify()}\n'

        return rtnStr if len(rtnStr) else EmptySet
    else:
        for i in range(len(extrema)):
            if extrema[i][0] == ('Maximum' if max else 'Minimum'):
                return extrema[i][1].simplify()


@confidence(70)
def findLocalExtremaOverIntervalUsingSecondDerivative(expr, solveVar, interval, order=2):
    seperate()
    # printVar('Critival Points', getCriticalPoints(expr, solveVar))
    D = expr.diff((solveVar, order))
    # D = Derivative(expr, (solveVar, order))
    printVar('Derivative', D)
    # return ensureNotIterable(constrainToInterval(solveset(Eq(D, 0), solveVar), interval), EmptySet)

    # criticalPoints = constrainToInterval(solve(Eq(D, 0), solveVar), interval)
    # criticalPoints = solveset(Eq(expr.diff(), 0), solveVar, domain=interval)
    criticalPoints = ensureIterable(getCriticalPoints(expr, solveVar, interval))
    printVar('Points where y is 0 (critical points)', criticalPoints)

    rtn = ''
    for i in criticalPoints:
        rtn += f"{'Minimum' if (D.subs(solveVar, i) > 0).simplify() else 'Maximum'} at x = {i}\n"
    return rtn


# @todo('increasing/decreasing is determined solely by the first diff and concavity is solely determined by the second diff')
@confidence(75)
def getConcaveIntervals(expr, solveVar, includeFirstIntervalTests=True):
    #* https://docs.sympy.org/latest/modules/calculus/index.html?highlight=concave#sympy.calculus.util.is_convex
    seperate()

    # firstDiff = expr.diff(expr, solveVar)
    firstDiff = Derivative(expr, solveVar)
    # secondDiff = expr.diff(expr, solveVar, 2)
    secondDiff = Derivative(expr, solveVar, 2)
    if includeFirstIntervalTests:
        critP = ensureIterable(getCriticalPoints(expr, solveVar))
        printVar("Critical Points", critP)
    else:
        critP = ()
    inflectP = ensureIterable(getInflectionPoints(expr, solveVar))
    printVar("Inflection Points", inflectP)

    intervals = getIntervalsFromPoints(tuple(inflectP) + (tuple(critP) if includeFirstIntervalTests else ()))
    printVar("Intervals", intervals)

    exampleVals = getTestingValues(intervals)
    printVar('Testing values', exampleVals)

    firstDiffPath  = [isPositive(firstDiff.subs(solveVar, i).simplify())  for i in exampleVals]
    # printVar('firstDiffPath', firstDiffPath)
    secondDiffPath = [isPositive(secondDiff.subs(solveVar, i).simplify()) for i in exampleVals]
    # printVar('secondDiffPath', secondDiffPath)


    decreasingPath = []
    concavity = []
    for i in range(len(firstDiffPath)):
        # positive is second diff means concave up, and - in first diff means decreasing
        decreasingPath.append('Increasing' if firstDiffPath[i] else 'Decreasing')
        concavity.append('Concave Up' if secondDiffPath[i] else 'Concave Down')


    # rtn = f"Intervals:               {[(i.start, i.end) for i in intervals]}\n"\
    #       f"First Derivative Signs:  {['+' if i else '-' for i in firstDiffPath]}\n"\
    #       f"Second Derivative Signs: {['+' if i else '-' for i in secondDiffPath]}\n"\
    #       f"Increasing/Decreasing:   {decreasingPath}\n"\
    #       f"Concavity:               {concavity}"\
    if includeFirstIntervalTests:
        data = [
            [(i.start, i.end) for i in intervals],
            ['+' if i else '-' for i in firstDiffPath],
            ['+' if i else '-' for i in secondDiffPath],
            decreasingPath,
            concavity
        ]
        names = ['Intervals', "f'(x) Signs", "f''(x) Signs", "Increment", "Concavity"]
    else:
        data = [
            [(i.start, i.end) for i in intervals],
            ['+' if i else '-' for i in secondDiffPath],
            decreasingPath,
            concavity
        ]
        names = ['Intervals', "f''(x) Signs", "Increment", "Concavity"]

    t = quickTable(data, interpretAsRows=False, fieldNames=names, returnStr=True)
    print(t)
    return t

    # firstDiffSigns = secondDiffSigns = []
    # for i in range(len(firstDiffPath)):
    #     firstDiffSigns.append()
    # for i in range(len(path) - 1):
        # if path[i] != path[i+1]:
            # extrema.append(('Maximum' if path[i] else 'Minimum', intervals[i].end))
    # printVar('Extrema', extrema)


@confidence(75)
def assumePositive(expr):
    # if isinstance(expr, Iterable):
    for i in expr:
        try:
            if i < 0:
                del i
        except:
            # try:
            if i.evalf() < 0:
                del i
            # except:
                # return sorted(expr)

    return expr
    # else:
        # return abs(expr)


@confidence(45)
def getWhenDiffEqualToAverageChange(expr, solveVar):
    seperate()
    timeTill0 = solveset(Eq(expr, 0), solveVar)
    printVar('Time till 0', list(timeTill0))
    if timeTill0 is EmptySet:
        return EmtpySet
    vAvgs = [getAvgRateOfChange(Lambda(solveVar, expr), Interval(0, i)) for i in list(timeTill0)]
    return [solveset(Eq(expr.diff(), i), solveVar) for i in vAvgs]


@confidence(65)
def getInflectionPoints(expr, solveVar):
    return solveset(Eq(expr.diff(solveVar, 2), 0), solveVar).simplify()
    # inflection points:
    # second diff
    # solve for 0
    # -> original equation, solve for y


@confidence(10)
def getMaxAreaOfInscribedRect(equation):
    x, y, A = symbols('x y A')
    solvedForY = ensureIterable(solve(equation, y))
    areaEqu = list(map(lambda y:Mul(Mul(2, x), Mul(2, y)), solvedForY))
    critP   = flattenList(map(getCriticalPoints, areaEqu, (x,)*len(areaEqu)))
    # print(critP)
    possibleAnswers = list(filter(lambda x: isPositive(x.evalf()), critP))
    # Multiply them all by 2
    lengths = list(map(Mul, possibleAnswers, (2,) * len(possibleAnswers)))
    widths  = list(map(lambda l, s: s.subs(x, l).simplify(), possibleAnswers, solvedForY))
    printVar('Possible Lengths', lengths)
    printVar('Possible Widths',  widths)
    return [l*w for l, w in zip(lengths, widths)]

@confidence(70)
def approxAreaUnderCurve(expr, interval, rects, rightPoint=True, solveVar=Symbol('x')):
    seperate()
    delta = (interval.end - interval.start) / rects
    printVar("Rect Width (Δx)", delta)

    xPoints = MappingList([interval.start + (delta * (i + (1 if rightPoint else 0))) for i in range(rects)])
    yPoints = MappingList([expr.subs(solveVar, i).simplify() for i in xPoints])
    printVar('x Points', xPoints)
    printVar('y Points', yPoints)

    areas = yPoints * delta
    printVar('areas', areas)

    return sum(areas).simplify()

@confidence(10)
def getDefiniteIntegralOfRiemannSum(expr):
    x, a, b, i = symbols('x_i a b i')

    factors = expr.as_ordered_factors()
    delta = Mul(*factors[0:-1]).doit()
    fOfXi = factors[-1]

    # Eq(x, a + i * delta)
    fOfXi.subs(x, a + i * delta)


def netSignedInterval(expr, interval):
    return 'graph it' \
           'above x axis is +, below is -' \
           'Find the area of the traingles (1/2*base*height), or just count it ' \
           'add (or subtract) all the areas'


def getIntersection(fx, gx, solveVar=Symbol('x')):
    return solve(Eq(fx, gx), solveVar)


# R_n = rational * Sum(expr * func(expr)),      expr is in the form of firstNum + <something>
def getRiemannSum(rational, x, expr, firstNum, solveVar=Symbol('x')):
    upperRational = rational.upper
    b = Symbol('b')
    upper = solve(Eq(upperRational, b-upperRational), b)
    printVar('upper', upper)
    return Integral((expr * func(expr)).subs(expr, solveVar), (solveVar, firstNum, upper))

# def relatedRateWordProblem():
    # maxFencing = 148
    # maxFencingEqu = 4x+y
    # area = x*y
    # ans = area / 3
    # area = x*(solve(Eq(maxFencing, maxFencingEqu), y))
    # findLocalExtremaOverIntervalUsingDerivative(area, x, interval=(-oo, oo))

    # HOW TO DO AREA RELATED RATES PROBLEMS:
    # x, y, area, per = symbols('x y area per')
    # area = 2166

    # solvedArea = Eq(area, x*y)
    # x = ensureNotIterable(solve(solvedArea, x))
    # solvedPerimeter = x * 3 + y * 2
    # solvedy = findLocalExtremaOverIntervalUsingDerivative(solvedPerimeter, y, interval, extrema='min')

    # print('x:', x.subs(y, solvedy))
    # print('y:', solvedy)

# self._addCustomFunc('Sigma Balls',           'i = Dummy()\n'
    #                                              'n = Symbol("n")\n'
    #                                              'm = Symbol("m")\n'
    #                                              'out = solve(Eq(Sum(, (i, 1, n), Sum(, (i, 1, m) + Sum(, (i, m+1, n)))',
    #                                              'm is a number between 1 and n')

@confidence(-5)
def solveEquals(*eqs, solveFor=None):
    if solveFor is None:
        variables = set(flattenList([i.atoms(Symbol) for i in eqs]))
    else:
        variables = set(ensureIterable(solveFor))

    definitions = {}
    maxIterations = len(eqs) * 3 + 1

    while variables not in variables.intersection(definitions.keys()) or maxIterations <= 0:
        # If any of the equals have either 1 or 2 variables, then they don't need to be reduced at all
        for i in eqs:
            if len(i.atoms(Symbol)) <= 2:
                definitions[i.lhs] = i.rhs

        debug(definitions, 'First try')

        # If there weren't any of those, find any 2 equals that involve the same variables, and figure them out based on that
        if not len(definitions):
            for i in eqs:
                for k in eqs:
                    if i == k:
                        continue
                    sharedSymbols = i.atoms(Symbol).intersection(k.atoms(Symbol))
                    if len(sharedSymbols):
                        # Arbitrarily choose the first symbol
                        s = sharedSymbols.pop()
                        val = i.subs(s, ensureNotIterable(solve(k, s)))
                        if isiterable(val):
                            val = val[0]
                        if type(val) is Eq:
                            val = val.rhs

                        if s != val:
                            try:
                                definitions[s]
                            except KeyError:
                                definitions[s] = val
                            else:
                                # A hack to see which is the simplest
                                if len(str(val)) < len(str(definitions[s])):
                                    definitions[s] = val

                        debug(definitions)

        debug(definitions, 'Second try')

        _definitions = {}
        for i in eqs:
            for sym, val, in definitions.items():
                # result = Subs(i, sym, val)
                result = i.subs(sym, val)
                if not isinstance(result, Boolean):
                    if len(result.atoms(Symbol)) <= 2:
                        _definitions[result.lhs] = result.rhs
        definitions.update(_definitions)

        debug(definitions, 'Third try')

        maxIterations -= 1

    return definitions


@confidence(80)
def getVolumeOfSolidRevolution(expr, lowerbound, upperbound, solveVar=Symbol('x'), simplify=False):
    i = Integral(pi * (expr)**2, (solveVar, lowerbound, upperbound))
    if simplify:
        i.doit().simplify()
    return i


@confidence(50)
def getAreaBetween(fx, gx, lowerbound=None, upperbound=None, solveVar=Symbol("x")):
    if bool(lowerbound) != bool(upperbound):
        raise TypeError

    if lowerbound:
        return Integral(fx - gx, (solveVar, lowerbound, upperbound)).simplify()
    else:
        return Integral(fx - gx, (solveVar, *sorted(list(getIntersection(fx, gx, solveVar))))).simplify()



    # HOW TO DO AREA RELATED RATES PROBLEMS:
    # x, y, area, per = symbols('x y area per')
    # area = 2166

    # solvedArea = Eq(area, x*y)
    # x = ensureNotIterable(solve(solvedArea, x))
    # solvedPerimeter = x * 3 + y * 2
    # solvedy = findLocalExtremaOverIntervalUsingDerivative(solvedPerimeter, y, interval, extrema='min')

    # print('x:', x.subs(y, solvedy))
    # print('y:', solvedy)


@confidence(45)
def getCrossSectionalVolume(baseFunction, crossSectionalAreaEquation, randomlyDouble=False, quadrant=None):
    def getLimits(xInts):
        xInts = list(xInts)
        if quadrant:
            if quadrant.lower() == 'first':
                return [0, max(xInts)]
            elif quadrant.lower() == 'second':
                return [min(xInts), 0]
            elif quadrant.lower() == 'third':
                todo('third quadrant')
            elif quadrant.lower() == 'fourth':
                return [max(xInts), 0]
            else:
                raise TypeError("Unrecognized quadrant. Please use first, second, third, or fourth.")
        else:
            return sorted(xInts)

    debug(baseFunction)
    debug(crossSectionalAreaEquation)
    x, y, area, radius = symbols('x, y, area, radius')
    solvedY = MappingList(solve(baseFunction, y))
    if randomlyDouble:
        solvedY *= 2

    crossSectionAtoms = crossSectionalAreaEquation.atoms(Symbol)
    assert(len(crossSectionAtoms) == 1)
    # Put solvedY into the crossSectionalAreaEquation
    possibleCrossSectionalEquations = []
    for i in solvedY:
        possibleCrossSectionalEquations.append(crossSectionalAreaEquation.subs(list(crossSectionAtoms)[0], i))

    xIntercepts = []
    for i in possibleCrossSectionalEquations:
        xIntercepts.append(solve(Eq(i, 0), x))

    # xIntercepts = ensureNotIterable(xIntercepts)

    printVar('solved Y', solvedY)
    printVar('possibleCrossSectionalEquations', MappingList(possibleCrossSectionalEquations).simplify())
    printVar('xintercepts', xIntercepts)
    if len(xIntercepts) == 1:
        xIntercepts = xIntercepts[0]
    printVar('Integral bounds', getLimits(xIntercepts))

    # xIntercepts = solve(Eq(crossSectionalAreaEquation, 0), x)
    if (len(xIntercepts) > 2):
        raise UserWarning(f"There are more than 2 xIntercepts somehow ({xIntercepts})")

    return ensureNotIterable(set(assumePositive([debug(Integral(cs, (x, *getLimits(xIntercepts)))).simplify() for cs in possibleCrossSectionalEquations])))


@confidence(80)
def getVolumeOfARotatedRegionBetweenCurves(fx, bounds:Interval, gx=0, axis='x'):
    # find the volume generated when the region between cuves is rotated around axis
    # flip x and y (f(x) becomes solve the equation for x) if its rotated around y-axis, othersize leave as is
    # use disk method
    # find volume under cuve of (curves) when rotated around axis
    # The disk method is just the washer method where g(x) is constant (0?)

    assertValue(axis, 'x', 'y')
    assert(len(fx.atoms(Symbol)) <= 1)

    x, y = symbols('x y')
    var = ensureNotIterable(fx.atoms(Symbol))
    otherVar = x if var == y else y

    if axis == 'y':
        fx = ensureNotIterable(solve(fx - otherVar, otherVar))
        fx = fx.subs(ensureNotIterable(var), x)
        printVar('flipped equation', fx)

    return Integral(pi * (fx**2 - gx**2), (var, bounds.start, bounds.end))


@confidence(40)
def getVolumeOfARotatedRegionUsingAShell(boundingEqu, limit, rotateAroundLine, secondBoundingEqu=0, secondLimit=None, areaEquation=parse_expr('2*pi*r*h'), axis='x', makeAbs=False, swapSides=False):
    assertValue(axis, 'x', 'y')
    boundingEqu = sympify(boundingEqu)
    secondBoundingEqu = sympify(secondBoundingEqu)
    limit = sympify(limit)
    secondLimit = sympify(secondLimit)
    rotateAroundLine = sympify(rotateAroundLine)
    areaEquation = sympify(areaEquation)
    assert(len(boundingEqu.atoms(Symbol)) <= 1)
    assert(len(secondBoundingEqu.atoms(Symbol)) <= 1)
    assert(len(limit.atoms(Symbol)) == 0)
    if secondLimit is not None:
        assert(len(secondLimit.atoms(Symbol)) == 0)

    vy, uy = sorted((boundingEqu, secondBoundingEqu), key=lambda x: x.subs(ensureNotIterable(x.atoms(Symbol)), limit).evalf()) # , reverse=flipEqations)
    var = ensureNotIterable(vy.atoms(Symbol))
    if isiterable(var) and not len(var):
        var = ensureNotIterable(uy.atoms(Symbol))

    x, y = symbols('x y')
    otherVar = x if var == y else y

    debug(var)

    # vy(d)
    # uy = vy.subs(var, upperLimit)
    # using assumePositive is an assumption
    if secondLimit is None:
        secondLimit = ensureNotIterable(solve(Eq(vy, uy), var), None)

    if secondLimit is None:
        raise Exception('vy = uy seems to not have any solutions...')
    # debug(limit)
    # debug(secondLimit)
    # if secondLimit is
    lowerLimit, upperLimit = sorted((limit, secondLimit))
    c = lowerLimit
    d = upperLimit
    k = rotateAroundLine
    radius = r = abs(var - k) if makeAbs else var - k
    height = h = (vy - uy) if swapSides else uy - vy
    Ay = areaEquation

    thingToIntegrate = areaEquation.subs(    Symbol('r'), radius)
    thingToIntegrate = thingToIntegrate.subs(Symbol('h'), height)

    printVar('upperLimit (d)', d)
    printVar('lowerLimit (c)', c)
    printVar('rotateAroundLine (k)', k)
    printVar('radius (r)', r)
    printVar('height (h)', h)
    printVar('Equation To integrate', thingToIntegrate)
    printVar('leftBoundEquation (v(y))',  vy)
    printVar('rightBoundEquation (u(y))', uy)

    if axis == 'y':
        todo('add rotation around the y axis')
    #     vy = ensureNotIterable(solve(vy - otherVar, otherVar))
    #     vy = vy.subs(ensureNotIterable(var), x)
    #     printVar('flipped equation', vy)

    return Integral(thingToIntegrate, (var, lowerLimit, upperLimit))


def workDone(expr_newtons, start_meters, end_meters):
    return integrate(expr_newtons, start_meters, end_meters)


def integral(expr, lower, upper, var=None):
    expr = sympify(expr)
    vars = expr.atoms(Symbol)
    if len(vars) == 0:
        if var is not None:
            if verbose(): print('You specified a variable when you didn\'t have to...')
        return Integral(expr, (Dummy(), lower, upper))
    elif len(vars) == 1:
        v = vars.pop()
        assert(v == var or var is None)
        return Integral(expr, (v, lower, upper))
    else:
        if var is None:
            raise TypeError(f'Can\'t integrate. Too many variables. Variables: {vars}, Expression: {expr}')
        else:
            return Integral(expr, (var, lower, upper))


@confidence(60)
def calculateNaturalStringLengthFrom2Measurements(joules1, start1, end1, joules2, start2, end2):
    length, k, x = symbols('length k x')
    # debug(integral(k * x, start1 - length, end1 - length, x).doit().simplify())
    solvedK = ensureNotIterable(solve(Eq(integral(k * x, start1 - length, end1 - length, x).doit(), joules1), k))
    printVar('k', solvedK)
    return ensureNotIterable(solve(Eq(integral(solvedK * x, start2 - length, end2 - length, x).doit(), joules2), length)).simplify()


def cartesian2Polar(x, y, useRadians=True, giveAsVectorType=True):
    r = sqrt(x**2 + y**2).simplify()
    theta = (atan2(y, x) if useRadians else degrees(atan2(y, x))).simplify()

    if giveAsVectorType:
        raise NotImplementedError()
        # return Vector()
    else:
        return FiniteSet(r, theta)


def polar2Cartesian(r, theta, useRadians=True):
    if not useRadians:
        theta = radians(theta)

    return FiniteSet(r * cos(theta).simplify(), r * sin(theta).simplify())


def getComponentsOfVector(r, theta, useRadians=True):
    todo()
    raise NotImplementedError()


if False:
    out = None
    expr = parse_expr(' (x**2)/10 + 1 ')
    curSymbol = solveVar = x = Symbol('x')
    interval = Interval(-oo, oo)
    x, y, s = symbols('x, y, s')

    # out = getVolumeOfARotatedRegionUsingAShell(3, (3*sqrt(y))/2, 0, -3/Integer(2), areaEquation=parse_expr('2*pi*r*h'), axis='x')
    out = calculateNaturalStringLengthFrom2Measurements(9, 1, 3, 9, 3, 8).evalf()

    # preview(out)
    # import clipboard
    # clipboard.copy(latex(out))

    # out = getCrossSectionalVolume(x**2 + y**2 - 11**2, s**2, randomlyDouble=True)

    # debug(solveEquals(a, p))
    # debug(something)

    # thing = reduce_inequalities([
    #     a,
    #     p
    # ], (x, y))

    # debug(solve(thing, x))

    # list(thing.args)[1]

    # debug(per)
    # debug(area)
    # debug(x)
    # debug(y)

    # h, p = symbols('h, p', cls=Function)
    # p = Function('p')
    # x = Symbol('x')
    # h = Lambda(x, (x**3+p(x))**4)
    # out = dsolve(h, Derivative(h(-1)))

    # #solve_univariate_inequality
    # # z = Symbol('z', real=True)
    # # z = Function('z')
    # t = Symbol('t')
    # # x, y = (4, 0)
    # x, y = symbols('x y')
    # x=1
    # y = Function('y')

    # eqs = [
    #     Eq(y(x), x**3 - 8),
    #     Eq(Derivative(x, t), -6),
    # ]
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
    try:
        print(out.simplify())
    except:
        pass
