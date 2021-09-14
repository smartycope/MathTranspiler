# This Python file uses the following encoding: utf-8
import math
import os
import sys
from math import *
# from numpy import *
import numpy as np
import sympy as sym
from sympy import *
from sympy.parsing.sympy_parser import *
try:
    from Cope import debug, debugged, ensureIterable
except ImportError:
    print("Can't seem to import Cope.py (for debugging). Try installing varname via pip.")
import re


from PyQt5 import *
from PyQt5 import QtCore, QtGui, QtMultimedia, QtWidgets, uic
# from PyQt5.QtCore import *
from PyQt5.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QWidget

DIR = os.path.dirname(__file__)



class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi(os.path.join(DIR, "main.ui"), self)
        self.setWindowTitle('Math Transpiler')

        # The equation input box
        self.equation.textChanged.connect(self.updateEquation)
        # The equation string value
        self.equ = ""

        # The outputted code
        assert(self.python)
        # The interal python code string
        # self.code = ""

        # The outputted solution
        assert(self.answer)
        # The interal answer
        self.ans = ""

        # The variables in the inputted equation
        # assert(self.variables)
        # The variables expressed as a list of sympy symbols -- default is lexpr, if there's no =
        self.symbols = ()
        self.vars = ()
        self.varNames = {}
        self.lexpr = None # Symbol()
        self.rexpr = None # Symbol()


        # The graph
        #*  self.plot

        # The error output
        assert(self.error)
        #// The interal error string
        #// self.err = ""

        # The ouput tab widget
        self.output.currentChanged.connect(self.updateLastTab)

        self.variables.currentIndexChanged.connect(self.updateVarInfo)

        self.save.triggered.connect(self._save)
        self.saveAs.triggered.connect(self._saveAs)
        self.load.triggered.connect(self._load)

        # The sympy transformations we use
        # self.trans = standard_transformations + (implicit_multiplication_application,)
        # self.trans = standard_transformations + (implicit_multiplication,)
        self.trans = standard_transformations
        # self.trans = implicit_multiplication_application

        self.lastTab = 0


    # Switch to the error tab, if there's an error, then switch back when there's not.
    def updateLastTab(self):
        if self.output.currentIndex() != 2:
            self.lastTab = self.output.currentIndex()


    def updateEquation(self):
        index = self.lastTab

        # Get the equation
        self.equ = self.equation.toPlainText()

        # Reset everything so we can re-set it later
        self.error.setPlainText("")
        self.variables.clear()
        self.python.setPlainText("")
        self.output.setTabIcon(2, QIcon())
        self.symbols = []
        self.lexpr = None
        self.rexpr = None


        # If we've just deleted everything, it's okay
        if not len(self.equ):
            return

        try:
            if self.equ.count('=') > 1:
                raise SyntaxError("More than 1 '=' in equation")

            self.variables.addItems(self.parseVars())
            self.python.setPlainText(self.genCode())
            self.answer.setPlainText(self.solve())
        except Exception as err:
            self.error.setPlainText(str(err))
            self.output.setTabIcon(2, QIcon("/home/marvin/Documents/assets/Misc/red!.png"))
            index = 2
            if self.throwError.isChecked():
                raise err

        self.output.setCurrentIndex(index)
        debug(self.lexpr)
        debug(self.rexpr)
        # for s in self.rsyms:
            # debug(s)
        print('------------------------------------------------------------------')


    def parseVars(self):
        rtnList = []

        if '=' in self.equ:
            lside, rside = re.split(r'=', self.equ)
            self.symbols = ensureIterable(sym.var(rside)) + ensureIterable(sym.var(lside))
            self.lexpr = sym.parse_expr(rside, transformations=self.trans)
            self.rexpr = sym.parse_expr(lside, transformations=self.trans)
            self.vars = list(self.lexpr.as_coefficients_dict().keys()) + list(self.rexpr.as_coefficients_dict().keys())
        else:
            self.lexpr = sym.parse_expr(self.equ, transformations=self.trans)
            self.vars = list(self.lexpr.as_coefficients_dict().keys())

        for s in self.vars:
            rtnList.append(str(s))

        return rtnList


    def updateVarInfo(self, varIndex):
        s = (self.vars)[varIndex]
        val = sym.solveset(sym.Eq(self.lexpr, self.rexpr), s) if '=' in self.equ else 'Undefined'
        self.varInfo.setPlainText(f'Name: {s}\nType: {type(s)}\nValue: {val}\nFunction: {s.is_Function}\nReal: {bool(s.is_real)}')



    # def getVarsDict(self):
    #     rtn = {}
    #     for s in self.rsyms + self.rexpr:
    #         rtn[s.]





    def genCode(self):
        args = {"local_dict":{}, "global_dict":globals(), "transformations":self.trans}

        if '=' in self.equ:
            lside, rside = re.split(r'=', self.equ)
            code = stringify_expr(rside, **args) + ' = ' + stringify_expr(lside, **args)
        else:
            code = stringify_expr(self.equ, **args)
        return self.genCodeFromStringify(code)


    def genCodeFromStringify(self, s):
        # Remove all whitespace
        s = re.sub(r'\s', '', s)

        # Remove all Integer statements
        # s = re.sub(r'Integer\(\(?:d+)\)', '', s)

        return s

    def solve(self):
        if '=' in self.equ:
            lside, rside = re.split(r'=', self.equ)
            # self.ans = sym.Eq((sym.simplify(rside)), (sym.simplify(lside)))
            self.ans = str(sym.simplify(rside)) + ' = ' + str(sym.simplify(lside))
        else:
            self.ans = sym.simplify(self.equ)
        return str(self.ans)

# f(x) = 2y + x


    def _saveAs(self):
        file = QFileDialog.getSaveFileName()[0]
        if len(file):
            with open(file, 'w') as f:
                f.write(self._getFunc())
            print('File Saved!')

    def _save(self):
        if self.lastSaveLoc:
            with open(self.lastSaveLoc, 'w') as f:
                f.write(self._getFunc())
            print('File Saved!')

    def _load(self):
        file = QFileDialog.getOpenFileName()[0]
        if len(file):
            with open(file, 'r') as f:
                self.code.setPlainText(f.read()[54:])

    def reset(self):
        self.num = self.resetVal.value()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    app.exec()
