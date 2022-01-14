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


class TriangleSolver(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        uic.loadUi(join(ROOT, "ui/trigInput.ui"), self)

        self.values = {
        }

        self.userChanged = {
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



"""
class Test:
    def __init__(self):
        self.prop = 6
    @property
    def this(self):
        print('getter called')
        return self.prop
    @this.setter
    def this(self, to):
        print('setter called')
        self.prop = to
"""


"""


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

displayAllPaths()

class TriangleSolver(QDialog):
    transformations = standard_transformations + (convert_xor, lambda_notation, implicit_multiplication)
    def __init__(self):
        super().__init__()
        uic.loadUi(join(dirname(__file__), "MathTranspiler/ui/trigInput.ui"), self)

        self._fullAngle = None
        self._fullBase = None
        self._height = None
        self._leftAngle = None
        self._leftBase = None
        self._notTheta = None
        self._rightAngle = None
        self._rightBase = None
        self._someLine = None
        self._theta = None
        self._yoMama = None

        # self._fullAngleUpToDate = True
        # self._fullBaseUpToDate = True
        # self._heightUpToDate = True
        # self._leftAngleUpToDate = True
        # self._leftBaseUpToDate = True
        # self._notThetaUpToDate = True
        # self._rightAngleUpToDate = True
        # self._rightBaseUpToDate = True
        # self._someLineUpToDate = True
        # self._thetaUpToDate = True
        # self._yoMamaUpToDate = True

        self.fullAngleBox.textEdited.connect(self.fullAngleChanged)
        self.fullBaseBox.textEdited.connect(self.fullBaseChanged)
        self.heightBox.textEdited.connect(self.heightChanged)
        self.leftAngleBox.textEdited.connect(self.leftAngleChanged)
        self.leftBaseBox.textEdited.connect(self.leftBaseChanged)
        self.notThetaBox.textEdited.connect(self.notThetaChanged)
        self.rightAngleBox.textEdited.connect(self.rightAngleChanged)
        self.rightBaseBox.textEdited.connect(self.rightBaseChanged)
        self.someLineBox.textEdited.connect(self.someLineChanged)
        self.thetaBox.textEdited.connect(self.thetaChanged)
        self.yoMamaBox.textEdited.connect(self.yoMamaChanged)

        self.solveSymbolic.pressed.connect(self.updateBoxes)
        self.isDeg.pressed.connect(self.updateBoxes)
        self.isRad.pressed.connect(self.updateBoxes)
        self.resetButton.pressed.connect(self.reset)

        self._recursiveCount = 0

    def reset(self):
        self.fullAngleBox.setText('')
        self._fullAngle = None
        self.fullBaseBox.setText('')
        self._fullBase = None
        self.heightBox.setText('')
        self._height = None
        self.leftAngleBox.setText('')
        self._leftAngle = None
        self.leftBaseBox.setText('')
        self._leftBase = None
        self.notThetaBox.setText('')
        self._notTheta = None
        self.rightAngleBox.setText('')
        self._rightAngle = None
        self.rightBaseBox.setText('')
        self._rightBase = None
        self.someLineBox.setText('')
        self._someLine = None
        self.thetaBox.setText('')
        self._theta = None
        self.yoMamaBox.setText('')
        self._yoMama = None

    def fullAngleChanged(self):
        if len(self.fullAngleBox.text()):
            self._fullAngle = parse_expr(self.fullAngleBox.text(), locals(), self.transformations, globals())
        else:
            self._fullAngle = None
        self.updateBoxes()


    def fullBaseChanged(self):
        if len(self.fullBaseBox.text()):
            self._fullBase = parse_expr(self.fullBaseBox.text(), locals(), self.transformations, globals())
        else:
            self._fullBase = None
        self.updateBoxes()


    def heightChanged(self):
        if len(self.heightBox.text()):
            self._height = parse_expr(self.heightBox.text(), locals(), self.transformations, globals())
        else:
            self._height = None
        self.updateBoxes()


    def leftAngleChanged(self):
        if len(self.leftAngleBox.text()):
            self._leftAngle = parse_expr(self.leftAngleBox.text(), locals(), self.transformations, globals())
        else:
            self._leftAngle = None
        self.updateBoxes()


    def leftBaseChanged(self):
        if len(self.leftBaseBox.text()):
            self._leftBase = parse_expr(self.leftBaseBox.text(), locals(), self.transformations, globals())
        else:
            self._leftBase = None
        self.updateBoxes()


    def notThetaChanged(self):
        if len(self.notThetaBox.text()):
            self._notTheta = parse_expr(self.notThetaBox.text(), locals(), self.transformations, globals())
        else:
            self._notTheta = None
        self.updateBoxes()


    def rightAngleChanged(self):
        if len(self.rightAngleBox.text()):
            self._rightAngle = parse_expr(self.rightAngleBox.text(), locals(), self.transformations, globals())
        else:
            self._rightAngle = None
        self.updateBoxes()


    def rightBaseChanged(self):
        if len(self.rightBaseBox.text()):
            self._rightBase = parse_expr(self.rightBaseBox.text(), locals(), self.transformations, globals())
        else:
            self._rightBase = None
        self.updateBoxes()


    def someLineChanged(self):
        if len(self.someLineBox.text()):
            self._someLine = parse_expr(self.someLineBox.text(), locals(), self.transformations, globals())
        else:
            self._someLine = None
        self.updateBoxes()


    def thetaChanged(self):
        if len(self.thetaBox.text()):
            self._theta = parse_expr(self.thetaBox.text(), locals(), self.transformations, globals())
        else:
            self._theta = None
        self.updateBoxes()


    def yoMamaChanged(self):
        if len(self.yoMamaBox.text()):
            self._yoMama = parse_expr(self.yoMamaBox.text(), locals(), self.transformations, globals())
        else:
            self._yoMama = None
        self.updateBoxes()



    @property
    def fullAngle(self):
        # if not self._fullAngleUpToDate:
            # self._fullAngle = parse_expr(self.fullAngleBox, locals(), self.transformations, globals())
            # self.updateBoxes()
        return self._fullAngle

    @fullAngle.setter
    def fullAngle(self, expr):
        # if self._fullAngle is not None:
        self.fullAngleBox.setText(str(expr))
        self._fullAngle = expr
        # self._fullAngleUpToDate = True
        # debug(self._fullAngle)

    @property
    def fullBase(self):
        # if not self._fullBaseUpToDate:
            # self._fullBase = parse_expr(self.fullBaseBox, locals(), self.transformations, globals())
            # self.updateBoxes()
        return self._fullBase

    @fullBase.setter
    def fullBase(self, expr):
        # if self._fullBase is not None:
        self.fullBaseBox.setText(str(expr))
        self._fullBase = expr
        # self._fullBaseUpToDate = True
        # debug(self._fullBase)

    @property
    def height(self):
        # if not self._heightUpToDate:
            # self._height = parse_expr(self.heightBox, locals(), self.transformations, globals())
            # self.updateBoxes()
        return self._height

    @height.setter
    def height(self, expr):
        # if self._height is not None:
        self.heightBox.setText(str(expr))
        self._height = expr
        # self._heightUpToDate = True
        # debug(self._height)

    @property
    def leftAngle(self):
        # if not self._leftAngleUpToDate:
            # self._leftAngle = parse_expr(self.leftAngleBox, locals(), self.transformations, globals())
            # self.updateBoxes()
        return self._leftAngle

    @leftAngle.setter
    def leftAngle(self, expr):
        # if self._leftAngle is not None:
        self.leftAngleBox.setText(str(expr))
        self._leftAngle = expr
        # self._leftAngleUpToDate = True
        # debug(self._leftAngle)

    @property
    def leftBase(self):
        # if not self._leftBaseUpToDate:
            # self._leftBase = parse_expr(self.leftBaseBox, locals(), self.transformations, globals())
            # self.updateBoxes()
        return self._leftBase

    @leftBase.setter
    def leftBase(self, expr):
        # if self._leftBase is not None:
        self.leftBaseBox.setText(str(expr))
        self._leftBase = expr
        # self._leftBaseUpToDate = True
        # debug(self._leftBase)

    @property
    def notTheta(self):
        # if not self._notThetaUpToDate:
            # self._notTheta = parse_expr(self.notThetaBox, locals(), self.transformations, globals())
            # self.updateBoxes()
        return self._notTheta

    @notTheta.setter
    def notTheta(self, expr):
        # if self._notTheta is not None:
        self.notThetaBox.setText(str(expr))
        self._notTheta = expr
        # self._notThetaUpToDate = True
        # debug(self._notTheta)

    @property
    def rightAngle(self):
        # if not self._rightAngleUpToDate:
            # self._rightAngle = parse_expr(self.rightAngleBox, locals(), self.transformations, globals())
            # self.updateBoxes()
        return self._rightAngle

    @rightAngle.setter
    def rightAngle(self, expr):
        # if self._rightAngle is not None:
        self.rightAngleBox.setText(str(expr))
        self._rightAngle = expr
        # self._rightAngleUpToDate = True
        # debug(self._rightAngle)

    @property
    def rightBase(self):
        # if not self._rightBaseUpToDate:
            # self._rightBase = parse_expr(self.rightBaseBox, locals(), self.transformations, globals())
            # self.updateBoxes()
        return self._rightBase

    @rightBase.setter
    def rightBase(self, expr):
        self._rightBase = expr
        # debug(self._rightBase)
        self.rightBaseBox.setText(str(expr))
        # if self._rightBase is not None:
        # self._rightBaseUpToDate = True

    @property
    def someLine(self):
        # if not self._someLineUpToDate:
            # self._someLine = parse_expr(self.someLineBox, locals(), self.transformations, globals())
            # self.updateBoxes()
        return self._someLine

    @someLine.setter
    def someLine(self, expr):
        # if self._someLine is not None:
        self.someLineBox.setText(str(expr))
        self._someLine = expr
        # self._someLineUpToDate = True
        # debug(self._someLine)

    @property
    def theta(self):
        # if not self._thetaUpToDate:
            # self._theta = parse_expr(self.thetaBox, locals(), self.transformations, globals())
            # self.updateBoxes()
        return self._theta

    @theta.setter
    def theta(self, expr):
        # if self._theta is not None:
        self.thetaBox.setText(str(expr))
        self._theta = expr
        # self._thetaUpToDate = True
        # debug(self._theta)

    @property
    def yoMama(self):
        # if not self._yoMamaUpToDate:
            # self._yoMama = parse_expr(self.yoMamaBox, locals(), self.transformations, globals())
            # self.updateBoxes()
        return self._yoMama

    @yoMama.setter
    def yoMama(self, expr):
        # if self._yoMama is not None:
        self.yoMamaBox.setText(str(expr))
        self._yoMama = expr
        # self._yoMamaUpToDate = True
        # debug(self._yoMama)


    def rot(self):
        return 2*pi if self.isRad.isChecked else Integer(360)


    def updateBoxes(self):
        lines  = {self.someLine, self.yoMama, self.leftBase, self.rightBase, self.fullBase, self.height}
        angles = {self.leftAngle, self.rightAngle, self.fullAngle, self.theta, self.notTheta}

        netLines  = len(tuple(filter(None, lines)))
        netAngles = len(tuple(filter(None, angles)))
        # debug(netLines)
        # debug(netAngles)

        if not (netLines >= 3 or netAngles >= 3 or netAngles + netLines >= 2):
            self.equation.setText('Not enough information')
            self.solution.setText('Not enough information')
            return
        else:
            self.calculate()


    def calculate(self):
        debug('Calculating...', clr=3)
        def have(*stuff):
            for i in stuff:
                if i is None:
                    return False
            return True

        def calc(setTo:str, a, b, func=lambda x: x, op=Rational):
            def actuallyCalculate(a, b):
                try:
                    ans = func(op(a, b))
                except TypeError as err:
                    if op is Rational:
                        ans = func(div(a, b))
                    else:
                        raise err
                if self.solveSymbolic.isChecked():
                    try:
                        ans.simplify()
                    except TypeError:
                        pass
                else:
                    ans.evalf()
                return ans

            if type(a) is str:
                a = getattr(self, a, None)
            if type(b) is str:
                b = getattr(self, b, None)

            # debug(a)
            # debug(b)

            if a is not None and b is not None:
                try:
                    rtn = actuallyCalculate(a, b)
                except:
                    return
                # if isiterable(a):
                #     for ai in a:
                #         if isiterable(b):
                #             for bi in b:
                #                 rtn += actuallyCalculate(ai, bi)
                #         else:
                #             rtn += actuallyCalculate(ai, b)
                # else:
                #     if isiterable(b):
                #         for bi in b:
                #             rtn += actuallyCalculate(a, bi)
                #     else:
                #         rtn += actuallyCalculate(a, b)

                setattr(self, setTo, rtn)

        #* Calculate any missing out of left/right/full angle/base
        if have(self.leftAngle, self.rightAngle):
            self.fullAngle = self.leftAngle + self.rightAngle
        if have(self.leftAngle, self.fullAngle):
            self.rightAngle = self.fullAngle - self.leftAngle
        if have(self.rightAngle, self.fullAngle):
            self.leftAngle = self.fullAngle - self.rightAngle

        if have(self.leftBase, self.rightBase):
            self.fullBase = self.leftBase + self.rightBase
        if have(self.fullBase, self.leftBase):
            self.rightBase = self.fullBase - self.leftBase
        if have(self.fullBase, self.rightBase):
            self.leftBase = self.fullBase - self.rightBase

        self.squareAngle = Integer(90)
        triangles = (
            ('fullAngle', 'theta', 'notTheta'),
            ('rightAngle', 'theta', 'squareAngle'),
            ('leftAngle', 'notTheta', 'squareAngle'),
            # (self.yoMama, self.fullBase, self.someLine)
        )

        for a, b, c in triangles:
            if have(a, b):
                debug('have a and b')
                setattr(self, c, self.rot() - getattr(self, a) - getattr(self, b))
            if have(a, c):
                debug('have a and c')
                setattr(self, b, self.rot() - getattr(self, a) - getattr(self, c))
            if have(b, c):
                debug('have b and c')
                setattr(self, a, self.rot() - getattr(self, b) - getattr(self, c))


        angleRelations = (
            ('theta', 'height', 'rightBase', 'someLine'),
            ('rightAngle', 'rightBase', 'height', 'someLine'),
            ('leftAngle', 'leftBase', 'height', 'yoMama'),
            ('notTheta', 'height', 'leftBase', 'yoMama')
        )
        for ang, opp, adj, hyp in angleRelations:
            # Soh Cah Toa
            calc(ang, opp, hyp, asin)
            calc(ang, adj, hyp, acos)
            calc(ang, opp, adj, atan)

            if getattr(self, ang) is not None:
                theta = getattr(self, ang)
                calc(opp, hyp, sin(theta), op=Mul)
                calc(hyp, opp, sin(theta))
                calc(adj, hyp, cos(theta), op=Mul)
                calc(hyp, adj, cos(theta))
                calc(opp, adj, tan(theta), op=Mul)
                calc(adj, opp, tan(theta))


        self._recursiveCount += 1
        if self._recursiveCount < self.recursiveLimit.value():
            debug('Calculating again...', color=3)
            self.calculate()
        else:
            self._recursiveCount = 0


if __name__ == "__main__":
    app = QApplication(argv)
    win = TriangleSolver()
    win.show()
    app.exec()

""
class Test:
    def __init__(self):
        self.prop = 6
    @property
    def this(self):
        print('getter called')
        return self.prop
    @this.setter
    def this(self, to):
        print('setter called')
        self.prop = to
 '''




  """