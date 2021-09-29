import sympy as sym

class Variable:
    def __init__(self, symbol: sym.Basic):
        self.symbol = symbol
        self.name = str(symbol)
        self.value = symbol
        self.valueChanged = False
        self.relationShip = '=='

    def __str__(self):
        # return self.name
        return repr(self)

    def __repr__(self):
        return f'Variable {self.symbol} = {{"{self.name}"={self.value}}}(changed={self.valueChanged})'
