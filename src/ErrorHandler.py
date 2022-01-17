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
                             QMainWindow, QTableWidgetItem, QWidget, QCompleter, QTextBrowser)
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
ROOT = dirname(dirname(dirname(__file__)))


class ErrorHandler(QTextBrowser):
    errorTabIndex = 2
    errorIcon = QIcon(join(ROOT, "assets/red!.png"))

    def __init__(self, mainWindow, *args, **kwargs):
        super(ErrorHandler, self).__init__(*args, **kwargs)
        self.main = mainWindow
        todo('go through this class and optimize it')

    def resetError(self):
        self.main.resetTab()
        self.main.errorBox.setPlainText('')
        self.main.resetIcon(self.errorTabIndex)
        self.main.errorLocLabel.setText(f'Error Generated by: Nothing')



    def setError(self, err, where):
        if err is None:
            self.main.resetError()
        else:
            if self.main.printError.isChecked():
                debug(err, clr=5, calls=2)
            self.main.errorBox.setPlainText(str(err))
            self.main.output.setTabIcon(self.main.errorHandler.errorTabIndex, self.main.errorHandler.errorIcon)
            self.main.errorLocLabel.setText(f'Error Generated by: {where}')

            if self.main.throwError.isChecked():
                raise err

            self.main.output.setCurrentIndex(self.main.errorTabIndex)
