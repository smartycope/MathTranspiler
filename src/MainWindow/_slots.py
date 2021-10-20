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
from Variable import Variable

from ._customFuncs import *


def connectEverything(self):
    #* File Connections
    self.save.triggered.connect(self._save)
    self.saveAs.triggered.connect(self._saveAs)
    self.load.triggered.connect(self._load)
    self.exportLatex.triggered.connect(self.exportAsLatex)
    self.exportMathML.triggered.connect(self.exportAsMathML)
    self.exportMathmatica.triggered.connect(self.exportAsMathmatica)

    #* Copy Actions
    self.copyLatex.triggered.connect(lambda: clip.copy(latex(self.solvedExpr)))
    self.copyMathML.triggered.connect(lambda: clip.copy(mathml(self.solvedExpr)))
    self.copyMathmatica.triggered.connect(lambda: clip.copy(mathematica_code(self.solvedExpr)))
    self.copySolution.triggered.connect(lambda: clip.copy(str(self.solvedExpr)))
    self.copyEquation.triggered.connect(lambda: clip.copy(self.equ))
    # self.copyCurVar.triggered.connect(lambda: clip.copy(self.varValueBox))
    self.copyCurVar.triggered.connect(lambda: clip.copy(todo('figure out current var copy to clipboard')))

    #* UI Buttons
    self.solveButton.clicked.connect(self.updateEquation)
    self.solveButton2.triggered.connect(self.updateEquation)
    self.resetVarButton.pressed.connect(self.resetCurVar)
    self.runCodeButton.pressed.connect(self.runCode)
    self.runCodeAction.triggered.connect(self.runCode)
    self.setRelationButton.pressed.connect(self.onVarValueChanged)
    self.newRelationButton.pressed.connect(self.onNewRelationWanted)
    self.resetCodeButton.pressed.connect(self.resetCode)

    #* Input widget connections
    self.output.currentChanged.connect(self.onTabChanged)
    self.varList.currentIndexChanged.connect(self.onCurrentVariableChanged)
    self.varList.editTextChanged.connect(self.onVarNameChanged)
    self.varSetter.returnPressed.connect(self.onVarValueChanged)
    self.varType.currentIndexChanged.connect(self.onVarTypeChanged)

    #* Actions
    self.throwError.triggered.connect(self.updateEquation)
    self.plotButton.triggered.connect(self._plot)
    self.limitButton.triggered.connect(self.onLimitButtonPressed)
    self.dontSimplify.triggered.connect(self.updateEquation)
    self.prettySolution.triggered.connect(self.updateEquation)
    self.doEval.triggered.connect(self.updateEquation)
    self.resetButton.triggered.connect(self.resetEverything)
    self.previewSolution.triggered.connect(self.onPreviewSolution)
    self.previewCurVar.triggered.connect(self.onPreviewCurVar)
    self.implicitMult.triggered.connect(self.updateImplicitMult)
    self.makePiecewise.triggered.connect(self.doPiecewise)
    # self.getContinuous.triggered.connect(self.onGetContinuous)
    self.getIntDiff.triggered.connect(self.onIntDiff)
    self.openNotes.triggered.connect(self.notes)
    self.convertLatex.triggered.connect(self.onConvertLatex)
    self.convertVarLatex.triggered.connect(lambda: self.onConvertLatex(True))
    self.resetVars.triggered.connect(self.onResetVars)
    # self.updateVars.triggered.connect(self.onUpdateVars)

    #* All the latex buttons
    self.equationPng.pressed.connect(lambda: clip.copy(latex(self.expr)))
    self.solutionPng.pressed.connect(lambda: clip.copy(latex(self.solvedExpr)))
    self.varPng.pressed.connect(lambda: clip.copy(latex(self.currentVar.value if self.currentVar is not None else '')))


def notes(self):
    win = QLabel()
    with open(join(ROOT, 'assets/notes.txt'), 'r') as f:
        win.setText(f.read())
        # It doesn't work without this line, I have NO idea why.
        debug(DIR)
    win.show()


def onIntDiff(self):
    if self.equ != self.equationInput.toPlainText():
        self.updateEquation()
    inputWindow = QDialog()
    uic.loadUi(join(ROOT, "ui/diffIntegral.ui"), inputWindow)

    def extractValues():
        self.updateIntDiff(inputWindow.doDiff.isChecked(),
                           inputWindow.var.text(),
                           inputWindow.addMainEquation.isChecked(),
                           inputWindow.order.value())

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
    if self.currentVar and not self.blockVarList:
        self.vars[self.varIndex].name = self.varList.currentText()
    # self.updateVarInfo()
    self.updateSolution()
    self.updateCode()


# *Sets* the current variable value when enter is pressed
def onVarValueChanged(self):
    try:
        val = parse_expr(self.varSetter.text(), transformations=self.trans)
    except Exception as err:
        debug('Failed to parse var value!')
        self.setError(err, "Varaible Parser")
    else:
        try:
            self.updateVars()
            if type(self.currentVar.symbol) in self.funcTypes + (Function,):
                self.vars[self.varIndex].value = Lambda(self.functionVar, val)
            else:
                self.vars[self.varIndex].value = val
            self.vars[self.varIndex].valueChanged = True
            self.vars[self.varIndex].relationship = self.relation.currentText()
            self.updateEquation()
            self.varPng.setIcon(self.getIcon(val))
        except Exception as err:
            self.setError(err, "Setting Varaible")
        else:
            self.resetError()


def onVarTypeChanged(self, index):
    self.vars[self.varIndex].type = self.varTypeMap[index]


def onLimitButtonPressed(self):
    if self.equ != self.equationInput.toPlainText():
        self.updateEquation()
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
    self.vars.append(var)


def _plot(self):
    try:
        plot(self.expr)
    except Exception as err:
        self.setError(err, "Plotting")
    else:
        self.resetError()


def doPiecewise(self):
    if self.equ != self.equationInput.toPlainText():
        self.updateEquation()
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


def onPreviewSolution(self):
    preview(self.solvedExpr, output='png')


def onPreviewCurVar(self):
    preview(solveset(self.subbedExpr, self.currentVar.symbol), output='png')


def resetCurVar(self):
    self.vars[self.varIndex] = Variable(self.currentVar.symbol)
    self.varSetter.setText('')
    self.updateEquation()


def onResetVars(self):
    self.vars = []
    # self.updateVars()
    self.varSetter.setText('Undefined')
    self.updateEquation()


def onConvertLatex(self, var=False):
    self.loading = True
    try:
        if var:
            self.varSetter.setText(str(parse_latex(self.sanatizeLatex(self.varSetter.text()))))
            self.onVarValueChanged()
        else:
            self.equationInput.setPlainText(str(parse_latex(self.sanatizeLatex(self.equationInput.toPlainText()))))
    except Exception as err:
        self.setError(err, "Latex Parser")
    else:
        self.resetError()
    self.updateEquation()
    self.loading = False


def resetCode(self):
    self.codeOutput.setPlainText('')
    self.codePng.setIcon(QIcon())
    self.codeInput.setPlainText('')
    self.resetError()


def runCode(self):
    self.codeLoading = True
    self.codeOutput.setPlainText('')
    code = self.codeInput.toPlainText()

    #* Set the locals (for convienence)
    expr       = self.expr if type(self.expr) is not Lambda else self.expr.expr
    try:
        func   = self.expr if type(self.expr) is Lambda else Lambda(Symbol('x'), self.expr)
    except Exception as err:
        self.setError(err, 'Making the Current expression into a lambda')
        return
    else:
        self.resetError()

    subbedExpr = self.subbedExpr
    subExpr    = subbedExpr
    sub        = subbedExpr
    curVar     = self.currentVar
    solution   = self.solvedExpr
    sol        = solution
    input      = lambda *_: None
    print      = self.printToCodeOutput
    show       = lambda e: self.codePng.setIcon(self.getIcon(e))
    out        = None
    # pi         = sym.pi
    if self.currentVar:
        curSymbol = curVar.symbol
        curValue = curVar.value
    else:
        curSymbol = None
        curValue = None
    curVal = curValue

    vars = dict(zip([i.name for i in self.vars], [i.value for i in self.vars]))

    try:
        _local = locals()
        _local.update(vars)

        exec(code, globals(), _local)

        out = _local['out']
        if out is not None:
            self.codePng.pressed.connect(lambda: clip.copy(latex(out)))
            print(out)
            # print()
            # print(latex(out))
            show(out)
    except Exception as err:
        self.setError(err, "Custom Code")
        self.codePng.setIcon(QIcon())
    else:
        self.resetError()

    self.codeLoading = False
