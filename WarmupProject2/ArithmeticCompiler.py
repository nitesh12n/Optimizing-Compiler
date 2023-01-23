class ExpressionEvaluator:

    plusMinus = ['+', '-']
    multDiv = ['*', '/']

    def __init__(self, expressions, variables):
        self.exp = expressions
        self.index = 0
        self.length = len(expressions)
        self.variables = variables

    def next(self):
        self.index+=1

    def getSym(self):
        while(self.index < self.length and self.exp[self.index] == ' '):
            self.next()
        if(self.index < self.length):
            return self.exp[self.index]
        return ""
    def evaluateExpressions(self):
        output = []
        val = self.evaluateExpression()
        if(self.index < self.length):
                if(self.index < self.length and self.getSym() == '.'):
                    output.append(val)
                else:
                    output.append("Invalid Input")
    
        while(self.index < self.length and self.getSym() == '.'):
            self.next()
            if(self.index < self.length):
                val = self.evaluateExpression()
                if(self.index < self.length and self.getSym() == '.'):
                    output.append(val)
                else:
                    output.append("Invalid Input")
                    break
        return output



    def evaluateExpression(self):
        val = self.term()
        while(self.index < self.length and self.getSym() in self.plusMinus):
            if(self.getSym() == '+'):
                self.next()
                val+= self.term()
            elif(self.getSym() == '-'):
                self.next()
                val-= self.term()
        return val

    
    def term(self):
        val = self.factor()
        while(self.index < self.length and self.getSym() in self.multDiv):

            if(self.getSym() == '*'):
                self.next()
                val*= self.factor()
            elif(self.getSym() == '/'):
                self.next()
                val/= self.factor()
        return val
                

    def factor(self):
        val = 0
        if(self.getSym() == '('):
            self.next()
            val = self.evaluateExpression()
            if(self.getSym() == ')'):
                self.next()
        
        elif(self.getSym().isnumeric()):
            val = int(self.getSym())
            self.next()
            while(self.index < self.length and self.getSym().isnumeric()):
                val = 10*val + int(self.getSym())
                self.next()
        elif(self.getSym().isalnum()):
            ident = self.getAndConsumeIdentifier()
            if ident in self.variables : 
                val = self.variables[ident]

        return val

    def getAndConsumeIdentifier(self):
        ident = ''
        while(self.getSym().isalnum()):
            ident+=self.getSym()
            self.next()
        return ident
        
# def main():
#     inputString = input("Input the string:\n")
#     ee = ExpressionEvaluator(inputString)
#     results = ee.evaluateExpressions()
#     for r in results:
#         print(r)
# if __name__ =="__main__":
#     main()





