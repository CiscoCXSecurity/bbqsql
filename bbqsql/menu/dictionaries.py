""" Python lists used for quick conversion of user input
    to strings used by the toolkit """

def http_method(comparison):
    """ 
    Takes the value sent from the user encoding menu and returns
    the actual value to be used. """

    return {
            '0':"",
            '1':"GET",
            '2':"POST",
            }.get(comparison,"ERROR")

def comparison(comparison):
    """ 
    Takes the value sent from the user encoding menu and returns
    the actual value to be used. """

    return {
            '0':"",
            '1':"text",
            '2':"type",
            '3':"time",
            '4':"whatelse?",
            }.get(comparison,"ERROR")
def category(category):
    """
    Takes the value sent from the user encoding menu and returns
    the actual value to be used. """

    return {
            '0':"0",
            '1':"blind_sql",
            '2':"bool_sqL"
           }.get(category,"ERROR")

