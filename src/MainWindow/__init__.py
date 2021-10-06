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


# TODO Pre-parse the input equation for || and replace with Abs() (capitol!)
# TODO Removed use varnames in solution QAction
class Main(QMainWindow):
    from ._file import (_load, _save, _saveAs, exportAsLatex,
                        exportAsMathmatica, exportAsMathML)
    from ._private import (calculateSolution, connectEverything,
                           fixEquationString, getPixmap, isContinuousAt,
                           printToCodeOutput, resetError, resetEverything,
                           resetIcon, resetOuput, resetTab)
    from ._slots import (doPiecewise, notes, onCurrentVariableChanged,
                         onGetContinuous, onIntDiff, onLimitButtonPressed,
                         onNewRelationWanted, onPreviewCurVar,
                         onPreviewSolution, onTabChanged, onVarNameChanged,
                         onVarValueChanged, plot, resetCode, resetCurVar,
                         runCode)
    from ._update import (updateCode, updateEquation, updateImplicitMult,
                          updateIntDiff, updateLimit, updatePiecewise,
                          updateSolution, updateVarInfo, updateVars,
                          updateVarValue)
    varTypes = (Symbol, )
    funcTypes =  (AppliedUndef, UndefinedFunction) #, Function, WildFunction)
    functionVar = Symbol('x')
    errorTabIndex = 2
    defaultDir = join(ROOT, 'Equations')
    fileExtensions = 'Text Files (*.txt)'
    latexFileExtensions = 'TeX Document (*.tex, *.latex)'
    mathmlFileExtensions = 'MathML Document (*.mathml, *.txt)'
    defaultExtension = ''
    defaultLatexExtension = ''
    defaultMathmlExtension = ''
    baseTrans = standard_transformations + (convert_xor, lambda_notation)
    trans = baseTrans
    varCount = 0
    windowStartingPos = (1000, 0)

    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi(join(ROOT, "ui/main.ui"), self)
        self.setWindowTitle('Math Transpiler')
        self.setGeometry(*self.windowStartingPos, self.width(), self.height())

        self.inputAlertIcon = self.errorIcon = QIcon(join(ROOT, "assets/red!.png"))
        if self.implicitMult.isChecked():
            self.trans += (implicit_multiplication,)

        self.connectEverything()

        self.lastTab = 0
        self.blockVarList = False
        # The equation string value
        self.equ = ""

        self.lastSaveLoc = None

        # self.inputHistory = ""
        self.customInputReady = False

        # A list of just the Variables in the equation
        self.eqVars = []
        # An ordered list of all the Variables in the combobox
        self.allVars = []
        self.expr = EmptySet
        self.solvedExpr = EmptySet

        # The list of relations to feed to the solver
        self.relations = []

        self._hack = True

        # self.pngBox = QSvgWidget(self.svgBox)


    @property
    def varIndex(self):
        return self.varList.currentIndex()

    @varIndex.setter
    def varIndex(self, value):
        self.varList.setCurrentIndex(value)

    @property
    def currentVar(self):
        try:
            return self.allVars[self.varIndex]
        except IndexError:
            try:
                tmp = self.allVars[0]
                self.varIndex = 0
                return tmp
            except IndexError:
                return None

    @currentVar.setter
    def currentVar(self, value):
        try:
            self.allVars[self.varIndex] = value
        except IndexError:
            pass

    @property
    def error(self):
        return self.errorBox.plainText()

    @error.setter
    def error(self, err):
        if err is None:
            self.resetError()
        else:
            self.errorBox.setPlainText(str(err))
            self.output.setTabIcon(self.errorTabIndex, self.errorIcon)

            if self.throwError.isChecked():
                raise err

            self.output.setCurrentIndex(self.errorTabIndex)
