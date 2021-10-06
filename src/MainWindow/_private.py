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
from PyQt5 import QtCore, QtGui, QtMultimedia, QtWidgets, uic
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


def connectEverything(self):
    self.save.triggered.connect(self._save)
    self.saveAs.triggered.connect(self._saveAs)
    self.load.triggered.connect(self._load)
    self.exportLatex.triggered.connect(self.exportAsLatex)
    self.exportMathML.triggered.connect(self.exportAsMathML)
    self.exportMathmatica.triggered.connect(self.exportAsMathmatica)

    self.copyLatex.triggered.connect(lambda: clip.copy(latex(self.solvedExpr)))
    self.copyMathML.triggered.connect(lambda: clip.copy(mathml(self.solvedExpr)))
    self.copyMathmatica.triggered.connect(lambda: clip.copy(mathematica_code(self.solvedExpr)))
    self.copySolution.triggered.connect(lambda: clip.copy(str(self.solvedExpr)))
    self.copyEquation.triggered.connect(lambda: clip.copy(self.equ))
    # self.copyCurVar.triggered.connect(lambda: clip.copy(self.varValueBox))
    self.copyCurVar.triggered.connect(lambda: clip.copy(todo('figure out current var copy to clipboard')))

    # The equation input box
    # self.equationInput.textChanged.connect(self.updateEquation)
    self.solveButton.clicked.connect(self.updateEquation)
    self.solveButton2.triggered.connect(self.updateEquation)
    self.resetVarButton.pressed.connect(self.resetCurVar)
    self.runCodeButton.pressed.connect(self.runCode)
    self.runCodeAction.triggered.connect(self.runCode)

    # The ouput tab widget
    self.output.currentChanged.connect(self.onTabChanged)
    self.varList.currentIndexChanged.connect(self.onCurrentVariableChanged)
    self.varList.editTextChanged.connect(self.onVarNameChanged)
    self.varSetter.returnPressed.connect(self.onVarValueChanged)
    self.setRelationButton.pressed.connect(self.onVarValueChanged)
    self.newRelationButton.pressed.connect(self.onNewRelationWanted)
    self.resetCodeButton.pressed.connect(self.resetCode)

    # self.exitButton.triggered.connect(lambda: exit(0))
    self.throwError.triggered.connect(self.updateEquation)
    self.plotButton.triggered.connect(self.plot)
    self.limitButton.triggered.connect(self.onLimitButtonPressed)
    self.dontSimplify.triggered.connect(self.updateEquation)
    self.prettySolution.triggered.connect(self.updateEquation)
    self.doEval.triggered.connect(self.updateEquation)
    self.resetButton.triggered.connect(self.resetEverything)
    self.previewSolution.triggered.connect(self.onPreviewSolution)
    self.previewCurVar.triggered.connect(self.onPreviewCurVar)
    self.implicitMult.triggered.connect(self.updateImplicitMult)
    self.makePiecewise.triggered.connect(self.doPiecewise)
    self.getContinuous.triggered.connect(self.onGetContinuous)
    self.getIntDiff.triggered.connect(self.onIntDiff)
    self.openNotes.triggered.connect(self.notes)


    # self.inputBox.returnPressed.connect(self.onInputAccepted)


def resetEverything(self):
    self.equationInput.setPlainText('')
    self.allVars = []
    self.eqVars = []
    self.resetOuput()
    # self.varList.setText('')
    self.varList.clear()
    self.varSetter.setText('')
    self.varInfoBox.setPlainText('')
    self.solutionPng.setPixmap(QPixmap())
    self.varPng.setPixmap(QPixmap())
    self.equationPng.setPixmap(QPixmap())
    self.updateEquation()
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
    self.updateVars()
    expr = self.expr

    if not self.dontSimplify.isChecked():
        try:
            expr = expr.doit()
        except Exception as err:
            debug(err, color=-1)


        # rels = []
        # for var in self.allVars:
        #     if var.valueChanged:
        #         rels += (var.)
        #         self.expr = self.expr.subs(var.symbol, var.value)

        # debug(self.expr, 'self.expr')
        # debug(self.relations, 'relations')
        # system = solve_rational_inequalities(self.relations + [self.expr])
        # debug(system, 'system')
        expr = expr.simplify()
        # try:
        #     expr = solveset(expr)
        #     debug('solving using solveset')
        # except ValueError:
        #     debug('solving using simplify')

    if self.doEval.isChecked():
        expr = expr.evalf()

    self.solvedExpr = expr


def isContinuousAt(self, x):
    # function f(x) is continuous at a point x=a if and only if:
    # f(a) is defined
    # lim(x→a, f(x)) exists
    # lim(x→a, f(x))=f(a)


    expr = self.solvedExpr
    expr.subs(self.currentVar.symbol, x)
    print(f'Result of f({x}) = {expr}')

    if not (self.solvedExpr):
        reason = 'Expression does not exist'
        cont = False
    # elif type(self.solvedExpr) is not Function:
    #     return False
    elif not expr:
        reason = f'expression is not defined at {x}'
        cont = False
    elif Limit(self.solvedExpr, self.currentVar.symbol, x, '-') != Limit(self.solvedExpr, self.currentVar.symbol, x, '+'):
        reason = f'limit at {x} does not exist'
        cont = False
    else:
        cont = True
        print(f"Expression is {'' if cont else 'not '}continuous at {x}" + (f':\n{reason}' if cont else ''))
    # return expr(x) == expr(a)


def getPixmap(self, expr):
    obj = BytesIO()
    preview(expr, output='png', viewer='BytesIO', outputbuffer=obj)
    return QPixmap(QImage.fromData(bytes(obj.getbuffer())))


def fixEquationString(self, eq:str):
    if self.implicitMult.isChecked():
        functionRegex = group(word()) + ifProceededBy(match('(') + stuff() + match(')'))
        eq = re.sub(functionRegex.str(), r"Function('\1')", eq)

    sides = re.split((match('=') + ifNotPrecededBy(anyOf('<>!='))).str(), eq)

    # We have more than 1 ' = ' in the equation
    if len(sides) > 2:
        raise SyntaxError("More than one '=' in the Equation")
    # thing = otherThing
    if len(sides) == 2:
        eq = f'Eq({sides[0]}, {sides[1]})'
        re.sub((match('=') + ifNotPrecededBy(anyOf('<>!='))).str(), '', sides[1])

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


def printToCodeOutput(self, *args, sep=' ', end='\n'):
    for i in ensureIterable(args):
        self.codeOutput.setPlainText(self.codeOutput.toPlainText() + str(i) + str(sep if sep != ensureIterable(args)[-1] else end))
    self.codeOutput.setPlainText(self.codeOutput.toPlainText() + str(end))
