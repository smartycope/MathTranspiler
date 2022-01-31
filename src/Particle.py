from Cope import *
from sympy import *
from Vector import Vector2D

# confidence is just a function decorator that I wrote that warns you when you call a function you're not sure will work
#   (it's half just for the programmer anyway)
# MappingList is one of my own classes that lets you treat a list of things as a single unit (i.e. MappingList([1, 2, 3]) + 3 -> [4, 5, 6])

class Particle2D:
    # I'm too lazy to do it this way and use self.positionEquation.subs() all the time
    # I have deep, intense loathing for single letter variables ever since I tried to read 25 yr. old C code.
    positionEquation = parse_expr('Eq(finalPos, startingPos + (initialVelocity * time) - (1/2) * constAccel * time**2)')
    def __init__(self, mass=1, position=Point2D(0, 0), velocity=Vector2D(), constXAccel=0, constYAccel=9.8):
        self.mass = mass
        self.position = position
        self.velocity = velocity
        # Negative, because we're subtracting all that stuff to get just x and y on the other side
        # Actually, just kidding, I guess that's not how it works?
        self.constXAccel = constXAccel
        self.constYAccel = constYAccel

    def impulse(self, forceVector):
        """ Erases whatever current velocity is around and adds a new velocity """
        self.velocity = forceVector
        # self.initalVelocity = self.velocity

    @confidence(75)
    def getAdjustedVelocity(self, time):
        x = self.position.x + (self.velocity.x * time) - (1/2)*self.constXAccel * (time ** 2)
        y = self.position.y + (self.velocity.y * time) - (1/2)*self.constYAccel * (time ** 2)
        # I HATE EVERYTHING AND EVERYONE
        # I JUST SPENT AN HOUR DEBUGGING AN EQUATION BECAUSE -100.000000000 != -100 AND STUPID FLOAT ERRORS AND YOU ALL SUCK
        x = round(float(x), 10)
        y = round(float(y), 10)
        return Vector2D.fromxy(x, y)

    @confidence(75)
    def getPositionAtTime(self, time:'seconds'):
        return self.getAdjustedVelocity(time).endPoint()

    @confidence(85)
    def getTimeToLanded(self):
        return MappingList(self.getTimesWhenYEquals(0)).evalf()

    @confidence(70)
    def getDisplacementToLanded(self):
        return ensureNotIterable(MappingList(self.getXDisplacementWhenYEquals(0)).evalf())

    @confidence(85)
    def getTimesWhenYEquals(self, value):
        time = symbols('time')
        return solve(Eq(self.position.y + (self.velocity.y * time) - ((1/2)*self.constYAccel * (time ** 2)), value), time)

    @untested
    def getTimesWhenXEquals(self, value):
        time = symbols('time')
        return solve(Eq(self.position.y + (self.velocity.y * time) - ((1/2)*self.constYAccel * (time ** 2)), value), time)

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
