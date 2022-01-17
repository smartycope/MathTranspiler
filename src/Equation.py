# This Python file uses the following encoding: utf-8
import math
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
import EasyRegex as er
from sympy.core.numbers import One
import re
# Hacking One so I don't have to make it a unit (cause I'm lazy)
One.name = 'one'
One.abbrev = ''
One.scale_factor = 1





class Equation(Expression):
    baseTrans = standard_transformations + (convert_xor, lambda_notation)
    trans = baseTrans
    arrowRegex    = (er.group(anything() + matchMax()) + match('->') + er.group(anything() + matchMax())).compile()
    doubleEqRegex = (er.group(anything() + matchMax()) + match('==') + er.group(anything() + matchMax())).compile()
    eqRegex       = (er.group(anything() + matchMax()) + match('=')  + er.group(anything() + matchMax())).compile()
    sciNotSigFigs = 4
    varTypes = (Symbol, Derivative, Function, FunctionCall, Integral)
    varTypeMap = {0: Symbol, 1: Function, 2: Derivative, 3: Integral}
    funcTypes =  (AppliedUndef, UndefinedFunction) #, Function, WildFunction)



    def __init__(self, constMainWindow, errorHandler, inputBox, latexButton, solutionExpression, varHandler, runCodeButton):
        super().__init__(inputBox, latexButton)
        self.subbedExpr = EmptySet
        self.solvedExpr = EmptySet
        self.plainExpr  = EmptySet
        self.string = ''
        self.solutionString = ''
        # self.calculating = False
        self.options = constMainWindow
        self.vars = []
        self.solutionExpression = solutionExpression
        self.varHandler = varHandler
        self.varHandler.updateEquation.connect(self.update)
        self.errorHandler = errorHandler
        self.runCodeButton = runCodeButton


    def update(self):
        self.options.loading = True
        try:
            self.string = self.text

            #* If there's nothing there, it's okay
            if not len(self.string):
                self.calculating = False
                return

            #* Now calculate everything
            # First, run the input self.string through our function to make sure we take care
            # of the things sympy won't take care of for us (= to Eq() and the like)
            if self._detectLatex(self.string):
                self.string = self._convertLatex(self.string)
                self.text = self.string
            else:
                sanatizedEquation = self._fixEquationString(self.string) if self.options.useFixString.isChecked() else self._sanatizeInput(self.string)

            # Actually parse the expression (but don't solve it yet!)
            self.plainExpr = parse_expr(sanatizedEquation, transformations=self.trans, evaluate=False)

            # See if we need to remove one side of the equation
            todo('make this smarter', False)
            if self.options.removeFx.isChecked() and type(self.plainExpr) is Eq:
                self.plainExpr = self.plainExpr.rhs
                self.string = str(self.plainExpr)
                self.text = self.string

            # Set the initial value of subbedExpr
            self.subbedExpr = self.plainExpr

            #* Load the png of what we're writing
            self.updateIcon(self.plainExpr)

            # # This order matters
            self.updateVars()
            self._updateSubbedExpr()
            self.varHandler.vars = self.vars
            self._calculateSolution()
            # # Yes, update it again, because we need to get the new vars in just the solution as well.
            self.updateVars()
            # self.updateCode()
            # Hand the variables off to varHandler
            self.varHandler.setVars(self.vars)
            # self.varHandler.updateVarInfo()
            # self.varHandler.updateVarValue()
            # Make sure the code box has updated values
            self.runCodeButton.pressed.emit()
            # except Exception as err:
                # self.setError(err, "Solver")
            # else:
                # self.resetError()
        except Exception as err:
            self.errorHandler.setError(err, 'Solver')
        else:
            self.errorHandler.resetError()

        self.options.loading = False


    def _calculateSolution(self, unit=One()):
        #* Calculate the solution
        self.solvedExpr = self.subbedExpr

        if not self.options.doEval.isChecked() and self.options.doExpand.isChecked():
            self.solvedExpr = self.solvedExpr.expand()

        if not self.options.dontSimplify.isChecked():
            # system = solve_rational_inequalities(self.relations + [self.self.solvedExpr])
            # system = solve_poly_set_something(...)
            self.solvedExpr = self.solvedExpr.simplify()

        if self.options.doEval.isChecked():
            self.solvedExpr = self.solvedExpr.evalf()

        if not self.options.dontSimplify.isChecked():
            self.solvedExpr = self.solvedExpr.doit()

        if unit != One():
            self.solvedExpr = convert_to(self.solvedExpr, unit)

        #* Now parse the solution into a string exactly how we want it
        if self.options.prettySolution.isChecked():
            self.solutionString = pretty(self.solvedExpr)
        else:
            if self.options.useSciNot.isChecked():
                try:
                    self.solutionString = scinot.format(self.solvedExpr, self.sciNotSigFigs)
                except ValueError:
                    self.solutionString = str(self.solvedExpr)
            else:
                self.solutionString = str(self.solvedExpr)

        self.solutionString = self._sanatizeOutput(self.solutionString)

        # Joes mortuary: you stab em', we bag em'
        if self.options.printSolution.isChecked():
            print(self.solutionString)

        self.solutionExpression.updateIcon(self.solvedExpr)
        self.solutionExpression.updateText(self.solutionString)


    def _updateSubbedExpr(self):
        if self.options.doExpand.isChecked():
            self.subbedExpr = self.subbedExpr.expand()
        if not self.options.dontSimplify.isChecked():
            self.subbedExpr = self.subbedExpr.simplify()
        # Actually do the substitutions
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


    def updateVars(self):
        atoms = self._getAtoms()

        #* Get all the things in atoms that aren't already in self.vars and add them
        # Get a set of the symbols in self.vars
        curSymbols = set([v.symbol for v in self.vars])
        for s in atoms.difference(curSymbols):
            # If it's likely a unit, fill it with that first
            self.vars.append(Variable(s))

        #* Now get all the things in self.vars that aren't in atoms and delete them
        if not self.options.rememberVarNames.isChecked():
            for s in curSymbols.difference(atoms):
                del self.vars[getIndexWith(self.vars, lambda x: x.symbol == s)]



    def _getAtoms(self):
        atoms = set()

        if self.options.getVarsFromVars.isChecked():
            #* Get any variables that are exclusively defined in the variable setter, and add them to atoms
            # iterate through the variables that have been changed
            for i in filter(lambda x: x.valueChanged, self.vars):
                # Get that atoms in the value of i
                atoms = atoms.union(i.value.atoms(*self.varTypes+self.funcTypes))
                funcs = set()
                for func in i.value.atoms(*self.funcTypes):
                    funcs = funcs.union((type(func),))
                atoms = atoms.union(funcs)

        #* Get the atoms in the input equation
        atoms = atoms.union(self.plainExpr.atoms(*self.varTypes))
        funcs = set()
        for func in self.plainExpr.atoms(*self.funcTypes):
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
        todo('this needs more work')
        atoms = filter(lambda a: type(a) not in (Quantity, Prefix), atoms)
        atoms = set(atoms)

        return atoms

    @depricated
    def _fixEquationString(self, eq:str):
        eq = self.sanatizeInput(eq)

        if self.implicitMult.isChecked():
            functionRegex = group(word()) + ifProceededBy(match('(') + stuff() + match(')'))
            eq = re.sub(functionRegex.str(), r"Function('\1')", eq)

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

    # The difference between these 2 functions is that sanatizeInput() does the bare essentials and should always be run, while
    # fixEquationString() does extra stuff enabled by the setting action, and also sanatizes it
    @staticmethod
    def _sanatizeInput(eq:str):

        eq = re.sub('−', '-', eq)
        eq = re.sub('π', 'pi', eq)
        eq = re.sub('∞', 'oo', eq)
        eq = re.sub('⋅', '*', eq)
        eq = re.sub('×', '*', eq)
        eq = re.sub('→', '->', eq)
        eq = re.sub('∫', 'Integral', eq)

        eRegex = match('e') + ifNotPrecededBy(wordChar()) + ifNotFollowedBy(wordChar())
        eq = re.sub(str(eRegex), 'E', eq)

        eq = re.subn(Equation.arrowRegex,    r'Lambda(\g<1>, \g<2>)', eq, 1)[0]
        eq = re.subn(Equation.doubleEqRegex, r'Eq(\g<1>, \g<2>)',     eq, 1)[0]
        eq = re.subn(Equation.eqRegex,       r'\g<2> - \g<1>', eq, 1)[0]

        # eq = re.sub((match('e') + optional(ifPrecededBy(digit())) + ifNotFollowedBy(anyAlphaNum()) + ifNotPrecededBy(alpha())).str(), 'E', eq)

        return eq

    def _sanatizeOutput(self, solution:str):
        todo('check if log has multiple parameters before converting it', False)
        if self.options.useLn.isChecked():
            solution = re.sub('log', 'ln', solution)
        return solution

    @staticmethod
    def _sanatizeLatex(latex):
        if latex[-1] == '.':
            latex = latex[:-1]
        latex = re.sub('\$_', '', latex)
        latex = re.sub('\$', '', latex)
        latex = re.sub('\\dfrac', '\\frac', latex)
        latex = re.sub(r'\\displaystyle', '', latex)
        # latex = re.sub(r'\\ ', '', latex)
        latex = re.sub(r'\\ dx', 'dx', latex)
        return latex

    @staticmethod
    def _detectLatex(s):
        return '\\' in s or '{' in s or '}' in s

    @staticmethod
    def _convertLatex(s):
        return str(parse_latex(Equation.sanatizeLatex(s)))
