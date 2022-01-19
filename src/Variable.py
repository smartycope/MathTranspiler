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
from PyQt5.QtWidgets import (QDialog, QFileDialog, QLabel, QLineEdit, QMainWindow, QTableWidgetItem, QWidget, QCompleter, QComboBox, QHBoxLayout)
# from PyQt5.QtWidgets import *
from sympy import *
import sympy as sym
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
from UnitSelector import UnitSelector
One.name = 'one'

funcTypes =  (AppliedUndef, UndefinedFunction) #, Function, WildFunction)

# A driver is just a hardware library
class Variable:
    autoParseUnits = True
    # Construct dicts of {string: Variable} of things we want to have as defualt
    autofillUnits    =   dict(zip([str(i.name)   for i in UnitSelector.allUnits], [(i, 1, i, Quantity) for i in UnitSelector.allUnits]))
    autofillUnits.update(dict(zip([str(i.abbrev) for i in UnitSelector.allUnits], [(i, 1, i, Quantity) for i in UnitSelector.allUnits])))
    autofillPrefixes =      dict(zip([str(i.name)   for i in UnitSelector.allPrefixes], [(i, 1, i, Prefix) for i in UnitSelector.allPrefixes]))
    autofillPrefixes.update(dict(zip([str(i.abbrev) for i in UnitSelector.allPrefixes], [(i, 1, i, Prefix) for i in UnitSelector.allPrefixes])))
    autofillCustom = {
        'µ': (micro, 1, micro, One(), Prefix)
    }

    def __init__(self, symbol: sym.Basic, name='', value=None, order=50, unit=One(), prefix=One(), _type=None):
        self.symbol = symbol
        self.prefix = prefix
        self.unit = unit
        self.valueChanged = False

        if self.autoParseUnits:
            if str(symbol) in self.autofillCustom.keys():
                self.symbol, self._value, self.prefix, self.unit, self.type = self.autofillUnits[str(symbol)]
                self.valueChanged = True
            elif str(symbol) in self.autofillPrefixes.keys():
                self.symbol, self._value, self.prefix, self.type = self.autofillPrefixes[str(symbol)]
                self.unit = unit
                self.valueChanged = True
            elif str(symbol) in self.autofillUnits.keys():
                self.symbol, self._value, self.unit, self.type = self.autofillCustom[str(symbol)]
                self.prefix = prefix
                self.valueChanged = True
            else:
                self._value = (symbol if value is None else value)
                self.type = type(symbol) if _type is None else _type
        else:
            self._value = (symbol if value is None else value)
            self.type = type(symbol) if _type is None else _type

        self.name = str(symbol) if not len(name) else name
        self.relationship = '=='
        self.substitutionOrder = order

    def reset(self):
        self.prefix = One()
        self.unit = One()
        self.valueChanged = False
        self.type = type(self.symbol)
        self._value = self.symbol
        self.name = str(self.symbol)
        self.relationship = '=='
        self.substitutionOrder = 50

        # if self.autoParseUnits:
        #     if str(symbol) in self.autofillCustom.keys():
        #         self.symbol, self._value, self.prefix, self.unit, self.type = self.autofillUnits[str(symbol)]
        #         self.valueChanged = True
        #     elif str(symbol) in self.autofillPrefixes.keys():
        #         self.symbol, self._value, self.prefix, self.type = self.autofillPrefixes[str(symbol)]
        #         self.unit = unit
        #         self.valueChanged = True
        #     elif str(symbol) in self.autofillUnits.keys():
        #         self.symbol, self._value, self.unit, self.type = self.autofillCustom[str(symbol)]
        #         self.prefix = prefix
        #         self.valueChanged = True
        #     else:
        #         self._value = (symbol if value is None else value)
        #         self.type = type(symbol) if _type is None else _type
        # else:
        #     self._value = (symbol if value is None else value)
        #     self.type = type(symbol) if _type is None else _type



    @property
    def value(self):
        return (self.unit * self.prefix.scale_factor) * self._value

    @value.setter
    def value(self, to):
        self._value = to

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Variable {type(self.symbol)} {self.symbol} = {{"{self.name}"={self.value}}}(changed={self.valueChanged})'

    def __eq__(self, other):
        return (
            self.symbol == other.symbol and
            self.name == other.name and
            self.value == other.value and
            self.prefix == other.prefix and
            self.unit == other.unit
        )

    def __hash__(self):
        return hash((self.symbol, self.name, self.value, self.prefix, self.unit))
