from Cope import *
from sympy import *
import clipboard
from io import StringIO, BytesIO
from Vector import Vector2D, EARTH_GRAVITY
from clipboard import copy
# Just using this to export nice looking free-body diagrams
try:
    from pyfreebody import Freebody, Direction, SystemType
except ImportError:
    print("Importing system pyfreebody instead of the local pyfreebody")
    from pyfreebody.pyfreebody import Freebody, Direction, SystemType

# confidence is just a function decorator that I wrote that warns you when you call a function you're not sure will work
# MappingList is one of my own classes that lets you treat a list of things as a single unit (i.e. MappingList([1, 2, 3]) + 3 -> [4, 5, 6])

class Particle2D:
    # I'm too lazy to do it this way and use self.positionEquation.subs() all the time
    # I have deep, intense loathing for single letter variables ever since I tried to read 25 yr. old C code.
    positionEquation = parse_expr('Eq(finalPos, startingPos + (initialVelocity * time) - (1/2) * constAccel * time**2)')
    def __init__(self, mass=1, pos=Point2D(0, 0), gravity:Vector2D=EARTH_GRAVITY, includeNormal=False, incline:'radians'=0, name=''):
        """ gravity must always be specified, even if it's just and empty Vector2D() """
        self.mass = mass
        self.position = pos
        self.forces = []
        self.forceNames = []
        self.incline = incline
        self.name = name
        # Because Gravity is in meters/s^2, not Newtons
        gravityForce = gravity * self.mass
        self.addForce(round(gravityForce, 3), "Gravity")
        self.constAccel = self.forces[0]
        if includeNormal:
            normal = Vector2D(round(gravityForce.r, 3), incline + pi/2)
            self.addForce(normal, "Normal")

    def copyDiagram(self, name=None):
        img = self.diagram(name)
        clipboard.copy(img.tobytes().decode())


    def showDiagram(self, name=None):
        self.diagram(name).show()

    def diagram(self, name=None, includeNet=True):
        diagram = Freebody(name if name is not None else self.name, self.mass, SystemType.basic if self.incline == 0 else SystemType.inclinedPlane, self.incline)
        # Assume constAccel is gravity if it's pointed down
        # if includeGravity:
        #     diagram.addForce('Gravity' if self.constAccel.theta == 3*pi/2 else '', self.constAccel.r, self.constAccel.theta)
        # if includeNormalForce:
        #     diagram.addForce('Normal'  if self.constAccel.theta == 3*pi/2 else '', self.constAccel.r, (-self.constAccel).theta)
        if includeNet:
            try:
                diagram.addForce('Net', self.netForce().r, self.netForce().theta)
            except UserWarning:
                print(f"Can't add Net Force to diagram: symbolic variables still present")

        for force, name in zip(self.forces, self.forceNames):
            diagram.addForce(name, force.r, force.theta)
        return diagram.diagram()

    def netForce(self, name=None):
        if not len(self.forces):
            return Vector2D()
        else:
            # return sum(self.forces)
            net = self.forces[0]
            for i in self.forces[1:]:
                net += i
            return net

    def addForce(self, force, name=''):
        self.forces.append(force)
        self.forceNames.append(name)

    def velocity(self, time):
        # If F=ma, and a=v/t, then v=F*t/m
        return self.netForce() * (time / self.mass)

    def acceleration(self):
        return self.netForce() / self.mass

    @confidence(75)
    def getAdjustedVelocity(self, time):
        """ Gets the velocity at a specific time """
        x = self.position.x + (self.velocity(time).x * time) - (1/2)*self.constAccel.x * (time ** 2)
        y = self.position.y + (self.velocity(time).y * time) - (1/2)*self.constAccel.y * (time ** 2)
        # I JUST SPENT AN HOUR DEBUGGING AN EQUATION BECAUSE -100.000000000 != -100 AND STUPID FLOAT ERRORS AND YOU ALL SUCK
        x = round(float(x), 10)
        y = round(float(y), 10)
        return Vector2D.fromxy(x, y)

    @confidence(75)
    def getPositionAtTime(self, time:'seconds'):
        return self.getAdjustedVelocity(time).endPoint()

    @confidence(85)
    def getTimeToLanded(self):
        return ensureNotIterable(MappingList(self.getTimesWhenYEquals(0))).evalf()

    @confidence(70)
    def getDisplacementToLanded(self):
        return ensureNotIterable(MappingList(self.getXDisplacementWhenYEquals(0)).evalf())

    @confidence(85)
    def getTimesWhenYEquals(self, value):
        time = symbols('time')
        return solve(Eq(self.position.y + (self.velocity.y * time) - ((1/2)*self.constAccel.y * (time ** 2)), value), time)

    @untested
    def getTimesWhenXEquals(self, value):
        time = symbols('time')
        return solve(Eq(self.position.y + (self.velocity.y * time) - ((1/2)*self.constAccel.y * (time ** 2)), value), time)

    @confidence(70)
    def getXDisplacementWhenYEquals(self, value):
        # get all the times x == value, then get the positions at those times, and get the displacement from where we started (and use set to remove duplicates)
        # This would be 1 line IF -100.0000000 == -100 AND I HATE EVERYONE WHY CANT PEOPLE WRITE WORKING CODE AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
        rtn = set()
        for time in ensureIterable(self.getTimesWhenYEquals(value)):
            try:
                rtn.add(abs(self.getPositionAtTime(time).x - self.position.x))
            except: pass
        return ensureNotIterable(rtn)

    @untested
    def getYDisplacementWhenXEquals(self, value):
        pass

    @untested
    def getInitialVelocityFromDisplacement(self, finalPoint:Point2D):
        pass





# ≈θ𝜙°Ω±𝛼𝚫𝜔𝛑
# 𝜔 = average angular speed == 𝚫θ/𝚫t (θ in radians)
# 𝛼 = angular acceleration  == 𝚫𝜔/𝚫t
