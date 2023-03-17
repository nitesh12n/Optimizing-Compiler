from Opcode import Opcode
import Instruction
class BasicBlock:
    number = 0
    def __init__(self, initSearchStructure=False):
        self.instructions = []
        self.__symbolTable = {}
        self.dominance = None
        self.fallThrough = None
        self.branch = None
        self.kills = set()
        self.blockNumber = BasicBlock.number
        self.blockName = "BB" + str(self.blockNumber)
        self.preAddedKills = set()
        BasicBlock.number+=1

        self.searchStructure = {}
        if initSearchStructure == True:
            for opcode in Opcode.ValidOpcodesForSearch:
                self.searchStructure[opcode] = None

    def getSymbolValue(self, key):
        return self.__symbolTable.get(key)
            
    def getSymbolTable(self):
        return self.__symbolTable
    
    def getSymbolTableKey(self, instr):
        for key, value in self.__symbolTable.items():          
            if instr == value:
                return key

    def updateSymbolTable(self, key, value):
        self.__symbolTable[key] = value
        if isinstance(value, Instruction.Instruction):
            value.getInstructionString()

    def copySymbolTable(self, sourceBlock):        
        self.__symbolTable = sourceBlock.getSymbolTable().copy()

    def removeInstruction(self, instr):     
        instr.deleteFlag = True
        if instr in self.instructions:   
            #pass
            self.instructions.remove(instr)

    def createNewInstruction(self, opcode, instType, operand1=None, operand2=None, ignoreSearchStructure=False, createAtTop=False):
     
        if instType == Instruction.Instruction.InstructionOneOperand:
            instr = self.searchInstruction(opcode, operand1) if ignoreSearchStructure == False else None
            if instr == None:
                instr = Instruction.Instruction_OneOperand(opcode, operand1)
            else:
                return instr

        elif instType == Instruction.Instruction.InstructionTwoOperand:
            instr = self.searchInstruction(opcode, operand1, operand2) if ignoreSearchStructure == False else None
            if instr == None:
                instr = Instruction.Instruction_TwoOperand(opcode, operand1, operand2)
            else:
                return instr
        else:
            instr = Instruction.Instruction(opcode)

        if opcode in Opcode.ValidOpcodesForSearch:
            instr.prevOpcodeInstr = self.searchStructure[opcode]
            self.searchStructure[opcode] = instr

        instr.block = self

        ##check
        if createAtTop:
            if len(self.instructions) > 0 and self.instructions[0].opcode == Opcode.EMPTY: 
                self.instructions.insert(1, instr)
            else:
                self.instructions.insert(0, instr)
        else:
            self.instructions.append(instr)
        return instr

    def searchInstruction(self, opcode, operand1=None, operand2=None, curr = None):
        
        if opcode in Opcode.ValidOpcodesForSearch or opcode in Opcode.ValidOpcodesForWhileSearch:
            #while loop code
            if curr != None:
                instr = curr.prevOpcodeInstr
            else:
                instr = self.searchStructure[opcode]

            while(instr != None):
                if instr.deleteFlag == False and instr.operand1 == operand1 and (isinstance(instr, Instruction.Instruction_OneOperand) or instr.operand2 == operand2):
                    return instr
                instr = instr.prevOpcodeInstr
        return None

    def searchInstructionForLoad(self, opcode, operand1=None, operand2=None, curr = None, ident=None):
        
        if opcode in Opcode.ValidOpcodesForSearch:
            #while loop code
            if curr != None:
                instr = curr.prevOpcodeInstr
            else:
                instr = self.searchStructure[opcode]

            while(instr != None):
                if instr.deleteFlag == False and instr.opcode == Opcode.KILL and instr.operand1 == ident:
                    return None, instr
                
                if instr.deleteFlag == False and instr.operand1 == operand1 and (isinstance(instr, Instruction.Instruction_OneOperand) or instr.operand2 == operand2):
                    return instr, None
                instr = instr.prevOpcodeInstr
        return None, None


