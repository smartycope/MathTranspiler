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




class Expression:
    """ A class that consists of some sort of text widget and a display button widget.
        Automatically handles latex rendering to the button
    """
    def __init__(self, textWidget, displayWidget):
        self.textWidget = textWidget
        self.display = displayWidget
        self._expr = EmptySet
        self.icon = None
        self.display.pressed.connect(lambda: clip.copy(latex(self._expr)))


    @property
    def text(self):
        try:
            return self.textWidget.toPlainText()
        except AttributeError:
            return self.textWidget.text()

    @text.setter
    def text(self, to):
        try:
            return self.textWidget.setPlainText(to)
        except AttributeError:
            return self.textWidget.setText(to)

    # def update(self, expr=None):
        # self.updateIcon(expr)
        # self.textWidget

    def updateIcon(self, expr=None):
        # To make things a little bit faster
        todo('make this even faster by calling parse_expr beforehand and comparing it too')
        if expr == self._expr:
            return

        obj = BytesIO()
        img = QPixmap()

        useExpr = parse_expr(self.input) if expr is None else expr
        todo('add transformations to this')
        preview(useExpr, output='png', viewer='BytesIO', outputbuffer=obj)
        img.loadFromData(bytes(obj.getbuffer()))
        self.icon = QIcon(img)
        self.display.setIcon(self.icon)
        self.display.pressed.connect(lambda: clip.copy(latex(useExpr)))

    def reset(self):
        todo('add clear() calls to make this faster')
        self.updateIcon(EmptySet)

    def updateText(self, expr):
        self.textWidget.setPlainText(str(expr))