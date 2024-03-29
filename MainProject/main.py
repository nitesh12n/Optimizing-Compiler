from Parser import Parser
from DotGraph import DotGraph

def main():

    #inFile = sys.argv[1]
    ##debug
    inFile = "MainProject/testprogram.smpl"
    with open(inFile,'r') as i:
        inputString = i.read()
        
    parser = Parser(inputString)
    parser.computation()

    dotGraph = DotGraph()
    graph = dotGraph.getRepresentation(parser.ssa.graph)

    if len(parser.ssa.uninitializedVar) > 0:
        print("\nThese uninitialized variables were used: " + ", ".join(parser.ssa.uninitializedVar))
        print("\n")
    print(graph)
    
    file = open('MainProject/output.txt', 'w')
    file.write(graph)
    file.close()

 
if __name__ =="__main__":
    main()

    