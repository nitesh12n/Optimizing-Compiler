import re

class Token:
    VAR = "var"
    MAIN = "main"
    ASSIGNMENT = "<-"
    SEMI_COLON = ";"
    END ="."
    PLUS="+"
    MINUS="-"
    MULT="*"
    DIV="/"
    OPAREN="("
    CPAREN=")"
    LCPAREN="{"
    RCPAREN="}"
    NUMBERS= re.compile(r'\d+')
    IDENTIFIER= re.compile(r'^[a-zA-Z][a-zA-Z0-9]*')
    DOT = "."
    LET = "let"
    IF = "if"
    THEN = "then"
    ELSE = "else"
    FI = "fi"
    WHILE = "while"
    DO = "do"
    OD = "od"
    RETURN = "return"
    COMMA = ","
    CALL="call"
    READINPUT= "InputNum()"
    WRITE = "OutputNum("
    WRITENEWLINE = "OutputNewLine()"
    COND_EQUAL = "=="
    COND_NOTEQUAL= "!="
    COND_LESSTHAN = "<"
    COND_LESSTHANEQUAL = "<="
    COND_GREATERTHAN = ">"
    COND_GREATERTHANEQUAL = ">="

    CONDITIONAL_TOKENS = [COND_EQUAL, COND_NOTEQUAL, COND_LESSTHANEQUAL, COND_LESSTHAN, COND_GREATERTHANEQUAL, COND_GREATERTHAN]

    TokenLookup = [READINPUT, WRITE, WRITENEWLINE, IDENTIFIER, VAR, MAIN, ASSIGNMENT, SEMI_COLON, END, PLUS, MINUS, MULT, DIV, 
                    OPAREN, CPAREN, NUMBERS, DOT, LET, IF, WHILE, RETURN, COMMA, CALL, 
                    COND_EQUAL, COND_NOTEQUAL, COND_LESSTHANEQUAL, COND_LESSTHAN, COND_GREATERTHANEQUAL, COND_GREATERTHAN]