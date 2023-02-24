
class DotGraph:

    def __init__(self):
        self.declarations = []
        self.relations = []
    
    def traverseInstructions(self, node):
        res = "{"
        for instruction in node.instructions:
            res += f" {instruction.getInstructionString()} |"
        res = res.rstrip(res[-1])
        res += "}"
        return res
        
    def getRepresentation(self, graph):
        for block in graph.getBlocks():
            self.traverseBlocks(block)
        representation = "digraph G {\n"
        
        for declaration in self.declarations:
            representation += f"{declaration}\n"

        for relation in self.relations:
            representation += f"{relation}\n"

        representation += '}'

        self.declarations.clear()
        self.relations.clear()

        return representation

    def traverseBlocks(self, block):
        self.declarations.append(f"{block.blockName} [shape=record, label=\"<b>{block.blockName} | {self.traverseInstructions(block)}\"];")
        
        if block.branch is not None:
            self.relations.append(f"{block.blockName}:s -> {block.branch.blockName}:n [color= darkorange,label=\"branch\"];")
        
        if block.fallThrough is not None:
            self.relations.append(f"{block.blockName}:s -> {block.fallThrough.blockName}:n [color= darkgreen, label=\"FT\"];")
        
        if block.dominance is not None:
            self.relations.append(f"{block.dominance.blockName}:b -> {block.blockName}:b [color=blue, style=dotted, label=\"dom\"]")

