import sympy as sym
from sympy.core.function import AppliedUndef, UndefinedFunction
from sympy.core.numbers import One
One.name = 'one'
# class _One(One):
    # name='one'

funcTypes =  (AppliedUndef, UndefinedFunction) #, Function, WildFunction)

class Variable:
    def __init__(self, symbol: sym.Basic, name='', value=None, order=50, unit=One(), prefix=One(), _type=None):
        self.symbol = symbol
        self.name = str(symbol) if not len(name) else name
        self._value = (symbol if not value else value)
        self.valueChanged = False
        self.relationship = '=='
        self.type = type(symbol) if _type is None else _type
        self.substitutionOrder = order
        self.prefix = prefix
        self.unit = unit

    # def isFunc(self):
        # return isinstance(self.symbol, funcTypes)

    @property
    def value(self):
        return self._value * (self.unit * self.prefix)

    @value.setter
    def value(self, to):
        self._value = to

    def __str__(self):
        # if isinstance(self.symbol, funcTypes):
            # return (str(self.symbol) if not self.valueChanged else self.name) + '(x)'
        # else:
        # return str(self.symbol) if not self.valueChanged else self.name
        return self.name
        # return repr(self)

    def __repr__(self):
        return f'Variable {type(self.symbol)} {self.symbol} = {{"{self.name}"={self.value}}}(changed={self.valueChanged})'
