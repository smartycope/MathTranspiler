from sympy import *
from Cope import *

@reprise
class Vector:
    def __init__(self, r, θ, radians=True):
        """ All angles are assumed to be measured from the positive x-axis. Please normalize angles to that before inputting them
            Theta is always stored interally in radians
        """
        self.r = r
        self._θ = θ if radians else rad(θ)
        self._degθ = θ if not radians else deg(θ)

    @staticmethod
    def fromxy(x, y):
        x, y = sympify(x), sympify(y)
        r = sqrt(x**2 + y**2).simplify()
        theta = atan2(y, x).simplify()
        return Vector(r, theta)

    def toxy(self, evaluate=False):
        if evaluate:
            return [self.r * cos(self.theta).evalf(), self.r * sin(self.theta).evalf()]
        else:
            return [self.r * cos(self.theta).simplify(), self.r * sin(self.theta).simplify()]

    def split(self):
        """ Returns an interable of Vectors that are added together to get this vector """
        # I think this is how this works?...
        x, y = self.toxy()
        x = Vector(x, 0,  False)
        y = Vector(y, 90, False)
        return (x, y)

    # def addHeadToTail(self, vector):
    #     r = sqrt((self.r**2) + (vector.r**2))
    #     theta = None
    #     return Vector(r, theta)
    #     # raise NotImplementedError()

    def simplify(self):
        return Vector(self.r.simplify(), self.theta.simplify())

    def evalf(self):
        return Vector(self.r.evalf(), self.theta.evalf())

    def __str__(self):
        return f"Vector(r={self.r}, θ={self.θ}, θ°={self.degθ.evalf()})"

    def __add__(self, other):
        todo()
        raise NotImplementedError()
        # myX, myY = self.split()
        # theirX, theirY = other.split()
        # r = myX.r + theirX.r

        # angleBetween = ?
        # r = sqrt((self.r**2) + (other.r**2) + (2*self.r*other.r*cos(angleBetween)))
        # return Vector(r, theta)

        #* Head to tail method

    def __sub__(self, other):
        return self + -other

    def __invert__(self):
        return Vector(self.r, self.θ - pi, False)

    def __eq__(self, other):
        return self.r == other.r and self.θ == other.θ


    @property
    def θ(self):
        return self._θ

    @θ.setter
    def θ(self, θ):
        self._θ = θ
        self._degθ = deg(θ)

    @property
    def theta(self):
        return self._θ

    @theta.setter
    def theta(self, theta):
        self.θ = theta

    @property
    def degθ(self):
        return self._degθ

    @degθ.setter
    def degθ(self, θ):
        self._θ = rad(θ)
        self._degθ = θ

    @property
    def degTheta(self):
        return self._degθ

    @degTheta.setter
    def degTheta(self, theta):
        self.degθ = theta



def addHeadToTail(startVector, endVector):
    """ startVector is pointing at endVector, endVector is pointing elsewhere. Order matters! """
    a = startVector
    b = endVector
    r = sqrt((a.r**2) + (b.r**2)).simplify()
    ax, ay = a.toxy()
    bx, by = b.toxy()
    endPoint = (ax+bx, ay+by)
    theta = asin(endPoint[1] / r).simplify()
    return Vector(r, theta)
