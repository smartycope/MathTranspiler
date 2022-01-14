from PyQt5 import uic
from PyQt5.QtCore import (QByteArray, QEvent, QFile, QLine, QLineF, QRect,
                          QRectF, Qt, QThread, QTimer)
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (QDialog, QFileDialog, QLabel, QLineEdit,
                             QMainWindow, QTableWidgetItem, QWidget, QApplication)
from sympy import *
from sympy import abc
from sympy.parsing.sympy_parser import (convert_xor, implicit_multiplication,
                                        implicit_multiplication_application,
                                        lambda_notation, parse_expr,
                                        standard_transformations)
from Cope import *
from sys import argv
import sympy
from sympy.core.sympify import SympifyError

# displayAllPaths()

# radians = lambda x: (x * (pi / 180)).simplify()
# degrees = lambda x: (x * (180 / pi)).simplify()


@confidence(80)
def isWithinInterval(val, interval):
    return isBetween(val, interval.start, interval.end, not interval.left_open, not interval.right_open)



@confidence('fairly')
def getCoterminalAngleOverInterval(angle, interval=Interval(0, 2*pi), isRadians=True):
    r = 2*pi if isRadians else 360
    if angle < 0:
        return angle + r
    elif angle > r:
        return angle - r
    else:
        return angle


    # answers = []
    # i = 2*pi if isRadians else 360
    # while True:
    #     testAngle = (angle + i).simplify()
    #     if isWithinInterval(testAngle, interval):
    #         answers.append(testAngle)

    #     testAngle = (angle - i).simplify()
    #     if isWithinInterval(testAngle, interval):
    #         answers.append(testAngle)

    #     i += 2*pi if isRadians else 360
    #     if not isWithinInterval(i, interval):
    #         break

    # return ensureNotIterable(answers)


class TriangleSolver(QDialog):
    transformations = standard_transformations + (convert_xor, lambda_notation, implicit_multiplication)
    lines  = {'someLine', 'yoMama', 'leftBase', 'rightBase', 'fullBase', 'height'}
    angles = {'leftAngle', 'rightAngle', 'fullAngle', 'theta', 'notTheta'}

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        uic.loadUi(join(ROOT, "ui/trigInput.ui"), self)

        self.values = {
            'fullAngle': None,
            'fullBase': None,
            'height': None,
            'leftAngle': None,
            'leftBase': None,
            'notTheta': None,
            'rightAngle': None,
            'rightBase': None,
            'someLine': None,
            'theta': None,
            'yoMama': None,
            'squareAngle': pi/2
        }

        self.userChanged = {
            'fullAngle': False,
            'fullBase': False,
            'height': False,
            'leftAngle': False,
            'leftBase': False,
            'notTheta': False,
            'rightAngle': False,
            'rightBase': False,
            'someLine': False,
            'theta': False,
            'yoMama': False,
        }

        self.fullAngleBox.textEdited.connect(  lambda: self.boxChanged("fullAngle"))
        self.fullBaseBox.textEdited.connect(   lambda: self.boxChanged("fullBase"))
        self.heightBox.textEdited.connect(     lambda: self.boxChanged("height"))
        self.leftAngleBox.textEdited.connect(  lambda: self.boxChanged("leftAngle"))
        self.leftBaseBox.textEdited.connect(   lambda: self.boxChanged("leftBase"))
        self.notThetaBox.textEdited.connect(   lambda: self.boxChanged("notTheta"))
        self.rightAngleBox.textEdited.connect( lambda: self.boxChanged("rightAngle"))
        self.rightBaseBox.textEdited.connect(  lambda: self.boxChanged("rightBase"))
        self.someLineBox.textEdited.connect(   lambda: self.boxChanged("someLine"))
        self.thetaBox.textEdited.connect(      lambda: self.boxChanged("theta"))
        self.yoMamaBox.textEdited.connect(     lambda: self.boxChanged("yoMama"))

        self.solveSymbolic.pressed.connect(self.wipeCalculated)
        self.isDeg.pressed.connect(self.wipeCalculated)
        self.isRad.pressed.connect(self.wipeCalculated)
        self.roundTo.valueChanged.connect(self.wipeCalculated)
        self.resetButton.pressed.connect(self.reset)
        self.calcButton.pressed.connect(self.updateVals)

        self._recursiveCount = 0
        self.show()

    def __getitem__(self, key):
        return self.values[key]

    def __setitem__(self, key, val):
        self.values[key] = val
        if self.values[key] is not None:
            if self.isDeg.isChecked() and key in self.angles:
                # val = getCoterminalAngleOverInterval(degrees(val), isRadians=False)
                val = deg(val)
            val = val.simplify() if self.solveSymbolic.isChecked() else round(val.evalf(), self.roundTo.value())
            # debug(self[key], key)
            getattr(self, key + 'Box').setText(str(val))

    def boxChanged(self, box):
        self.userChanged[box] = True

    def updateBox(self, box):
        text = getattr(self, box + 'Box').text()
        if len(text):
            try:
                p = parse_expr(text, locals(), self.transformations, globals())
                self.values[box] = (rad(p)) if self.isDeg.isChecked() and box in self.angles else p
                # debug(self[box], box)
            except:
                self.values[box] = None
        else:
            self.values[box] = None

    def reset(self):
        self.fullAngleBox.setText('')
        self.fullBaseBox.setText('')
        self.heightBox.setText('')
        self.leftAngleBox.setText('')
        self.leftBaseBox.setText('')
        self.notThetaBox.setText('')
        self.rightAngleBox.setText('')
        self.rightBaseBox.setText('')
        self.someLineBox.setText('')
        self.thetaBox.setText('')
        self.yoMamaBox.setText('')
        self.values = {
            'fullAngle': None,
            'fullBase': None,
            'height': None,
            'leftAngle': None,
            'leftBase': None,
            'notTheta': None,
            'rightAngle': None,
            'rightBase': None,
            'someLine': None,
            'theta': None,
            'yoMama': None,
            'squareAngle': pi/2
        }
        self.userChanged = {
            'fullAngle': False,
            'fullBase': False,
            'height': False,
            'leftAngle': False,
            'leftBase': False,
            'notTheta': False,
            'rightAngle': False,
            'rightBase': False,
            'someLine': False,
            'theta': False,
            'yoMama': False,
        }

    def wipeCalculated(self, *_):
        for box, changed in self.userChanged.items():
            if not changed:
                getattr(self, box + 'Box').setText('')
        self.update()
        # self.updateVals()

    def recalculate(self):
        self.wipeCalculated()
        # self.repaint()
        # self.calcButton.pressed.emit()
        # self.updateVals()

    def updateVals(self):
        l = list(self.values.keys())
        l.remove('squareAngle')
        for i in l:
            self.updateBox(i)

        netLines  = 0
        netAngles = 0

        for i in self.lines:
            if self[i] is not None:
                netLines += 1

        for i in self.angles:
            if self[i] is not None:
                netAngles += 1

        # if not (netLines >= 3 or netAngles = or netAngles + netLines >= 2):
        #     self.equation.setText('Not enough information')
        #     self.solution.setText('Not enough information')
        #     return
        # else:
        self.equation.setText('Not implemented')
        self.solution.setText('Not implemented')
        self.calculate()

    def calculate(self):
        # debug('Calculating...', clr=3)

        def have(*stuff:str):
            for i in stuff:
                if self[i] is None:
                    return False
            return True

        def calc(setTo, expr):
            if self[setTo] is None:
                self[setTo] = expr


        #* Calculate any missing out of left/right/full angle/base
        if have('leftAngle', 'rightAngle'): calc('fullAngle',  self['leftAngle'] + self['rightAngle'])
        if have('leftAngle', 'fullAngle'):  calc('rightAngle', self['fullAngle'] - self['leftAngle'])
        if have('rightAngle', 'fullAngle'): calc('leftAngle',  self['fullAngle'] - self['rightAngle'])

        if have('leftBase', 'rightBase'):   calc('fullBase',   self['leftBase']  + self['rightBase'])
        if have('fullBase', 'leftBase'):    calc('rightBase',  self['fullBase']  - self['leftBase'])
        if have('fullBase', 'rightBase'):   calc('leftBase',   self['fullBase']  - self['rightBase'])


        triangles = (
            ('fullAngle', 'theta', 'notTheta'),
            ('rightAngle', 'theta', 'squareAngle'),
            ('leftAngle', 'notTheta', 'squareAngle'),
        )
        for a, b, c in triangles:
            if have(a, b): calc(c, pi - self[a] - self[b])
            if have(a, c): calc(b, pi - self[a] - self[c])
            if have(b, c): calc(a, pi - self[b] - self[c])


        angleRelations = (
            ('theta', 'height', 'rightBase', 'someLine'),
            ('rightAngle', 'rightBase', 'height', 'someLine'),
            ('leftAngle', 'leftBase', 'height', 'yoMama'),
            ('notTheta', 'height', 'leftBase', 'yoMama')
        )
        for ang, opp, adj, hyp in angleRelations:
            # Soh Cah Toa
            if have(opp, hyp): calc(ang, asin(self[opp] / self[hyp]))
            if have(adj, hyp): calc(ang, acos(self[adj] / self[hyp]))
            if have(opp, adj): calc(ang, atan(self[opp] / self[adj]))

            if have(ang):
                theta = self[ang]
                if have(hyp):
                    calc(opp, self[hyp] * sin(theta))
                    calc(adj, self[hyp] * cos(theta))
                if have(opp):
                    calc(hyp, self[opp] / sin(theta))
                    calc(adj, self[opp] / tan(theta))
                if have(adj):
                    calc(hyp, self[adj] / cos(theta))
                    calc(opp, self[adj] * tan(theta))


        self._recursiveCount += 1
        if self._recursiveCount < self.recursiveLimit.value():
            self.calculate()
        else:
            self._recursiveCount = 0


# if __name__ == "__main__":
#     app = QApplication(argv)
#     win = TriangleSolver()
#     win.show()
#     app.exec()
