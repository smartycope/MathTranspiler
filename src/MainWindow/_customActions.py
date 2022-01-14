
def addCustomFuncs(self):
    self._addCustomFunc('Basic Utilities',           'Deg to Rad',
                        'out = degrees(expr)')
    self._addCustomFunc('Basic Utilities',           'Rad to Deg',
                        'out = radians(expr)')
    self._addCustomFunc('Basic Utilities',           'Get the Function between 2 points',
                        'out = getFunctionBetweenPoints((ax, ay), (bx, by))')
    self._addCustomFunc('Basic Utilities',           'Get Quadrant of Angle',
                        'out = getQuadrant(angle=expr, isRadians=True)')
    self._addCustomFunc('Basic Utilities',           'Get Reference Angle',
                        'out = getReferenceAngle(angle=expr, isRadians=True)')
    self._addCustomFunc('Basic Utilities',           'Get Coterminal Angle',
                        'out = getCoterminalAngleOverInterval(angle=expr, interval=Interval(0, 2*pi), isRadians=True)')
    self._addCustomFunc('Basic Calculus',            'Get Continuous at',
                        'out = isContinuousAt(expr, symbol=Symbol("x"), at=S.Reals)')
    self._addCustomFunc('Basic Calculus',            'Get Equation of Tangent Line',
                        'out = getTanSlopeEquation(expr, symbol=curSymbol, symbolVal=curValue)')
    self._addCustomFunc('Basic Calculus',            'Get Slope of Tangent Line',
                        'out = getTanSlope(expr, symbol=curSymbol, symbolVal=curValue)')
    self._addCustomFunc('Basic Calculus',            'Get Equation of Normal Line',
                        'out = getNormalSlopeEquation(expr, symbol=curSymbol, symbolVal=curValue)')
    self._addCustomFunc('Basic Calculus',            'Find Average Rate of Change over Interval',
                        'out = getAvgRateOfChange(func=func, interval=Interval(-oo, oo))')
    self._addCustomFunc('Basic Calculus',            'Solve as Implicit Derivative',
                        'out = idiff(eq=expr, y=y, x=x, n=1)', 'eq is the equation. Must equal 0 (use -, not Eq() or =)', 'n is the order of the derivative')
    self._addCustomFunc('Solve For Specific Points', 'Get left/right at time',
                        'print(leftOrRight(func=func, timeVal=curSymbol))')
    self._addCustomFunc('Solve For Specific Points', 'Get times at veolcity',
                        'out = timesAtHeight(expr, timeVar=curSymbol, height=0)')
    self._addCustomFunc('Solve For Specific Points', 'Get Velocity at height',
                        'out = velocityAtHeight(expr, timeVar=curSymbol, height=0)')
    self._addCustomFunc('Solve For Specific Points', 'Get acceleration at time',
                        'out = accAtTime(expr, timeVar=curSymbol, time=curValue)')
    self._addCustomFunc('Solve For Specific Points', 'Is speeding up at time',
                        'print(isSpeedingUpAtTime(expr, timeVar=curSymbol, time=curValue))')
    self._addCustomFunc('Solve For Specific Points', 'Get Time when Instant Velocity equals Average Velocity',
                        'out = getWhenDiffEqualToAverageChange(expr, solveVar=Symbol("t"))')
    self._addCustomFunc('Special Points',            'Get Critical Points',
                        'out = getCriticalPoints(expr, var=curSymbol, order=1)')
    self._addCustomFunc('Special Points',            'Get Critical Points over Interval',
                        'out = getCriticalPointsOverInterval(expr, var=curSymbol, interval=Interval(-oo, oo), order=1)')
    self._addCustomFunc('Special Points',            'Get Min and Max over Interval',
                        'print(minMaxOverInterval(expr, var=curSymbol, interval=Interval(-oo, oo)))')
    self._addCustomFunc('Special Points',            'Find Local Extrema',
                        'print(findLocalExtrema(expr, solveVar=Symbol("x")))')
    self._addCustomFunc('Special Points',            'Find Local Extrema using Derivative',
                        'print(findLocalExtremaOverIntervalUsingDerivative(expr, solveVar=Symbol("x"), interval=Interval(-oo, oo), order=1))')
    self._addCustomFunc('Special Points',            'Find Local Extrema using Second Derivative',
                        'print(findLocalExtremaOverIntervalUsingSecondDerivative(expr, solveVar=Symbol("x"), interval=Interval(-oo, oo)))')
    self._addCustomFunc('Special Points',            'Find Absolute Extrema',
                        'print(findAbsExtremaOverInterval(expr, solveVar=Symbol("x"), interval=Interval(-oo, oo)))')
    self._addCustomFunc('Special Points',            'Get Concave Intervals',
                        'print(getConcaveIntervals(expr, solveVar=Symbol("x")))')
    self._addCustomFunc('Special Points',            'Get Inflection Points',
                        'out = getInflectionPoints(expr, solveVar=Symbol("x"))')
    self._addCustomFunc('Special Points',            'Get Intersecting Points',
                        'out = getIntersection(fx, gx, solveVar=Symbol("x"))')
    self._addCustomFunc('Areas',                     'Get Max Area of Inscribed Rectangle',
                        'out = getMaxAreaOfInscribedRect(equation=expr)', 'Make sure equation has an x and a y in it')
    self._addCustomFunc('Areas',                     'Approximate Area Under Curve',
                        'out = approxAreaUnderCurve(expr, Interval(from, to), rects=, rightPoint=True, solveVar=Symbol("x"))')
    self._addCustomFunc('Areas',                     'Get Volume of a Revolved Curve (Disk Method)',
                        'out = getVolumeOfSolidRevolution(expr, lowerbound, upperbound, solveVar=Symbol("x")).simplify()')
    self._addCustomFunc('Areas',                     'Get Area Between Functions',
                        'out = getAreaBetween(fx, gx, lowerbound=None, upperbound=None, solveVar=Symbol("x"))')
    self._addCustomFunc('Areas',                     'Get Cross Sectional Volume',
                        'out = getCrossSectionalVolume(baseFunction=expr, crossSectionalAreaEquation=Symbol("s")**2, randomlyDouble=False, quadrant=None)')
    self._addCustomFunc('Areas',                     'Get Volume of a Rotated Region',
                        'out = getVolumeOfARotatedRegionBetweenCurves(fx=expr, bounds=Interval(), gx=0, axis="x").simplify()')
    self._addCustomFunc('Areas',                     'Get Volume of a Rotated Region Using Shell Method',
                        'out = getVolumeOfARotatedRegionUsingAShell(boundingEqu=expr, limit, rotateAroundLine, secondBoundingEqu=0, secondLimit=None, areaEquation=parse_expr("2*pi*r*h"), axis="x", makeAbs=False, swapSides=False).simplify()')
    self._addCustomFunc('Physics',                     'Get the Amount of Work Done',
                        'out = integral(expr_newtons, start_meters, end_meters, var=None).simplify()')
    self._addCustomFunc('Physics',                     'Hooke\'s law (Work to move a spring)',
                        'out = integral((newtons / meters) * x, start_meters, end_meters, var=x).simplify()')
    self._addCustomFunc('Physics',                     'Get Natural Spring Length from 2 Force Measurements',
                        'out = calculateNaturalStringLengthFrom2Measurements(joules1, start1, end1, joules2, start2, end2).evalf()')
    self._addCustomFunc('Physics',                     'Pulling a Cable up a building',
                        'out = integral(x * (net_mass / length_meters) * 9.8, 0, length_meters, var=x).simplify()')
    self._addCustomFunc('Explanations',              'Solve Related Rate',
                        "out = solveRelatedRate(equation=expr, changeExpr=, solveVar=Symbol('x'))",
                        "changeExpr is the amount its changing",
                        "equation must be an Eq() statement of type Eq(<stuff>, <stuff involving solveVar>)")
    self._addCustomFunc('Explanations',              'Solve Related Rate -- instructions',
                        "# Put one of these in the box, then fill the variables with what you know (rate of change of volume is Derivative(v,t), current value, ect.)",
                        'For a Triangle, with the base changing: Eq(Derivative(volume(time), time), (1/2)*Derivative(base(time), time)*height)',
                        'Cube, with the side changing: Eq(Derivative(volume(time), time), Derivative(side(time), time)**3)',
                        'Rectangle, with any side changing: Eq(Derivative(volume(time), time), Derivative(side(time), time)*width*height)'
                        'Cylinder = V=pi*h*r^2',
                        'Cone: (1/3)*pi*(r^2)*h')
    self._addCustomFunc('Explanations',              'Mean Value Theorem',
                        'out = meanValueTheorem(expr, solveVar=Symbol("x"), interval=Interval(-oo, oo))')
    self._addCustomFunc('Explanations',              'Mean Value Theorem -- Raw',
                        'c = Symbol("c")\n'
                        'interval = Interval(, )\n'
                        'f = Function("f")\n'
                        'equ = Eq(Derivative(f(c)), (f(interval.end) - f(interval.start)) / (interval.end - interval.start))\n'
                        '# equ = equ.subs(f(interval.start), )\n'
                        '# equ = equ.subs(f(interval.end), )\n'
                        'out = equ.simplify()')
    self._addCustomFunc('Explanations',              'Get Riemann Sum',
                        'out = getRiemannSum(rational=6/6, x=6 + 6/6, expr=6 + 6/6 * ln(6 + 6/6), firstNum=6, solveVar=Symbol("x"))',
                        'R_n = rational * Sum(x * func(x)), where x is in the form of firstNum + <something>, and expr is in the form x * func(x)')
    self._addCustomFunc('Misc.',                     'Intermediate Value Theorem',
                        'out = leastPossibleVal(func=func, interval=Interval(, ))')
    self._addCustomFunc('Misc.',                     'Get all Derivatives equal to 0',
                        'out = getAllDiffsAt0(expr, interval=Interval(-oo, oo), solveVar=Symbol("x"))')
    self._addCustomFunc('Misc.',                     'Find netSigned interval',
                        'print(netSignedInterval(expr, None))')

    # self._addCustomFunc('', '', '')

def addCommonEqus(self):
    # self._addCommonEqu('Definition of an Integral',      lambda: self.equationInput.setPlainText(''))
    self._addCommonEqu('Volume and Area', 'Volume of a Cylinder',           'π * height * radius^2')
    self._addCommonEqu('Volume and Area', 'Volume of a Cone',               '(1/3) * π * height * radius^2')
    self._addCommonEqu('Volume and Area', 'Volume of a Prism',              'base * height')
    self._addCommonEqu('Volume and Area', 'Volume of a Sphere',             '(4/3) * π * radius^3')
    self._addCommonEqu('Volume and Area', 'Circumfrence of a Circle',       '2 * π * radius')
    self._addCommonEqu('Volume and Area', 'Area of a Circle',               'π * radius^2')
    self._addCommonEqu('Volume and Area', 'Area of a Traingle',             '(base * height) / 2')
    self._addCommonEqu('Volume and Area', 'Surface Area of a Sphere',       '4 * radius^2')
    self._addCommonEqu('Volume and Area', 'Lateral Surface Area of a Cone', 'π * radius * slantHeight')
    self._addCommonEqu('Volume and Area', 'Area Between 2 Functions',       'Integral(f(x) - g(x), (x, lowerbound, upperbound))')
    self._addCommonEqu('Math Formulae',   'Definition of a Derivative',     'Limit((f(x+h) - f(x)) / h, h, 0)')
    self._addCommonEqu('Math Formulae',   'Pythagorean Theorem',            'c = sqrt(a^2 + b^2)')
    self._addCommonEqu('Math Formulae',   'Slope Function',                 'y = a*x + b')
    self._addCommonEqu('Electronics',     'Resistance of a Wire',           'Resistance = resistivity * (length / crossSectionalArea)')
    self._addCommonEqu('Electronics',     'Charge or Something',            'Charge(time) = Integral(time, time_0, current(time)')
    self._addCommonEqu('Misc',            'Function of a Circle',           'x^2 + y^2 = radius^2')
    # self._addCommonEqu('', '', '')
    # Q is the charge?
    # 1 coulomb/second = 1 Amp
    # Q(t) = integral(high=t, low=t_0, i(t))
    # i = current = Amps = derivative(high=q, low=t, coulomb/second)

def addUnits(self):
    self._addUnit('Electronics', 'Current', 'I/E', 'sqrt(power / resistance)', 'power / voltage', 'voltage / resistance')
    self._addUnit('Electronics', 'Voltage', 'V', 'sqrt(power*resistance)', 'power / current', 'current * resistance')
    self._addUnit('Electronics', 'Resistance', 'R', '(voltage^2) / power', 'power / (current^2)', 'voltage / current', 'resistivity * (wireLength / crossSectionalArea)')
    self._addUnit('Electronics', 'Resisivity', 'ρ')
    self._addUnit('Electronics', 'Conductance', 'Siemens', '1/resistance')
    self._addUnit('Electronics', 'Cross-Sectional Wire Area', 'A')
    self._addUnit('Electronics', 'Wire Length', 'ℓ')
    # self._addUnit('Electronics', 'Amps',    'A', )
    self._addUnit('Electronics', 'Power',   'P', 'voltage * current', 'resistance * (current^2)', '(volts^2) / resistance')
    self._addUnit('Physics',     'Time',    't')

def addConstants(self):
    _addConstant(self, "Electronics", "Coloumb",
     '1.602176634×10^-19')


def _addCustomFunc(self, catagory, name, code, *comments):
    if catagory not in self._catagories.keys():
        self._catagories[catagory] = self.menuCustomFunctions.addMenu(catagory)

    self._catagories[catagory].addAction(name, lambda: self.runCustomFuncInCode(code, *comments))

def _addCommonEqu(self, catagory, name, equ):
    if catagory not in self._commonEquCatagories.keys():
        self._commonEquCatagories[catagory] = self.menuCommonEquations.addMenu(catagory)

    self._commonEquCatagories[catagory].addAction(name, lambda: self.equationInput.setPlainText(equ))

def _addUnit(self, catagory, name, symbol, *equs):
    if catagory not in self._unitCatagories.keys():
        self._unitCatagories[catagory] = self.menuUnits.addMenu(catagory)
    # self._unitCatagories[catagory].addAction(name + ' (' + symbol + ')', lambda: self.equationInput.setPlainText(equ)
    menu = self._unitCatagories[catagory].addMenu(name + ' (' + symbol + ')')
    menu.setToolTip(symbol)
    for i in equs:
        menu.addAction(i, lambda: self.equationInput.setPlainText(i))

def _addConstant(self, catagory, name, value):
    if catagory not in self._constantCatagories.keys():
        self._constantCatagories[catagory] = self.menuConstants.addMenu(catagory)

    self._constantCatagories[catagory].addAction(name, lambda: self.equationInput.setPlainText(value)).setToolTip(value)
