# This Python file uses the following encoding: utf-8
import re
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
from sympy.physics.units import *
import sympy.physics.units as units
from sympy.physics.units import Quantity
from sympy.physics.units.prefixes import Prefix
from Variable import Variable

from ._customFuncs import *
from trigAutoSolver import TriangleSolver
from EquationSearch import EquationSearch
ROOT = join(dirname(__file__), '../../')

def connectEverything(self):
    #* File Connections
    self.save.triggered.connect(self._save)
    self.saveAs.triggered.connect(self._saveAs)
    self.load.triggered.connect(self._load)
    self.exportLatex.triggered.connect(self.exportAsLatex)
    self.exportMathML.triggered.connect(self.exportAsMathML)
    self.exportMathmatica.triggered.connect(self.exportAsMathmatica)

    #* Copy Actions
    self.copyLatex.triggered.connect(lambda: clip.copy(latex(self.equation.solvedExpr)))
    self.copyMathML.triggered.connect(lambda: clip.copy(mathml(self.equation.solvedExpr)))
    self.copyMathmatica.triggered.connect(lambda: clip.copy(mathematica_code(self.equation.solvedExpr)))
    self.copySolution.triggered.connect(lambda: clip.copy(str(self.equation.solvedExpr)))
    self.copyEquation.triggered.connect(lambda: clip.copy(self.equation.string))
    # self.copyCurVar.triggered.connect(lambda: clip.copy(self.varValueBox))
    self.copyCurVar.triggered.connect(lambda: clip.copy(todo('figure out current var copy to clipboard')))

    #* UI Buttons
    self.solveButton.clicked.connect(self.equation.update)
    self.solveButton2.triggered.connect(self.equation.update)
    self.runCodeButton.pressed.connect(self.runCode)
    self.runCodeAction.triggered.connect(self.runCode)
    self.resetCodeButton.pressed.connect(self.resetCode)

    #* Input widget connections
    self.output.currentChanged.connect(self.onTabChanged)
    self.solutionUnitSelector.prefixIndexChanged.connect(self.equation.update)
    # QCompleter is the best!

    #* Actions
    self.throwError.triggered.connect(self.equation.update)
    self.doExpand.triggered.connect(self.equation.update)
    self.useSolve.triggered.connect(self.equation.update)
    self.plotButton.triggered.connect(self._plot)
    self.limitButton.triggered.connect(self.onLimitButtonPressed)
    self.getSum.triggered.connect(self.onGetSumPressed)
    self.dontSimplify.triggered.connect(self.equation.update)
    self.prettySolution.triggered.connect(self.equation.update)
    self.useSciNot.triggered.connect(self.equation.update)
    self.doEval.triggered.connect(self.equation.update)
    self.resetButton.triggered.connect(self.resetEverything)
    self.previewSolution.triggered.connect(self.onPreviewSolution)
    self.previewCurVar.triggered.connect(self.onPreviewCurVar)
    self.implicitMult.triggered.connect(self.updateImplicitMult)
    self.makePiecewise.triggered.connect(self.doPiecewise)
    # self.getContinuous.triggered.connect(self.onGetContinuous)
    self.getIntDiff.triggered.connect(self.onIntDiff)
    self.openUnitSolver.triggered.connect(self.onOpenUnitSolver)
    self.openNotes.triggered.connect(self.notes)
    self.convertLatex.triggered.connect(self.onConvertLatex)
    self.convertVarLatex.triggered.connect(lambda: self.onConvertLatex(True))
    self.openTrigSolver.triggered.connect(self.doOpenTrigSolver)
    self.resetVars.triggered.connect(self.varHandler.reset)
    self.resetSolutionUnit.triggered.connect(self.resetTheSolutionUnit)
    self.autoParseUnits.triggered.connect(self.updateAutoParseUnits)
    self.openSearchForEquation.triggered.connect(self.searchForEquation)
    self.solveCurVar.triggered.connect(self.varHandler.solveVar)
    # self.actionDimentionless.triggered.connect(lambda: self.updateUnitSystem("Dimentionless"))
    # self.actionPhysics.triggered.connect(lambda: self.updateUnitSystem("Physics"))
    # self.actionAstrophysics.triggered.connect(lambda: self.updateUnitSystem("Astrophysics"))
    # self.actionElectronics.triggered.connect(lambda: self.updateUnitSystem("Electronics"))
    # self.updateVars.triggered.connect(self.onUpdateVars)


def onPreviewCurVar(self):
    preview(solveset(self.equation.subbedExpr, self.varHandler.currentVar.symbol), output='png')


def notes(self):
    win = QLabel()
    with open(join(ROOT, 'assets/notes.txt'), 'r') as f:
        win.setText(f.read())
        # It doesn't work without this line, I have NO idea why.
        debug(DIR)
    win.show()


def onIntDiff(self):
    if self.equ != self.equationInput.toPlainText():
        self.equation.update()
    inputWindow = QDialog()
    uic.loadUi(join(ROOT, "ui/diffIntegral.ui"), inputWindow)
    inputWindow.label_4.hide()
    inputWindow.label_5.hide()
    inputWindow.lowerBound.hide()
    inputWindow.upperBound.hide()

    def extractValues():
        self.updateIntDiff(inputWindow.doDiff.isChecked(),
                           inputWindow.var.text(),
                           inputWindow.addMainEquation.isChecked(),
                           inputWindow.order.value(),
                           inputWindow.upperBound.text(),
                           inputWindow.lowerBound.text())

    inputWindow.accepted.connect(extractValues)
    inputWindow.show()


def onTabChanged(self):
    # Switch to the error tab, if there's an error, then switch back when there's not.
    if self.output.currentIndex() != self.errorHandler.errorTabIndex:
        self.lastTab = self.output.currentIndex()


def onLimitButtonPressed(self):
    if self.equ != self.equationInput.toPlainText():
        self.equation.update()
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


def onGetSumPressed(self):
    if self.equ != self.equationInput.toPlainText():
        self.equation.update()
    inputWindow = QDialog()
    uic.loadUi(join(ROOT, "ui/sumInput.ui"), inputWindow)

    def extractValues():
        self.updateSum(inputWindow.count.text(),
                       inputWindow.var.text(),
                       inputWindow.val.text(),
                       inputWindow.addMainEquation.isChecked())

    inputWindow.accepted.connect(extractValues)
    inputWindow.show()


def _plot(self):
    try:
        plot(self.expr)
    except Exception as err:
        self.setError(err, "Plotter")
    else:
        self.resetError()


def doPiecewise(self):
    if self.equ != self.equationInput.toPlainText():
        self.equation.update()
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


def doOpenTrigSolver(self):
    TriangleSolver(self)


def searchForEquation(self):
    if self.equ != self.equationInput.toPlainText():
        self.equation.update()
    search = EquationSearch(self.updateEquationSearch, transformations=self.trans)
    search.show()


def onOpenUnitSolver(self):
    pass


def onPreviewSolution(self):
    preview(self.solvedExpr, output='png')


def onConvertLatex(self, var=False):
    self.loading = True
    try:
        latex = self._convertLatex(self.varSetter.text() if var else self.equationInput.toPlainText())
        if var:
            self.varSetter.setText(latex)
            self.onVarValueChanged()
        else:
            self.equationInput.setPlainText(latex)
    except Exception as err:
        self.setError(err, "Latex Parser")
    else:
        self.resetError()
    self.equation.update()
    self.loading = False


def resetCode(self):
    self.codeExpr.reset()
    self.codeInput.setPlainText('')
    self.errorHandler.resetError()


def runCode(self):
    self.codeLoading = True
    self.codeOutput.setPlainText('')
    code = self.codeInput.toPlainText()

    #* Set the locals (for convienence)
    expr       = self.expr if type(self.expr) is not Lambda else self.expr.expr
    try:
        func   = self.expr if type(self.expr) is Lambda else Lambda(Symbol('x'), self.expr)
    except Exception as err:
        self.errorHandler.setError(err, 'Making the Current expression into a lambda')
        return
    else:
        self.errorHandler.resetError()

    def show(e):
        self.codeExpr.updateIcon(e)

    subbedExpr = subExpr = sub = self.equation.subbedExpr
    curVar     = self.varHandler.currentVar
    solution   = sol = self.equation.solvedExpr
    input      = lambda *_: None
    print      = self.printToCodeOutput
    out        = None
    # pi         = sym.pi
    if self.varHandler.currentVar:
        curSymbol = curVar.symbol
        curValue = curVar.value
    else:
        curSymbol = None
        curValue = None
    curVal = curValue

    vars = dict(zip([i.name for i in self.vars], [i.value for i in self.vars]))
    for i in self.vars:
        locals()[i.name] = i.symbol
        locals()[i.name + 'Val'] = i.value

    try:
        _local = locals()
        _local.update(vars)

        exec(code, globals(), _local)

        out = _local['out']
        if out is not None:
            print(out)
            # print()
            # print(latex(out))
            show(out)
    except Exception as err:
        self.errorHandler.setError(err, "Custom Code")
        self.codeExpr.reset()
    else:
        self.errorHandler.resetError()

    self.codeLoading = False


def updateAutoParseUnits(self):
    Variable.autoParseUnits = self.autoParseUnits.isChecked()