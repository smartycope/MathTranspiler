from sympy.parsing.sympy_parser import (parse_expr, standard_transformations,
                                        implicit_multiplication_application,
                                        implicit_multiplication, convert_xor)
from sympy.printing.preview import preview
from sympy.solvers.inequalities import solve_rational_inequalities
from sympy.sets.conditionset import ConditionSet
from sympy.core.function import AppliedUndef
from sympy.plotting import plot
from sympy import abc
from sympy.abc import *
from sympy import *
from sympy.calculus.util import continuous_domain


var('x')
var('y')
a = sqrt(x+2)
b = -x**2-3*x-5,

f = Piecewise((a, -2 < x), (a, x <= 2), (b, x > 2))

print(continuous_domain(f, x, Reals))