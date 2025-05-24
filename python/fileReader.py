from utils import *
import math
import dice

def ReadFromFile(filePath):

    # First read
    characterFile = []

    # Ignore everything after the end sheet mark to allow for notes
    for line in open(filePath, "r").readlines():

        if("[[end]]" in line):
            break

        characterFile.append(line)

    rawOutput = ""

    # Get rid of extra new lines
    for i, line in enumerate(characterFile):
        line = line.replace('\n','')

        characterFile[i] = f"{line}"

    # Parse Variables
    mdVars = {}
    for line in characterFile:

        #Only look at lines with vars
        if(tryGetVarDef(line) == None and  tryGetScoreVarDef(line) == None):
            continue

        # Divide the string, as multiple vars may be on one line, and some sections may be just comments
        for string in line.split(' '):    

            # Test for normal var
            parsed = tryGetVarDef(string)
            if(parsed != None):
                var = parsed.split(':')
                mdVars[var[0]] = var[1]
                continue
            
            # Test for score var
            parsed = tryGetScoreVarDef(string)
            if(parsed != None):
                var = parsed.split(':')
                mdVars[var[0]] = var[1] # Add in the score
                var[0] = var[0].replace('(','')
                var[0] = var[0].replace(')','')
                mdVars[var[0]] = str(math.floor(int(var[1])/2)-5) # Add in the mod

    # Replace vars with their values, and do cleanup
    for i, line in enumerate(characterFile):

        replacedLine = ''
        for substring in line.split(' '):

            # Skip sections that are less than 3 chars 
            if (len(substring) < 3):
                replacedLine += substring + ' '
                continue

            # Skip sections that themselves define the var
            if(tryGetVarDef(substring) != None or tryGetScoreVarDef(substring) != None):
                replacedLine += substring + ' '
                continue

            # Check for var usage
            for var in mdVars:
                substring = substring.replace(var, mdVars[var])

            diceNotation = tryGet_FullDiceEquation(substring)
            if(diceNotation != None):

                # Convert raw, standalone operations to constants
                # 8+4+3 => 15
                if ('d' not in substring):
                    try:
                        substring = str(dice.roll(substring))
                    except:
                        pass

                # Simplify any constants in the dice notation
                # 1d20+5+3+2 => 1d20+10
                toSimplify = ''
                while(toSimplify != None):
                    toSimplify = tryGetConstantsInDiceNotation(substring)
                    if(toSimplify != None):

                        # We don't want to replace the first operator
                        # But the behavior for that looks different for negative numbers
                        if(toSimplify.startswith('-')):
                            substring = substring.replace(toSimplify, str(dice.roll(toSimplify)), 1)
                        else:
                            substring = substring.replace(toSimplify[1:], str(dice.roll(toSimplify)), 1)

                # Convert things like 1d20+-1 to 1d20-1
                substring = substring.replace("+-","-") 

            replacedLine += substring + ' '
        
        characterFile[i] = replacedLine.strip()

    return characterFile