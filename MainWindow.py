# This Python file uses the following encoding: utf-8
import re, math
from os.path import dirname, join
import clipboard as clip
from LoadingBar import LoadingBar
# from PyQt5 import *
from PyQt5 import QtCore, QtGui, QtMultimedia, QtWidgets, uic
from PyQt5.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt, QTimer, QByteArray
from PyQt5.QtGui import QIcon, QPixmap, QImage
# from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget, QDialog, QLabel
# from PyQt5.QtSvg import QSvgWidget

# from PySide.QtXml import *
# from PySide.QtSvg import *

# import sympy as sym
from sympy.parsing.sympy_parser import (parse_expr, standard_transformations,
                                        implicit_multiplication_application,
                                        implicit_multiplication, convert_xor)
from sympy.printing.pycode import pycode
from sympy.printing.latex import latex
from sympy.parsing.latex import parse_latex
from sympy.printing.mathml import mathml
from sympy.printing.preview import preview
from sympy.printing.mathematica import mathematica_code
from sympy.solvers.inequalities import solve_rational_inequalities
from sympy.sets.conditionset import ConditionSet
from sympy.core.function import AppliedUndef
from sympy.plotting import plot
from sympy import abc
from sympy.abc import *
from sympy import *

from io import BytesIO

from Variable import Variable
from EasyRegex import *
from Cope import *

displayAllFiles(True)
displayAllFuncs(True)
displayAllLinks(True)

DIR = dirname(__file__)


# TODO Look into the sympy.Expr.rewrite function (or possibly the sympy.Function.rewrite function)
# TODO Pre-parse the input equation for || and replace with Abs() (capitol!)
# TODO Removed use varnames in solution QAction
class Main(QMainWindow):
    varTypes = (Symbol, AppliedUndef) #, WildFunction)
    errorTabIndex = 2
    defaultDir = '/home/marvin/Documents/College/Calculus/'
    fileExtensions = 'Text Files (*.txt)'
    latexFileExtensions = 'TeX Document (*.tex, *.latex)'
    mathmlFileExtensions = 'MathML Document (*.mathml, *.txt)'
    defaultExtension = ''
    defaultLatexExtension = ''
    defaultMathmlExtension = ''
    baseTrans = standard_transformations + (convert_xor, )
    trans = baseTrans
    undefinedLatex = r'$_\varnothing$_ '
    varCount = 0
    windowStartingPos = (1000, 0)

    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi(join(DIR, "main.ui"), self)
        self.setWindowTitle('Math Transpiler')
        self.setGeometry(*self.windowStartingPos, self.width(), self.height())

        self.inputAlertIcon = self.errorIcon = QIcon(DIR + "/red!.png")
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
        self._loading = False

        # self.pngBox = QSvgWidget(self.svgBox)


# Getters, setters
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
        self.errorBox.setPlainText(str(err))
        self.output.setTabIcon(self.errorTabIndex, self.errorIcon)

        if self.throwError.isChecked():
            raise err

        self.output.setCurrentIndex(self.errorTabIndex)


    @property
    def loading(self):
        return self._loading

    @loading.setter
    def loading(self, isLoading):
        self._loading = isLoading
        if isLoading:
            self.loader.start()
        else:
            self.loader.stop()


# Private
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
        # self.copyCurVar.triggered.connect(lambda: clip.copy(self.varValueBox))
        self.copyCurVar.triggered.connect(lambda: clip.copy(todo('figure out current var copy to clipboard')))

        # The equation input box
        # self.equationInput.textChanged.connect(self.updateEquation)
        self.solveButton.clicked.connect(self.updateEquation)
        self.solveButton2.triggered.connect(self.updateEquation)

        # The ouput tab widget
        self.output.currentChanged.connect(self.onTabChanged)
        self.varList.currentIndexChanged.connect(self.onCurrentVariableChanged)
        self.varList.editTextChanged.connect(self.onVarNameChanged)
        self.varSetter.returnPressed.connect(self.onVarValueChanged)
        self.setRelationButton.pressed.connect(self.onVarValueChanged)
        self.newRelationButton.pressed.connect(self.onNewRelationWanted)

        self.plotButton.triggered.connect(self.plot)
        self.limitButton.triggered.connect(self.onLimitButtonPressed)
        self.dontSimplify.triggered.connect(self.updateEquation)
        self.prettySolution.triggered.connect(self.updateEquation)
        self.doEval.triggered.connect(self.updateEquation)
        self.resetButton.triggered.connect(self.resetEverything)
        self.previewSolution.triggered.connect(self.onPreviewSolution)
        self.previewCurVar.triggered.connect(self.onPreviewCurVar)
        self.implicitMult.triggered.connect(self.updateImplicitMult)
        self.makePiecewise.triggered.connect(self.makePiecewise)

        # self.inputBox.returnPressed.connect(self.onInputAccepted)


    def resetEverything(self):
        self.equationInput.setPlainText('')
        self.updateEquation()
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


    def resetTab(self):
        self.output.setCurrentIndex(self.lastTab)


    def resetIcon(self, tabIndex):
        self.output.setTabIcon(tabIndex, QIcon())


    def resetOuput(self):
        self.errorBox.setPlainText('')
        self.answerBox.setPlainText('')
        self.codeBox.setPlainText('')
        self.resetIcon(self.errorTabIndex)


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

            debug(expr, 'solved expr')

        if self.doEval.isChecked():
            expr = expr.evalf()

        self.solvedExpr = expr


    def isContinuous(self, expr, x, a)->bool:
        # function f(x) is continuous at a point x=a if and only if:
        # f(a) is defined
        # lim(x→a, f(x)) exists
        # lim(x→a, f(x))=f(a)
        if not (expr):
            return False
        if type(expr) is not Function:
            return False
        if not expr(x):
            return False
        return expr(x) == expr(a)


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


# Slots
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
        self.allVars[self.varIndex].name = self.varList.currentText()
        # self.updateVarInfo()
        self.updateSolution()
        self.updateCode()


    def onVarValueChanged(self):
        loads = False
        if not self.loading:
            self.loading = True
            loads = True

        try:
            val = parse_expr(self.varSetter.text(), transformations=self.trans)
            self.resetTab()
        except Exception as err:
            debug('Failed to parse var value!', color=-1)
            self.error = err
        else:
            # self.relations.append(Rel(self.currentVar.value, val, self.relation.currentText()))
            self.updateVars()
            self.allVars[self.varIndex].value = val
            self.allVars[self.varIndex].valueChanged = True
            self.allVars[self.varIndex].relationship = self.relation.currentText()
            self.calculateSolution()
            self.updateVarInfo()
            self.updateSolution()
            self.updateCode()
            self.varPng.setPixmap(self.getPixmap(val))
            # debug(self.allVars, 'vars', color=2)

            # No idea why this is nessicary, but it makes it work.
            # if self._hack:
            #     self._hack = False
            #     self.varSetter.returnPressed.emit()
            # else:
            #     self._hack = True

        if loads:
            self.loading = False


    def onLimitButtonPressed(self):
        inputWindow = QDialog()
        uic.loadUi(join(DIR, "limitsInput.ui"), inputWindow)

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


    def makePiecewise(self):
        inputWindow = QDialog()
        uic.loadUi(join(DIR, "addPiecewise.ui"), inputWindow)

        def extractValues():

            self.updatePiecewise()

        inputWindow.accepted.connect(extractValues)
        inputWindow.show()


    def onPreviewSolution(self):
        preview(self.solvedExpr, output='png')


    def onPreviewCurVar(self):
        preview(solveset(self.expr, self.currentVar.symbol), output='png')


    # def getExprSet(self):
        # l = [self.expr]
        # for i in self.vars:
        #     if i.valueChanged:
        #         l += i.value


# Update Functions
    def updateEquation(self):
        self.loading = True
        self.resetOuput()

        try:
            # Get the equation
            if self.interpretAsLatex.isChecked():
                self.equ = str(parse_latex(self.equationInput.toPlainText()))
            else:
                self.equ = self.equationInput.toPlainText()

            # If we've just deleted everything, it's okay
            if not len(self.equ):
                return

            # Now calculate everything

            # First, run the input string through our function to make sure we take care
            # of the things sympy won't take care of for us (= to Eq() and the like)
            equation = self.fixEquationString(self.equ)

            self.expr = parse_expr(equation, transformations=self.trans, evaluate=False)
            self.calculateSolution()

            # Load the png of what we're writing
            self.equationPng.setPixmap(self.getPixmap(self.expr))

            self.updateVars()
            self.updateSolution()
            self.updateCode()
            self.updateVarInfo()
            self.updateVarValue()
            self.resetTab()

        except Exception as err:
            self.error = err


        self.loading = False


    def updateVarInfo(self):
        if self.currentVar:
            self.varInfoBox.setPlainText(f'Type: {type(self.currentVar.value)}')


    def updateVarValue(self):
        if self.currentVar and self.currentVar.valueChanged:
            ans = pretty(self.currentVar.value) if self.prettySolution.isChecked() else str(self.currentVar.value)
            self.relation.setCurrentText(self.currentVar.relationship)
            self.varPng.setPixmap(self.getPixmap(self.currentVar.value))

        elif self.currentVar:
            # Some inequalities aren't impolemented in the complex domain.
            # (I totally understand what that means.)
            if type(self.expr) is Eq:
                try:
                    sol = solve(self.expr, self.currentVar.symbol)
                    # sol = solveset(self.expr, self.currentVar.symbol)
                except NotImplementedError:
                    sol = solve(self.expr, self.currentVar.symbol, domain=S.Reals)
                    # sol = solveset(self.expr, self.currentVar.symbol, domain=S.Reals)

                self.varPng.setPixmap(self.getPixmap(sol))
                ans = pretty(sol) if self.prettySolution.isChecked() else str(sol)
            else:
                ans = 'Undefined'
                self.varPng.setPixmap(self.getPixmap(EmptySet))

        self.varSetter.setText(ans)


    def updateVars(self):
        atoms = set()
        # Get any variables that are exclusively defined in the variable setter, and add them to atoms
        for i in self.allVars:
            if i.valueChanged:
                atoms = atoms.union(i.value.atoms(*self.varTypes))

        # Get all the variables that are exclusively defined in the relations, and add them to atoms
        # for i in self.relations:
            # atoms = atoms.union(i.atoms(*self.varTypes))

        # Get the variables in the input equation
        atoms = atoms.union(self.expr.atoms(*self.varTypes))

        # Get all the things in what we've just parsed that aren't already in self.vars and add them
        curSymbols = set([v.symbol for v in self.allVars])
        for s in atoms.difference(curSymbols):
            self.allVars.append(Variable(s))
            self.eqVars.append(Variable(s))

        # Now get all the things in self.vars that aren't in the thing we just parsed and delete them
        if not self.rememberVarNames.isChecked():
            for s in curSymbols.difference(atoms):
                del self.allVars[getIndexWith(self.allVars, lambda x: x.symbol == s)]

        # Make sure our expression is updated with the new values
        for var in self.allVars:
            if var.valueChanged:
                self.expr = self.expr.subs(var.symbol, var.value)

        # Totally reset the index box
        lastVarIndex = self.varIndex
        self.blockVarList = True
        self.varList.clear()
        self.varList.addItems([str(v.symbol) for v in self.allVars])
        self.varIndex = lastVarIndex if lastVarIndex > 0 else 0
        self.blockVarList = False


    def updateSolution(self):
        self.solutionPng.setPixmap(self.getPixmap(self.solvedExpr))

        if self.prettySolution.isChecked():
            ans = pretty(self.solvedExpr)
        else:
            ans = str(self.solvedExpr)

        if self.printSolution.isChecked():
            print(ans)

        self.answerBox.setPlainText(ans)


    def updateCode(self):
        self.codeBox.setPlainText(pycode(self.expr, fully_qualified_modules=False))
        # return python(self.expr)
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

        # return s


    def updatePiecewise(self, *values):
        self.relations = values


    def updateLimit(self, updateVar, updateVal, addToMainEquation, dir):
        if addToMainEquation:
            withLimit = f"Limit({self.equationInput.toPlainText()}, {updateVar}, {updateVal}" + (f", '{dir}'" if dir else '') + ')'
            self.equationInput.setPlainText(withLimit)
            self.updateEquation()
        else:
            withLimit = f"Limit({self.varSetter}, {updateVar}, {updateVal}" + (f", '{dir}'" if dir else '') + ')'
            self.varValueBox = withLimit
            # A small hack, make sure we accept the input so we don't overwrite it
            self.varSetter.returnPressed.emit()


    def updateImplicitMult(self):
        if self.implicitMult.isChecked():
            self.trans = self.baseTrans + (implicit_multiplication,)
        else:
            self.trans = self.baseTrans
        self.implicitMulLabel.setText(f'Implicit Multiplication is: {"On" if self.implicitMult.isChecked() else "Off"}')
        self.updateEquation()


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
                f.write(latex(self.solvedExpr))
            print('File Saved!')
            self.lastSaveLoc = file


    def exportAsMathML(self):
        file = QFileDialog.getSaveFileName(directory=self.defaultDir, filter=self.mathmlFileExtensions, initialFilter=self.defaultMathmlExtension)[0]
        if len(file):
            with open(file, 'w') as f:
                f.write(mathml(self.solvedExpr))
            print('File Saved!')
            self.lastSaveLoc = file


    def exportAsMathmatica(self):
        file = QFileDialog.getSaveFileName(directory=self.defaultDir, filter=self.fileExtensions, initialFilter=self.defaultExtension)[0]
        if len(file):
            with open(file, 'w') as f:
                f.write(mathematica_code(self.solvedExpr))
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
                self.updateEquation()
            self.lastSaveLoc = file
