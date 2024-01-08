# This Python file uses the following encoding: utf-8
import math
import re
import threading
from io import BytesIO
from os.path import dirname, join

import clipboard as clip
# from Cope import *
from ezregex import *
from LoadingBar import LoadingBar, showLoading, showWithLoading
from PyQt5 import uic
from PyQt5.QtCore import (QByteArray, QEvent, QFile, QLine, QLineF, QRect,
                          QRectF, Qt, QThread, QTimer)
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (QDialog, QFileDialog, QLabel, QLineEdit,
                             QMainWindow, QTableWidgetItem, QWidget, QCompleter)
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
from sympy.physics.units import *
import sympy.physics.units as _units
# from sympy.physics.units import Quantity
from sympy.physics.units.prefixes import Prefix
# from sympy.plotting import plot
# from sympy.printing.latex import latex
# from sympy.printing.mathematica import mathematica_code
# from sympy.printing.mathml import mathml
# from sympy.printing.preview import preview
# from sympy.printing.pycode import pycode
# from sympy.sets.conditionset import ConditionSet
# from sympy.solvers.inequalities import solve_rational_inequalities
from Variable import Variable
from UnitSelector import UnitSelector
from Equation import Equation
from VarHandler import VarHandler
from ErrorHandler import ErrorHandler
from Expression import Expression

from sympy.core.numbers import One
# Hacking One so I don't have to make it a unit (cause I'm lazy)
One.name = 'one'
One.abbrev = '1'
One.scale_factor = 1

# Because Cope.ROOT stopped working and I use it to find ui files
ROOT = dirname(dirname(dirname(__file__)))
# hideAllTodos(True)

class Main(QMainWindow):
    from ._file import (_load, _save, _saveAs, exportAsLatex,
                        exportAsMathmatica, exportAsMathML)
    from ._private import (printToCodeOutput,  resetEverything,
                           resetIcon, resetTab, runCustomFuncInCode,
                           resetTheSolutionUnit)
    from ._slots import (doPiecewise, notes, onPreviewCurVar,
                         onIntDiff, onLimitButtonPressed, searchForEquation,
                         onPreviewSolution, onTabChanged, updateAutoParseUnits,
                         _plot, resetCode, runCode, connectEverything, onConvertLatex,
                         onGetSumPressed, doOpenTrigSolver, onOpenUnitSolver)
    from ._update import (updateCode, updateImplicitMult, updateEquationSearch,
                          updateIntDiff, updateLimit, updatePiecewise, updateSum)
    from ._customActions import (addCustomFuncs, addCommonEqus, addUnits, addConstants)

    baseTrans = standard_transformations + (convert_xor, lambda_notation)
    trans = baseTrans
    functionVar = Symbol('x')
    codeTabIndex = 1
    defaultDir = join(ROOT, 'Equations')
    fileExtensions = 'Text Files (*.txt)'
    latexFileExtensions = 'TeX Document (*.tex, *.latex)'
    mathmlFileExtensions = 'MathML Document (*.mathml, *.txt)'
    defaultExtension = ''
    defaultLatexExtension = ''
    defaultMathmlExtension = ''
    varCount = 0
    windowStartingPos = (3000, 0)

    # todo('reset isnt resetting the variables (and is throwing an error')
    # todo('also the reset vars button doesnt work')
    # todo('add a setting that optionally solves for the current variable to make switching between vars faster')
    # todo('make the var value box have undefined as a placeholder text instead of actual text')
    # #// todo('latex parsing is broken')
    # todo('get vars from vars is running all the time, and when it does run, it doesnt substitute the values correctly (at all)')

    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi(join(ROOT, "ui/main.ui"), self)
        self.setWindowTitle('Math Transpiler')
        self.setGeometry(*self.windowStartingPos, self.width(), self.height())
        self.setUpdatesEnabled(True)

        if self.implicitMult.isChecked():
            self.trans += (implicit_multiplication,)

        self._catagories = {}
        self._commonEquCatagories = {}
        self._unitCatagories = {}
        self._constantCatagories = {}

        self.blockVarUnitSignal = False

        # Make sure this is initially set up (it's updated, not called as needed)
        Variable.autoParseUnits = self.autoParseUnits.isChecked()

        # Set up the utility classes
        self.errorHandler = ErrorHandler(self, self.implicitMulLabel)
        self.varExpr = Expression(self.varSetter, self.varPng)
        self.solutionExpr = Expression(self.answerBox, self.solutionPng)
        self.codeExpr = Expression(self.codeOutput, self.codePng)
        self.equation = Equation(self, self.errorHandler, self.equationInput, self.equationPng, self.solutionExpr, self.runCodeButton)
        self.varHandler = VarHandler(self, self.equation, self.errorHandler, self.varList, self.varType, self.varExpr, self.varUnitSelector, self.varOrderSetter,
                                     self.newRelationButton, self.setRelationButton, self.resetVarButton, self.relation)

        self.connectEverything()
        self.addCustomFuncs()
        self.addCommonEqus()
        self.addUnits()
        self.addConstants()

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
        self.vars = []
        self.expr = EmptySet
        self.solvedExpr = EmptySet
        self.subbedExpr = EmptySet

        # The list of relations to feed to the solver
        self.relations = []

        self._hack = True
        self._loading = False
        self._codeLoading = False

        # self.pngBox = QSvgWidget(self.svgBox)

    @property
    def loading(self):
        return self._loading

    @loading.setter
    def loading(self, startLoading):
        if self._loading == startLoading:
            return
        else:
            self._loading = startLoading
            if startLoading:
                self.equationPng.setIcon(QIcon())
                self.solutionPng.setIcon(QIcon())
                self.equationPng.setText('Loading...')
                self.solutionPng.setText('Loading...')
                self.equationPng.repaint()
                self.solutionPng.repaint()
                # self.update()
                # self.repaint()
            else:
                self.equationPng.setText('')
                self.solutionPng.setText('')

    @property
    def codeLoading(self):
        return self._codeLoading

    @codeLoading.setter
    def codeLoading(self, startLoading):
        if self._codeLoading == startLoading:
            return
        else:
            self._codeLoading = startLoading
            if startLoading:
                self.codePng.setIcon(QIcon())
                self.codePng.setText('Loading...')
                self.codePng.repaint()
                # self.update()
                # self.repaint()
            else:
                self.codePng.setText('')
