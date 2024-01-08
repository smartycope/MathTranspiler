# This Python file uses the following encoding: utf-8
import math
import re
import threading, json
from io import BytesIO
from os.path import dirname, join

import clipboard as clip
from Cope import *
from ezregex import *
from LoadingBar import LoadingBar, showLoading, showWithLoading
from PyQt5 import uic
from PyQt5.QtCore import (QByteArray, QEvent, QFile, QLine, QLineF, QRect,
                          QRectF, Qt, QThread, QTimer)
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (QDialog, QFileDialog, QLabel, QLineEdit,
                             QMainWindow, QTableWidgetItem, QWidget, QCompleter, QListWidget)
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
from UnitSelector import UnitSelector

ROOT = join(dirname(__file__), '../')

class EquationSearch(QDialog):
    def __init__(self, updateFunc, transformations, *args, **kwargs):
        super(EquationSearch, self).__init__(*args, **kwargs)
        uic.loadUi(join(ROOT, "ui/equationSearch.ui"), self)
        self.updateFunc = updateFunc
        self.equation = EmptySet
        self.equations = {}

        with open(join(ROOT, "assets/commonEquations.json"), 'r') as _f:
            for i in json.load(_f):
                self.equations[i['definition']] = parse_expr(i['definition'],
                                                             transformations=transformations,
                                                            #  evaluate=False).atoms(Symbol)
                                                             evaluate=False).args()

        self.unitSelector.unitIndexChanged.connect(self.updateEquations)
        self.accepted.connect(self.finish)

        self.show()

        # self.completer = QCompleter(self.equationsBox)

        debug(self.equations)
        self.equationsBox = QListWidget()

    def updateEquations(self):
        self.units = {self.unitSelector.unit}
        for name, atoms in self.equations.items():
            if self.units.issubset(atoms):
                self.equationsBox.addItem(QLabel(name))

    def finish(self):
        self.updateFunc(self.equationsBox.selectedItems())
