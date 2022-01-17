# This Python file uses the following encoding: utf-8
import math
import threading
from io import BytesIO
from os.path import dirname, join

import clipboard as clip
from Cope import *
from EasyRegex import *
import EasyRegex as er
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
from sympy.physics.units import *
from sympy.physics.units import convert_to
from sympy.physics.units.prefixes import Prefix
from sympy.core.numbers import One
# from sympy.solvers.inequalities import solve_rational_inequalities
from sympy.solvers.inequalities import *
from Variable import Variable
from copy import deepcopy
import re
from UnitSelector import UnitSelector


todo('all this stuff')
# todo('add an option to use solve or solveset', False)
# todo('add an option to automatically replace the logs in the solution with ln\'s', False)
# todo('add automatic latex detection', False)
# todo(r'automatically convert from \dfrac{} to \frac{} in latex', False)
todo('autofill derivative variable box', False)
todo('fix and finish implementing Type box', False)
todo('add a function (and/or variable) to detect whether self.equ/self.solution/self.expr is updated to the current equation, and add it to everything', False)
todo('add auto-uncondition or un-finiteset an answer with only one entry in sanatize solution/sanitize output', False)
todo('autoconvert to lambda (func and implicitly in varsetter) smartly, ie via a private function and get the atoms first instead of assuming x', False)
todo('auto sanatize == to Eq(), = to -, and -> to Lambda()', False)
todo('update the button box before the hard calculations so we can make sure its calculating the right thing and not something wrong that takes forever', False)
todo('multithread the hard parts eventually', False)
todo('make ctrl+R move the focus to the input box', False)
todo('make the math latex button bigger', False)
# todo sort the custom funcs into drop down groups

# todo('update code box tooltip', False)
# TODO Pre-parse the input equation for || and replace with Abs() (capitol!)
# TODO Removed use varnames in solution QAction


def resetEverything(self):
    self.equationInput.setPlainText('')
    self.vars = []
    self.eqVars = []
    self.resetOuput()
    # self.varList.setText('')
    self.varList.clear()
    self.varSetter.setText('')
    self.equation.update()
    self.onResetVars()
    self.varPng.setIcon(QIcon())
    self.solutionPng.setIcon(QIcon())
    self.equationPng.setIcon(QIcon())
    self.codePng.setIcon(QIcon())
    self.loading = False
    self.codeLoading = False
    self.unitBox.setCurrentIndex(self.unitBox.findText('one'))
    self.prefixBox.setCurrentIndex(self.prefixBox.findText('one (1)'))
    # self.codeInput.setPlainText('')


def resetTab(self):
    self.output.setCurrentIndex(self.lastTab)


def resetIcon(self, tabIndex):
    self.output.setTabIcon(tabIndex, QIcon())


def resetTheSolutionUnit(self):
    self.solutionUnitSelector.reset()
    self.equation.update()


def resetOuput(self):
    self.answerBox.setPlainText('')
    self.codeOutput.setPlainText('')
    self.resetError()


def printToCodeOutput(self, *args, sep=' ', end='\n'):
    for i in ensureIterable(args):
        self.codeOutput.setPlainText(self.codeOutput.toPlainText() + str(i) + str(sep if sep != ensureIterable(args)[-1] else end))
    self.codeOutput.setPlainText(self.codeOutput.toPlainText() + str(end))


def runCustomFuncInCode(self, funcString, *comments):
    if self.equ != self.equationInput.toPlainText():
        self.equation.update()
    self.codeInput.setPlainText(('# ' + ('\n# '.join(comments)) + '\n' if len(comments) else '') + funcString)
    self.runCodeButton.pressed.emit()
    self.output.setCurrentIndex(self.codeTabIndex)
