from Token import Token
import re
class Tokenizer:

    def __init__(self, input):
        self.input = input
        self.index = 0
        self.length = len(input)
        self.token = None
        self.tokenize()
        
    def currentToken(self):
        return self.token

    def consume(self, pattern):  
        self.index+= len(self.token)
        self.tokenize()  

    def match(self, token):
        self.skipWhiteSpace()
        if isinstance(token, re.Pattern):
            match = re.match(token, self.token)
            if match != None:
                return True

        elif self.token == token:
                return True
        
        return False


    def skipWhiteSpace(self):
        while(self.index < self.length and self.input[self.index] == ' '):
            self.index+=1

    def tokenize(self):
        self.skipWhiteSpace()
        for token in Token.TokenLookup:
            if isinstance(token, re.Pattern):
                match = re.match(token, self.input[self.index:])
                if match != None:
                    self.token = match.group()
                    break
            elif self.input[self.index:].startswith(token):
                self.token = token
                break
    