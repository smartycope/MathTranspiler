from sympy import *
# My own personal globally useful functions
from Cope import *
from typing import SupportsInt

# Phi is the angle measured from the y axis towards the z axis
# Theta is the angle measured from the x axis towards the y axis

 #* Don't know what this is, but it seems useful?
# newr = sqrt((self.r**2) + (other.r**2) + (2*self.r*other.r*cos(newTheta)))
# return Vector(newr, newTheta)

# Sympy's Vector class sucks, it's all "ReferenceFrame" and "Reference Angle" and complicated stuff like that.
# I just want one that will store values and equations for me, so I don't have to remember them all

# ≈θ𝜙°Ω
'''
class Vector:
    def __init__(self, i, j=0, k=0):
        self.i, self.j, self.k = self.x, self.y, self.z = sympify((i, j, k))


    # polar coordinates are 2d, spherical coordinates are 3d

    @staticmethod
    @confidence(50)
    def fromrθ(r, θ, 𝜙=0, radians=True):
        r, theta, phi = sympify((r, θ, 𝜙))
        if phi == 0:
            # This is what I looked up, but it doesn't seem right...
            return Vector(r*cos(phi)*sin(theta),
                          r*cos(phi)*cos(theta),
                          r*sin(phi)).simplify()
        else:
            return Vector(r*cos(theta),
                          r*sin(theta),
                          0).simplify()
    fromrtheta = fromrθ

    @confidence(30)
    def split(self):
        """ Returns an interable of Vectors that are added together to get this vector """
        # I think this is how this works?...
        x = UnitVector(self.x, Symbol('i'), False)
        y = UnitVector(self.y, Symbol('j'), False)
        z = UnitVector(self.z, Symbol('k'), False)
        return (x, y, z)

    @confidence(99)
    def simplify(self):
        # Just for convenience
        return Vector(self.i.simplify(), self.j.simplify(), self.k.simplify())

    @confidence(99)
    def evalf(self):
        # Just for convenience
        return Vector(self.i.evalf(), self.j.evalf(), self.k.evalf())

    @confidence(90)
    def __str__(self):
        # Because I want things to be *more* complicated than they already are
        # return f"Vector(i/x={self.i}, j/y={self.j}, k/z={self.k}, r={self.r}, θ={self.θ}, 𝜙={self.𝜙})"
        return f"""Vector( i/x={self.i}\n\tj/y={self.j}\n\tk/z={self.k}\n\tr={self.r}\n\tθ={self.θ}, θ°={self.degθ}\n\t𝜙={self.𝜙}, 𝜙°={self.deg𝜙}\n)"""

    @confidence(65)
    def __add__(self, other):
        # I'm confident that this way does what it's supposed to, I'm not confident that this is the way you're supposed to use by default
        return Vector(self.x+other.x, self.y+other.y, self.z+other.z)

    @confidence(75)
    def __sub__(self, other):
        return self + -other

    @confidence(85)
    def __mul__(self, other):
        # If it's an int or a float (I think this i show SupportsInt works??), then just multiply all the components by it
        if SupportsInt(other):
            return Vector(self.i * other, self.j * other, self.k * other)
        else:
            todo(blocking=True)

    @confidence(50)
    def __invert__(self):
        # I'm not sure which makes more sense
        return Vector(-self.i, -self.k, -self.k)
        # return Vector.fromrθ(self.r, self.θ - pi, self.phi - pi)

    @confidence(99)
    def __eq__(self, other):
        return self.i == other.i and self.j == other.j and self.k == other.k

    @property
    @confidence(75)
    def r(self):
        return sqrt(self.x**2 + self.y**2, self.z**2).simplify()

    @property
    @confidence(30)
    def θ(self):
        # This *seems* like an atan2 thing, but that's not what the book says.
        return atan(self.y/abs(self.x)).simplify()
        return atan2(self.y, self.x).simplify()
    @property
    def theta(self):
        return self.θ

    @property
    @confidence(20)
    def 𝜙(self):
        # I reasoned this out myself, which means I don't remember how it works, but I did at one point.
        # abs(C) = sqrt(c_x^2 + C_y^2)
        # atan(y/x)
        return atan(self.z/abs(self.x)).simplify()
        return atan2(self.z, self.x).simplify()
    @property
    def phi(self):
        return self.𝜙

    @property
    @confidence(80)
    def deg𝜙(self):
        return deg(self.𝜙).evalf()
    @property
    def degPhi(self):
        # return self.θ
        return deg(self.𝜙)

    @property
    @confidence(80)
    def degθ(self):
        return deg(self.θ).evalf()
    @property
    def degTheta(self):
        return self.degθ

@confidence(65)
def addHeadToTail(startVector, endVector):
    """ startVector is pointing at endVector, endVector is pointing elsewhere. Order matters! """
    todo('this only works in 2 dimentions')
    a, b = (startVector, endVector)

    r = sqrt((a.r**2) + (b.r**2)).simplify()
    endPoint = (a.x+b.x, a.y+b.y, a.x+b.z)
    theta = asin(endPoint[1] / r).simplify()
    # Don't know how phi fits into all this
    phi = 0
    return Vector.fromrθ(r, theta, phi)
'''

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
        return Vector2D(sqrt(x**2 + y**2), atan(y/x))

    @staticmethod
    @confidence(-1)
    def addTailToTail(v1, v2):
        pass

    @staticmethod
    @confidence(65)
    def addHeadToTail(startVector, endVector):
        """ startVector is pointing at endVector, endVector is pointing elsewhere. Order matters! """
        a = startVector
        b = endVector
        r = sqrt((a.r**2) + (b.r**2)).simplify()
        ax, ay = a.asxy()
        bx, by = b.asxy()
        endPoint = (ax+bx, ay+by)
        theta = asin(endPoint[1] / r).simplify()
        return MagVector(r, theta)

    @confidence(75)
    def split(self):
        """ Returns an interable of Vectors that are added together to get this vector """
        # I think this is how this works?...
        x, y = self.asxy()
        x = Vector2D(x, Symbol('i'), False)
        y = Vector2D(y, Symbol('j'), False)
        return (x, y)

    @confidence(99)
    def simplify(self):
        return Vector2D(self.r.simplify(), self._θ.simplify())

    @confidence(99)
    def evalf(self):
        return Vector2D(self.r.evalf(), self._θ.evalf())

    @confidence(99)
    def __str__(self):
        return f"Vector2D(r={round(self.r.evalf(), 3)}, θ={round(self.θ.evalf(), 3)}, θ°={round(self.degθ.evalf(), 3)})"

    # This assumes tail-tail adding
    @confidence(80)
    def __add__(self, other):
        #* Don't know what this is, but it seems useful?
        # newTheta = atan()
        # newr = sqrt((self.r**2) + (other.r**2) + (2*self.r*other.r*cos(newTheta)))
        # return UnitVector(newr, newTheta)
        return self.addTailToTail(self, other)

    @confidence(90)
    def __sub__(self, other):
        return self + -other

    @confidence(-1)
    def __mul__(self, other):
        if SupportsInt(other):
            return Vector2D(self.i * other, self.j * other, self.k * other)

    @confidence(0)
    def __invert__(self):
        return Vector(-self.i, -self.k, -self.k)
        return Vector.fromrθ(self.r, self.θ - pi, self.phi - pi)

    @confidence(90)
    def __eq__(self, other):
        return self.r == other.r and self.θ == other.θ

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
        return self.r * sin(self.θ)
    @x.setter
    def x(self, to):
        todo(blocking=True)
    @property
    def i(self):
        return self.x
    @x.setter
    def i(self, to):
        self.x = to

    @property
    def y(self):
        return self.r * cos(self.θ)
    @x.setter
    def y(self, to):
        todo(blocking=True)
    @property
    def j(self):
        return self.y
    @x.setter
    def j(self, to):
        self.y = to


    # @property
    # def r(self):
    #     return sqrt(self.x**2 + self.y**2, self.z**2)

    # @property
    # def θ(self):
    #     return atan(self.y/abs(self.x)).simplify()
    #     return atan2(self.y, self.x).simplify()
    # @property
    # def theta(self):
    #     return self.θ

    # @property
    # def degθ(self):
    #     return deg(self.θ)
    # @property
    # def degTheta(self):
    #     return self.degθ
