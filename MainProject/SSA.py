from BasicBlock import BasicBlock 
from Instruction import Instruction
from ControlFlowGraph import ControlFlowGraph
from Opcode import Opcode

class SSA:

    def __init__(self):
        self.instructionCounter = 0
        self.graph = ControlFlowGraph()
        self.rootBlock = self.graph.createNewBlock()
        self.activeBlock = self.graph.createNewBlock()
        self.activeBlock.dominance = self.rootBlock
        self.rootBlock.fallThrough = self.activeBlock

    def getNextInstructionNumber(self):
        self.instructionCounter+=1
        return self.instructionCounter

    def updateSymbolTable(self, key, value):
        self.activeBlock.updateSymbolTable(key, value)
    
    def getSymbolValue(self, key):
        return self.activeBlock.symbolTable[key]

    def createNewInstruction(self, opcode, instType, operand1=None, operand2=None):
        return self.activeBlock.createNewInstruction(opcode, instType, operand1, operand2)

    def createEmptyInstruction(self, block):
        return block.createNewInstruction(Opcode.EMPTY, Instruction.InstructionZeroOperand)

    def createRootInstruction(self, operand1):
        
        for instr in self.rootBlock.instructions : 
            if instr.opcode == Opcode.CONST and instr.operand1 == operand1:
                return instr
    
        return self.rootBlock.createNewInstruction(Opcode.CONST, Instruction.InstructionOneOperand, operand1)

    def createIfElseBlocks(self, relOp, cmpInstruction):
        self.isNested = True

        branch = self.graph.createNewBlock()
        branchInstr = self.createEmptyInstruction(branch)
        fallThrough = self.graph.createNewBlock()
        joinBlock = self.graph.createNewBlock()
        joinInstr = self.createEmptyInstruction(joinBlock)
        ##check
        joinBlock.fallThrough = self.activeBlock.fallThrough
        self.activeBlock.branch = branch
        self.activeBlock.fallThrough = fallThrough

        branch.fallThrough = joinBlock
        fallThrough.fallThrough = joinBlock
        
        branch.dominance = self.activeBlock
        fallThrough.dominance = self.activeBlock
        joinBlock.dominance = self.activeBlock

        branch.symbolTable = self.activeBlock.symbolTable.copy()
        fallThrough.symbolTable = self.activeBlock.symbolTable.copy()
        joinBlock.symbolTable = self.activeBlock.symbolTable.copy()

        self.createNewInstruction(relOp, Instruction.InstructionTwoOperand, cmpInstruction, branchInstr)

        return branch, fallThrough, joinBlock
    
    def updateJoin(self, branch, fallThrough, join):
        ##find current branch and fallthrough

        tempBranch = branch
        tempFallThrough = fallThrough
        while tempBranch.fallThrough != join:
            tempBranch = tempBranch.fallThrough
        
        while tempFallThrough.fallThrough != join:
            tempFallThrough = tempFallThrough.fallThrough

        #update phi in join block
        for ident in tempBranch.symbolTable:
            joinInstr = join.symbolTable[ident]

            if joinInstr == None or  tempBranch.symbolTable[ident] != tempFallThrough.symbolTable[ident]:
                joinInstr = join.createNewInstruction(Opcode.PHI, Instruction.InstructionTwoOperand, tempFallThrough.symbolTable[ident], tempBranch.symbolTable[ident])
                join.updateSymbolTable(ident, joinInstr)
                joinInstr.getInstructionString()









    
