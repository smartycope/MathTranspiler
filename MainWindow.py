# This Python file uses the following encoding: utf-8
import re, math
from os.path import dirname, join

# from PyQt5 import *
from PyQt5 import QtCore, QtGui, QtMultimedia, QtWidgets, uic
from PyQt5.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt, QTimer, QByteArray
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget, QDialog
from PyQt5.QtSvg import QSvgWidget

# from PySide.QtXml import *
# from PySide.QtSvg import *

import sympy as sym
from sympy.parsing.sympy_parser import (parse_expr, standard_transformations,
                                        implicit_multiplication_application,
                                        implicit_multiplication, convert_xor)
from sympy.printing.pycode import pycode
from sympy.printing.latex import latex
from sympy.printing.mathml import mathml
from sympy.printing.mathematica import mathematica_code
from sympy import abc
from sympy.abc import *
from sympy import *

# from xml import sax
# from xml.sax.saxutils import XMLGenerator
# from svgmath.tools.saxtools import XMLGenerator, ContentFilter
# from svgmath.mathhandler import MathHandler, MathNS
# import libxml2

# import StringIO

import ziamath as zm


from Variable import Variable
from EasyRegex import EasyRegex as ere
from Cope import *

displayAllFiles(True)
displayAllFuncs(True)
displayAllLinks(True)

DIR = dirname(__file__)

_parsingDict = {}
for i in dir(abc):
    if i[0] != '_':
        _parsingDict[i] = abc.symbols(i)

# TODO Look into the sympy.Expr.rewrite function (or possibly the sympy.Function.rewrite function)
class Main(QMainWindow):
    varTypes = (sym.Symbol, sym.core.function.AppliedUndef) #, sym.WildFunction)
    errorTabIndex = 2
    defaultDir = '/home/marvin/Documents/College/Calculus/'
    fileExtensions = 'Text Files (*.txt)'
    latexExtensions = 'TeX Document (*.tex, *.latex)'
    mathmlFileExtensions = 'MathML Document (*.mathml, *.txt)'
    defaultExtension = ''
    defaultLatexExtension = ''
    defaultMathmlExtension = ''
    # self.trans = standard_transformations + (implicit_multiplication_application,)
    trans = standard_transformations + (convert_xor, implicit_multiplication_application)
    # self.trans = standard_transformations
    # self.trans = implicit_multiplication_application
    parsingDict = _parsingDict
    # inputTabIndex = 2

    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi(join(DIR, "main.ui"), self)
        self.setWindowTitle('Math Transpiler')
        self.setGeometry(0, 0, self.width(), self.height())

        self.inputAlertIcon = self.errorIcon = QIcon(DIR + "/red!.png")

        self.save.triggered.connect(self._save)
        self.saveAs.triggered.connect(self._saveAs)
        self.load.triggered.connect(self._load)
        self.exportLatex.triggered.connect(self.exportAsLatex)
        self.exportMathML.triggered.connect(self.exportAsMathML)
        self.exportMathmatica.triggered.connect(self.exportAsMathmatica)

        # The equation input box
        self.equationInput.textChanged.connect(self.onEquationChanged)

        # The ouput tab widget
        self.output.currentChanged.connect(self.onTabChanged)
        self.variableSelector.currentIndexChanged.connect(self.onCurrentVariableChanged)
        self.varNamer.returnPressed.connect(self.onVarNameChanged)
        self.varSetter.returnPressed.connect(self.onVarValueChanged)

        self.plotButton.triggered.connect(self.plot)
        self.limitButton.triggered.connect(self.onLimitButtonPressed)
        self.dontSimplify.triggered.connect(self.updateEquation)
        self.prettySolution.triggered.connect(self.updateEquation)
        self.doEval.triggered.connect(self.updateEquation)
        self.resetButton.triggered.connect(self.resetEverything)

        # self.inputBox.returnPressed.connect(self.onInputAccepted)

        self.lastTab = 0
        self.blockVariableSelector = False
        # The equation string value
        self.equ = ""

        self.lastSaveLoc = None

        # self.inputHistory = ""
        self.customInputReady = False

        self._vars = [] # An ordered list of Variables
        self._lexpr = None
        self._rexpr = None

        self.svgBox = QSvgWidget(self.svgBox)
        # self.widgetSvg.setGeometry(10, 10, 1080, 1080)

        # self.chessboardSvg = chess.svg.board(self.chessboard).encode("UTF-8")
        # self.widgetSvg.load(self.chessboardSvg)



# Getters, setters, and deleters
    @property
    def vars(self):
        return self._vars

    @vars.setter
    def vars(self, value):
        self._vars = value


    @property
    def lexpr(self):
        return self._lexpr

    @lexpr.setter
    def lexpr(self, value):
        self._lexpr = value


    @property
    def rexpr(self):
        return self._rexpr

    @rexpr.setter
    def rexpr(self, value):
        self._rexpr = value


    @property
    def varIndex(self):
        return self.variableSelector.currentIndex()

    @varIndex.setter
    def varIndex(self, value):
        self.variableSelector.setCurrentIndex(value)


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
    def varInfo(self):
        return self.varInfoBox.getPlainText()

    @varInfo.setter
    def varInfo(self, value):
        self.varInfoBox.setPlainText(value)


    @property
    def varName(self):
        return self.varNamer.text()

    @varName.setter
    def varName(self, value):
        self.varNamer.setText(value)


    @property
    def varValueBox(self):
        return self.varSetter.text()

    @varValueBox.setter
    def varValueBox(self, value):
        self.varSetter.setText(value)


    @property
    def outputCode(self):
        return self.codeBox.plainText()

    @outputCode.setter
    def outputCode(self, value):
        self.codeBox.setPlainText(value)


    @property
    def solution(self):
        return self.answerBox.plainText()

    @solution.setter
    def solution(self, value):
        self.answerBox.setPlainText(value)


    @property
    def error(self):
        return self.errorBox.plainText()

    @error.setter
    def error(self, err):
        self.errorBox.setPlainText(str(err))
        self.output.setTabIcon(self.errorTabIndex, self.errorIcon)

        if self.throwError.isChecked():
            raise err

        self.output.setCurrentIndex(self.errorTabIndex)


# Private
    def resetEverything(self):
        self.equationInput.setPlainText('')
        self.vars = []
        self.resetOuput()
        self.varName = ''
        self.varValueBox = ''
        self.variableSelector.clear()


    def resetTab(self):
        self.output.setCurrentIndex(self.lastTab)


    def resetIcon(self, tabIndex):
        self.output.setTabIcon(tabIndex, QIcon())


    def resetOuput(self):
        self.errorBox.setPlainText("")
        self.solution = ""
        self.outputCode = ""
        self.resetIcon(self.errorTabIndex)


    def genCodeFromExpr(self, expr):
        # return pycode(expr, fully_qualified_modules=False)
        return sym.python(expr)
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

        return s


    def getFullExpr(self):
        if '=' in self.equ:
            rtn = sym.Eq(self.lexpr, self.rexpr)
        else:
            rtn = self.lexpr
        # debug(self.parsingDict)
        # Update with constants
            # rtn = rtn.subs(self.parsingDict)
            # rtn = rtn.subs('e', abc.E)

        # debug(rtn)
        return rtn
        # return rtn.subs(self.parsingDict)


    def subVarNames(self, string):
        # Replace all the variables with their names
        for var in self.vars:
            string = re.sub(str(var.symbol), var.name, string)

        return string


    def getSubbedFullExpr(self):
        e = self.getFullExpr()
        for v in self.vars:
            if v.valueChanged:
                e = e.subs(v.symbol, v.value)
        debug(e)
        return e


    def addEqualsSign(self, string):
        regex = ere().match('.+-.+').ifPrecededBy('Eq(').ifProceededBy(ere(',').optional(ere().whitechunk()).add('0)')).debug().compile()
        match = re.search(regex, string)
        if match:
            return re.sub('-', '=', match.string)
        else:
            return string


    def rebalanceEqualsSign(self):
        regex = ere().match('.+-.+=').ifPrecededBy('Eq(').ifProceededBy(ere(',').optional(ere().whitechunk()).add('0)')).debug().compile()
        match = re.search(regex, string)
        if match:
            return re.sub('-', '=', match.string)
        else:
            return string


    def getAsLatex(self):
        # Simplify both sides of the equation
        if '=' in self.equ:
            # lside, rside = re.split(r'=', self.equ)
            try:
                ans = self.getFullExpr().doit()
            except:
                debug()
            else:
                ans = self.getFullExpr()

        else:
            ans = self.equ

        if not self.dontSimplify.isChecked():
            ans = sym.simplify(ans)

        ans = latex(ans)

        if self.useVarNamesInSolution.isChecked():
            ans = self.subVarNames(ans)

        return ans


    def getAsMathML(self):
        # Simplify both sides of the equation
        if '=' in self.equ:
            # lside, rside = re.split(r'=', self.equ)
            try:
                ans = self.getFullExpr().doit()
            except:
                debug()
            else:
                ans = self.getFullExpr()

        else:
            ans = self.equ

        if not self.dontSimplify.isChecked():
            ans = sym.simplify(ans)

        ans = mathml(ans)

        if self.useVarNamesInSolution.isChecked():
            ans = self.subVarNames(ans)

        return ans


    def getAsMathmatica(self):
        # Simplify both sides of the equation
        if '=' in self.equ:
            # lside, rside = re.split(r'=', self.equ)
            try:
                ans = self.getFullExpr().doit()
            except:
                debug()
            else:
                ans = self.getFullExpr()

        else:
            ans = self.equ

        if not self.dontSimplify.isChecked():
            ans = sym.simplify(ans)

        ans = mathematica_code(ans)

        if self.useVarNamesInSolution.isChecked():
            ans = self.subVarNames(ans)

        return ans


    def loadSVG(self, eq):
        self.svgBox.load(QByteArray(bytes(zm.Math.fromlatex(latex(e)).svg(), 'ascii')))


# Slots
    def onTabChanged(self):
        # Switch to the error tab, if there's an error, then switch back when there's not.
        if self.output.currentIndex() != self.errorTabIndex:
            self.lastTab = self.output.currentIndex()


    def onEquationChanged(self):
        self.updateEquation()


    def onCurrentVariableChanged(self, varIndex):
        if not self.blockVariableSelector:
            self.updateVarName()
            self.updateVarValue()
            self.updateVarInfo()


    def onVarNameChanged(self):
        self.currentVar.name = self.varName
        # self.updateVarInfo()
        self.updateSolution()
        self.updateCode()


    def onVarValueChanged(self):
        try:
            val = parse_expr(self.varValueBox, transformations=self.trans)
            self.resetTab()
        except Exception as err:
            debug('Failed to parse var value!')
            self.error = err
        else:
            # self.updateVarValue() # This updates the input box, which should already be up to date
            self.updateExprsAndVars()
            self.vars[self.varIndex].value = val
            self.vars[self.varIndex].valueChanged = True
            self.updateVarInfo()
            self.updateSolution()
            self.updateCode()

            # Twice, because why not?!
            # It makes it work, I do not know why.
            self.varValueBox = self.varValueBox
            # self.updateVarValue()
            # self.updateExprsAndVars()
            self.updateSolution()
            # self.updateCode()


    def onLimitButtonPressed(self):
        inputWindow = QDialog()
        uic.loadUi(join(DIR, "limitsInput.ui"), inputWindow)


        def extractValues():
            self.updateLimit(inputWindow.limitVar.text(), inputWindow.limitVal.text())

        inputWindow.accepted.connect(extractValues)
        inputWindow.show()


    def plot(self):
        if '=' in self.equ:
            sym.plotting.plot(self.lexpr)
        else:
            sym.plotting.plot(self.getFullExpr())


# Update Functions
    def updateEquation(self):
        self.resetOuput()

        # Get the equation
        self.equ = self.equationInput.toPlainText()

        # If we've just deleted everything, it's okay
        if not len(self.equ):
            return

        # Now calculate everything
        try:
            if self.equ.count('=') > 1:
                raise SyntaxError("More than 1 '=' in equation")

            self.updateExprsAndVars()

            self.updateSolution()
            self.updateCode()
            self.updateVarInfo()
            self.updateVarName()
            self.updateVarValue()
            self.resetTab()

        except Exception as err:
            self.error = err


    def updateVarName(self):
        if self.currentVar:
            self.varName = self.currentVar.name


    def updateVarInfo(self):
        if self.currentVar:
            self.varInfo = f'Type: {type(self.currentVar.value)}'


    def updateVarValue(self):
        if self.currentVar and self.currentVar.valueChanged:
            if self.prettySolution.isChecked():
                ans = sym.pretty(self.currentVar.value)
            else:
                ans = str(self.currentVar.value)

            self.varValueBox = ans
        else:
            if '=' in self.equ:
                if self.prettySolution.isChecked():
                    ans = sym.pretty(sym.solveset(self.getFullExpr(), self.currentVar.symbol))
                else:
                    ans = str(sym.solveset(self.getFullExpr(), self.currentVar.symbol))
            else:
                ans = 'Undefined'

            self.varValueBox = ans


    def _updateVars(self):
        # Update with constants
        # if self.lexpr:
        #     self.lexpr = self.lexpr.subs(self.parsingDict)
        #     self.lexpr = self.lexpr.subs('e', abc.E)
        # if self.rexpr:
        #     self.rexpr = self.rexpr.subs(self.parsingDict)
        #     self.lexpr = self.lexpr.subs('e', abc.E)

        atoms = set()
        if '=' in self.equ:
            atoms = self.lexpr.atoms(*self.varTypes).union(self.rexpr.atoms(*self.varTypes))
        else:
            if self.lexpr:
                atoms = self.lexpr.atoms(*self.varTypes)

        curSymbols = set([v.symbol for v in self.vars])

        # Get all the things in what we've just parse that aren't already in self.vars and add them
        for s in atoms.difference(curSymbols):
            self.vars.append(Variable(s))

        # Now get all the things in self.vars that aren't in the thing we just parsed and delete them
        if self.rememberVarNames.isChecked():
            for s in curSymbols.difference(atoms):
                del self.vars[getIndexWith(self.vars, lambda x: x.symbol == s)]

        # Make sure our expressions are updated with the new values
        for var in self.vars:
            if self.lexpr and var.valueChanged:
                self.lexpr = self.lexpr.subs(var.symbol, var.value)
            if self.rexpr and var.valueChanged:
                self.rexpr = self.rexpr.subs(var.symbol, var.value)


        # # Update with constants
        # if self.lexpr:
        #     # self.lexpr = self.lexpr.subs(self.parsingDict)
        #     self.lexpr = self.lexpr.subs('e', abc.E)
        # if self.rexpr:
        #     # self.rexpr = self.rexpr.subs(self.parsingDict)
        #     self.lexpr = self.lexpr.subs('e', abc.E)

        lastVarIndex = self.varIndex
        self.blockVariableSelector = True
        self.variableSelector.clear()
        self.variableSelector.addItems([str(v.symbol) for v in self.vars])
        self.varIndex = lastVarIndex
        self.blockVariableSelector = False


    def updateSolution(self):
        # Simplify both sides of the equation
        try:
            ans = self.getFullExpr().doit()
        except Exception as err:
            debug(err)
        else:
            ans = self.getFullExpr()

        if not self.dontSimplify.isChecked():
            # if type(ans) is str:
                # ans = sym.parse_expr(sym, transformations=self.trans)
            ans = ans.simplify() #, transformations=self.trans)

        if self.doEval.isChecked():
            ans = ans.evalf()

        if self.prettySolution.isChecked():
            ans = sym.pretty(ans, use_unicode=False)
            # ans = self.rebalanceEqualsSign(sym.pretty(ans, use_unicode=False))

        # ans = self.addEqualsSign(str(ans))
        ans = str(ans)

        if self.useVarNamesInSolution.isChecked():
            ans = self.subVarNames(ans)

        ans = re.sub(r'\t', '    ', ans)

        if self.printSolution.isChecked():
            print(ans)

        self.loadSVG(ans)

        self.solution = ans


    def updateCode(self):
        if '=' in self.equ:
            lside, rside = re.split(r'=', self.equ)
            self.outputCode = self.genCodeFromExpr(rside) + ' = ' + self.genCodeFromExpr(lside)
        else:
            self.outputCode = self.genCodeFromExpr(self.equ)


    def updateExprsAndVars(self):
        if r'limit(' in self.equ:
            equation = re.search(ere().anything().matchMax().ifPrecededBy(ere().match('limit(')).ifProceededBy(ere().match(',').anything().matchMax().match(',')).str(), self.equ).string
            self.lexpr = sym.parse_expr(equation, transformations=self.trans)
        elif '=' in self.equ:
            lside, rside = re.split(r'=', self.equ)
            self.lexpr = sym.parse_expr(rside, transformations=self.trans)
            self.rexpr = sym.parse_expr(lside, transformations=self.trans)
            # self.rexpr = sym.parse_expr(lside, transformations=self.trans).str()
            # self.rexpr = str(sym.parse_expr(lside, transformations=self.trans))
        else:
            self.lexpr = sym.parse_expr(self.equ, transformations=self.trans)

        self._updateVars()


    def updateLimit(self, updateVar, updateVal):
        withLimit = f'limit({self.equationInput.toPlainText()}, {updateVar}, {updateVal})'
        self.equationInput.setPlainText(withLimit)


# File functions
    def _saveAs(self):
        file = QFileDialog.getSaveFileName(directory=self.defaultDir, filter=self.fileExtensions, initialFilter=self.defaultExtension)[0]
        if len(file):
            with open(file, 'w') as f:
                f.write(self.equ)
            print('File Saved!')
            self.lastSaveLoc = file


    def exportAsLatex(self):
        file = QFileDialog.getSaveFileName(directory=self.defaultDir, filter=self.latexFileExtensions, initialFilter=self.defaultLatexExtension)[0]
        if len(file):
            with open(file, 'w') as f:
                f.write(self.getAsLatex())
            print('File Saved!')
            self.lastSaveLoc = file


    def exportAsMathML(self):
        file = QFileDialog.getSaveFileName(directory=self.defaultDir, filter=self.mathmlFileExtensions, initialFilter=self.defaultMathmlExtension)[0]
        if len(file):
            with open(file, 'w') as f:
                f.write(self.getAsMathML())
            print('File Saved!')
            self.lastSaveLoc = file


    def exportAsMathmatica(self):
        file = QFileDialog.getSaveFileName(directory=self.defaultDir, filter=self.fileExtensions, initialFilter=self.defaultExtension)[0]
        if len(file):
            with open(file, 'w') as f:
                f.write(self.getAsMathmatica())
            print('File Saved!')
            self.lastSaveLoc = file


    def _save(self):
        if self.lastSaveLoc:
            with open(self.lastSaveLoc, 'w') as f:
                f.write(self.equ)
            print('File Saved!')


    def _load(self):
        file = QFileDialog.getOpenFileName(directory=self.defaultDir, filter=self.fileExtensions, initialFilter=self.defaultExtension)[0]
        if len(file):
            with open(file, 'r') as f:
                self.equationInput.setPlainText(f.read())
                # self.updateEquation()
            self.lastSaveLoc = file
