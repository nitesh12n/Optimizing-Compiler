from Token import Token
class Opcode:
    ADD = "add"
    SUB ="sub"
    MUL="mul"
    DIV ="div"
    READ= "read"
    WRITE = "write"
    WRITENEWLINE= "writeNL"
    CONST = "const"
    CMP = "cmp"
    EMPTY = "empty"
    BRA = "bra"
    PHI = "phi"
    COND_EQUAL = "bne",
    COND_NOTEQUAL = "beq",
    COND_GREATERTHAN = "ble",
    COND_GREATERTHANEQUAL = "blt",
    COND_LESSTHAN = "bge",
    COND_LESSTHANEQUAL = "bgt"
    ValidOpcodesForSearch = [ADD, SUB, MUL, DIV, COND_EQUAL, COND_NOTEQUAL, COND_GREATERTHAN, 
                        COND_GREATERTHANEQUAL, COND_LESSTHAN, COND_LESSTHANEQUAL, CMP]
    CONDITIONS = {
        Token.COND_EQUAL : "bne",
        Token.COND_NOTEQUAL : "beq",
        Token.COND_GREATERTHAN : "ble",
        Token.COND_GREATERTHANEQUAL : "blt",
        Token.COND_LESSTHAN : "bge",
        Token.COND_LESSTHANEQUAL : "bgt"
    }
     

#bne x y branch to y on x not equal
# beq x y branch to y on x equal
# ble x y branch to y on x less or equal
# blt x y branch to y on x less
# bge x y branch to y on x greater or equal
# bgt x y branch to y on x greater
