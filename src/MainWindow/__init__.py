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

from sympy.core.numbers import One
# Hacking One so I don't have to make it a unit (cause I'm lazy)
One.name = 'one'
One.abbrev = '1'
One.scale_factor = 1

# Because Cope.ROOT stopped working and I use it to find ui files
ROOT = dirname(dirname(dirname(__file__)))

_quantityStrings = filter(lambda u: type(getattr(_units, u)) is Quantity, dir(_units))
_prefixStrings   = filter(lambda u: type(getattr(_units, u)) is Prefix,   dir(_units))

_quantities = list(set(map(lambda i: getattr(_units, i), _quantityStrings)))
_prefixes   = list(set(map(lambda i: getattr(_units, i), _prefixStrings)))

customUnits = [
    Quantity('m/s', abbrev='m/s', dimension=length/time, scale_factor=meter/second)
    # Quantity('m/s', abbrev='m/s', dimension=meters/second)
]

class Main(QMainWindow):
    from ._file import (_load, _save, _saveAs, exportAsLatex,
                        exportAsMathmatica, exportAsMathML)
    from ._private import (calculateSolution, sanatizeInput, sanatizeLatex,
                           fixEquationString, getIcon, setError, detectLatex,
                           printToCodeOutput, resetError, resetEverything,
                           resetIcon, resetOuput, resetTab, runCustomFuncInCode,
                           _convertLatex, sanatizeOutput, resetTheSolutionUnit,
                           initializeVariable)
    from ._slots import (doPiecewise, notes, onCurrentVariableChanged,
                         onIntDiff, onLimitButtonPressed, onResetVars,
                         onNewRelationWanted, onPreviewCurVar, #onUpdateVars,
                         onPreviewSolution, onTabChanged, onVarNameChanged,
                         onVarValueChanged, _plot, resetCode, resetCurVar,
                         runCode, connectEverything, onConvertLatex,
                         onVarTypeChanged, onGetSumPressed, doOpenTrigSolver,
                         onVarUnitChanged, onOpenUnitSolver)
    from ._update import (updateCode, updateEquation, updateImplicitMult,
                          updateIntDiff, updateLimit, updatePiecewise,
                          updateSolution, updateVarInfo, updateVars,
                          updateVarValue, updateSubbedExpr, updateSum)
                          #fillVarUnit) #changeVarUnit, updateUnitSystem)
    from ._customActions import (addCustomFuncs, addCommonEqus, addUnits, addConstants)

    varTypes = (Symbol, Derivative, Function, FunctionCall, Integral)
    varTypeMap = {0: Symbol, 1: Function, 2: Derivative, 3: Integral}
    funcTypes =  (AppliedUndef, UndefinedFunction) #, Function, WildFunction)
    functionVar = Symbol('x')
    allUnits    = [One()] + sorted(_quantities + customUnits, key=lambda i: str(i.name))
    allPrefixes = sorted([One()] + _prefixes, key=lambda i: i.scale_factor, reverse=True)
    # This line of code was *awesome*
    # allUnits    = [One()] + sorted(list(set(map(lambda i: getattr(_units, i), filter(lambda u: type(getattr(_units, u)) in Quantity, dir(_units))))), key=lambda i: str(i))
    # allPrefixes = [One()] + sorted(list(set(map(lambda i: getattr(_units, i), filter(lambda u: type(getattr(_units, u)) in Prefix,   dir(_units))))), key=lambda i: str(i))
    codeTabIndex = 1
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
    windowStartingPos = (3000, 0)
    sciNotSigFigs = 4

    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi(join(ROOT, "ui/main.ui"), self)
        self.setWindowTitle('Math Transpiler')
        self.setGeometry(*self.windowStartingPos, self.width(), self.height())
        self.setUpdatesEnabled(True)

        self.inputAlertIcon = self.errorIcon = QIcon(join(ROOT, "assets/red!.png"))
        if self.implicitMult.isChecked():
            self.trans += (implicit_multiplication,)


        # Construct dicts of string: Variable of things we want to have as defualt
        self.autofillUnits    =   dict(zip([str(i.name)   for i in self.allUnits], [Variable(i, value=1, unit=i, _type=Quantity) for i in self.allUnits]))
        self.autofillUnits.update(dict(zip([str(i.abbrev) for i in self.allUnits], [Variable(i, value=1, unit=i, _type=Quantity) for i in self.allUnits])))
        self.autofillPrefixes =      dict(zip([str(i.name)   for i in self.allPrefixes], [Variable(i, value=1, prefix=i, _type=Prefix) for i in self.allPrefixes]))
        self.autofillPrefixes.update(dict(zip([str(i.abbrev) for i in self.allPrefixes], [Variable(i, value=1, prefix=i, _type=Prefix) for i in self.allPrefixes])))
        self.autofillCustom = {
            'µ': Variable(micro, value=1, prefix=micro, _type=Prefix)
        }

        # Set the dropdown box completers (Based)
        self.unitBox.setCompleter(QCompleter([str(i.name) for i in self.allUnits]))
        self.solutionUnitBox.setCompleter(QCompleter([str(i.name) for i in self.allUnits]))
        self.prefixBox.setCompleter(QCompleter([str(i.name) for i in self.allPrefixes]))

        # Fill the dropdown boxes
        self.unitBox.addItems([str(i.name) for i in self.allUnits])
        self.solutionUnitBox.addItems([str(i.name) for i in self.allUnits])
        self.prefixBox.addItems([f"{i.name} ({i.abbrev})" for i in self.allPrefixes])

        # Set tooltips
        for cnt, prefix in enumerate(self.allPrefixes):
            self.prefixBox.setItemData(cnt, str(prefix.scale_factor), Qt.ItemDataRole.ToolTipRole)

        for cnt, unit in enumerate(self.allUnits):
            self.unitBox.setItemData(cnt, str(unit.abbrev), Qt.ItemDataRole.ToolTipRole)

        # One isn't at the top of the prefix box
        self.prefixBox.setCurrentIndex(self.prefixBox.findText('one (1)'))

        self._catagories = {}
        self._commonEquCatagories = {}
        self._unitCatagories = {}
        self._constantCatagories = {}

        self.blockVarUnitSignal = False

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
    def varIndex(self):
        return self.varList.currentIndex()

    @varIndex.setter
    def varIndex(self, value):
        self.varList.setCurrentIndex(value)

    @property
    def currentVar(self):
        try:
            return self.vars[self.varIndex]
        except IndexError:
            try:
                tmp = self.vars[0]
                self.varIndex = 0
                return tmp
            except IndexError:
                return None

    @currentVar.setter
    def currentVar(self, value):
        try:
            self.vars[self.varIndex] = value
        except IndexError:
            pass

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
