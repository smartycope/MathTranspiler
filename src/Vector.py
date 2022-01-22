from sympy import *
from Cope import *



@reprise
class Vector:
    def __init__(self):
        pass

    @staticmethod
    def fromxy(x, y, z=0):
        x, y, z = sympify((x, y, z))
        r = sqrt(x**2 + y**2).simplify()
        theta = atan2(y, x).simplify()
        return MagVector(r, theta)


    @staticmethod
    def fromrθ(r, θ, radians=True):
        r, theta = sympify((r, θ))
        todo('this only works in 2 dimentions')
        return UnitVector(self.r * cos(self.theta).simplify(), self.r * sin(self.theta).simplify(), 0)

    def asrθ(self, evaluate=False):
        raise NotImplementedError()

    def asxy(self, evaluate=False):
        raise NotImplementedError()

    def split(self):
        raise NotImplementedError()

    def simplify(self):
        return Vector.fromxy(self.x.simplify(), self.y.simplify(), self.z.simplify())

    def evalf(self):
        return Vector.fromxy(self.x.evalf(), self.y.evalf(), self.z.evalf())

    def __add__(self, other):
        ax, ay, az = self.asxy()
        bx, by, bz = other.asxy()
        newx, newy, newz = (ax+bx, ay+by, az+bz)
        return Vector.fromxy(newx, newy, newz)

        # This is not correct. How does pythagorean theorem work in 3 dimentions?
        newr = sqrt(newx**2 + newy**2)
        # This is what is says
        newTheta = atan(newy/abs(newx))
        # This is what I suspect might be accurate
        # newTheta = atan2(newy, newx)

        #* Don't know what this is, but it seems useful?
        # newTheta = atan()
        # newr = sqrt((self.r**2) + (other.r**2) + (2*self.r*other.r*cos(newTheta)))
        return Vector.fromrθ(newr, newθ)

        #* Head to tail method

    def __sub__(self, other):
        return self + -other

    def __invert__(self):
        return Vector.fromrθ(self.r, self.θ - pi)

    def __eq__(self, other):
        raise NotImplementedError()


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

    # @property
    # i, j, k, x, y, z




class MagVector(Vector):
    def __init__(self, r, θ, 𝜙=0, radians=True):
        """ All angles are assumed to be measured from the positive x-axis. Please normalize angles to that before inputting them
            Theta is always stored interally in radians
        """
        r, θ, 𝜙 = sympify((r, θ, 𝜙))
        self.r = r
        self._θ = θ if radians else rad(θ)
        self._degθ = θ if not radians else deg(θ)
        self._𝜙 = 𝜙
        self._deg𝜙 = 𝜙 if not radians else deg(𝜙)

    @staticmethod
    def fromxy(x, y, z=0):
        x, y, z = sympify((x, y, z))
        r = sqrt(x**2 + y**2).simplify()
        theta = atan2(y, x).simplify()
        return MagVector(r, theta)

    def asxy(self, evaluate=False):
        if evaluate:
            return [self.r * cos(self.theta).evalf(), self.r * sin(self.theta).evalf(), 0]
        else:
            return [self.r * cos(self.theta).simplify(), self.r * sin(self.theta).simplify(), 0]

    def split(self):
        """ Returns an interable of Vectors that are added together to get this vector """
        # I think this is how this works?...
        x, y, z = self.asxy()
        x = MagVector(x, 0,  False)
        y = MagVector(y, 90, False)
        # ??? No idea how this works
        z = MagVector(z, Symbol('zAngle'), False)
        return (x, y, z)

    def simplify(self):
        return MagVector(self.r.simplify(), self.theta.simplify())

    def evalf(self):
        return MagVector(self.r.evalf(), self.theta.evalf())

    def __str__(self):
        return f"MagVector(r={self.r}, θ={self.θ}, θ°={self.degθ.evalf()})"

    def __add__(self, other):
        ax, ay, az = self.asxy()
        bx, by, bz = other.asxy()
        newx, newy, newz = (ax+bx, ay+by, az+bz)
        # This is not correct. How does pythagorean theorem work in 3 dimentions?
        newr = sqrt(newx**2 + newy**2)
        # This is what is says
        newTheta = atan(newy/abs(newx))
        # This is what I suspect might be accurate
        # newTheta = atan2(newy, newx)

        #* Don't know what this is, but it seems useful?
        # newTheta = atan()
        # newr = sqrt((self.r**2) + (other.r**2) + (2*self.r*other.r*cos(newTheta)))
        return MagVector(newr, newTheta)

        #* Head to tail method

    def __sub__(self, other):
        return self + -other

    def __invert__(self):
        return MagVector(self.r, self.θ - pi, False)

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

    @property
    def 𝜙(self):
        return self._𝜙
    @𝜙.setter
    def 𝜙(self, 𝜙):
        self._𝜙 = 𝜙
        self._deg𝜙 = deg(𝜙)

    @property
    def phi(self):
        return self._𝜙
    @phi.setter
    def phi(self, phi):
        self.𝜙 = phi

    @property
    def deg𝜙(self):
        return self._deg𝜙
    @deg𝜙.setter
    def deg𝜙(self, 𝜙):
        self._𝜙 = rad(𝜙)
        self._deg𝜙 = 𝜙

    @property
    def degPhi(self):
        return self._deg𝜙
    @degPhi.setter
    def degPhi(self, phi):
        self.deg𝜙 = phi


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

# Phi is the angle measured from the y axis towards the z axis
# Theta is the angle measured from the x axis towards the y axis


class UnitVector(Vector):
    def __init__(self, i, j=0, k=0):
        self.i, self.j, self.k = self.x, self.y, self.z = sympify((i, j, k))

    @staticmethod
    def fromrθ(r, θ, 𝜙=0, radians=True):
        r, theta, phi = sympify((r, θ, 𝜙))
        return UnitVector(r*cos(phi)*sin(theta),
                          r*cos(phi)*cos(theta),
                          r*sin(phi)
                         ).simplify()

    def asrθ(self, evaluate=False):
        r = sqrt(self.x**2 + self.y**2, self.z**2)
        theta = atan(self.y/abs(self.x))
        # Throwing in an abs here because why not
        phi = atan(self.z/abs(self.x))
        return MagVector(r, theta, phi)

    def split(self):
        """ Returns an interable of Vectors that are added together to get this vector """
        # I think this is how this works?...
        x, y, z = self.asxy()
        x = UnitVector(x, Symbol('i'), False)
        y = UnitVector(y, Symbol('j'), False)
        z = UnitVector(z, Symbol('k'), False)
        return (x, y, z)

    def simplify(self):
        return UnitVector(self.i.simplify(), self.j.simplify(), self.k.simplify())

    def evalf(self):
        return UnitVector(self.i.evalf(), self.j.evalf(), self.k.evalf())

    def __str__(self):
        return f"UnitVector(i/x={self.i}, j/y={self.j}, k/z={self.k})"

    def __add__(self, other):
        #* Don't know what this is, but it seems useful?
        # newTheta = atan()
        # newr = sqrt((self.r**2) + (other.r**2) + (2*self.r*other.r*cos(newTheta)))
        # return UnitVector(newr, newTheta)
        return UnitVector(self.x+other.x, self.y+other.y, self.z+other.z)

    def __sub__(self, other):
        return self + -other

    def __invert__(self):
        todo(blocking=True)
        # return Vector(self.r, self.θ - pi, False)

    def __eq__(self, other):
        return self.i == other.i and self.j == other.j and self.k == other.k


    @property
    def r(self):
        todo('this only works in 2 dimentions')
        return sqrt(self.i**2 + self.j**2).simplify()

    @property
    def θ(self):
        debug('note that uses atan2, not atan')
        return atan2(self.j, self.i).simplify()
    @property
    def theta(self):
        return self.θ

    @property
    def 𝜙(self):
        debug('note that uses atan2, not atan')
        return atan2(self.z, self.x).simplify()
    def phi(self):
        return self.𝜙

    @property
    def deg𝜙(self):
        return deg(self.𝜙)
    @property
    def degPhi(self):
        return self.θ
        return deg(self.𝜙)

    @property
    def degθ(self):
        return deg(self.θ)
    @property
    def degTheta(self):
        return self.degθ



print(MagVector(3.10, 25, radians=False).evalf().asxy())
# print(UnitVector.fromrθ(3.1, 25))

# A = UnitVector.fromrθ(3, 30, radians=False)
# B = UnitVector.fromrθ(3, 0, radians=False)
# print(A.evalf())
# print(B.evalf())
# print((A+B).evalf())