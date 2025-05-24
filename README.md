# Why use this tool?

For me, this was to escape Roll20's ecosystem. They do let you export characters, but they're in .json and therefore not readable or directly useful without conversion. It also makes it far easier hoard characters, I can have every character I've ever made all in one spot, and it will only take a few MBs, and since they're on my machine I have complete control over them.

So markdown is the obvious format for such a task. It will always be readable regardless of what machine or operating system is used. And the syntax to make the character sheet interactive is simple enough that it goes well with the format of markdown. This also means that regardless of which TTRPG is being used, the format of the character sheet can be understood by this program. It also ensures that any text in any of your files can be easily searched from a top level. 

This project supports:
* Clickable dice buttons
* Integer variables
* DnD style Score variables (10 = +0, 12 = +1, etc)
* Most markdown stylings

# To install
Python 3.8 is a requirement for this program.

### Windows
Either a dedicated IDE for python can be used, or you can install python 3.8 directly and run the program.

### Linux
A script is provided to install python 3.8 as well as the required python virtual environment. You will want to install python 3.8 first, then the virtual environment.  

# Usage
* Lines that include dice syntax will be converted to buttons: "[[1d20+5]]"
* Variables can be set with colons, an all caps signature, and no space: "PROF:2"
* Variables can be invoked in dice buttons: "[[1d20+5+PROF]]"
* Variables set within parenthesis are considered DnD style mods: "(STR:16)" will create a value called STR with a value of 4, and can be invoked directly as "(STR)"
* Lines that contain Variables will be automatically converted to a displayable format: "Passive Perception: 10+WIS" will turn into "Passive Perception 12"
* When the character's file is being read, if the reader comes across the line "[[end]]", then the scanner will not continue scanning. This is useful for if you would like to keep campaign notes on the file without the resource impact or clutter from your notes.

For an example of this syntax, use Kraaldren_Xarvull.md as a test character sheet. I was using this tool throughout the majority of the Curse of Strahd campaign a friend was running, so it is a great example of how a character sheet can be set up for use with this program.