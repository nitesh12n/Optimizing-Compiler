import Tokenizer as t
from  Token import Token
import re

class Parser:

    def __init__(self, input):
        self.tokenizer = t.Tokenizer(input)
        self.variables = {}

    def consume(self, pattern):      
        self.tokenizer.consume(pattern) 
    
    def match(self, pattern):
        return self.tokenizer.match(pattern)

    def currentToken(self):
        return self.tokenizer.currentToken()

    def getAndConsumeIdentifier(self):
        ident = self.currentToken()
        self.consume(Token.IDENTIFIER)
        return ident

    def getAndConsumeExpression(self):
        return self.evaluateExpression()

    def consumeVar(self):
        self.consume(Token.VAR)
        ident = self.getAndConsumeIdentifier()
        self.consume(Token.ASSIGNMENT)
        expr = self.getAndConsumeExpression()
        self.variables[ident] = expr

    def computation(self):
        results = []
        self.consume(Token.COMPUTATION)
        while self.match(Token.VAR):
            self.consumeVar()
            self.consume(Token.SEMI_COLON)
           
        result = self.getAndConsumeExpression()
        results.append(result)

        while self.match(Token.SEMI_COLON):
            self.consume(Token.SEMI_COLON)
            result = self.getAndConsumeExpression()
            results.append(result)
        self.consume(Token.END)

        return results      

    def evaluateExpression(self):
        val = self.term()
        while self.match(Token.PLUS) or self.match(Token.MINUS):
            if self.match(Token.PLUS):
                self.consume(Token.PLUS)
                val+= self.term()
            elif self.match(Token.MINUS):
                self.consume(Token.MINUS)
                val-= self.term()
        return val

    
    def term(self):
        val = self.factor()
        while self.match(Token.MULT) or self.match(Token.DIV):
            if self.match(Token.MULT):
                self.consume(Token.MULT)
                val*= self.factor()
            elif self.match(Token.DIV):
                self.consume(Token.DIV)
                val/= self.factor()
        return val
                

    def factor(self):
        val = 0
        if self.match(Token.OPAREN):
            self.consume(Token.OPAREN)
            val = self.evaluateExpression()
            if self.match(Token.CPAREN):
                self.consume(Token.CPAREN)
        
        elif self.match(Token.NUMBERS):
            val = int(self.currentToken())
            self.consume(Token.NUMBERS)

        elif self.match(Token.IDENTIFIER):
            ident = self.getAndConsumeIdentifier()
            if ident in self.variables : 
                val = self.variables[ident]

        return val

def main():
    #inputString = "computation var i <- 2 * 3; var abracadabra <- 7; (((abracadabra * i))); i - 5 - 1 ."
    inputString = input("Enter the input:\n")
    p = Parser(inputString)
    results = p.computation()
    for r in results:
        print(r)


    
if __name__ =="__main__":
    main()