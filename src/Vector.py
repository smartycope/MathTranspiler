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
        # a=a.normalized(); b=b.normalized()
        # r = sqrt(negPow(a.r, 2) + negPow(b.r, 2)).simplify()
        # tmp = negPow(a.r, 2) + negPow(b.r, 2)
        # isneg = tmp < 0
        # r = sqrt(abs(tmp)) * Integer(-1 if isneg else 1).simplify()
        angBetween = abs(a.theta - b.theta)
        # debug(a.theta)
        # debug(b.theta)
        # debug(angBetween)

        # r = -debug(a.r + b.r)*cos(angBetween)
        endPoint = (a.x+b.x, a.y+b.y)
        return Vector2D.fromxy(*endPoint)
        # theta = asin(endPoint[1] / r)
        # print('-----------')

        # r = r = sqrt(a.r**2 + b.r**2 + 2*a.r*b.r*cos(angBetween))
        # theta = atan2(b.r*sin(angBetween), a.r + b.r * cos(angBetween))


        return Vector2D(r, theta).simplify()

    @staticmethod
    def angleBetween(a, b):
        mag = a.x * b.x + a.y * b.y
        return acos(mag/(a.r * b.r))

    @staticmethod
    def dotProduct(a, b):
        mag = a.x * b.x + a.y * b.y
        theta = acos(mag/(a.r * b.r))
        return Vector2D(mag, theta)

    def normalize(self):
        """ Constrains the Vector to the upper quadrants and makes r negative if needed """
        try:
            if self.theta >= PI:
                self.r *= -1
            self.theta %= PI
        except:
            return

    def normalized(self):
        """ Inline version of normalize, i.e. makes and returns a normalized copy """
        try:
            if self.theta >= PI:
                r = self.r * -1
            else:
                r = self.r
            theta = self.theta % PI
            return Vector2D(r, theta)
        except:
            return Vector2D(self.r, self.theta)

    @confidence(75)
    def split(self):
        """ Returns an interable of Vectors that are added together to get this vector """
        # I think this is how this works?...
        x = Vector2D(self.x, Symbol('i'), False)
        y = Vector2D(self.y, Symbol('j'), False)
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
        if isnumber(other) or isinstance(other, (Expr, Symbol)):
            return Vector2D(self.r + other, self.theta)
        elif type(other) is Vector2D:
            return self.addHeadToTail(self, other)

    @confidence(80)
    def __sub__(self, other):
        if isnumber(other):
            return Vector2D(self.r - other, self.theta)
        else:
            return self + -other

    @confidence(80)
    def __mul__(self, other):
        if isnumber(other) or isinstance(other, (Expr, Symbol)):
            return Vector2D(self.r * other, self.theta)
        # elif type(other) is Vector2D:
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
        try:
            return Vector2D(round(self.r, prec), round(self.theta, prec))
        except TypeError:
            return Vector2D(self.r, self.theta)


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


from sympy.physics.vector import *
refFrame = ReferenceFrame('N')
