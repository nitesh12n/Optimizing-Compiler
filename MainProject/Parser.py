from Tokenizer import Tokenizer
from Instruction import Instruction
from SSA import SSA
from  Token import Token
from Opcode import Opcode 
from DotGraph import DotGraph 
import sys
class Parser:

    def __init__(self, input):
        self.tokenizer = Tokenizer(input)
        self.ssa = SSA()

    def consume(self, pattern):      
        self.tokenizer.consume(pattern) 
    
    def match(self, pattern):
        return self.tokenizer.match(pattern)

    def matchAny(self, tokens):
        for token in tokens:
             if self.tokenizer.match(token):
                return True
        return False

    def currentToken(self):
        return self.tokenizer.currentToken()

    def getAndConsumeIdentifier(self):
        ident = self.currentToken()
        self.consume(Token.IDENTIFIER)
        return ident

    def getAndConsumeExpression(self):
        return self.evaluateExpression()

    def consumeVar(self, rootDefaultInst):
        self.consume(Token.VAR)
        ident = self.getAndConsumeIdentifier()
        self.ssa.updateSymbolTable(ident, rootDefaultInst)
        while self.match(Token.COMMA):
            self.consume(Token.COMMA)
            ident = self.getAndConsumeIdentifier()
            self.ssa.updateSymbolTable(ident, rootDefaultInst)

        self.consume(Token.SEMI_COLON)

    def computation(self):

        self.consume(Token.MAIN)
        rootDefaultInst = self.ssa.createRootInstruction(0)
        while self.match(Token.VAR):
            self.consumeVar(rootDefaultInst)

        self.consume(Token.LCPAREN)
        self.consumeStatements()
        self.consume(Token.RCPAREN)
        self.consume(Token.DOT)

    def consumeStatements(self):

        while self.matchAny([Token.LET, Token.IF, Token.WHILE, Token.RETURN, Token.CALL]):          
            if self.match(Token.LET):
                self.consumeLetStatement()
            elif self.match(Token.CALL):
                self.consumeCallStatement()
            elif self.match(Token.IF):
                self.consumeIfStatement()
        
    def consumeIfStatement(self):
        
        self.consume(Token.IF)        
        relOp, cmpInstruction = self.consumeRelation()

        branch, fallThrough, join = self.ssa.createIfElseBlocks(relOp, cmpInstruction)
        self.consume(Token.THEN)

        self.ssa.activeBlock = fallThrough
        self.consumeStatements()
        self.ssa.createNewInstruction(Opcode.BRA, Instruction.InstructionOneOperand, join.instructions[0])
        
        if self.match(Token.ELSE):
            self.consume(Token.ELSE)
            self.ssa.activeBlock = branch
            self.consumeStatements()
        self.consume(Token.FI)
        if self.match(Token.SEMI_COLON):
            self.consume(Token.SEMI_COLON)
        self.ssa.activeBlock = join

        ##find current branch and fallthrough and calculate phi
        self.ssa.updateJoin(branch, fallThrough, join)

    def consumeRelation(self):
        leftOperand = self.getAndConsumeExpression()
        relOp = self.getAndConsumeRelOp()
        rightOperand = self.getAndConsumeExpression()
        instruction = self.ssa.createNewInstruction(Opcode.CMP, Instruction.InstructionTwoOperand, leftOperand, rightOperand)

        return relOp, instruction

    def getAndConsumeRelOp(self):
        relOp = Opcode.CONDITIONS[self.tokenizer.currentToken()]
        self.consume(self.tokenizer.currentToken())
        return relOp

    def consumeCallStatement(self):
        self.consume(Token.CALL)
        if self.match(Token.WRITE):
            self.consume(Token.WRITE)
            ident = self.getAndConsumeIdentifier()
            self.ssa.createNewInstruction(Opcode.WRITE, Instruction.InstructionOneOperand, self.ssa.getSymbolValue(ident))
            self.consume(Token.CPAREN)
        elif self.match(Token.WRITENEWLINE):
            self.consume(Token.WRITENEWLINE)
            self.ssa.createNewInstruction(Opcode.WRITENEWLINE, Instruction.InstructionZeroOperand)

        self.consume(Token.SEMI_COLON)

    def consumeLetStatement(self):
        self.consume(Token.LET)
        ident = self.getAndConsumeIdentifier()
        self.consume(Token.ASSIGNMENT)
        if self.match(Token.CALL):
            self.consume(Token.CALL)
            if self.match(Token.READINPUT):
                self.consume(Token.READINPUT)
                instruction = self.ssa.createNewInstruction(Opcode.READ, Instruction.InstructionZeroOperand)
        else:
            instruction = self.getAndConsumeExpression()

        self.ssa.updateSymbolTable(ident, instruction)
        if self.match(Token.SEMI_COLON):
            self.consume(Token.SEMI_COLON)

    def evaluateExpression(self):
        instruction = self.term()
        while self.matchAny({Token.PLUS,Token.MINUS}):
            if self.match(Token.PLUS):
                self.consume(Token.PLUS)
                opcode = Opcode.ADD
            elif self.match(Token.MINUS):
                opcode = Opcode.SUB
                self.consume(Token.MINUS)

            operand2= self.term()
            instruction = self.ssa.createNewInstruction(opcode, Instruction.InstructionTwoOperand, instruction, operand2)

        return instruction 

    
    def term(self):
        instruction = self.factor()

        while self.matchAny([Token.MULT, Token.DIV]):
            if self.match(Token.MULT):
                opcode = Opcode.MUL
                self.consume(Token.MULT)
            elif self.match(Token.DIV):
                opcode = Opcode.DIV
                self.consume(Token.DIV)

            operand2 = self.factor()
            instruction = self.ssa.createNewInstruction(opcode, Instruction.InstructionTwoOperand, instruction, operand2)

        return instruction
                
    def factor(self):
        if self.match(Token.OPAREN):
            self.consume(Token.OPAREN)
            instr = self.evaluateExpression()
            if self.match(Token.CPAREN):
                self.consume(Token.CPAREN)
        
        elif self.match(Token.NUMBERS):
            val = int(self.currentToken())
            instr = self.ssa.createRootInstruction(val)
            self.consume(Token.NUMBERS)

        elif self.match(Token.IDENTIFIER):
            ident = self.getAndConsumeIdentifier()
            instr = self.ssa.getSymbolValue(ident)

        return instr



def main():

    inFile = sys.argv[1]
    ##debug
    #inFile = "MainProject/Examples/Code3.smpl"
    with open(inFile,'r') as i:
        inputString = i.read()
        
    p = Parser(inputString)
    p.computation()

    dotGraph = DotGraph()
    graph = dotGraph.getRepresentation(p.ssa.graph)
    print(graph)


      
if __name__ =="__main__":
    main()