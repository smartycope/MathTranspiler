import sympy as sym
from sympy.core.function import AppliedUndef, UndefinedFunction

funcTypes =  (AppliedUndef, UndefinedFunction) #, Function, WildFunction)

class Variable:
    def __init__(self, symbol: sym.Basic, name=None, value=None):
        self.symbol = symbol
        self.name = str(symbol) if not name else name
        self.value = symbol if not value else value
        self.valueChanged = False
        self.relationship = '=='

    def isFunc(self):
        return isinstance(self.symbol, funcTypes)

    def __str__(self):
        # if isinstance(self.symbol, funcTypes):
            # return (str(self.symbol) if not self.valueChanged else self.name) + '(x)'
        # else:
        # return str(self.symbol) if not self.valueChanged else self.name
        return self.name
        # return repr(self)

    def __repr__(self):
        return f'Variable {type(self.symbol)} {self.symbol} = {{"{self.name}"={self.value}}}(changed={self.valueChanged})'
