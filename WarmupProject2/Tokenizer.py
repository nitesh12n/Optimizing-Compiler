class Tokenizer:

    VAR = "var"
    COMP = "computation"
    tokenLookup = { VAR, COMP}


    def __init__(self, input, index):
        self.input = input
        self.index = index
        self.length = len(input)