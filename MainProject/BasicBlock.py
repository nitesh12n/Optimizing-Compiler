from Opcode import Opcode
import Instruction
class BasicBlock:
    number = 0
    def __init__(self):
        self.instructions = []
        self.symbolTable = {}
        self.dominance = None
        self.fallThrough = None
        self.branch = None
        self.blockNumber = BasicBlock.number
        self.blockName = "BB" + str(self.blockNumber)
        BasicBlock.number+=1

    def updateSymbolTable(self, key, value):
        self.symbolTable[key] = value

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
        self.instructions.append(instr)
        return instr

    def searchInstruction(self, opcode, operand1=None, operand2=None):
        
        block = self
        while(block != None):
            for instr in block.instructions[::-1]:
                if opcode in Opcode.ValidOpcodesForSearch and instr.opcode == opcode and instr.operand1 == operand1 and (isinstance(instr, Instruction.Instruction_OneOperand) or instr.operand2 == operand2):
                    return instr
            block = block.dominance
        return None


