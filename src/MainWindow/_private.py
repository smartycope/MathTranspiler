# This Python file uses the following encoding: utf-8
import math
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
from Variable import Variable
from copy import deepcopy
import re


def resetEverything(self):
    self.equationInput.setPlainText('')
    self.vars = []
    self.eqVars = []
    self.resetOuput()
    # self.varList.setText('')
    self.varList.clear()
    self.varSetter.setText('')
    self.varInfoBox.setPlainText('')
    self.updateEquation()
    self.varPng.setPixmap(QPixmap())
    self.solutionPng.setPixmap(QPixmap())
    self.equationPng.setPixmap(QPixmap())
    self.codePng.setPixmap(QPixmap())
    self.loading = False
    self.codeLoading = False
    # self.codeInput.setPlainText('')


def resetTab(self):
    self.output.setCurrentIndex(self.lastTab)


def resetIcon(self, tabIndex):
    self.output.setTabIcon(tabIndex, QIcon())


def resetError(self):
    self.errorBox.setPlainText('')
    self.resetIcon(self.errorTabIndex)


def resetOuput(self):
    self.answerBox.setPlainText('')
    self.codeOutput.setPlainText('')
    self.resetError()


def calculateSolution(self):
    # NOTE: Must call UpdateVars() before this is run!
    expr = self.subbedExpr
    if not self.dontSimplify.isChecked():
        try:
            expr = expr.doit()
        except Exception as err:
            debug(err, color=-1)

        # rels = []
        # for var in self.vars:
        #     if var.valueChanged:
        #         rels += (var.)
        #         self.expr = self.expr.subs(var.symbol, var.value)

        # system = solve_rational_inequalities(self.relations + [self.expr])
        # system = solve_poly_set_something(...)
        expr = expr.simplify()

    if self.doEval.isChecked():
        expr = expr.evalf()

    self.solvedExpr = expr

def getPixmap(self, expr):
    obj = BytesIO()
    preview(expr, output='png', viewer='BytesIO', outputbuffer=obj)
    return QPixmap(QImage.fromData(bytes(obj.getbuffer())))


def fixEquationString(self, eq:str):
    eq = self.sanatizeInput(eq)

    if self.implicitMult.isChecked():
        functionRegex = group(word()) + ifProceededBy(match('(') + stuff() + match(')'))
        eq = re.sub(functionRegex.str(), r"Function('\1')", eq)

    # There are no ' = ' in equation, check for other inequalities
    sides = re.split('<=', eq)
    parenCnt = 0
    eq = ""
    for i in sides[:-1]:
        eq += f'Le({i}, '
        parenCnt += 1
    eq += sides[-1] + ')' * parenCnt

    sides = re.split('>=', eq)
    parenCnt = 0
    eq = ""
    for i in sides[:-1]:
        eq += f'Ge({i}, '
        parenCnt += 1
    eq += sides[-1] + ')' * parenCnt

    sides = re.split('!=', eq)
    parenCnt = 0
    eq = ""
    for i in sides[:-1]:
        eq += f'Ne({i}, '
        parenCnt += 1
    eq += sides[-1] + ')' * parenCnt

    sides = re.split('==', eq)
    parenCnt = 0
    eq = ""
    for i in sides[:-1]:
        eq += f'Eq({i}, '
        parenCnt += 1
    eq += sides[-1] + ')' * parenCnt

    sides = re.split((match('<') + ifNotPrecededBy('=')).str(), eq)
    parenCnt = 0
    eq = ""
    for i in sides[:-1]:
        eq += f'Lt({i}, '
        parenCnt += 1
    eq += sides[-1] + ')' * parenCnt

    sides = re.split((match('>') + ifNotPrecededBy('=')).str(), eq)
    parenCnt = 0
    eq = ""
    for i in sides[:-1]:
        eq += f'Gt({i}, '
        parenCnt += 1
    eq += sides[-1] + ')' * parenCnt

    return eq

# The difference between these 2 functions is that sanatizeInput() does the bare essentials and should always be run, while
# fixEquationString() does extra stuff enabled by the setting action, and also sanatizes it

def sanatizeInput(self, eq:str):
    #* Replace the weird minus symbol with a proper minus symbol
    eq = re.sub('−', '-', eq)

    #* Replace all '='s with 'Eq()' statements
    sides = (match('=') + ifNotPrecededBy(anyOf('<>!='))).compile().split(eq)

    # We have more than 1 ' = ' in the equation
    if len(sides) > 2:
        raise SyntaxError("More than one '=' in the Equation")
    # thing = otherThing
    if len(sides) == 2:
        eq = f'Eq({sides[0]}, {sides[1]})'
        re.sub((match('=') + ifNotPrecededBy(anyOf('<>!='))).str(), '', sides[1])

    return eq


def sanatizeLatex(self, latex):
    latex = re.sub('$', '', latex)
    return latex


def printToCodeOutput(self, *args, sep=' ', end='\n'):
    for i in ensureIterable(args):
        self.codeOutput.setPlainText(self.codeOutput.toPlainText() + str(i) + str(sep if sep != ensureIterable(args)[-1] else end))
    self.codeOutput.setPlainText(self.codeOutput.toPlainText() + str(end))


def runCustomFuncInCode(self, funcString):
    self.codeInput.setPlainText(funcString)
    self.runCodeButton.pressed.emit()
    self.output.setCurrentIndex(self.codeTabIndex)
