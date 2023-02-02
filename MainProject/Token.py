import re

class Token:
    VAR = "var"
    COMPUTATION = "computation"
    ASSIGNMENT = "<-"
    SEMI_COLON = ";"
    END ="."
    PLUS="+"
    MINUS="-"
    MULT="*"
    DIV="/"
    OPAREN="("
    CPAREN=")"
    NUMBERS= re.compile(r'\d+')
    IDENTIFIER= re.compile(r'^[a-zA-Z][a-zA-Z0-9]*')
    
    TokenLookup = [IDENTIFIER, VAR, COMPUTATION, ASSIGNMENT, SEMI_COLON, END, PLUS, MINUS, MULT, DIV, 
                    OPAREN, CPAREN, NUMBERS]