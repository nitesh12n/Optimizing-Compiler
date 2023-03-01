import Instruction
from ControlFlowGraph import ControlFlowGraph
from Opcode import Opcode

class SSA:

    def __init__(self):
        self.instructionCounter = 0
        self.graph = ControlFlowGraph()
        self.rootBlock = self.graph.createNewBlock()
        self.activeBlock = self.graph.createNewBlock(True)
        self.activeBlock.dominance = self.rootBlock
        self.rootBlock.fallThrough = self.activeBlock
        self.useChain = {}
        self.uninitializedVar = set()

    def getNextInstructionNumber(self):
        self.instructionCounter+=1
        return self.instructionCounter

    def updateSymbolTable(self, key, value):
        self.activeBlock.updateSymbolTable(key, value)
    
    def getSymbolValue(self, key):
        value = self.activeBlock.getSymbolValue(key)
        if isinstance(value, Instruction.Instruction) and value.instructionNumber == 0:
            self.uninitializedVar.add(key) 
        return value

    def createInstructionInActiveBlock(self, opcode, instType, operand1=None, operand2=None):
        return self.createNewInstruction(self.activeBlock, opcode, instType, operand1, operand2)

    def createNewInstruction(self, block, opcode, instType, operand1=None, operand2=None):
        
        instr = block.createNewInstruction(opcode, instType, operand1, operand2)
        
        if isinstance(instr, Instruction.Instruction_OneOperand) or isinstance(instr, Instruction.Instruction_TwoOperand): 
            if instr.operand1 != None:
                self.updateUseChain(instr.operand1, instr)
            if isinstance(instr, Instruction.Instruction_TwoOperand) and instr.operand2 != None:
                self.updateUseChain(instr.operand2, instr)
                
        return instr
    def removeInstructionFromRoot(self, instruction):
        self.rootBlock.removeInstruction(instruction)

    def createEmptyInstruction(self, block):
        return self.createNewInstruction(block, Opcode.EMPTY, Instruction.Instruction.InstructionZeroOperand)

    def createOrGetRootInstruction(self, operand1):
        
        for instr in self.rootBlock.instructions : 
            if instr.opcode == Opcode.CONST and instr.operand1 == operand1:
                return instr
    
        return self.createNewInstruction(self.rootBlock, Opcode.CONST, Instruction.Instruction.InstructionOneOperand, operand1)

    def createWhileBlocks(self):
        
        joinBlock = self.graph.createNewBlock()
        fallThrough = self.graph.createNewBlock()

        #follow block
        branch = self.graph.createNewBlock()   
        branchInstr = self.createEmptyInstruction(branch)

        joinBlock.dominance = self.activeBlock
        joinBlock.copySymbolTable(self.activeBlock)

        joinBlock.searchStructure = self.activeBlock.searchStructure.copy()
        joinBlock.kills.update(self.activeBlock.kills)
        
        self.activeBlock.fallThrough = joinBlock
        branch.branch = self.activeBlock.branch
        self.activeBlock.branch = None
        self.activeBlock = joinBlock

        self.activeBlock.branch = branch
        self.activeBlock.fallThrough = fallThrough

        branch.dominance = self.activeBlock   
        fallThrough.dominance = self.activeBlock

        fallThrough.copySymbolTable(self.activeBlock)
        fallThrough.branch = joinBlock

        ## we should copy from joinBlock after everything is done?
        #branch.symbolTable = self.activeBlock.symbolTable.copy()

        branch.searchStructure = self.activeBlock.searchStructure.copy()
        fallThrough.searchStructure = self.activeBlock.searchStructure.copy()

        #create phis
        for ident, instr in joinBlock.getSymbolTable().items():
            joinInstr = self.createInstructionInActiveBlock(Opcode.PHI, Instruction.Instruction.InstructionTwoOperand, instr)
            joinBlock.updateSymbolTable(ident, joinInstr)
        
        fallThrough.copySymbolTable(self.activeBlock)

        return branch, fallThrough, joinBlock  

    def updateJoinForWhile(self, branch, fallThrough, join):

        for ident, fallThroughInstr in fallThrough.getSymbolTable().items():
            joinPhiInstr = join.getSymbolValue(ident)

            if fallThroughInstr != joinPhiInstr:
                joinPhiInstr.operand2 = fallThroughInstr
                self.updateUseChain(joinPhiInstr.operand2, joinPhiInstr)
            else:
                self.deletePhi(join, ident)

        branch.copySymbolTable(join)

        for kill in fallThrough.kills:
            instr = self.createNewInstruction(join, Opcode.KILL, Instruction.Instruction.InstructionOneOperand, kill)
            latestValue  = join.searchStructure[Opcode.LOAD]
            instr.prevOpcodeInstr = latestValue
            join.searchStructure[Opcode.LOAD] = instr
            join.kills.add(kill)
        
        branch.kills.update(join.kills)
        branch.searchStructure = join.searchStructure.copy()

    def updateUseChain(self, inst, value):

        if isinstance(inst, Instruction.Instruction):
            key = inst.instructionNumber
            instructions = self.useChain.get(key)
            if instructions == None:
                self.useChain[key] = [value]
            elif value not in instructions:
                self.useChain[key].append(value)


    def deletePhi(self, join, ident):
        modified = []
        joinPhiInstr = join.getSymbolValue(ident)
        if joinPhiInstr.operand2 == None:
            originalValue = joinPhiInstr.operand1
            useChain = self.useChain.get(joinPhiInstr.instructionNumber)   
            if useChain != None:
                for instr in useChain:
                    if instr.operand1 == joinPhiInstr or (isinstance(instr, Instruction.Instruction_TwoOperand) and instr.operand2 == joinPhiInstr):
                        modified.append(instr)
                        if instr.operand1 == joinPhiInstr:
                            instr.operand1 = originalValue
                        if isinstance(instr, Instruction.Instruction_TwoOperand) and instr.operand2 == joinPhiInstr:
                            instr.operand2 = originalValue

            join.instructions.remove(joinPhiInstr)
            join.updateSymbolTable(ident, originalValue)

        while(len(modified) > 0):
            curr = modified.pop()
            block = curr.block
            prevInstr = curr.getInstructionFromSearchStructure()
            if prevInstr != None:
                block.removeInstruction(curr)

                useChain = self.useChain.get(curr.instructionNumber)
                if useChain != None:
                    for instr in useChain:
                        if instr.operand1 == curr or instr.operand2 == curr:
                            modified.append(instr)                          
                            if instr.operand1 == curr:
                                instr.operand1 = prevInstr
                            if instr.operand2 == curr:
                                instr.operand2 = prevInstr

        ##check again if need to update symbol table          
               
    def createIfElseBlocks(self, relOp, cmpInstruction):

        branch = self.graph.createNewBlock()
        branchInstr = self.createEmptyInstruction(branch)
        fallThrough = self.graph.createNewBlock()
        joinBlock = self.graph.createNewBlock()
        joinInstr = self.createEmptyInstruction(joinBlock)

        ## -if join already exists, we need to point correctly, 
        # for 1st time, self.activeBlock.fallThrough is None
        joinBlock.fallThrough = self.activeBlock.fallThrough if self.activeBlock.fallThrough != None else self.activeBlock.branch

        self.activeBlock.branch = branch
        self.activeBlock.fallThrough = fallThrough

        branch.fallThrough = joinBlock
        #..
        fallThrough.branch = joinBlock
        
        branch.dominance = self.activeBlock
        fallThrough.dominance = self.activeBlock
        joinBlock.dominance = self.activeBlock

        branch.copySymbolTable(self.activeBlock)
        fallThrough.copySymbolTable(self.activeBlock)
        joinBlock.copySymbolTable(self.activeBlock)

        branch.searchStructure = self.activeBlock.searchStructure.copy()
        fallThrough.searchStructure = self.activeBlock.searchStructure.copy()
        joinBlock.searchStructure = self.activeBlock.searchStructure.copy()

        branch.kills.update(self.activeBlock.kills)
        fallThrough.kills.update(self.activeBlock.kills)

        self.createInstructionInActiveBlock(relOp, Instruction.Instruction.InstructionTwoOperand, cmpInstruction, branchInstr)

        return branch, fallThrough, joinBlock
    
    def updateJoin(self, branch, fallThrough, join):
        #find current branch and fallthrough
        
        tempBranch = branch
        tempFallThrough = fallThrough
        #TODO: need to change
        #while tempBranch.fallThrough != None and tempBranch.fallThrough != join:
        #    tempBranch = tempBranch.fallThrough

        while (tempBranch.fallThrough != None and tempBranch.fallThrough != join) or (tempBranch.branch != None and tempBranch.branch != join):
            if tempBranch.fallThrough != None:
                tempBranch = tempBranch.fallThrough
            else: 
                tempBranch = tempBranch.branch


        while (tempFallThrough.fallThrough != None and tempFallThrough.fallThrough != join) or (tempFallThrough.branch != None and tempFallThrough.branch != join):          
            if tempFallThrough.branch != None:
                tempFallThrough = tempFallThrough.branch
            else: 
                tempFallThrough = tempFallThrough.fallThrough

        ##check
        if tempFallThrough.branch == None and tempFallThrough.fallThrough == None:
            tempFallThrough.branch = join
        if tempBranch.branch == None and tempBranch.fallThrough == None:
            tempBranch.fallThrough = join

        #update phi in join block
        for ident in tempBranch.getSymbolTable():
            joinInstr = join.getSymbolValue(ident)

            if joinInstr == None or  tempBranch.getSymbolValue(ident) != tempFallThrough.getSymbolValue(ident):
                joinInstr = self.createNewInstruction(join, Opcode.PHI, Instruction.Instruction.InstructionTwoOperand, tempFallThrough.getSymbolValue(ident), tempBranch.getSymbolValue(ident))
                join.updateSymbolTable(ident, joinInstr)
                joinInstr.getInstructionString()
        
        #update kills
        kills = tempBranch.kills
        kills |= tempFallThrough.kills
        
        for kill in kills:
            instr = self.createNewInstruction(join, Opcode.KILL, Instruction.Instruction.InstructionOneOperand, kill)
            latestValue  = join.searchStructure[Opcode.LOAD]
            instr.prevOpcodeInstr = latestValue
            join.searchStructure[Opcode.LOAD] = instr
            join.kills.add(kill)

        

    def updateSearchStructureForLoad(self, reqAddress):

        instr = self.createInstructionInActiveBlock(Opcode.KILL, Instruction.Instruction.InstructionOneOperand, reqAddress)
        #self.activeBlock.instructions.remove(instr)
        latestValue  = self.activeBlock.searchStructure[Opcode.LOAD]
        instr.prevOpcodeInstr = latestValue
        self.activeBlock.searchStructure[Opcode.LOAD] = instr












    
