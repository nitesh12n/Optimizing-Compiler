import ArithmeticCompiler as ac
import re
VAR = "var"
COMPUTATION = "computation"
ASSIGNMENT = "<-"
SEMI_COLON = ";"
DOT ="."
tokenLookup = { VAR, COMPUTATION, ASSIGNMENT, SEMI_COLON}

class Parser:

    plusMinus = ['+', '-']
    multDiv = ['*', '/']

    def __init__(self, input):
        self.input = input
        self.index = 0
        self.length = len(input)
        self.variables = {}

    def next(self):
        self.index+=1

    def skipWhiteSpace(self):
        while(self.index < self.length and self.input[self.index] == ' '):
            self.next() 

    def getSym(self):
        self.skipWhiteSpace()
        if(self.index < self.length):
            return self.input[self.index]

    def match(self, pattern):
        self.skipWhiteSpace()
        if re.match(pattern, self.input[self.index:]):
            self.consume(pattern)
            return True
        return False

    def consume(self, pattern):
        self.skipWhiteSpace()
        self.index+= len(pattern) 
        self.skipWhiteSpace()      

    def getAndConsumeIdentifier(self):
        ident = ""
        while(self.getSym().isalnum()):
            ident+= self.getSym()
            self.next()
        return ident

    def getAndConsumeExpression(self):
        expr = ''
        while(self.getSym().isalnum() or self.getSym() in "+-/*()"):
            expr+= self.getSym()
            self.next()
                
        ee = ac.ExpressionEvaluator(expr, self.variables)
        return ee.evaluateExpression()

    def consumeVar(self):
        ident = self.getAndConsumeIdentifier()
        self.match(ASSIGNMENT)
        expr = self.getAndConsumeExpression()
        self.variables[ident] = expr

    def computation(self):
        results = []
        self.match(COMPUTATION)
        while(self.match(VAR)):
            self.consumeVar()
            self.match(SEMI_COLON)
           
        result = self.getAndConsumeExpression()
        results.append(result)
        ##CHECK
        while(self.getSym() == SEMI_COLON):
            self.match(SEMI_COLON)
            result = self.getAndConsumeExpression()
            results.append(result)
        self.match(DOT)

        return results      


def main():
    inputString = "computation var i <- 2 * 3; var abracadabra <- 7; (((abracadabra * i))); i - 5 - 1 ."
    p = Parser(inputString)
    results = p.computation()
    for r in results:
        print(r)


    
if __name__ =="__main__":
    main()