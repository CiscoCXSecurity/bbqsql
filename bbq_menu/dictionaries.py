#!/usr/bin/env python

""" Python lists used for quick conversion of user input
    to strings used by the toolkit """

def comparison(comparison):
    """ 
    Takes the value sent from the user encoding menu and returns
    the actual value to be used. """

    return {
            '0':"",
            '1':"Response Code",
            '2':"Response Size",
            '3':"Response Time",
            '4':"Response Etc.",
            }.get(comparison,"ERROR")
