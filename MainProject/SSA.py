import Instruction
from ControlFlowGraph import ControlFlowGraph
from Opcode import Opcode

class SSA:
    INTEGER_SIZE = 4
    UNDEFINED_INT = 9999
    BASE_CONST = "#BASE"
    def __init__(self):
        self.instructionCounter = 0
        self.graph = ControlFlowGraph()
        self.rootBlock = self.graph.createNewBlock()
        self.activeBlock = self.graph.createNewBlock(True)
        self.activeBlock.dominance = self.rootBlock
        self.rootBlock.fallThrough = self.activeBlock
        self.useChain = {}
        self.uninitializedVar = set()
        self.arrayDimensions = {}
        self.phis = set()
        self.currentWhileBlocks = set()

    def getNextInstructionNumber(self):
        self.instructionCounter+=1
        return self.instructionCounter

    def updateSymbolTable(self, key, value):
        self.activeBlock.updateSymbolTable(key, value)
    
    def getSymbolValue(self, key):
        value = self.activeBlock.getSymbolValue(key)
        if isinstance(value, Instruction.Instruction):
            if value.instructionNumber == 0 or (value.opcode==Opcode.PHI and value.operand1 != None and value.operand1.instructionNumber==0):
                self.uninitializedVar.add(key) 
        return value

    def createInstructionInActiveBlock(self, opcode, instType, operand1=None, operand2=None, ignoreSearchStructure=False, createAtTop=False):
        return self.createNewInstruction(self.activeBlock, opcode, instType, operand1, operand2, ignoreSearchStructure, createAtTop)

    def createNewInstruction(self, block, opcode, instType, operand1=None, operand2=None, ignoreSearchStructure=False, createAtTop=False):
        
        instr = block.createNewInstruction(opcode, instType, operand1, operand2, ignoreSearchStructure, createAtTop)
        
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
        
        if len(self.activeBlock.instructions) == 0:
            self.createEmptyInstruction(self.activeBlock)
        joinBlock = self.graph.createNewBlock()
        joinInstr = self.createEmptyInstruction(joinBlock)
        fallThrough = self.graph.createNewBlock()

        #follow block
        branch = self.graph.createNewBlock()   
        branchInstr = self.createEmptyInstruction(branch)

        joinBlock.dominance = self.activeBlock
        joinBlock.copySymbolTable(self.activeBlock)

        joinBlock.searchStructure = self.activeBlock.searchStructure.copy()

        #helps in while inside if
        #joinBlock.kills.update(self.activeBlock.kills)

        self.activeBlock.fallThrough = joinBlock
        branch.branch = self.activeBlock.branch
        self.activeBlock.branch = None
        self.activeBlock = joinBlock

        self.activeBlock.branch = branch
        self.activeBlock.fallThrough = fallThrough

        branch.dominance = self.activeBlock   
        fallThrough.dominance = self.activeBlock

        fallThrough.branch = joinBlock

        ## we should copy from joinBlock after everything is done?
        #branch.symbolTable = self.activeBlock.symbolTable.copy()

        #create phis
        for ident, instr in joinBlock.getSymbolTable().items():
            joinInstr = self.createInstructionInActiveBlock(Opcode.PHI, Instruction.Instruction.InstructionTwoOperand, instr)
            self.updateUseChain(joinInstr.operand1, joinInstr)
            joinBlock.updateSymbolTable(ident, joinInstr)
        
        for ident in self.arrayDimensions.keys():
            kill = self.updateSearchStructureForLoad(ident, joinBlock)
            joinBlock.preAddedKills.add(kill)
        
        fallThrough.copySymbolTable(self.activeBlock)

        return branch, fallThrough, joinBlock  

    def updateJoinForWhile(self, branch, oldfallThrough, fallThrough, join):
        flag = False
        idents = list(fallThrough.getSymbolTable().keys())
        for ident in idents:
            joinPhiInstr = join.getSymbolValue(ident)
            fallThroughInstr = fallThrough.getSymbolValue(ident)
            
            #TODO:
            if fallThroughInstr.deleteFlag == False and fallThroughInstr != joinPhiInstr and fallThroughInstr != joinPhiInstr.operand1:
                joinPhiInstr.operand2 = fallThroughInstr
                self.updateUseChain(joinPhiInstr.operand2, joinPhiInstr)
            else:
                flag = self.deletePhi(join, ident)

        self.deleteKills(branch, oldfallThrough, fallThrough, join)

        branch.copySymbolTable(join)
        branch.searchStructure = join.searchStructure.copy()
        
        #if flag == True:
        self.currentWhileBlocks = set()
        self.traverseWhileBlocks(join.fallThrough, join)
        self.currentWhileBlocks.add(join)
        threshold=10
        self.runCommonSubexpressionElimination(join, self.currentWhileBlocks, threshold)
        self.currentWhileBlocks = set()

        
    def runCommonSubexpressionElimination(self, join, blocks, threshold):
        if threshold <=0:
            return
        
        modified = []
        for block in blocks:
            instructions = block.instructions
            for instruction in instructions:
                if instruction.deleteFlag == False and instruction.opcode in Opcode.ValidOpcodesForWhileSearch:
                    prevInstr = block.searchInstruction(instruction.opcode, instruction.operand1, instruction.operand2, instruction)
                    if prevInstr != None:
                        modified.append(instruction)

        if len(modified) > 0:
            self.updateModifiedInstructions(modified)
            self.runCommonSubexpressionElimination(join, blocks, threshold - 1)


    def traverseWhileBlocks(self, block, join):

        if block is None or block == join or block in self.currentWhileBlocks:
            return
        
        self.currentWhileBlocks.add(block)

        self.traverseWhileBlocks(block.branch, join)
        self.traverseWhileBlocks(block.fallThrough, join)    

    


    def deleteKills(self, branch, oldfallThrough, fallThrough, join):
               
        kills = oldfallThrough.kills.copy()
        kills |= fallThrough.kills.copy()

        finalKills = set()
        modified = []
        
        for kill in join.preAddedKills:
            ident = kill.operand1

            if self.searchKillInSet(kill, kills) == False:
                join.removeInstruction(kill)
                for load in kill.loads:
                    modified.append(load)
            else:
                finalKills.add(kill.operand1)

            self.updateModifiedInstructions(modified, ident)
            '''
            while(len(modified) > 0):
                curr = modified.pop()
                if curr.opcode == Opcode.ADDA:
                    continue
                block = curr.block
                if curr.opcode == Opcode.LOAD:
                    previousADDA = block.searchInstruction(Opcode.ADDA, curr.operand1.operand1, curr.operand1.operand2, curr.operand1)
                    prevInstr, _ = block.searchInstructionForLoad(Opcode.LOAD, previousADDA, ident=ident)
                    if prevInstr != None:
                        block.removeInstruction(curr.operand1)
                        block.removeInstruction(curr)
                else:
                    prevInstr = curr.getInstructionFromSearchStructure()
                    if prevInstr != None:
                        block.removeInstruction(curr)
                
                if prevInstr != None:
                    
                    useChain = self.useChain.get(curr.instructionNumber)
                    if useChain != None:
                        for instr in useChain:
                            if instr.operand1 == curr or (isinstance(instr, Instruction.Instruction_TwoOperand) and instr.operand2 == curr):
                                modified.append(instr)                          
                                if instr.operand1 == curr:
                                    instr.operand1 = prevInstr
                                if isinstance(instr, Instruction.Instruction_TwoOperand) and instr.operand2 == curr:
                                    instr.operand2 = prevInstr

            '''
        if branch.fallThrough != None or branch.branch != None:
            branch.kills.update(finalKills)
            
    def searchKillInSet(self, searchKill, kills):

        for kill in kills:
            if kill == searchKill.operand1:
                return True
        return False
    def updateUseChain(self, inst, value):

        if isinstance(inst, Instruction.Instruction):
            key = inst.instructionNumber
            instructions = self.useChain.get(key)
            if instructions == None:
                self.useChain[key] = [value]
            elif value not in instructions:
                self.useChain[key].append(value)


    def deletePhi(self, join, ident):
        flag = False
        modified = []
        joinPhiInstr = join.getSymbolValue(ident)
        if joinPhiInstr.operand2 == None or joinPhiInstr.operand2 == joinPhiInstr.operand1:
            originalValue = joinPhiInstr.operand1
            useChain = self.useChain.get(joinPhiInstr.instructionNumber)   
            if useChain != None:
                for instr in useChain:
                    if instr.operand1 == joinPhiInstr or (isinstance(instr, Instruction.Instruction_TwoOperand) and instr.operand2 == joinPhiInstr):
                        modified.append(instr)
                        if instr.operand1 == joinPhiInstr:
                            instr.operand1 = originalValue
                            self.updateUseChain(instr.operand1, instr)
                            instr.getInstructionString()
                        if isinstance(instr, Instruction.Instruction_TwoOperand) and instr.operand2 == joinPhiInstr:
                            instr.operand2 = originalValue
                            self.updateUseChain(instr.operand2, instr)
                            instr.getInstructionString()

            #join.instructions.remove(joinPhiInstr)
            join.removeInstruction(joinPhiInstr)
            join.updateSymbolTable(ident, originalValue)
            res = self.updateModifiedInstructions(modified)
            if res == True:
                flag = True

        return flag
        ##check again if need to update symbol table          
        
    def updateModifiedInstructions(self, modified, ident=None):
        flag = False
        while(len(modified) > 0):
            curr = modified.pop()
            if curr.opcode == Opcode.ADDA or curr.deleteFlag == True:
                continue
            
            block = curr.block
            if curr.opcode == Opcode.PHI and curr.operand1 == curr.operand2:
                prevInstr = curr.operand1
            elif curr.opcode == Opcode.LOAD:
                    previousADDA = block.searchInstruction(Opcode.ADDA, curr.operand1.operand1, curr.operand1.operand2, curr.operand1)
                    prevInstr, _ = block.searchInstructionForLoad(Opcode.LOAD, previousADDA, ident=ident)
                    if prevInstr != None:
                        block.removeInstruction(curr.operand1)
            else:
                prevInstr = curr.getInstructionFromSearchStructure()
                
            if prevInstr != None:
                block.removeInstruction(curr)
                key = block.getSymbolTableKey(curr)
                if key != None:
                    block.updateSymbolTable(key, prevInstr)

                useChain = self.useChain.get(curr.instructionNumber)
                if useChain != None:
                    for instr in useChain:
                        if instr.operand1 == curr or (isinstance(instr, Instruction.Instruction_TwoOperand) and instr.operand2 == curr):
                            modified.append(instr)                          
                            if instr.operand1 == curr:
                                instr.operand1 = prevInstr
                                self.updateUseChain(instr.operand1, instr)
                                instr.getInstructionString()
                            if isinstance(instr, Instruction.Instruction_TwoOperand) and instr.operand2 == curr:
                                instr.operand2 = prevInstr
                                self.updateUseChain(instr.operand2, instr)
                                instr.getInstructionString()

            elif prevInstr == None and curr.opcode in Opcode.ValidOpcodesForWhileSearch:
                flag = True

        return flag

                        



    def createIfElseBlocks(self, relOp, cmpInstruction):

        branch = self.graph.createNewBlock()
        branchInstr = self.createEmptyInstruction(branch)
        fallThrough = self.graph.createNewBlock()
        joinBlock = self.graph.createNewBlock()
        joinInstr = self.createEmptyInstruction(joinBlock)

        ## -if join already exists, we need to point correctly, 
        # for 1st time, self.activeBlock.fallThrough is None
        joinBlock.fallThrough = self.activeBlock.fallThrough
        joinBlock.branch = self.activeBlock.branch

        ## if there may be a while outside this if else
        #if self.activeBlock.branch != None:
        #   if  self.activeBlock.dominance != None:
        #        self.activeBlock.dominance.kills.update(self.activeBlock.kills)
        #joinBlock.fallThrough = self.activeBlock.fallThrough if self.activeBlock.fallThrough != None else self.activeBlock.branch

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

        ##check - it is for if inside while
        #branch.kills.update(self.activeBlock.kills)
        #fallThrough.kills.update(self.activeBlock.kills)
        #joinBlock.kills.update(self.activeBlock.kills)

        self.createInstructionInActiveBlock(relOp, Instruction.Instruction.InstructionTwoOperand, cmpInstruction, branchInstr)

        return branch, fallThrough, joinBlock
    
    def updateJoinforIf(self, branch, fallThrough, join):
        #find current branch and fallthrough
        
        tempBranch = branch
        tempFallThrough = fallThrough

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

        if tempFallThrough.branch == None and tempFallThrough.fallThrough == None:
            tempFallThrough.branch = join
        if tempBranch.branch == None and tempBranch.fallThrough == None:
            tempBranch.fallThrough = join

        #update kills
        
        kills = branch.kills.copy()
        kills |= fallThrough.kills.copy()
        kills |= tempBranch.kills.copy()
        kills |= tempFallThrough.kills.copy()

        for kill in kills:
            self.updateSearchStructureForLoad(kill, join)
            join.kills.add(kill)

        #update phi in join block
        for ident in tempBranch.getSymbolTable():
            joinInstr = join.getSymbolValue(ident)

            if joinInstr == None or  tempBranch.getSymbolValue(ident) != tempFallThrough.getSymbolValue(ident):
                joinInstr = self.createNewInstruction(join, Opcode.PHI, Instruction.Instruction.InstructionTwoOperand, tempFallThrough.getSymbolValue(ident), tempBranch.getSymbolValue(ident))
                self.updateUseChain(joinInstr.operand1, joinInstr)
                self.updateUseChain(joinInstr.operand2, joinInstr)
                join.updateSymbolTable(ident, joinInstr)
                joinInstr.getInstructionString()
        

    def updateSearchStructureForLoad(self, ident, block, isFromJoin=True):

        killInstr = self.createNewInstruction(block, Opcode.KILL, Instruction.Instruction.InstructionOneOperand, ident, createAtTop=isFromJoin)
        #self.activeBlock.instructions.remove(instr)
        instr  = block.searchStructure[Opcode.LOAD]

        if isFromJoin == False or instr == None or instr.block != block: 
            killInstr.prevOpcodeInstr = instr
            block.searchStructure[Opcode.LOAD] = killInstr
        
        else:
            prev = None
            while instr!= None and instr.block == block:
                prev = instr
                instr = instr.prevOpcodeInstr
            
            if prev != None:
                prev.prevOpcodeInstr = killInstr
                
            killInstr.prevOpcodeInstr = instr
        
        return killInstr
            

















    
