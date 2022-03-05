from random import randint
import clipboard
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from enum import Enum
from PyQt5.QtWidgets import QApplication
from time import sleep
from PyQt5.QtGui import QPixmap, QImage
import os
try:
    from sympy import sin, cos, pi, atan, atan2, deg, sympify
    from sympy.core.evalf import N as evalf
    _symbolic = True
except ImportError:
    from math  import sin, cos, degrees as deg
    _symbolic = False

from math import pi as PI

from Cope import debug

# def copyImage(f):
    # header = '<img src=\'data:image/png;base64,
    # tail = "' />"
    # data =
    # runCmd(f'TMP={f}; echo "<img src=\'data:image/png;base64,"$(base64 -w0 "$TMP")"\' />" | xclip -selection clipboard -t text/html')
    # assert(os.path.exists(f), "file does not exist")
    # image = gtk.gdk.pixbuf_new_from_file(f)

    # clipboard = gtk.clipboard_get()
    # clipboard.set_image(image)
    # clipboard.store()

ARROW_WIDTH = 5
LENGTH_MULTIPLIER = 2
PUT_VALUE_IN_MIDDLE = True
USE_FULL_NAMES = True
SIG_FIGS = 3
UNKNOWN_VECTOR_LEN = 50
BACKGROUND_COLOR = (255,255,255)
REQUIRE_CUSTOM_FONT = False
TAG_OFFSET = -1.5
TAG_RANDOMNESS = 30
ARROW_HEAD_SIZE = 8

size = 600
cw = 400 * 0.1
center = size / 2
rectW = size * 0.4

black = (0,0,0)
white = (225,225,225)

# Check if the font file is in home
home = os.path.expanduser("~")

possibleLocations = (
    home+"/pyfreebody.ttf",
    home+"/.pyfreebody/pyfreebody.ttf",
    # You have matplotlib installed?
    home+"/.local/lib/python3.9/site-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans.ttf",
    # How bout pygame?
    home+"/.local/lib/python3.9/site-packages/pygame/examples/data/sans.ttf",
)

fontPath = None
for p in possibleLocations:
    if os.path.exists(p):
        fontPath = p
        break

if fontPath is None:
    if REQUIRE_CUSTOM_FONT:
        raise UserWarning("Couldn't find a pyfreebody.ttf file anywhere. Try running the command "
                          '"mkdir ~/.pyfreebody && curl -L https://github.com/danalves24com/pyfreebody/raw/main/SourceCodePro-Regular.ttf -o ~/.pyfreebody/pyfreebody.ttf"')
    else:
        font = ImageFont.FreeTypeFont()
        fontTag = ImageFont.FreeTypeFont()
else:
    font = ImageFont.truetype(fontPath, 20)
    fontTag = ImageFont.truetype(fontPath, 12)


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
        img  = Image.new(mode="RGB", size=(size, size), color=BACKGROUND_COLOR)
        canvas = ImageDraw.Draw(img)
        sm = sum(map(lambda f: f.magnitude, self.body.forces))

        if(self.system.sysType == SystemType.basic):
            canvas.rectangle(((center*0.8, center*0.8), (center*1.2, center*1.2)),
                             outline=black, fill=white)

            # The ellipse is stupid
            # canvas.ellipse(((center*0.96, center*0.96), (center*1.04, center*1.04)),
            #                outline = black, fill = black)

        # BROKEN FOR THETA  >= PI/5
        elif(self.system.sysType == SystemType.inclinedPlane):
            theta = self.system.incline
            theta = pi/2 - theta
            rvw = center * 0.4

            vertices = makeRectangle(rvw, rvw, theta, offset=(center, center))
            verticesPlane = makeRectangle(10, size*1.2, theta, offset=(center, center+rvw/1.9))

            canvas.polygon(vertices, fill=white, outline = black)
            canvas.polygon(verticesPlane, fill = 0)

        for cnt, force in enumerate(self.body.forces):
            color = randomColor()
            # Adjust the length of the line
            force.prop = force.magnitude / (sm * 100)
            CreateArrow(canvas, force, color)
            ForceLegend(canvas, force, cnt, color)

        masstxt  = str(self.body.mass) + ("kg" if isnumber(self.body.mass) else '')
        mtsw, mtsh = canvas.textsize(masstxt, font=font)
        canvas.text((center-(mtsw/2), center+(mtsh/2)), masstxt, fill = black, font=font)
        canvas.text((10,size-30), str(self.body.name), fill = black, font=font)

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

    def copyDiagram(self):
        path = '/tmp/__diagram.png'
        self.saveDiagram(path)
        app = QApplication([])
        app.clipboard().setPixmap(QPixmap(path))
        # app.clipboard().setText('testing--it worked!')
        print('copied!')
        sleep(1)
        return

        # pixmap = self.canvas.grab()
        # header = "<img src='data:image/png;base64,"
        # tail = "' />"`¢`
        # img = self.diagram()
        # data = str(img.tobytes())
        # clipboard.copy(header + data + tail)
        # self.saveDiagram(path)
        # copyImage(path)

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
    x, y = arrowCords[1]
    centerx, centery = arrowCords[0]
    theta = atan2(y-centery, x-centerx)
    dx = TAG_OFFSET*sin(theta)
    dy = TAG_OFFSET*cos(theta)
    dx += randint(0, TAG_RANDOMNESS)
    dy += randint(0, TAG_RANDOMNESS)
    return (x + dx, y + dy)

def ArrowHeadCordinates(arrowCords):
    x, y = arrowCords[1]
    centerx, centery = arrowCords[0]
    hyp = ARROW_HEAD_SIZE
    # Not sure why subtracting and then adding pi/4 makes it work, but it works, don't question it.
    theta = (pi/4) - atan2(y-centery, x-centerx)

    # debug(arrowCords)
    dx = hyp*cos(theta + pi/4)
    dy = hyp*sin(theta + pi/4)
    # debug(x, clr=3)
    # debug(y)
    # debug(dx)
    # debug(dy)
    return (
        (x-dx, y + dy),
        (x+dx, y - dy),
        (x + hyp*sin(theta + pi/4), y + hyp*cos(theta + pi/4))
    )

def ForceLegend(canvas, force, i, color):
    mag   = str(round(force.magnitude,  SIG_FIGS)) + 'N' if isnumber(force.magnitude) else str(force.magnitude)
    theta = str(round(deg(force.theta), SIG_FIGS)) + "°" if isnumber(force.theta)     else str(deg(force.theta))
    text = f"{'Force' if force.name == '' else force.name} = {mag} @ {theta}"
    canvas.text((5,5+i*20), text, fill=color, font=font)

def CreateArrow(canvas, force, color):
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
    # Make it an arrow, not just a line
    canvas.polygon(ArrowHeadCordinates(arrowBase), fill=color)
    # Add teh text
    canvas.text(tagCordinates(arrowBase), label, fill=black, font=fontTag)
