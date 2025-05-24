import re
import os
from os import walk

def GetAllCharacterSheetPaths():

    paths = result = [os.path.join(dp, f) for dp, dn, filenames in os.walk('..') for f in filenames if os.path.splitext(f)[1] == '.md']

    goodPaths = []
    for path in paths:
        if("readme" in path.lower()):
            continue

        if("license" in path.lower()):
            continue

        goodPaths.append(path)

    return goodPaths


# Regex is cursed, so above each of these is an example of what they are intended 
# to select, with the selection in square brackets

"""
This selects variable definitions in parenthesis, to be calculated into scores

Vars must be at least three capital letters, a colon, then some number of digits

Example:
 [PROF:3] [DEX:-2]
"""
def tryGetVarDef(string):
    match = re.search('[A-Z]{3,}:(-)?\d*', string)
    return match.group(0) if match else None

"""
This selects variable definitions in parenthesis, to be calculated into scores

Vars must be same as normal variable definitions, but the letters must be in parenthesis    

Example:
 [(STR):18] [(DEX):12] [(CON):12] [(INT):8] [(WIS):10] [(CHA):18]
"""
def tryGetScoreVarDef(string): 
    match = re.search('\([A-Z]{3,}\):\d+', string)
    return match.group(0) if match else None

"""
This selects the xdx notation most TTRPG players are familiar with

Example:
 Greataxe          [1d20]+4+2    to hit     1d12+4 Slashing
"""
def tryGet_xds_DiceNotation(string):
    match = re.findall('\d+d\d+', string)
    return match if match else None

"""
This selects the part you do math on, with

Example:
Greataxe          [1d20+4+2]    to hit     1d12+4 Slashing
"""
def tryGet_FullDiceEquation(string):
    match = re.search('\d+d(\w|\d|\+|\-|\\|\*)+', string)
    return match.group(0) if match else None


def tryGet_DiceButton(string):
    match = re.search('\[\[.*?\]\]', string)
    return match.group(0) if match else None


"""
This selects any constant nums that can be simplified

Example:
Spell Save          8[+2+4]       

This intentionally does not select the entire simplifiable string. The intended use of this is to iterate over
a string until it is no longer detected as being able to be simplified.

This was done so that it does no select a string like this:
1d2[0+4+2]
If it were to select like that, then your 1d20+4+2 would turn into 1d26, which is not correct
"""
def tryGetConstantsInDiceNotation(string):
    match = re.search('(\+|-|\\|\*)\d(\+|-|\\|\*)\d*(?!\d*d)', string)
    return match.group(0) if match else None

    