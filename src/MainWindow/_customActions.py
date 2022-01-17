import json
from os.path import join, dirname
from copy import copy, deepcopy
from Cope import *

dataDir = join(dirname(__file__), '../../assets')
commonEquFile = join(dataDir, 'commonEquations.json')
customFuncsFile = join(dataDir, 'customFunctions.json')
unitsFile = join(dataDir, 'units.json')
constantsFile = join(dataDir, 'constants.json')

def autism(func, *args, **kwargs):
    return lambda: func(*args, **kwargs)
# autism = FunctionCall

todo('replace the unit solver with a search for equation box, given the units involved')
todo('maybe make getting atoms exclusively in the variable boxes optional')
todo('remove (1) from one in the prefix box')
todo('add a prefix box to the solution unit')

def addCustomFuncs(self):
    with open(customFuncsFile, 'r') as f:
        for item in json.load(f):
            if item['catagory'] not in self._catagories.keys():
                self._catagories[item['catagory']] = self.menuCustomFunctions.addMenu(item['catagory'])
            if 'comments' in item.keys():
                ihateeveryone = deepcopy(item['string'])
                self._catagories[item['catagory']].addAction(item['name'], autism(self.runCustomFuncInCode, ihateeveryone, *item['comments'])) # lambda: self.runCustomFuncInCode(ihateeveryone, *item['comments']))
            else:
                ihateeveryone = deepcopy(item['string'])
                self._catagories[item['catagory']].addAction(item['name'], autism(self.runCustomFuncInCode, ihateeveryone)) # lambda: self.runCustomFuncInCode(ihateeveryone))

def addCommonEqus(self):
    with open(commonEquFile, 'r') as f:
        for item in json.load(f):
            if item['catagory'] not in self._commonEquCatagories.keys():
                self._commonEquCatagories[item['catagory']] = self.menuCommonEquations.addMenu(item['catagory'])
            ihateeveryone = deepcopy(item['definition'])
            self._commonEquCatagories[item['catagory']].addAction(item['name'], autism(self.equationInput.setPlainText, ihateeveryone)) # lambda: self.equationInput.setPlainText(ihateeveryone))

def addUnits(self):
    with open(unitsFile, 'r') as f:
        for item in json.load(f):
            if item['catagory'] not in self._unitCatagories.keys():
                self._unitCatagories[item['catagory']] = self.menuUnits.addMenu(item['catagory'])

            menu = self._unitCatagories[item['catagory']].addMenu(item['name'] + ' (' + item['symbol'] + ')')
            menu.setToolTip(item['symbol'])
            for i in item['equations']:
                ihateeveryone = deepcopy(i)
                menu.addAction(i, autism(self.equationInput.setPlainText, ihateeveryone)) # lambda: self.equationInput.setPlainText(ihateeveryone))

def addConstants(self):
    with open(constantsFile, 'r') as f:
        for item in json.load(f):
            if item['catagory'] not in self._constantCatagories.keys():
                self._constantCatagories[item['catagory']] = self.menuConstants.addMenu(item['catagory'])

            menu = self._constantCatagories[item['catagory']].addMenu(item['name'])
            try:
                menu.setToolTip(item['tooltip'])
            except KeyError: pass
            ihateeveryone = deepcopy(item['definition'])
            menu.addAction(item['definition'], autism(self.equationInput.setPlainText, ihateeveryone)) # lambda: self.equationInput.setPlainText(ihateeveryone))
