from random import randint
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from enum import Enum
import os
try:
    from sympy import sin, cos, pi, __version__
    from sympy.core.evalf import N as evalf
    _symbolic = True
except ImportError:
    from math  import sin, cos
    _symbolic = False

from math import pi as PI

from Cope import debug

ARROW_WIDTH = 5
LENGTH_MULTIPLIER = 2
PUT_VALUE_IN_MIDDLE = True
USE_FULL_NAMES = True
SIG_FIGS = 3
UNKNOWN_VECTOR_LEN = 50

def isnumber(obj):
    # return isinstance(obj, (int, float))
    try:
        float(obj)
    except:
        return False
    else:
        return True


class SystemType(Enum):
    basic = 0
    inclinedPlane = 1

class System:
    def __init__(self, sysType=SystemType.basic, incline=0):
        self.sysType = sysType
        self.incline = incline

class Body:
    def __init__(self, name, mass):
        self.name = name
        self.mass = mass
        self.forces = []

class Force:
    def __init__(self, name, magnitude, theta):
        self.name = name
        self.magnitude = magnitude
        self.theta = theta

class Direction(Enum):
    up = pi /2
    down = (3 * pi) / 2
    left = pi
    right = 0

class Freebody:
    def __init__ (self,name="empty", mass=24, sysType = SystemType.basic, incline=pi/6):
        body = Body(name, mass)
        self.system = System(sysType, incline)
        self.body = body

    def addForce(self, name, magnitude, theta):
        v = theta
        if type(v) == Direction:
            v = theta.value
        if not isnumber(theta):
            raise UserWarning(f"Theta ({theta}) can't be symbolic (even though the magnitude can be)")

        self.body.forces.append(Force(name, magnitude, v))

    def diagram(self):
        img  = Image.new( mode = "RGB", size = (size, size), color = (225,225,225))
        canvas = ImageDraw.Draw(img)
        # sm = 0
        # for force in self.body.forces:
        #     sm+=force.magnitude

        sm = sum(map(lambda f: f.magnitude, self.body.forces))

        # print(self.body.forces)
        for cnt, force in enumerate(self.body.forces):
            color = randomColor()
            force.prop = force.magnitude / (sm * 100)
            # print(force.prop)
            CreatArrow(canvas, force, color)
            ForceLegend(canvas, force, cnt, color)

        if(self.system.sysType == SystemType.basic):

            canvas.rectangle(((center*0.8, center*0.8), (center*1.2, center*1.2)),
                             outline = black)

            canvas.ellipse(((center*0.96, center*0.96), (center*1.04, center*1.04)),
                           outline = black, fill = black)

        #    img.show()
        # BROKEN FOR THETA  >= PI/5
        elif(self.system.sysType == SystemType.inclinedPlane):
            theta = self.system.incline
            theta = pi/2 - theta
            rvw = center * 0.4

            vertices = makeRectangle(rvw, rvw, theta, offset=(center, center))
            verticesPlane = makeRectangle(10, size*1.2, theta, offset=(center, center+rvw/1.9))

            canvas.polygon(vertices, fill=white, outline = black)
            canvas.polygon(verticesPlane, fill = 0)

        masstxt  = str(self.body.mass) + "kg"
        mtsw, mtsh = canvas.textsize(masstxt, font = font)
        canvas.text((center-(mtsw/2), center+(mtsh/2)), masstxt, fill = black, font = font)
        canvas.text((10,size-30), str(self.body.name), fill = black, font = font)

        return img

    def saveDiagram(self, path:str=None) -> 'path':
        img = self.diagram()
        if path is None:
            now = datetime.now()
            dtstr = now.strftime("%d-%m-%Y %H:%M:%S")
            autopath = "pyfreebody-"+self.body.name+".png"
            img.save(autopath)
            return autopath
        else:
            img.save(path)
            return path


size = 600
arrowHeadSize = 15
cw = 400 * 0.1
center = size / 2
rectW = size * 0.4

black = (0,0,0)
white = (225,225,225)

# Check if the font file is in home
home = os.path.expanduser("~")

possibleLocations = (
    home+"/pyfreebody.ttf",
    home+"/.pyfreebody/pyfreebody.ttf"
)
fontPath = None
for p in possibleLocations:
    if os.path.exists(p):
        fontPath = p
        break

if fontPath is None:
    raise UserWarning("Couldn't find a pyfreebody.ttf file anywhere. Try running the command "
                      '"mkdir ~/.pyfreebody && curl -L https://github.com/danalves24com/pyfreebody/raw/main/SourceCodePro-Regular.ttf -o ~/.pyfreebody/pyfreebody.ttf"')
    exit(0)

font = ImageFont.truetype(fontPath, 20)
fontTag = ImageFont.truetype(fontPath, 12)

def makeRectangle(l, w, theta, offset=(0,0)):
    c, s = cos(theta), sin(theta)
    rectCoords = [(l/2.0, w/2.0), (l/2.0, -w/2.0), (-l/2.0, -w/2.0), (-l/2.0, w/2.0)]
    return [(c*x-s*y+offset[0], s*x+c*y+offset[1]) for (x,y) in rectCoords]

def randomColor():
    return (randint(0, 180),
          randint(0, 180),
          randint(0, 180))

def ArrowCordinates(force):
    m = (force.prop * 100) if isnumber(force.prop) else UNKNOWN_VECTOR_LEN
    m+=rectW/2
    yc = m * sin(force.theta)
    xc = m * cos(force.theta)
    if isnumber(m) and (not isnumber(yc) or not isnumber(xc)):
        raise UserWarning(f"Theta ({force.theta}) can't be symbolic (even though the magnitude can be)")
    if _symbolic:
        return ((evalf(center), evalf(center)), (evalf(center+ xc), evalf(center - yc)))
    else:
        return ((center, center), (center+ xc, center - yc))

def tagCordinates(arrowCords):
    x, y = arrowCords[1][0], arrowCords[1][1]
    return ((x*1.06), (y*1.06))

# faulty
def ArrowHeadCordinates(arrowCords):
    x, y = arrowCords[1][0], arrowCords[1][1]
    dx = arrowHeadSize * cos(pi/4)
    dy = (2 * arrowHeadSize * sin(pi/4))/2
    # print(dx, dy)
    # print(x, y)
    return (
        (x-dx, y + dy),
        (x+dx, y - dy),
        (x-arrowHeadSize, y + arrowHeadSize)
    )

def ForceLegend(canvas, force, i, color):
    mag = str(round(force.magnitude, SIG_FIGS)) + 'N' if isnumber(force.magnitude) else str(force.magnitude)

    text = f"{'Force' if force.name == '' else force.name} = {mag}"
    canvas.text((5,5+i*20), text, fill = color, font = font)

def CreatArrow(canvas, force, color):
    mag = str(round(force.magnitude, SIG_FIGS)) + 'N' if isnumber(force.magnitude) else str(force.magnitude)

    arrowBase = ArrowCordinates(force)
    canvas.line(arrowBase, width=ARROW_WIDTH, fill = color)
    name = force.name if USE_FULL_NAMES else (force.name[0:1]).lower()
    if name == '':
        name = 'F'
    if PUT_VALUE_IN_MIDDLE:
        label = f"{name} = {mag}"
    else:
        label = "F" + name
    canvas.text(tagCordinates(arrowBase), label, font=fontTag, fill = black)
    #canvas.polygon(ArrowHeadCordinates(arrowBase), fill = color)
