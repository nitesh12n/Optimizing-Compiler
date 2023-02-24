from Opcode import Opcode
import Instruction
class BasicBlock:
    number = 0
    def __init__(self, initSearchStructure=False):
        self.instructions = []
        self.symbolTable = {}
        self.dominance = None
        self.fallThrough = None
        self.branch = None
        self.blockNumber = BasicBlock.number
        self.blockName = "BB" + str(self.blockNumber)
        BasicBlock.number+=1

        self.searchStructure = {}
        if initSearchStructure == True:
            for opcode in Opcode.ValidOpcodesForSearch:
                self.searchStructure[opcode] = None

    def updateSymbolTable(self, key, value):
        self.symbolTable[key] = value
        value.getInstructionString()

    def removeInstruction(self, instr):     
        instr.deleteFlag = True   
        ##check
        self.instructions.remove(instr)

    def createNewInstruction(self, opcode, instType, operand1=None, operand2=None):
     
        if instType == Instruction.Instruction.InstructionOneOperand:
            instr = self.searchInstruction(opcode, operand1)
            if instr == None:
                instr = Instruction.Instruction_OneOperand(opcode, operand1)
            else:
                return instr

        elif instType == Instruction.Instruction.InstructionTwoOperand:
            instr = self.searchInstruction(opcode, operand1, operand2)
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
        self.instructions.append(instr)
        return instr

    def searchInstruction(self, opcode, operand1=None, operand2=None, curr = None):
        
        if opcode in Opcode.ValidOpcodesForSearch:
            if curr != None:
                instr = curr.prevOpcodeInstr
            else:
                instr = self.searchStructure[opcode]

            while(instr != None):
                if instr.deleteFlag == False and instr.operand1 == operand1 and (isinstance(instr, Instruction.Instruction_OneOperand) or instr.operand2 == operand2):
                    return instr
                instr = instr.prevOpcodeInstr
        return None


