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
    
    def getInstructionString(self):
        instructionString = str(self.instructionNumber) + ": " + self.opcode
        if isinstance(self, Instruction_OneOperand):
            if isinstance(self.operand1, numbers.Number):
                instructionString+= "#" + str(self.operand1)
            else:
                instructionString+= " (" + str(self.operand1.instructionNumber) + ")"
        
        elif isinstance(self, Instruction_TwoOperand):
            instructionString+= " (" + str(self.operand1.instructionNumber) + ")" + " " + "(" + str(self.operand2.instructionNumber) + ")"
        self.instructionString = instructionString
        return instructionString
    

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
        self.instructionString = self.opcode + " (" + str(self.operand1.instructionNumber) + ")" + " " + "(" + str(self.operand2.instructionNumber) + ")"

