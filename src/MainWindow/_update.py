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


def updateEquation(self):
    self.loading = True
    try:
        self.resetOuput()
        #* Get the equation
        if self.interpretAsLatex.isChecked():
            self.equ = str(parse_latex(self.sanatizeLatex(self.equationInput.toPlainText())))
        else:
            self.equ = self.equationInput.toPlainText()

        #* If we've just deleted everything, it's okay
        if not len(self.equ):
            return

        #* Now calculate everything
        if self.interpretAsPython.isChecked():
            expr = None
            exec(self.equ, globals(), locals())
            self.expr = expr
        else:
            # First, run the input string through our function to make sure we take care
            # of the things sympy won't take care of for us (= to Eq() and the like)
            equation = self.fixEquationString(self.equ) if self.useFixString.isChecked() else self.sanatizeInput(self.equ)
            self.expr = parse_expr(equation, transformations=self.trans, evaluate=False)

        #* Load the png of what we're writing
        self.equationPng.setPixmap(self.getPixmap(self.expr))

        # This order matters
        self.updateVars()
        self.calculateSolution()
        self.updateSolution()
        # self.updateCode()
        self.updateVarInfo()
        self.updateVarValue()
        # Make sure the code box has updated values
        self.runCodeButton.pressed.emit()
        self.resetTab()

    except Exception as err:
        self.error = err

    self.loading = False


def updateVarInfo(self):
    string = ''

    if self.currentVar:
        #* Type:
        string += f'Type: {type(self.currentVar.symbol) if type(self.currentVar.symbol) in self.funcTypes else type(self.currentVar.value)}\n'

        #* Continuous at (doesn't work):
        try:
            string += f'Continuous at: {continuous_domain(self.solvedExpr, self.currentVar.symbol, Reals)}'
        except Exception as err:
            # debug(err, color=-1)
            if self.throwError.isChecked():
                raise err

    if threading.current_thread().name == "MainThread":
        self.varInfoBox.setPlainText(string)
    else:
        return string


# *Fills* the variable setter box when the current variable is changed
def updateVarValue(self):
    ans = ''
    if self.currentVar and type(self.currentVar.value) is Lambda:
        value = self.currentVar.value.expr
    elif self.currentVar:
        value = self.currentVar.value
    else:
        return

    if self.currentVar.valueChanged:
        ans = pretty(value) if self.prettySolution.isChecked() else str(value)
        self.relation.setCurrentText(self.currentVar.relationship)
        self.varPng.setPixmap(self.getPixmap(value))

    else:
        # Some inequalities aren't impolemented in the complex domain.
        # (I totally understand what that means.)
        if type(self.subbedExpr) is Eq:
            try:
                sol = solve(self.subbedExpr, self.currentVar.symbol)
                # sol = solveset(self.subbedExpr, self.currentVar.symbol)
            except NotImplementedError:
                sol = solve(self.subbedExpr, self.currentVar.symbol, domain=S.Reals)
                # sol = solveset(self.subbedExpr, self.currentVar.symbol, domain=S.Reals)

            self.varPng.setPixmap(self.getPixmap(sol))
            ans = pretty(sol) if self.prettySolution.isChecked() else str(sol)
        else:
            ans = 'Undefined'
            self.varPng.setPixmap(self.getPixmap(EmptySet))

    self.varSetter.setText(ans)


def updateVars(self):
    atoms = set()
    # Get any variables that are exclusively defined in the variable setter, and add them to atoms
    for i in self.vars:
        if i.valueChanged:
            atoms = atoms.union(i.value.atoms(*self.varTypes+self.funcTypes))
            funcs = set()
            for func in i.value.atoms(*self.funcTypes):
                funcs = funcs.union((type(func),))
            atoms = atoms.union(funcs)

    # Get all the variables that are exclusively defined in the relations, and add them to atoms
    # for i in self.relations:
        # atoms = atoms.union(i.atoms(*self.varTypes))

    # Get the variables in the input equation
    atoms = atoms.union(self.expr.atoms(*self.varTypes))
    funcs = set()
    for func in self.expr.atoms(*self.funcTypes):
        funcs = funcs.union((type(func),))
    atoms = atoms.union(funcs)

    # atoms.remove(Symbol('xxx'))

    # Get all the things in what we've just parsed that aren't already in self.vars and add them
    curSymbols = set([v.symbol for v in self.vars])
    for s in atoms.difference(curSymbols):
        self.vars.append(Variable(s))

    # Now get all the things in self.vars that aren't in the thing we just parsed and delete them
    if not self.rememberVarNames.isChecked():
        for s in curSymbols.difference(atoms):
            del self.vars[getIndexWith(self.vars, lambda x: x.symbol == s)]

    # Make sure our expression is updated with the new values
    #// Also, iterate through all the vars and edit any of the Functions to add "(x)" to their name
    for var in self.vars:
        # debug(var.symbol, 'var')
        if var.valueChanged:
            self.subbedExpr = self.expr.subs(var.symbol, var.value)
        # if isinstance(var.symbol, self.funcTypes):
        # if type(var.symbol) in self.funcTypes:
        #     var.name += '(x)'
        #     debug()

    # debug(self.vars, useRepr=True)

    # Totally reset the index box
    lastVarIndex = self.varIndex
    self.blockVarList = True
    self.varList.clear()
    self.varList.addItems([str(v) for v in self.vars])
    # self.varList.addItems([str(v.name) for v in self.vars])
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

    if threading.current_thread().name == "MainThread":
        self.answerBox.setPlainText(ans)
    else:
        return ans


#! Depricated
def updateCode(self):
    return
    try:
        self.codeBox.setPlainText(pycode(self.expr, fully_qualified_modules=False))
    except Exception as err:
        debug(err, 'CodeGenError', color=-1)
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


def updatePiecewise(self, relations, addToMainEquation):
    result = f"Piecewise{tuple(relations)}"

    if addToMainEquation:
        self.equationInput.setPlainText(result)
        self.updateEquation()
    else:
        self.varValueBox = result
        # A small hack, make sure we accept the input so we don't overwrite it
        self.varSetter.returnPressed.emit()


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


def updateIntDiff(self, diff, var, addToMainEquation):
    if addToMainEquation:
        result = ('Derivative' if diff else "Integral") + f"({self.equationInput.toPlainText()}, {var})"
        self.equationInput.setPlainText(result)
        self.updateEquation()
    else:
        result = ('Derivative' if diff else "Integral") + f"({self.varSetter}, {var})"
        self.varValueBox = result
        # A small hack, make sure we accept the input so we don't overwrite it
        self.varSetter.returnPressed.emit()


def updateImplicitMult(self):
    if self.implicitMult.isChecked():
        self.trans = self.baseTrans + (implicit_multiplication,)
    else:
        self.trans = self.baseTrans
    self.implicitMulLabel.setText(f'Implicit Multiplication is: {"On" if self.implicitMult.isChecked() else "Off"}')
    self.updateEquation()
