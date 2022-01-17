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
from UnitSelector import UnitSelector
from Expression import Expression
import scinot

todo('update all the json files and replace = with ==')

class VarHandler:
    def __init__(self, constMainWindow, equation, errorHandler, varSelector, typeBox, varExpression, varUnitSelector, substitutionBox,
                 newVarButton, setButton, resetButton, relationSelector):
        self.varSelector = varSelector
        self.typeBox = typeBox
        self.expression = varExpression
        self.unitSelector = varUnitSelector
        self.subOrderBox = substitutionBox
        self.newButton = newVarButton
        self.setButton = setButton
        self.resetButton = resetButton
        self.relationSelector = relationSelector
        self.equation = equation
        self.errorHandler = errorHandler
        self.options = constMainWindow

        self.varSelector.currentIndexChanged.connect(self.switchVar)
        self.varSelector.editTextChanged.connect(self._onVarNameChanged)
        self.expression.textWidget.returnPressed.connect(self.update)
        # self.varType.currentIndexChanged.connect(self._onVarTypeChanged)
        self.unitSelector.unitIndexChanged.connect(self.update)
        self.unitSelector.prefixIndexChanged.connect(self.update)
        self.resetButton.pressed.connect(self.reset)
        self.setButton.pressed.connect(self.update)
        self.newButton.pressed.connect(self._onNewRelationWanted)

        self.equation.setVars.connect(self.setVars)

        self.vars = []
        self.dontUpdatevarSelector = False
        self.dontUpdateEquation = False


    def resetVarSelector(self):
        #* Totally reset the index box
        lastVarIndex = self.varIndex
        self.dontUpdatevarSelector = True
        self.varSelector.clear()
        self.varSelector.addItems([str(v) for v in self.vars])
        self.varIndex = lastVarIndex if lastVarIndex > 0 else 0
        self.dontUpdatevarSelector = False


    def setVars(self, vars):
        self.vars = vars
        self.resetVarSelector()
        self.dontUpdateEquation = True
        self.update()
        self.switchVar()

    # *Sets* the current variable value when enter is pressed
    def update(self):
        try:
            if self.expression.textWidget.text() not in ('', 'Undefined'):
                val = parse_expr(self.expression.textWidget.text(), transformations=self.options.trans)
            else:
                return
        except Exception as err:
            debug(f'Failed to parse var value: "{self.expression.textWidget.text()}"', color=Colors.ERROR)
            self.errorHandler.setError(err, "Varaible Parser")
        else:
            try:
                # self.equation.update()
                if type(self.currentVar.symbol) in self.equation.funcTypes + (Function,):
                    self.currentVar.value = Lambda(self.functionVar, val)
                else:
                    self.currentVar.value = val
                self.currentVar.valueChanged = True
                self.currentVar.relationship = self.relationSelector.currentText()
                self.currentVar.substitutionOrder = self.subOrderBox.value()
                self.currentVar.unit = self.unitSelector.unit
                self.currentVar.prefix = self.unitSelector.prefix
                self.expression.updateIcon(val)
                if self.dontUpdateEquation:
                    self.dontUpdateEquation = False
                elif self.options.getVarsFromVars.isChecked():
                    self.equation.update()
            except Exception as err:
                self.errorHandler.setError(err, "Setting Varaible")
            else:
                self.errorHandler.resetError()


    # *Fills* the variable setter box when the current variable is changed
    def switchVar(self):
        # To prevent a recursive loop
        if self.dontUpdatevarSelector:
            return

        ans = ''
        # _value instead of value because we don't want to get the unit and prefix too
        if self.currentVar and type(self.currentVar.value) is Lambda:
            value = self.currentVar._value.expr
        elif self.currentVar:
            value = self.currentVar._value
        else:
            return

        if self.currentVar.valueChanged:
            ans = pretty(value) if self.options.prettySolution.isChecked() else str(value)
            self.relationSelector.setCurrentText(self.currentVar.relationship)

            self.expression.updateIcon(value)

        else:
            # Some inequalities aren't implemented in the complex domain.
            # (I totally understand what that means.)
            if type(self.equation.subbedExpr) is Eq:
                func = solve if self.useSolve.isChecked() else solveset
                sol = func(self.equation.subbedExpr, self.currentVar.symbol, domain=S.Reals)
                self.expression.updateIcon(sol)
                if self.options.useSciNot.isChecked():
                    try:
                        ans = scinot.format(ensureNotIterable(sol), self.sciNotSigFigs)
                    except ValueError:
                        ans = pretty(sol) if self.options.prettySolution.isChecked() else str(sol)
                else:
                    ans = pretty(sol) if self.options.prettySolution.isChecked() else str(sol)
            else:
                ans = 'Undefined'
                self.expression.reset()
        self.expression.textWidget.setText(ans)
        self.subOrderBox.setValue(self.currentVar.substitutionOrder)
        # Sets the unitbox to the current unit
        self.unitSelector.unit = self.currentVar.unit
        self.unitSelector.prefix = debug(self.currentVar.prefix, 'setting prefix to')


    def reset(self):
        self.vars = []
        self.expression.textWidget.setText('Undefined')
        self.unitSelector.reset()
        self.equation.update()


    def _onVarTypeChanged(self, index):
        self.currentVar.type = self.varTypeMap[index]


    def _onVarNameChanged(self):
        if self.currentVar and not self.dontUpdatevarSelector:
            # self.vars[self.varIndex].name = self.varSelector.currentText()
            self.currentVar.name = self.varSelector.currentText()
            self.equation.update()


    def _onNewRelationWanted(self):
        self.varCount += 1
        name = f'newVar{self.varCount}'
        self.varSelector.addItem(name)
        # var = Variable(name, order=len(self.vars)+1)
        var = Variable(name)
        var.valueChanged = True
        var.value = EmptySet
        self.vars.append(var)


    def _resetCurrentVar(self):
        # self.vars[self.varIndex] = Variable(self.currentVar.symbol)
        self.currentVar = Variable(self.currentVar.symbol)
        self.expression.textWidget.setText('')
        self.unitSelector.reset()
        self.equation.update()

    @depricated
    def updateVarInfo(self):
        pass
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


    @property
    def varIndex(self):
        return self.varSelector.currentIndex()

    @varIndex.setter
    def varIndex(self, value):
        self.varSelector.setCurrentIndex(value)

    @property
    def currentVar(self):
        try:
            debug(self.varIndex)
            debug(self.vars[self.varIndex], repr=True)
            return self.vars[self.varIndex]
        except IndexError:
            # If we can't find the asked for var, then just set it to the top
            try:
                debug(self.varIndex, 'couldnt get the var with index')
                tmp = self.vars[0]
                self.varIndex = 0
                return tmp
            except IndexError:
                return None

    @currentVar.setter
    def currentVar(self, value):
        try:
            debug(self.varIndex)
            debug(self.vars[self.varIndex], repr=True)
            self.vars[self.varIndex] = value
        except IndexError:
            debug(self.varIndex, 'couldnt set the var with index')
