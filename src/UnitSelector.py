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
                          QRectF, Qt, QThread, QTimer, QSize)
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (QDialog, QFileDialog, QLabel, QLineEdit, QMainWindow,
                             QTableWidgetItem, QWidget, QCompleter, QComboBox, QHBoxLayout)
# from PyQt5.QtWidgets import *
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

from sympy.core.numbers import One
# Hacking One so I don't have to make it a unit (cause I'm lazy)
One.name = 'one'
One.abbrev = ''
One.scale_factor = 1

todo('prefixes dont work still')
todo("somehow make just switching variables not update the equation (maybe don't update the equation if currentVar doesn't have the changed variable set?)")


_quantityStrings = filter(lambda u: type(getattr(_units, u)) is Quantity, dir(_units))
_prefixStrings   = filter(lambda u: type(getattr(_units, u)) is Prefix,   dir(_units))

_quantities = list(set(map(lambda i: getattr(_units, i), _quantityStrings)))
_prefixes   = list(set(map(lambda i: getattr(_units, i), _prefixStrings)))

customUnits = [
    # Quantity('m/s', abbrev='m/s', dimension=length/time, scale_factor=meter/second)
    # Quantity('m/s', abbrev='m/s', dimension=meters/second)
]

class UnitSelector(QWidget):
    allUnits    = [One()] + sorted(_quantities + customUnits, key=lambda i: str(i.name))
    allPrefixes = sorted([One()] + _prefixes, key=lambda i: i.scale_factor, reverse=True)


    def __init__(self, *args, **kwargs):
        super(UnitSelector, self).__init__(*args, **kwargs)
        self.setMinimumSize(QSize(300, 35))

        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(1)

        self.prefixBox = QComboBox(self)
        self.unitBox = QComboBox(self)

        self.layout.addWidget(self.prefixBox)
        self.layout.addWidget(self.unitBox)

        self.prefixBox.setEditable(True)
        self.unitBox.setEditable(True)

        self.prefixIndexChanged = self.prefixBox.currentIndexChanged
        self.unitIndexChanged = self.unitBox.currentIndexChanged

        # Set the dropdown box completers (Based)
        self.unitBox.setCompleter(QCompleter([str(i.name) for i in self.allUnits]))
        self.prefixBox.setCompleter(QCompleter([str(i.name) for i in self.allPrefixes]))

        # Fill the dropdown boxes
        self.unitBox.addItems([str(i.name) for i in self.allUnits])
        self.prefixBox.addItems([self.getPrefixString(i) for i in self.allPrefixes])

        # Set tooltips
        for cnt, prefix in enumerate(self.allPrefixes):
            self.prefixBox.setItemData(cnt, str(prefix.scale_factor), Qt.ItemDataRole.ToolTipRole)

        for cnt, unit in enumerate(self.allUnits):
            self.unitBox.setItemData(cnt, str(unit.abbrev), Qt.ItemDataRole.ToolTipRole)

        self.reset()

    @debug
    def reset(self):
        self.unit = One()
        self.prefix = One()


    @staticmethod
    def getPrefixString(prefix):
        return f"{str(prefix.abbrev) + ' ' if prefix.name != 'one' else ''}{prefix.name}"

    @property
    def unit(self):
        return self.allUnits[self.unitBox.currentIndex()]

    @unit.setter
    def unit(self, unit):
        if type(unit) is str:
            self.unitBox.setCurrentIndex(self.unitBox.findText(unit))
        else:
            self.unitBox.setCurrentIndex(self.unitBox.findText(str(unit.name)))

    @property
    def prefix(self):
        return self.allPrefixes[self.prefixBox.currentIndex()]

    @prefix.setter
    def prefix(self, unit:Prefix):
        if type(unit) is str:
            raise NotImplementedError()
            self.prefixBox.setCurrentIndex(self.prefixBox.findText(unit))
        else:
            self.prefixBox.setCurrentIndex(self.prefixBox.findText(self.getPrefixString(unit)))
