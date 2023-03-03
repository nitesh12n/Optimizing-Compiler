from Tokenizer import Tokenizer
from Instruction import Instruction
from SSA import SSA
from  Token import Token
from Opcode import Opcode 

class Parser:
    INTEGER_SIZE = 4
    UNDEFINED_INT = 9999
    BASE_CONST = "#BASE"
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

    def getAndConsumeExpression(self, ignoreSearchStructure=False):
        return self.evaluateExpression(ignoreSearchStructure)

    def consumeVar(self, rootDefaultInst):

        self.consume(Token.VAR)
        ident = self.getAndConsumeIdentifier()
        self.ssa.updateSymbolTable(ident, rootDefaultInst)
        while self.match(Token.COMMA):
            self.consume(Token.COMMA)
            ident = self.getAndConsumeIdentifier()
            self.ssa.updateSymbolTable(ident, rootDefaultInst)
        self.consume(Token.SEMI_COLON)
    
    def consumeArrayDeclaration(self):

        self.consume(Token.ARRAY)
        #self.ssa.createOrGetRootInstruction(self.INTEGER_SIZE)
        #self.ssa.createOrGetRootInstruction(self.BASE_CONST)
        sizes = []
        while self.match(Token.SQUARE_OPAREN):
            self.consume(Token.SQUARE_OPAREN)
            val = int(self.currentToken())
            sizes.append(val)
            instr = self.ssa.createOrGetRootInstruction(val)
            self.consume(Token.NUMBERS)
            self.consume(Token.SQUARE_CPAREN)
        
            
        self.consumeArrayIdentifier(sizes)
        while self.match(Token.COMMA):
            self.consume(Token.COMMA)
            self.consumeArrayIdentifier(sizes)          
        self.consume(Token.SEMI_COLON)        

    def consumeArrayIdentifier(self, sizes):
        ident = self.getAndConsumeIdentifier()
        self.ssa.arrayDimensions[ident] = sizes
        #value = self.getArrayBaseAddressValue(ident)
        #self.ssa.createOrGetRootInstruction(value)
        
    def getArrayBaseAddressValue(self, ident):
        return f"#{ident}_base_adr"
         
    def computation(self):

        self.consume(Token.MAIN)
        rootDefaultInst = self.ssa.createOrGetRootInstruction(self.UNDEFINED_INT)
        while self.matchAny([Token.VAR, Token.ARRAY]):
            if self.match(Token.VAR):
                self.consumeVar(rootDefaultInst)
            elif self.match(Token.ARRAY):
                self.consumeArrayDeclaration()

        self.consume(Token.LCPAREN)
        self.consumeStatements()
        self.consume(Token.RCPAREN)
        self.consume(Token.DOT)
        self.ssa.removeInstructionFromRoot(rootDefaultInst)

    def consumeStatements(self):

        while self.matchAny([Token.LET, Token.IF, Token.WHILE, Token.RETURN, Token.CALL]):          
            if self.match(Token.LET):
                self.consumeLetStatement()
            elif self.match(Token.CALL):
                self.consumeCallStatement()
            elif self.match(Token.IF):
                self.consumeIfStatement()
            elif self.match(Token.WHILE):
                self.consumeWhileStatement()
    
    def consumeWhileStatement(self):
        self.consume(Token.WHILE)
        branch, fallThrough, join = self.ssa.createWhileBlocks()
        
        
        relOp, cmpInstruction = self.consumeRelation(True)
        self.ssa.createInstructionInActiveBlock(relOp, Instruction.InstructionTwoOperand, cmpInstruction, branch.instructions[0])
        self.consume(Token.DO)
        fallThrough.searchStructure = self.ssa.activeBlock.searchStructure.copy()

        self.ssa.activeBlock = fallThrough
        self.consumeStatements()

        ##should we create at the end?
        self.ssa.createInstructionInActiveBlock(Opcode.BRA, Instruction.InstructionOneOperand, join.instructions[0])
        
        ##update second parameter of phi
        self.ssa.updateJoinForWhile(branch, fallThrough, self.ssa.activeBlock, join)
        
        branch.copySymbolTable(join)
        branch.searchStructure = join.searchStructure.copy()

        self.consume(Token.OD)
        if self.match(Token.SEMI_COLON):
            self.consume(Token.SEMI_COLON)
        
        self.ssa.activeBlock = branch

    def consumeIfStatement(self):
        
        self.consume(Token.IF)        
        relOp, cmpInstruction = self.consumeRelation()

        branch, fallThrough, join = self.ssa.createIfElseBlocks(relOp, cmpInstruction)
        self.consume(Token.THEN)

        self.ssa.activeBlock = fallThrough
        self.consumeStatements()
        self.ssa.createInstructionInActiveBlock(Opcode.BRA, Instruction.InstructionOneOperand, join.instructions[0])
        
        if self.match(Token.ELSE):
            self.consume(Token.ELSE)
            self.ssa.activeBlock = branch
            self.consumeStatements()
        self.consume(Token.FI)
        if self.match(Token.SEMI_COLON):
            self.consume(Token.SEMI_COLON)
        self.ssa.activeBlock = join

        ##find current branch and fallthrough and calculate phi
        self.ssa.updateJoinforIf(branch, fallThrough, join)

    def consumeRelation(self, ignoreSearchStructure = False):
        leftOperand = self.getAndConsumeExpression(ignoreSearchStructure)
        relOp = self.getAndConsumeRelOp()
        rightOperand = self.getAndConsumeExpression(ignoreSearchStructure)
        instruction = self.ssa.createInstructionInActiveBlock(Opcode.CMP, Instruction.InstructionTwoOperand, leftOperand, rightOperand)

        return relOp, instruction

    def getAndConsumeRelOp(self):
        relOp = Opcode.CONDITIONS[self.tokenizer.currentToken()]
        self.consume(self.tokenizer.currentToken())
        return relOp

    def consumeCallStatement(self):
        self.consume(Token.CALL)
        if self.match(Token.WRITE):
            self.consume(Token.WRITE)
            #ident = self.getAndConsumeIdentifier()
            expression = self.getAndConsumeExpression()
            self.ssa.createInstructionInActiveBlock(Opcode.WRITE, Instruction.InstructionOneOperand, expression)
            self.consume(Token.CPAREN)
        elif self.match(Token.WRITENEWLINE):
            self.consume(Token.WRITENEWLINE)
            self.ssa.createInstructionInActiveBlock(Opcode.WRITENEWLINE, Instruction.InstructionZeroOperand)
        
        if self.match(Token.SEMI_COLON):
            self.consume(Token.SEMI_COLON)
    
    def consumeLetStatement(self):
        self.consume(Token.LET)
        ident = self.getAndConsumeIdentifier()

        isArray = self.match(Token.SQUARE_OPAREN)
        expression = None
        if isArray:
            expression = self.calculateArrayIndexExpression(ident)
                       
        self.consume(Token.ASSIGNMENT)
        if self.match(Token.CALL):
            self.consume(Token.CALL)
            if self.match(Token.READINPUT):
                self.consume(Token.READINPUT)
                instruction = self.ssa.createInstructionInActiveBlock(Opcode.READ, Instruction.InstructionZeroOperand)
        else:
            instruction = self.getAndConsumeExpression()

        if isArray:
            self.processArrayStore(ident, expression, instruction)
        else:
            self.ssa.updateSymbolTable(ident, instruction)
  
        if self.match(Token.SEMI_COLON):
            self.consume(Token.SEMI_COLON)

    def evaluateExpression(self, ignoreSearchStructure=False):
        instruction = self.term(ignoreSearchStructure)
        while self.matchAny({Token.PLUS,Token.MINUS}):
            if self.match(Token.PLUS):
                self.consume(Token.PLUS)
                opcode = Opcode.ADD
            elif self.match(Token.MINUS):
                opcode = Opcode.SUB
                self.consume(Token.MINUS)

            operand2 = self.term(ignoreSearchStructure)
            instruction = self.ssa.createInstructionInActiveBlock(opcode, Instruction.InstructionTwoOperand, instruction, operand2)

        return instruction 

    
    def term(self, ignoreSearchStructure=False):
        instruction = self.factor(ignoreSearchStructure)

        while self.matchAny([Token.MULT, Token.DIV]):
            if self.match(Token.MULT):
                opcode = Opcode.MUL
                self.consume(Token.MULT)
            elif self.match(Token.DIV):
                opcode = Opcode.DIV
                self.consume(Token.DIV)

            operand2 = self.factor(ignoreSearchStructure)
            instruction = self.ssa.createInstructionInActiveBlock(opcode, Instruction.InstructionTwoOperand, instruction, operand2)

        return instruction
                
    def factor(self, ignoreSearchStructure=False):
        if self.match(Token.OPAREN):
            self.consume(Token.OPAREN)
            instr = self.evaluateExpression(ignoreSearchStructure)
            if self.match(Token.CPAREN):
                self.consume(Token.CPAREN)
        
        elif self.match(Token.NUMBERS):
            val = int(self.currentToken())
            instr = self.ssa.createOrGetRootInstruction(val)
            self.consume(Token.NUMBERS)

        elif self.match(Token.IDENTIFIER):
            ident = self.getAndConsumeIdentifier()
            
            #isArray
            if self.match(Token.SQUARE_OPAREN):
                #TODO:add support for multi dimensional array
                instr = self.processArrayLoad(ident, ignoreSearchStructure)
            
            else:
                instr = self.ssa.getSymbolValue(ident)

        return instr

    def calculateArrayIndexExpression(self, ident):
        index = 0
        if self.match(Token.SQUARE_OPAREN):
            self.consume(Token.SQUARE_OPAREN)
            expression = self.getAndConsumeExpression()
            self.consume(Token.SQUARE_CPAREN)
            index+=1
            
        sizes = self.ssa.arrayDimensions[ident]

        while self.match(Token.SQUARE_OPAREN):
            self.consume(Token.SQUARE_OPAREN)
            indexInstr = self.ssa.createOrGetRootInstruction(sizes[index])
            index+=1
            mul = self.ssa.createInstructionInActiveBlock(Opcode.MUL, Instruction.InstructionTwoOperand, expression, indexInstr)
            expression = self.getAndConsumeExpression()
            expression = self.ssa.createInstructionInActiveBlock(Opcode.ADD, Instruction.InstructionTwoOperand, mul, expression)
            self.consume(Token.SQUARE_CPAREN) 
        
        return expression

    def processArrayStore(self, ident, expression, instruction):
        integerSizeInstr = self.ssa.createOrGetRootInstruction(self.INTEGER_SIZE)
        mulInstruction = self.ssa.createInstructionInActiveBlock(Opcode.MUL, Instruction.InstructionTwoOperand, expression, integerSizeInstr)
        baseInstruction = self.ssa.createOrGetRootInstruction(self.BASE_CONST)
        baseAddrValue = self.ssa.createOrGetRootInstruction(self.getArrayBaseAddressValue(ident))
        arrayBaseAdd = self.ssa.createInstructionInActiveBlock(Opcode.ADD, Instruction.InstructionTwoOperand, baseInstruction, baseAddrValue)           
        
        reqAddress = self.ssa.createInstructionInActiveBlock(Opcode.ADDA, Instruction.InstructionTwoOperand, mulInstruction, arrayBaseAdd, ignoreSearchStructure=True)
        storeInst = self.ssa.createInstructionInActiveBlock(Opcode.STORE, Instruction.InstructionTwoOperand, reqAddress, instruction)
        self.ssa.updateSearchStructureForLoad(ident, self.ssa.activeBlock, False)
        self.ssa.activeBlock.kills.add(ident)
        return storeInst
            
    def processArrayLoad(self, ident, ignoreSearchStructure=False):
        
        integerSizeInstr = self.ssa.createOrGetRootInstruction(self.INTEGER_SIZE)
        baseInstruction = self.ssa.createOrGetRootInstruction(self.BASE_CONST)
        expression = self.calculateArrayIndexExpression(ident)
        mulInstruction = self.ssa.createInstructionInActiveBlock(Opcode.MUL, Instruction.InstructionTwoOperand, expression, integerSizeInstr)
        baseAddrValue = self.ssa.createOrGetRootInstruction(self.getArrayBaseAddressValue(ident))
        arrayBaseAdd = self.ssa.createInstructionInActiveBlock(Opcode.ADD, Instruction.InstructionTwoOperand, baseInstruction, baseAddrValue)

        killInstr = None
        if ignoreSearchStructure == False:
            previousADDA = self.ssa.activeBlock.searchInstruction(Opcode.ADDA, mulInstruction, arrayBaseAdd)
            previousLOAD, killInstr = self.ssa.activeBlock.searchInstructionForLoad(Opcode.LOAD, previousADDA, ident=ident)

            if previousLOAD != None:
                return previousLOAD

        reqAddress = self.ssa.createInstructionInActiveBlock(Opcode.ADDA, Instruction.InstructionTwoOperand, mulInstruction, arrayBaseAdd, ignoreSearchStructure=True)             
        loadInstr =  self.ssa.createInstructionInActiveBlock(Opcode.LOAD, Instruction.InstructionOneOperand, reqAddress) 
        if killInstr != None:
            killInstr.loads.add(loadInstr)

        return loadInstr