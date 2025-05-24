import dice
import re
import math
import os
import datetime

from utils import *
from fileReader import *

from textual import events, on
from textual.app import App, ComposeResult, Screen
from textual.color import Color
from textual.message import Message
from textual.widgets import Markdown, Static, RichLog, Button, Footer, Collapsible, Input
from textual.validation import Function, Number, ValidationResult, Validator

selectedFile = ''
doReload = False
previousManualRole = None

class SectionHolder():
    def __init__(self, title = '', composables = []):
        self.title = title
        self.composables = composables

class SectionParser():

    def __init__(self):
        global selectedFile
        self.previousFileSize = None
        self.sectionHolders = [SectionHolder('', [])]

    def UpdateSectionsFromFile(self, file, diceLog):
        
        # Do not update if the file size hasn't changed
        filesize = os.path.getsize(file)
        if(filesize == self.previousFileSize and filesize != None):
            return
        else:
            self.previousFileSize = filesize
            self.sectionHolders = [SectionHolder('', [])]

        self.markdownSection = ""

        rawFile = ReadFromFile(file)
        self.sectionHolderIdex = 0
        for i, line in enumerate(rawFile):

            # Check for section headers
            if(line.startswith("# " )):
                self.sectionHolders.append(SectionHolder(line.replace('# ', '', 1), []))
                self.sectionHolderIdex += 1
            
            # If there are any things turned to composables this 
            # line, add it to the current section
            composables = self.LineToComposable(line, diceLog)
            if(len(composables)):
                self.sectionHolders[self.sectionHolderIdex].composables.append(composables)

        # If there is anything leftover, add that as well
        if(len(self.markdownSection)):
            self.sectionHolders[self.sectionHolderIdex].composables.append([Markdown(self.markdownSection)])

    def LineToComposable(self, line, diceLog):

        toYield = []

        # Keep going until a dice notation is found            
        if(tryGet_DiceButton(line)):

            # Found, add the previous sections as markdown, before handling 
            # this dice, but only if there actually is a section
            if(self.markdownSection != ""):
                toYield.append(Markdown(self.markdownSection))
                self.markdownSection = ""

            # Store each of the buttons for this line, the dice button class will parse them individually
            diceButtonStrings = []

            # Keep pulling from the line as long as there are equations in it
            while(tryGet_DiceButton(line)):

                # Try get the string
                string = tryGet_DiceButton(line)

                # Skip if nothing found
                if(string == None):
                    continue
                
                # Add to list
                diceButtonStrings.append(string.replace('[','').replace(']', '').strip())

                # Remove the found string from the line, so we don't pull the same thing twice
                line = line.replace(string, '', 1)

            # Make the button
            toYield.append(DiceButtonLine(diceLog, diceButtonStrings, ''))

        else:
            # No dice, add it to markdown section, or add line break if blank

            if(line.strip() != ''):
                # Add to markdown
                self.markdownSection += f"\n\n {line.strip()}"
            else:
                # Blank line, so this is a line break
                
                # If the previous markdownSection had content, yield that first so the 
                # line break happens in the right order
                if(len(self.markdownSection)):
                    toYield.append(Markdown(self.markdownSection))
                    self.markdownSection = ''

                # Linebreak
                toYield.append(LineBreak())
        
        return toYield

class SelfRollingDie():
    def __init__(self, rawInfo):
        # Grab the equation
        self.rollableEquation = tryGet_FullDiceEquation(rawInfo)

        # Separate rawInfo by the equation
        rawInfoSplit = rawInfo.split(self.rollableEquation, 1)

        # Set labels
        self.frontLabel = rawInfoSplit[0]
        self.rearLabel = rawInfoSplit[1]

    def roll(self):
        self.displayEquation = self.rollableEquation
        for diceNotation in tryGet_xds_DiceNotation(self.rollableEquation):
            roll = dice.roll(diceNotation)
            roll = str(roll)
            self.displayEquation = self.displayEquation.replace(diceNotation, roll, 1)

        finalCalculation = self.displayEquation
        finalCalculation = finalCalculation.replace('[', '')
        finalCalculation = finalCalculation.replace(']', '')
        finalCalculation = finalCalculation.replace(',', '+')
        finalCalculation = finalCalculation.replace(' ', '')

        # Combine everything for the output
        output = ""

        # Prepend the label only if there is one
        if(len(self.frontLabel) > 0):
            output += f"{self.frontLabel.strip()} "
        output += f"{self.rollableEquation} => {self.displayEquation} = {dice.roll(finalCalculation)}{self.rearLabel}"

        return output

class DiceButtonLine(Static):

    def on_mount(self) -> None:
        # Add the clickable text for each button
        buttonText = ''
        for i, die in enumerate(self.diceBag):
            buttonText += f"[@click='next_roll_{i}']{die.frontLabel}{die.rollableEquation}{die.rearLabel}[/]     "

        # Set the final text
        self.update(f"{buttonText} {self.endOfLine}")

    def __init__(self, diceLog, diceButtonStrings, endOfLine):
        self.diceLog = diceLog
        self.endOfLine = endOfLine
        self.diceBag = []
        for string in diceButtonStrings:
            self.diceBag.append(SelfRollingDie(string))

        self.add_roll_methods(len(self.diceBag))
        super().__init__()

    def error(self, die):
        self.diceLog.write(f"There was a problem with the provided dice notation: {die.rollableEquation}")
        self.update(f"!Error - Invalid dice notation: {die.rollableEquation}")

    @classmethod
    def add_roll_methods(cls, num_methods):
        for i in range(num_methods):
            def action_next_roll(self, index=i):
                try:
                    self.diceLog.write(self.diceBag[index].roll())
                except:
                    self.error(self.diceBag[index])
            
            # Assign the dynamically created method to the class with the appropriate name
            setattr(cls, f"action_next_roll_{i}", action_next_roll)

class LineBreak(Static):
    def on_mount (self):
        self.update('')

class FilePickerApp(App):

    class ColorButton(Static):

        class Selected(Message):
            def __init__(self, path) -> None:
                self.filePath = path
                super().__init__()

        def __init__(self, inputPath) -> None:
            self.filePath = inputPath
            super().__init__()

        def on_mount(self) -> None:
            self.update(f"{self.filePath}")

        def on_click(self) -> None:
            self.post_message(self.Selected(self.filePath))

        def render(self) -> str:
            return str(self.filePath)

    CSS_PATH = "styleFilePicker.tcss"
    BINDINGS = [("x", "exit", "Exit")]

    def compose(self) -> ComposeResult:
        
        global selectedFile
        paths = GetAllCharacterSheetPaths()
        for path in paths:
            yield self.ColorButton(path)

        self.diceLog = RichLog()
        yield self.diceLog
        self.diceLog.write("Select a character file")

        yield Footer()

    def on_color_button_selected(self, message: ColorButton.Selected) -> None:
        global doReload, selectedFile
        doReload = True
        selectedFile = message.filePath
        self.exit()

    def action_exit(self) -> None:
        global doReload
        doReload = False
        self.exit()

parser = SectionParser()
class MarkdownApp(App):

    CSS_PATH = "styleMarkdownViewer.tcss"
    BINDINGS = [("x", "exit", "Exit"),
                ("r", "reload", "Reload"), 
                ("c", "clear", "Clear Log"),
                ("h", 'hide', "Hide Console")]

    
    @on(Input.Submitted)
    def show_invalid_reasons(self, event: Input.Changed) -> None:
        # Updating the UI to show the reasons why validation failed
        global previousManualRole
        try:
            eq = event.value.strip()
            if(eq == '' and previousManualRole != None):
                eq = previousManualRole

            result = dice.roll(eq)
            self.diceLog.write(f"{eq} => {result}")

            previousManualRole = eq

            self.query_one("Input").value = ''
            return True
            
        except:
            self.diceLog.write("Invalid notation")

            self.query_one("Input").value = ''
            return False  



    def compose(self) -> ComposeResult:
        
        self.diceLog = RichLog()

        parser.UpdateSectionsFromFile(selectedFile, self.diceLog)

        # Yield from each section
        # Or yield all as one if there is only one section
        if(len(parser.sectionHolders) == 1):
                
            for composableLine in parser.sectionHolders[0].composables:
                for composable in composableLine:
                    yield composable
        else:
            for sectionHolder in parser.sectionHolders:

                # Skip section if it has nothing
                if(not len(sectionHolder.composables)):
                    continue

                if(len(sectionHolder.title)):
                    with Collapsible(collapsed=True, title=sectionHolder.title):
                        for composableLine in sectionHolder.composables:
                            for composable in composableLine:
                                yield composable
                else:
                    for composableLine in sectionHolder.composables:
                        for composable in composableLine:
                            yield composable

        yield Input(placeholder="Enter a dice roll...")

        yield self.diceLog
        yield Footer()

    def on_mount(self) -> None:
        global doReload
        self.diceLog.write(f"Loaded {selectedFile}")
        doReload = False

    def action_reload(self) -> None:
        global doReload
        doReload = True
        self.exit()

    def action_exit(self) -> None:
        global doReload
        doReload = False
        self.exit()

    def action_clear(self) -> None:
        self.diceLog.clear()

    def action_hide(self) -> None:
        self.diceLog.display = not self.diceLog.display
        input = self.query_one("Input")
        input.display = not input.display
        pass
        
if __name__ == "__main__":
    app = FilePickerApp()
    app.run()

    while(doReload):
        doReload = False 
        app = MarkdownApp()
        app.run()
