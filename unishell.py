#!/usr/bin/env python3

import sys
sys.path.extend(["lib"])

import os
import cmd
import string
import readline
from objects import FileInfo
from pprint import pprint

def printBanner():
    print("UniShell Version 0.0.1")
    print("Copyright (C) Sandeep Datta, 2015")
    print("")


def main(args):
    printBanner()

    if args:
        with open(args[1], "r") as f:
            for line in f:
                processInput(line)
    else:
        while True:
            try:
                cwd = os.getcwd()
                inp = input(cwd + "> ")
            except EOFError:
                print("")
                break

            if not processInput(inp):
                break

def processInput(cmd):
    if not cmd:
        return True
    
    cmd = cmd.strip()
    
    if cmd == "quit" or cmd == "exit":
        return False

    cmdPart = cmd.split()

    if not cmdPart:
        return True

    if cmdPart[0] == "stat":
        pprint(FileInfo(cmdPart[1]))
    else:
        print(cmd)

    return True


if __name__ == '__main__':
    main(sys.argv)
