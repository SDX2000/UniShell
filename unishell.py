#!/usr/bin/env python3

import sys
sys.path.extend(["lib"])

import os
import string
import readline
#from objects import FileInfo
from commands import *
from pprint import pprint


def printBanner():
    print("UniShell Version 0.0.1")
    print("Copyright (C) Sandeep Datta, 2015")
    print("")


cmds = {"stat" : Stat()
        #, "cd" : ChangeDirectory
        #, "exit" : Exit
        #, "quit" : Exit
}


#TODO: handle KeyboardInterrupt
def main(args):
    if len(args) > 1:
        with open(args[1], "r") as f:
            for line in f:
                processInput(line)
    else:
        printBanner()
        while True:
            try:
                cwd = os.getcwd()
                inp = input(cwd + "> ")
            except EOFError:
                print("")
                break

            if not processInput(inp):
                break

def processInput(cmdLine):
    if not cmdLine:
        return True
    
    cmdLine = cmdLine.strip()

    #Skip comments
    if cmdLine.startswith("#"):
        return True

    #TODO: replace with quit command
    if cmdLine == "quit" or cmdLine == "exit":
        return False

    cmdLinePart = cmdLine.split()

    if not cmdLinePart:
        return True

    try:
        cmd = cmds[cmdLinePart[0]]
        print(cmd.execute(cmdLinePart[1:]))
    except KeyError:
        print("ERROR: Unkown command: {}".format(cmdLinePart[0]))

    return True


if __name__ == '__main__':
    main(sys.argv)
