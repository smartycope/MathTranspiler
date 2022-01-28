from Cope import *
from sympy import *
from Vector import Vector2D

class Particle2D:
    # positionEquation = Eq(Symbol('finalPos'), Symbol('startingPos') + (Symbol('initalVelocity') *
    # Symbol('time')) - (Rational(.5) * Symbol('acceleration') * (Symbol('time')**2))
    positionEquation = parse_expr('Eq(finalPos, startingPos + (initialVelocity * time) - (1/2) * constAccel * time**2)')
    def __init__(self, mass=1, position=Point2D(0, 0), velocity=Vector2D()):
        self.mass = mass
        self.position = position
        self.velocity = velocity
        self.constXAccel = 0
        self.constYAccel = 9.8

    def impulse(self, forceVector):
        """ Erases whatever current velocity is around and adds a new velocity """
        self.velocity = forceVector
        # self.initalVelocity = self.velocity

    @untested
    @confidence(50)
    def getAdjustedVelocity(self, time):
        # Negative, because we're subtracting all that stuff to get just x and y on the other side
        # Actually, just kidding, I don't think that's how it works?
        x = (self.position.x + (self.velocity.x * time) - ((1/2)*self.constXAccel * (time ** 2)))
        y = (self.position.y + (self.velocity.y * time) - ((1/2)*self.constYAccel * (time ** 2)))
        return Vector2D.fromxy(x, y)

    @untested
    def getPositionAtTime(self, time:'seconds'):
        adj = self.getAdjustedVelocity(time, self.constXAccel, self.constYAccel)
        return (adj.x, adj.y)

    # def getFinalPosition(self, constXAccel=0, constYAccel=gravity):

    def getTimeToLanded(self):
        return MappingList(self.getTimesWhenYEquals(0)).evalf()

    @confidence(50)
    @untested
    def getTimesWhenYEquals(self, value):
        time = symbols('time')
        return solve(debug(Eq(self.position.y + (self.velocity.y * time) - ((1/2)*self.constYAccel * (time ** 2)), value)), time)

    @confidence(20)
    @untested
    def getTimesWhenXEquals(self, value):
        return solve(Eq(self.position.y + (self.velocity.y * time) - ((1/2)*self.constYAccel * (time ** 2)), value), time)


projectile = Particle2D(velocity=Vector2D(50, 40, False), position=Point2D(0, 75))
time = projectile.getTimeToLanded()
debug(time)
adj = projectile.getAdjustedVelocity(abs(time[0]))
debug(round(adj.x, 3))
debug(round(adj.y, 3))
