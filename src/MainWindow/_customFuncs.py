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
    self._addCustomFunc('Get Continuous at',            'out = isContinuousAt(expr=expr, symbol=curSymbol, at=S.Reals)')
    self._addCustomFunc('Get Equation of Tangent Line', 'out = getTanSlopeEquation(expr=expr, symbol=curSymbol, symbolVal=curValue)')
    self._addCustomFunc('Get Equation of Normal Line',  'out = getNormalSlopeEquation(expr=expr, symbol=curSymbol, symbolVal=curValue)')
    self._addCustomFunc('Find Average Rate of Change over Interval', 'out = getAvgRateOfChange(func=func, interval=Interval(from, to))')
    self._addCustomFunc('Intermediate Value Theorem',   'out = leastPossibleVal(func=func, interval=Interval(from, to))')
    self._addCustomFunc('Solve as Implicit Derivative', 'out = idiff(eq=expr, y=y, x=x, n=1)', 'eq is the equation. Must equal 0 (use -, not Eq() or =)', 'n is the order of the derivative')
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
