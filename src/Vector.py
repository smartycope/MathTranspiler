from sympy import *
# My own personal globally useful functions
from Cope import *

# Don't know what this is, but it seems useful?
# newr = sqrt((self.r**2) + (other.r**2) + (2*self.r*other.r*cos(newTheta)))

# Sympy's Vector class sucks, it's all "ReferenceFrame" and "Reference Angle" and complicated stuff like that.
# I just want one that will store values and equations for me, so I don't have to remember them all, cause I have a crap memory


@reprise
class Vector2D:
    def __init__(self, r=0, θ=0, radians=True):
        """ All angles are assumed to be measured from the positive x-axis. Please normalize angles to that before inputting them
            Theta is always stored interally in radians
        """
        r, θ = sympify((r, θ))
        self.r = r
        self._θ = θ if radians else rad(θ)
        self._degθ = θ if not radians else deg(θ)

    @staticmethod
    @confidence(99)
    def fromrθ(r, θ, radians=True):
        r, theta = sympify((r, θ))
        return Vector2D(r, theta, radians)
    fromrtheta = fromrθ

    @staticmethod
    @confidence(75)
    def fromxy(x, y):
        # can't divide by 0 when x is 0
        # return Vector2D(sqrt(x**2 + y**2), atan(y/x))
        return Vector2D(sqrt(x**2 + y**2), atan2(y,x))

    @staticmethod
    @confidence(65)
    def addHeadToTail(a, b):
        """ a is pointing at b, b is pointing elsewhere. Order matters! """
        r = sqrt((a.r**2) + (b.r**2)).simplify()
        endPoint = (a.x+b.x, a.y+b.y)
        theta = asin(endPoint[1] / r).simplify()
        return Vector2D(r, theta)

    @confidence(75)
    def split(self):
        """ Returns an interable of Vectors that are added together to get this vector """
        # I think this is how this works?...
        x, y = self.asxy()
        x = Vector2D(x, Symbol('i'), False)
        y = Vector2D(y, Symbol('j'), False)
        return (x, y)

    @confidence(95)
    def endPoint(self):
        return Point2D(self.x, self.y)

    @confidence(99)
    def simplify(self):
        return Vector2D(self.r.simplify(), self._θ.simplify())

    @confidence(99)
    def evalf(self):
        return Vector2D(self.r.evalf(), self._θ.evalf())

    @confidence(99)
    def __str__(self):
        try:
            return f"Vector2D(r={round(self.r.evalf(), 3)}, θ={round(self.θ.evalf(), 3)}, θ°={round(self.degθ.evalf(), 3)})"
        except TypeError:
            return f"Vector2D(r={self.r.simplify()}, θ={self.θ.simplify()}, θ°={self.degθ.simplify()})"

    @confidence(80)
    def __add__(self, other):
        if isnumber(other):
            return Vector2D(self.r + other, self.theta)
        else:
            return self.addHeadToTail(self, other)

    @confidence(80)
    def __sub__(self, other):
        if isnumber(other):
            return Vector2D(self.r - other, self.theta)
        else:
            return self + -other

    @confidence(80)
    def __mul__(self, other):
        if isnumber(other):
            return Vector2D(self.r * other, self.theta)
        else:
            todo('multiplying vectors', blocking=True)

    @confidence(80)
    def __div__(self, other):
        if isnumber(other):
            return Vector2D(self.r / other, self.theta)
        else:
            todo('dividing vectors', blocking=True)

    @confidence(90)
    def __neg__(self):
        return Vector2D(self.r, self.theta + (pi if self.theta < pi else -pi))

    @confidence(90)
    def __eq__(self, other):
        return self.r == other.r and self.θ == other.θ

    def __hash__(self):
        return hash((self.r, self._θ))

    def __round__(self, prec=3):
        return Vector2D(round(self.r, prec), round(self.theta, prec))

    @property
    def θ(self):
        return self._θ
    @θ.setter
    def θ(self, to):
        self._θ = to
    @property
    def theta(self):
        return self.θ
    @theta.setter
    def theta(self, to):
        self.θ = to

    @property
    def degθ(self):
        return deg(self.θ)
    @degθ.setter
    def degθ(self, to):
        self._θ = deg(to)
    @property
    def degTheta(self):
        return self.degθ
    @degTheta.setter
    def degTheta(self, to):
        self.degθ = to

    @property
    def x(self):
        return self.r * cos(self.θ)
    @x.setter
    def x(self, to):
        todo(blocking=True)
    @property
    def i(self):
        return self.x
    @i.setter
    def i(self, to):
        self.x = to

    @property
    def y(self):
        return self.r * sin(self.θ)
    @y.setter
    def y(self, to):
        todo(blocking=True)
    @property
    def j(self):
        return self.y
    @j.setter
    def j(self, to):
        self.y = to


DOWN = 3*pi/2
UP   = pi/2
LEFT = pi
RIGHT= 0

EARTH_GRAVITY = Vector2D(9.8, DOWN)
GRAVITY = EARTH_GRAVITY