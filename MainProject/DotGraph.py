
class DotGraph:

    def __init__(self):
        self.declarations = []
        self.relations = []

    def get_representation(self, graph):
        for block in graph.getBlocks():
            self.traverse_node(block, graph)
        representation = "digraph G {\n"
        
        for declaration in self.declarations:
            representation += f"{declaration}\n"

        for relation in self.relations:
            representation += f"{relation}\n"

        representation += '}'

        self.declarations.clear()
        self.relations.clear()

        return representation

    def traverse_node(self, node, graph):
        self.declarations.append(f"{node.blockName} [shape=record, label=\"<b>{node.blockName} | {self.traverseInstructions(node)}\"];")
        fallthrough_label = ""
        if node.branch is not None:
            self.relations.append(f"{node.blockName}:s -> {node.branch.blockName}:n [label=\"branch\"];")
            fallthrough_label = f"[label=\"fall-through\"]"
        
        if node.fallThrough is not None:
            self.relations.append(f"{node.blockName}:s -> {node.fallThrough.blockName}:n {fallthrough_label};")
        
        if node.dominance is not None:
            self.relations.append(f"{node.dominance.blockName}:b -> {node.blockName}:b [color=blue, style=dotted, label=\"dom\"]")

    def traverseInstructions(self, node):
        instructions = "{"
        for instruction in node.instructions:
            instructions += f" {instruction.getInstructionString()} |"
        instructions = instructions.rstrip(instructions[-1])
        instructions += "}"
        return instructions