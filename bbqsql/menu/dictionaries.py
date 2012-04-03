#file: dictionaries.py

def category(category):
    """
    Takes the value sent from the user encoding menu and returns
    the actual value to be used. """

    return {
            '0':"0",
            '1':"blind_sql",
            '2':"bool_sqL"
           }.get(category,"ERROR")

