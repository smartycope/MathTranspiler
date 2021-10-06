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


def notes(self):
    win = QLabel()
    with open(join(ROOT, 'assets/notes.txt'), 'r') as f:
        win.setText(f.read())
        # It doesn't work without this line, I have NO idea why.
        debug(DIR)
    win.show()


def onIntDiff(self):
    inputWindow = QDialog()
    uic.loadUi(join(ROOT, "ui/diffIntegral.ui"), inputWindow)

    def extractValues():
        self.updateIntDiff(inputWindow.doDiff.isChecked(),
                            inputWindow.var.text(),
                            inputWindow.addMainEquation.isChecked())

    inputWindow.accepted.connect(extractValues)
    inputWindow.show()


def onTabChanged(self):
    # Switch to the error tab, if there's an error, then switch back when there's not.
    if self.output.currentIndex() != self.errorTabIndex:
        self.lastTab = self.output.currentIndex()


def onCurrentVariableChanged(self, varIndex):
    if not self.blockVarList:
        self.updateVarValue()
        self.updateVarInfo()


def onVarNameChanged(self):
    # debug(showFunc=True)
    if self.currentVar:
        self.allVars[self.varIndex].name = self.varList.currentText()
    # self.updateVarInfo()
    self.updateSolution()
    self.updateCode()


# *Sets* the current variable value when enter is pressed
# @showLoading(_loadingBar)
def onVarValueChanged(self):
    # This is literally so I can have access to self
    # @showLoading(self.loader)
    def hack():
        try:
            val = parse_expr(self.varSetter.text(), transformations=self.trans)
            self.resetTab()
        except Exception as err:
            debug('Failed to parse var value!')
            self.error = err
        else:
            try:
                self.updateVars()
                if type(self.currentVar.symbol) in self.funcTypes + (Function,):
                    self.allVars[self.varIndex].value = Lambda(self.functionVar, val)
                else:
                    self.allVars[self.varIndex].value = val
                self.allVars[self.varIndex].valueChanged = True
                self.allVars[self.varIndex].relationship = self.relation.currentText()
                self.updateEquation()
                self.varPng.setPixmap(self.getPixmap(val))
            except Exception as err:
                self.error = err
    hack()


def onLimitButtonPressed(self):
    inputWindow = QDialog()
    uic.loadUi(join(ROOT, "ui/limitsInput.ui"), inputWindow)

    def extractValues():
        d = ''
        if inputWindow.usePlus.isChecked() and inputWindow.useMinus.isChecked():
            pass
        elif inputWindow.usePlus.isChecked():
            d = '+'
        elif inputWindow.useMinus.isChecked():
            d = '-'

        self.updateLimit(inputWindow.limitVar.text(),
                            inputWindow.limitVal.text(),
                            inputWindow.addMainEquation.isChecked(),
                            d)

    inputWindow.accepted.connect(extractValues)
    inputWindow.show()


def onNewRelationWanted(self):
    self.varCount += 1
    name = f'newVar{self.varCount}'
    self.varList.addItem(name)
    var = Variable(name)
    var.valueChanged = True
    var.value = EmptySet
    self.allVars.append(var)


def plot(self):
    try:
        plot(self.expr)
    except Exception as err:
        self.error = err


def doPiecewise(self):
    inputWindow = QDialog()
    uic.loadUi(join(ROOT, "ui/addPiecewise.ui"), inputWindow)
    inputWindow.table.setItem(0, 0, QTableWidgetItem(str(self.expr)))
    inputWindow.table.setItem(0, 1, QTableWidgetItem('True'))

    def extractValues():
        rels = []
        curRel = ()
        for row in range(inputWindow.table.rowCount()):
            for col in range(inputWindow.table.columnCount()):
                item = inputWindow.table.item(row, col)
                if item:
                    item = item.text()
                if item:
                    curRel += (parse_expr(item, transformations=self.trans), )
                    if col == 1:
                        rels.append(curRel)
                        curRel = ()
        # self.piecewise = rels

        # debug(tuple(rels), 'relations', color=3)
        self.updatePiecewise(rels, inputWindow.addMainEquation.isChecked())

    inputWindow.accepted.connect(extractValues)
    inputWindow.show()


def onGetContinuous(self):
    get = QLineEdit()
    def getInput():
        self.isContinuousAt(get.text())
        get.destroy()

    get.returnPressed.connect(getInput)
    get.show()


def onPreviewSolution(self):
    preview(self.solvedExpr, output='png')


def onPreviewCurVar(self):
    preview(solveset(self.expr, self.currentVar.symbol), output='png')


def resetCurVar(self):
    self.allVars[self.varIndex] = Variable(self.currentVar.symbol)
    self.varSetter.setText('')
    self.updateEquation()


def resetCode(self):
    self.codeOutput.setPlainText('')
    self.codePng.setPixmap(QPixmap())
    self.codeInput.setPlainText('')


def runCode(self):
    self.codeOutput.setPlainText('')
    code = self.codeInput.toPlainText()
    #* Set the locals (for convienence)
    expr = self.expr
    curVar = self.currentVar
    solution = self.solvedExpr
    if self.currentVar:
        curSymbol = curVar.symbol
        curValue = curVar.value
    else:
        curSymbol = None
        curValue = None
    print = self.printToCodeOutput
    show = lambda e: self.codePng.setPixmap(self.getPixmap(e))
    x, y = symbols('x y')
    out = None

    # def isContinuous(expr, x, symbol):
        # return (limit(func, symbol, x).is_real)
    # So then what about the question: Find the values of x that make f(x)=(x+1)/(x−5) continuous

    try:
        _local = locals()
        exec(code, globals(), _local)
        out = _local['out']
        if out is not None:
            print(out)
            show(out)
    except Exception as err:
        self.error = err
        self.codePng.setPixmap(QPixmap())
    else:
        self.error = None
