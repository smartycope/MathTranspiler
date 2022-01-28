import json

searchMethod = 'and'

eqFile = '../assets/commonEquations.json'
unitsFile = '../assets/units.json'

with open(eqFile, 'r') as f:
    equations = json.load(f)
with open(unitsFile, 'r') as f:
    unitEquations = json.load(f)

searchfor = input('Search Equations for: ')
keys = searchfor.split(' ')
possibles = {}

def searchAndAddString(s, eq):
    if searchMethod == 'or':
        for key in keys:
            if key in s:
                possibles.add(eq)
    elif searchMethod == 'and':
        fail = false
        for key in keys:
            if key not in s:
                fail = True
        if not fail:
            possibles.add(eq)
    else:
        raise UserWarning(f"Unknown search method {searchMethod}")


for equation in equations:
    for s in equation.values():
        searchAndAddString(s, equation['definition'])

for equation in unitEquations:
    for s in equation.values():
        if type(s) is list:
            for i in s:
                searchAndAddString(i, equation['definition'])
        else:
            searchAndAddString(s, equation['definition'])




print('Possible Equations:')
for i in possibles:
    print(i)
