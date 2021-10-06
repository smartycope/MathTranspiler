# This Python file uses the following encoding: utf-8
from os.path import join

from PyQt5.QtWidgets import QFileDialog
from sympy.printing.latex import latex
from sympy.printing.mathematica import mathematica_code
from sympy.printing.mathml import mathml
from sympy.printing.pycode import pycode


def _saveAs(self):
    file = QFileDialog.getSaveFileName(directory=self.defaultDir, filter=self.fileExtensions, initialFilter=self.defaultExtension)[0]
    if len(file):
        with open(file, 'w') as f:
            f.write(self.equ)
        print('File Saved!')
        self.lastSaveLoc = file


def exportAsLatex(self):
    file = QFileDialog.getSaveFileName(directory=self.defaultDir, filter=self.latexFileExtensions, initialFilter=self.defaultLatexExtension)[0]
    if len(file):
        with open(file, 'w') as f:
            f.write(latex(self.solvedExpr))
        print('File Saved!')
        self.lastSaveLoc = file


def exportAsMathML(self):
    file = QFileDialog.getSaveFileName(directory=self.defaultDir, filter=self.mathmlFileExtensions, initialFilter=self.defaultMathmlExtension)[0]
    if len(file):
        with open(file, 'w') as f:
            f.write(mathml(self.solvedExpr))
        print('File Saved!')
        self.lastSaveLoc = file


def exportAsMathmatica(self):
    file = QFileDialog.getSaveFileName(directory=self.defaultDir, filter=self.fileExtensions, initialFilter=self.defaultExtension)[0]
    if len(file):
        with open(file, 'w') as f:
            f.write(mathematica_code(self.solvedExpr))
        print('File Saved!')
        self.lastSaveLoc = file


def _save(self):
    if self.lastSaveLoc:
        with open(self.lastSaveLoc, 'w') as f:
            f.write(self.equ)
        print('File Saved!')


def _load(self):
    file = QFileDialog.getOpenFileName(directory=self.defaultDir, filter=self.fileExtensions)[0] #, initialFilter=self.defaultExtension + 'All Files (*)'
    if len(file):
        with open(file, 'r') as f:
            self.equationInput.setPlainText(f.read())
            self.updateEquation()
        self.lastSaveLoc = file
