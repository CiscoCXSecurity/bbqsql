#file: utils.py

from sys import stdout

def update_char(c=None):
    '''
    This just helps with fancy output. This deletes the last printed character from
    the terminal and replaces it with the specified character. This way, with blind sqli,
    we can have it appear to scroll through the characters it is testing and whatnot...
    Note that when using this you will need to manually delete the last character if you don't
    want it there and probably will need to use the end_line() function (bellow) for printing 
    a good looking new line.....
    '''
    if not QUIET:
        if c:
            stdout.write("\x08")
            stdout.write(c)
            stdout.flush()
        else:
            stdout.write(" ")
            stdout.flush()

def end_line():
    '''
    This is for fancy output. It deletes the last character printed to the terminal and
    starts a new line...
    '''
    if not QUIET:
        stdout.write("\x08 \n")
        stdout.flush()