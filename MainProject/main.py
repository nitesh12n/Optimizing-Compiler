from Parser import Parser
from DotGraph import DotGraph

def main():

    #inFile = sys.argv[1]
    ##debug
    inFile = "MainProject/Examples/Code16.smpl"
    with open(inFile,'r') as i:
        inputString = i.read()
        
    parser = Parser(inputString)
    parser.computation()

    dotGraph = DotGraph()
    graph = dotGraph.getRepresentation(parser.ssa.graph)

    if len(parser.ssa.uninitializedVar) > 0:
        print("These uninitialized variables were used: " + ", ".join(parser.ssa.uninitializedVar))
    print(graph)
 
if __name__ =="__main__":
    main()