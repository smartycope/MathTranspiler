from Cope import *
from EasyRegex import *

from sympy import *
from sympy import abc
from sympy.abc import *
from sympy.calculus.util import continuous_domain
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
    self._addCustomFunc('Get Equation of Tangent Line', 'out = getTanSlopeEquation(expr=expr, symbol=curSymbol, symbolVal=curValue)')
    self._addCustomFunc('Get Equation of Normal Line',  'out = getNormalSlopeEquation(expr=expr, symbol=curSymbol, symbolVal=curValue)')
    self._addCustomFunc('Is Continuous At...',          'out = isContinuousAt(expr=expr, symbol=curSymbol, at=S.Reals)')

def _addCustomFunc(self, name, code):
    self.menuTools.addAction(name, lambda: self.runCustomFuncInCode(code))





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
    # y = mx+b
    # The slope of the tangent line is just the derivative
    simp = Derivative(expr, symbol).simplify()
    slope = simp.subs(symbol, symbolVal)
    point = (symbolVal, expr.subs(symbol, symbolVal))
    print('derivative:', simp, '\tslope:', slope, '\tpoint:', point)
    return Eq(y, solve(Eq(y - point[1], slope * (x - point[0])), y)[0])


def getNormalSlopeEquation(expr, symbol, symbolVal):
    # y = mx+b
    # The slope of the tangent line is just the derivative
    simp = Derivative(expr, symbol).simplify()
    slope = simp.subs(symbol, symbolVal)
    slope = (1 / slope) * -1
    point = (symbolVal, expr.subs(symbol, symbolVal))
    print('derivative:', simp, '\tslope:', slope, '\tpoint:', point)
    return Eq(y, solve(Eq(y - point[1], slope * (x - point[0])), y)[0])