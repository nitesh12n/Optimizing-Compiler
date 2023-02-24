import numbers

class Instruction:
    InstructionZeroOperand = 0
    InstructionOneOperand = 1
    InstructionTwoOperand = 2
    InstructionNumber = 0
    def __init__(self, opcode):
        self.opcode = opcode
        Instruction.InstructionNumber+=1
        self.instructionNumber = Instruction.InstructionNumber
        self.instructionString = self.opcode
        self.prevOpcodeInstr = None
        self.block = None
        self.deleteFlag = False
    
    def getInstructionString(self):
        instructionString = str(self.instructionNumber) + ": " + self.opcode
        if isinstance(self, Instruction_OneOperand):
            if isinstance(self.operand1, numbers.Number):
                instructionString+= "#" + str(self.operand1)
            else:
                instructionString+= " (" + str(self.operand1.instructionNumber) + ")"
        
        elif isinstance(self, Instruction_TwoOperand):
            operand2String = str(self.operand2.instructionNumber if self.operand2 != None else " ")
            instructionString+= " (" + str(self.operand1.instructionNumber) + ")" + " " + "(" + operand2String + ")"
        self.instructionString = instructionString
        return instructionString
    
    def getInstructionFromSearchStructure(self):
        operand1 = self.operand1 if (isinstance(self, Instruction_OneOperand) or isinstance(self, Instruction_TwoOperand)) else None
        operand2 = self.operand2 if isinstance(self, Instruction_TwoOperand) else None
        return self.block.searchInstruction(self.opcode, operand1, operand2, self)
    

class Instruction_OneOperand(Instruction):
    
    def __init__(self, opcode, operand1):
        super().__init__(opcode)
        self.operand1 = operand1 
        self.instructionString = self.opcode

        if isinstance(self.operand1, numbers.Number):
            self.instructionString+= "#" + str(self.operand1)
        elif isinstance(self.operand1, Instruction_OneOperand):
            self.instructionString+= " (" + str(self.operand1.instructionNumber) + ")"


class Instruction_TwoOperand(Instruction):
    
    def __init__(self, opcode, operand1, operand2):
        super().__init__(opcode)
        self.operand1 = operand1 
        self.operand2 = operand2 

        operand2String = str(self.operand2.instructionNumber if self.operand2 != None else " ")
        self.instructionString = self.opcode + " (" + str(self.operand1.instructionNumber) + ")" + " " + "(" + operand2String + ")"

