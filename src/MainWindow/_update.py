# This Python file uses the following encoding: utf-8
import math
import re
import threading
from io import BytesIO
from os.path import dirname, join

import clipboard as clip
from Cope import *
from EasyRegex import *
from LoadingBar import LoadingBar, showLoading, showWithLoading
from PyQt5 import uic
from PyQt5.QtCore import (QByteArray, QEvent, QFile, QLine, QLineF, QRect,
                          QRectF, Qt, QThread, QTimer)
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (QDialog, QFileDialog, QLabel, QLineEdit,
                             QMainWindow, QTableWidgetItem, QWidget)
from sympy import *
from sympy import abc
from sympy.abc import *
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
from sympy.physics.units import Quantity
from sympy.physics.units.prefixes import Prefix
from sympy import S
from Variable import Variable
import scinot

@depricated
def updateCode(self):
    return
    try:
        self.codeBox.setPlainText(pycode(self.expr, fully_qualified_modules=False))
    except Exception as err:
        debug(err, 'CodeGenError', color=-1)
    # return python(self.expr)
    # # Remove all whitespace
    # s = re.sub(r'\s', '', s)
    # debug(s)

    # # First find the end of all the Integer(12) and Symbol('a') statements, remove the trailing ), and then remove Integer( and Symbol(
    # intRe = ere().match('Integer(').ifProceededBy(ere().number()).compile()
    # symRe = ere().match('Symbol(').optional(ere().quote()).ifProceededBy(ere().anyAlphaNum_().optional(ere().quote())).compile()
    # intReWhole = re.findall(ere().match('Integer(').number().match(')').compile(), s)
    # symReWhole = re.findall(ere().match('Symbol(').optional(ere().quote()).anyAlphaNum_().optional(ere().quote()).match(')').compile(), s)

    # debug(intReWhole)
    # debug(symReWhole)

    # for i in intReWhole:
    #     s = insertChar(s, i.end() - 1, '')
    # for i in symReWhole:
    #     s = insertChar(s, i.end() - 1, '')
    #     s = insertChar(s, i.end() - 2, '')
    # s = re.sub(intRe, '', s)
    # s = re.sub(symRe, '', s)

    # # functionRegex = ere().match('Function(').ifProceededBy(
    # #     ere().word().match('(').multiOptional(
    # #         ere().word().match(',').optional(' ')
    # #     ).matchAtLeast(2,
    # #         ere().match(')')
    # #     )
    # # ).str()

    # functionRegex = ere().match('Function(').ifProceededBy(
    #     ere().word().match('(').word().matchAtLeast(2, ere().match(')'))
    # ).str()
    # s = re.sub(functionRegex, '\ndef ', s)

    # # Loop through all the instances of "def f(x))" and replace the last character with ":\n"
    # functionRegex2 = ere().match('\ndef ').word().match('(').word().matchAtLeast(2, ere().match(')')).compile()
    # for i in re.findall(functionRegex2, s):
    #     s = insertChar(s, i.end() - 1, ':\n')

    # # Substitute all the variables for their proper names
    # for var in self.vars:
    #     s = re.sub(str(var.symbol), var.name, s)

    # # Properly space all the operators (since we removed all the whitespace earlier)
    # s = re.sub("\+", " + ", s)
    # s = re.sub("\*", " * ", s)
    # s = re.sub("\-", " - ", s)
    # s = re.sub("\/", " / ", s)
    # s = re.sub("\*\*", " ** ", s)

    # return s


def updatePiecewise(self, relations, addToMainEquation):
    result = f"Piecewise{tuple(relations)}"

    if addToMainEquation:
        self.equationInput.setPlainText(result)
        self.equation.update()
    else:
        self.varValueBox = result
        # A small hack, make sure we accept the input so we don't overwrite it
        self.varSetter.returnPressed.emit()


def updateLimit(self, updateVar, updateVal, addToMainEquation, dir):
    if addToMainEquation:
        withLimit = f"Limit({self.expr}, {updateVar}, {updateVal}" + (f", '{dir}'" if dir else '') + ')'
        self.equationInput.setPlainText(withLimit)
        self.equation.update()
    else:
        withLimit = f"Limit({self.currentVar.value}, {updateVar}, {updateVal}" + (f", '{dir}'" if dir else '') + ')'
        self.varValueBox = withLimit
        # A small hack, make sure we accept the input so we don't overwrite it
        self.varSetter.returnPressed.emit()


def updateIntDiff(self, diff, var, addToMainEquation, order, upperBound, lowerBound):
    #* First check if the input we got is valid
    if diff and len(upperBound):
        print("Ignoring upper bound that was given (derivatives don't have upper bounds)")
    if diff and len(lowerBound):
        print("Ignoring lower bound that was given (derivatives don't have lower bounds)")
    if not diff and not len(var) and (len(upperBound) or len(lowerBound)):
        print("ERROR: upper bound/lower bound specified, but no variable was specified")
        return

    currentEqu = self.equationInput.toPlainText() if addToMainEquation else self.currentVar.value

    if diff:
        if not len(var):
            result = f"Derivative({currentEqu})"
        else:
            result = f"Derivative({currentEqu}, ({var}, {order}))"
    else:
        if not len(var):
            result = f"Integral({currentEqu})"
        else:
            result = f"Integral({currentEqu}, ({var}, {lowerBound}, {upperBound}))"

    if addToMainEquation:
        self.equationInput.setPlainText(result)
        self.equation.update()
    else:
        self.varValueBox = result
        # A small hack, make sure we accept the input so we don't overwrite it
        self.varSetter.returnPressed.emit()


def updateSum(self, count, var, val, addToMainEquation):
    if addToMainEquation:
        withit = f"Sum({self.expr}, ({var}, {val}, {count}))"
        self.equationInput.setPlainText(withit)
        self.equation.update()
    else:
        withit = f"Sum({self.currentVar.value}, ({var}, {val}, {count}))"
        self.varValueBox = withit
        # A small hack, make sure we accept the input so we don't overwrite it
        self.varSetter.returnPressed.emit()


def updateImplicitMult(self):
    if self.implicitMult.isChecked():
        self.trans = self.baseTrans + (implicit_multiplication,)
    else:
        self.trans = self.baseTrans
    self.errorHandler.implicitMulLabel.setText(f'Implicit Multiplication is {"On" if self.implicitMult.isChecked() else "Off"}')
    self.equation.update()


def updateEquationSearch(self, equation):
    self.varValueBox = equation
    # A small hack, make sure we accept the input so we don't overwrite it
    self.varSetter.returnPressed.emit()