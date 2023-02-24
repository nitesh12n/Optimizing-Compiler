from BasicBlock import BasicBlock
class ControlFlowGraph:

    def __init__(self):
        self.blocks = []

    def createNewBlock(self, initSearchStructure = False):
        block = BasicBlock(initSearchStructure)
        self.blocks.append(block)
        return block

    def getBlocks(self):
        return self.blocks

    def getRoot(self):
        return self.blocks[0]
