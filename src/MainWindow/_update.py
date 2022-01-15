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
from sympy.calculus.util import continuous_domain, function_range
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
from sympy.physics.units import Quantity
from sympy.physics.units.prefixes import Prefix
from sympy import S
from Variable import Variable
import scinot

def updateEquation(self):
    self.loading = True
    try:
        self.resetOuput()

        #* Get the equation
        self.equ = self.equationInput.toPlainText()

        #* If we've just deleted everything, it's okay
        if not len(self.equ):
            return

        #* Now calculate everything
        # First, run the input string through our function to make sure we take care
        # of the things sympy won't take care of for us (= to Eq() and the like)
        if self.detectLatex(self.equ):
            equation = self._convertLatex(self.equ)
            self.equationInput.setPlainText(equation)
        else:
            equation = self.fixEquationString(self.equ) if self.useFixString.isChecked() else self.sanatizeInput(self.equ)
        self.expr = parse_expr(equation, transformations=self.trans, evaluate=False)

        if self.removeFx.isChecked() and type(self.expr) is Eq:
            self.expr = self.expr.rhs
            self.equationInput.setPlainText(str(self.expr))

        # Set the initial value of subbedExpr
        self.subbedExpr = self.expr

        #* Load the png of what we're writing
        self.equationPng.setIcon(QIcon(self.getIcon(self.expr)))

        # This order matters
        self.updateVars()
        self.calculateSolution()
        self.updateSolution()
        # Yes, update it again, because we need to get the new vars in just the solution as well.
        self.updateVars()
        # self.updateCode()
        self.updateVarInfo()
        self.updateVarValue()
        # Make sure the code box has updated values
        self.runCodeButton.pressed.emit()
    except Exception as err:
        self.setError(err, "Solver")
    else:
        self.resetError()

    self.loading = False


def updateVarInfo(self):
    pass
    # string = ''

    # if self.currentVar:
    #     #* Type:
    #     string += f'Type: {type(self.currentVar.symbol) if type(self.currentVar.symbol) in self.funcTypes else type(self.currentVar.value)}\n'

    #     #* Continuous at (doesn't work):
    #     # try:
    #         # string += f'Continuous at: {continuous_domain(self.solvedExpr, self.currentVar.symbol, Reals)}'
    #     # except Exception as err:
    #         # debug(err, color=-1)
    #         # if self.throwError.isChecked():
    #             # raise err

    # if threading.current_thread().name == "MainThread":
    #     self.varInfoBox.setPlainText(string)
    # else:
    #     return string


# *Fills* the variable setter box when the current variable is changed
def updateVarValue(self):
    ans = ''
    # _value instead of value because we don't want to get a unit too
    if self.currentVar and type(self.currentVar.value) is Lambda:
        value = self.currentVar._value.expr
    elif self.currentVar:
        value = self.currentVar._value
    else:
        return

    if self.currentVar.valueChanged:
        ans = pretty(value) if self.prettySolution.isChecked() else str(value)
        self.relation.setCurrentText(self.currentVar.relationship)
        self.varPng.setIcon(self.getIcon(value))
        self.varPng.pressed.connect(lambda: clip.copy(latex(value)))

    else:
        # Some inequalities aren't impolemented in the complex domain.
        # (I totally understand what that means.)
        if type(self.subbedExpr) is Eq:
            # try:
                # sol = solve(self.subbedExpr, self.currentVar.symbol)
                # sol = solveset(self.subbedExpr, self.currentVar.symbol)
            # except NotImplementedError:
            func = solve if self.useSolve.isChecked() else solveset
            sol = func(self.subbedExpr, self.currentVar.symbol, domain=S.Reals)
                # sol = solveset(self.subbedExpr, self.currentVar.symbol, domain=S.Reals)
            self.varPng.setIcon(self.getIcon(sol))
            self.varPng.pressed.connect(lambda: clip.copy(latex(sol)))
            if self.useSciNot.isChecked():
                try:
                    ans = scinot.format(ensureNotIterable(sol), self.sciNotSigFigs)
                except ValueError:
                    ans = pretty(sol) if self.prettySolution.isChecked() else str(sol)
            else:
                ans = pretty(sol) if self.prettySolution.isChecked() else str(sol)
        else:
            ans = 'Undefined'
            self.varPng.setIcon(self.getIcon(EmptySet))
            self.varPng.pressed.connect(lambda: clip.copy(latex(EmptySet)))

    self.varSetter.setText(ans)
    self.varOrderSetter.setValue(self.currentVar.substitutionOrder)
    # Sets the unitbox to the current unit
    self.unitBox.setCurrentIndex(self.unitBox.findText(str(self.currentVar.unit.name)))
    self.prefixBox.setCurrentIndex(self.prefixBox.findText(f'{self.currentVar.prefix.name} ({self.currentVar.prefix.abbrev})'))


def updateVars(self):
    def getAtoms():
        atoms = set()
        #* Get any variables that are exclusively defined in the variable setter, and add them to atoms
        for i in filter(lambda x: x.valueChanged, self.vars):
            atoms = atoms.union(i.value.atoms(*self.varTypes+self.funcTypes))
            funcs = set()
            for func in i.value.atoms(*self.funcTypes):
                funcs = funcs.union((type(func),))
            atoms = atoms.union(funcs)

        # Get all the variables that are exclusively defined in the relations, and add them to atoms
        # for i in self.relations:
            # atoms = atoms.union(i.atoms(*self.varTypes))

        #* Get the atoms in the input equation
        atoms = atoms.union(self.expr.atoms(*self.varTypes))
        funcs = set()
        for func in self.expr.atoms(*self.funcTypes):
            funcs = funcs.union((type(func),))
        atoms = atoms.union(funcs)

        #* Get the atoms in the solution
        atoms = atoms.union(self.solvedExpr.atoms(*self.varTypes))
        # There shouldn't be any new function types exclusively in the solution
        # funcs = set()
        # for func in self.expr.atoms(*self.funcTypes):
            # funcs = funcs.union((type(func),))
        # atoms = atoms.union(funcs)

        # Remove any unit from atoms (we only want to touch those internally)
        atoms = filter(lambda a: type(a) not in (Quantity, Prefix), atoms)
        # atoms = filter(lambda a: type(a) not in (Quantity, Prefix), atoms)
        atoms = set(atoms)
        # debug(atoms)

        return atoms

    def resetVarBox():
        #* Totally reset the index box
        lastVarIndex = self.varIndex
        self.blockVarList = True
        self.varList.clear()
        self.varList.addItems([str(v) for v in self.vars])
        self.varIndex = lastVarIndex if lastVarIndex > 0 else 0
        self.blockVarList = False

    # if self.doExpand.isChecked():
        # self.expr = self.expr.expand().simplify()

    atoms = getAtoms()

    #* Get all the things in what we've just parsed that aren't already in self.vars and add them
    curSymbols = set([v.symbol for v in self.vars])
    for s in atoms.difference(curSymbols):
        # If it's likely a unit, fill it with that first
        self.vars.append(self.initializeVariable(s))

    #* Now get all the things in self.vars that aren't in the thing we just parsed and delete them
    if not self.rememberVarNames.isChecked():
        for s in curSymbols.difference(atoms):
            del self.vars[getIndexWith(self.vars, lambda x: x.symbol == s)]

    #* MOVED to calculateSolution() in private
    #* Make sure our expression is updated with the new values
    self.updateSubbedExpr()

    resetVarBox()


def updateSubbedExpr(self):
    if self.doExpand.isChecked():
        self.subbedExpr = self.subbedExpr.expand()
    if not self.dontSimplify.isChecked():
        self.subbedExpr = self.subbedExpr.simplify()
    for var in sorted(list(filter(lambda x: x.valueChanged, self.vars)), key=lambda x: x.substitutionOrder):
        self.subbedExpr = self.subbedExpr.subs(var.symbol, var.value)


    # for var in sorted(self.vars, key=lambda v: len(str(v.symbol)), reverse=True):
        # if var.valueChanged:
            # symbols.append(var.symbol)
            # vals.append(var.value)
            # self.subbedExpr = self.subbedExpr.subs(var.symbol, var.value)
            # self.subbedExpr = Subs(self.subbedExpr, var.symbol, var.value)
    # self.subbedExpr = self.subbedExpr.subs(symbols, vals)
    # self.subbedExpr = Subs(self.expr, symbols, vals).doit()


def updateSolution(self):
    self.solutionPng.setIcon(self.getIcon(self.solvedExpr))

    if self.prettySolution.isChecked():
        ans = pretty(self.solvedExpr)
    else:
        if self.useSciNot.isChecked():
            try:
                ans = scinot.format(self.solvedExpr, self.sciNotSigFigs)
            except ValueError:
                ans = str(self.solvedExpr)
        else:
            ans = str(self.solvedExpr)

    ans = self.sanatizeOutput(ans)

    # Joes mortuary: you stab em', we bag em'
    if self.printSolution.isChecked():
        print(ans)

    self.answerBox.setPlainText(ans)


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
        withLimit = f"Limit({self.expr}, {updateVar}, {updateVal}" + (f", '{dir}'" if dir else '') + ')'
        self.equationInput.setPlainText(withLimit)
        self.updateEquation()
    else:
        withLimit = f"Limit({self.currentVar.value}, {updateVar}, {updateVal}" + (f", '{dir}'" if dir else '') + ')'
        self.varValueBox = withLimit
        # A small hack, make sure we accept the input so we don't overwrite it
        self.varSetter.returnPressed.emit()


def updateIntDiff(self, diff, var, addToMainEquation, order, upperBound, lowerBound):
    #* First check if the input we got is valid
    if diff and len(upperBound):
        print("Ignoring upper bound that was given (derivatives don't have upper bounds)")
    if diff and len(lowerBound):
        print("Ignoring lower bound that was given (derivatives don't have lower bounds)")
    if not diff and not len(var) and (len(upperBound) or len(lowerBound)):
        print("ERROR: upper bound/lower bound specified, but no variable was specified")
        return

    currentEqu = self.equationInput.toPlainText() if addToMainEquation else self.currentVar.value

    if diff:
        if not len(var):
            result = f"Derivative({currentEqu})"
        else:
            result = f"Derivative({currentEqu}, ({var}, {order}))"
    else:
        if not len(var):
            result = f"Integral({currentEqu})"
        else:
            result = f"Integral({currentEqu}, ({var}, {lowerBound}, {upperBound}))"

    if addToMainEquation:
        self.equationInput.setPlainText(result)
        self.updateEquation()
    else:
        self.varValueBox = result
        # A small hack, make sure we accept the input so we don't overwrite it
        self.varSetter.returnPressed.emit()


def updateSum(self, count, var, val, addToMainEquation):
    if addToMainEquation:
        withit = f"Sum({self.expr}, ({var}, {val}, {count}))"
        self.equationInput.setPlainText(withit)
        self.updateEquation()
    else:
        withit = f"Sum({self.currentVar.value}, ({var}, {val}, {count}))"
        self.varValueBox = withit
        # A small hack, make sure we accept the input so we don't overwrite it
        self.varSetter.returnPressed.emit()


def updateImplicitMult(self):
    if self.implicitMult.isChecked():
        self.trans = self.baseTrans + (implicit_multiplication,)
    else:
        self.trans = self.baseTrans
    self.implicitMulLabel.setText(f'Implicit Multiplication is {"On" if self.implicitMult.isChecked() else "Off"}')
    self.updateEquation()


# def updateUnitSystem(self, to):
    # self.unitSystem = to
    # if to == 'Dimentionless':
    #     self.actionPhysics.setChecked(False)
    #     self.actionElectronics.setChecked(False)
    #     self.actionAstrophysics.setChecked(False)
    # elif to == 'Physics':
    #     self.actionElectronics.setChecked(False)
    #     self.actionAstrophysics.setChecked(False)
    #     self.actionDimentionless.setChecked(False)
    # elif to == 'Astrophysics':
    #     self.actionPhysics.setChecked(False)
    #     self.actionElectronics.setChecked(False)
    #     self.actionDimentionless.setChecked(False)
    # elif to == 'Electronics':
    #     self.actionPhysics.setChecked(False)
    #     self.actionAstrophysics.setChecked(False)
    #     self.actionDimentionless.setChecked(False)
    # else:
    #     raise Exception(f"Unknown unit system {to}")


    # for i in self.getAvailableUnits():
    #     self.convertSolutionToUnit.addAction(str(i)).triggered.connect(self.updateEquation)

    # self.unitBox.addItems([str(i) for i in self.getAvailableUnits()])


# def fillVarUnit(self):
#     self.unitBox.setCurrentText(str(self.currentVar.unit.name))

# def fillVarPrefix(self):
#     self.prefixBox.setCurrentText(str(self.currentVar.prefix.name))

# def changeVarUnit(self):
    # pass