from src.setCases.setCases import SetCases
from config.config import graph_array, graph_array_ratio

class Node:
    def __init__(self, data: SetCases, id_node: int , val_attr = None):
        """Initializes a node with a set of data, an identifier and a value of attribute

        Args:
            data (SetCases): set of data object to be used in the node
            id_node (int): node identifier
            val_attr ([type], optional): [description]. Defaults to None.
        """        
        
        self.data = data
        self.children = []
        self.curr_class = ''
        self.chosen_att = ''
        self.id_node = id_node
        self.val_attr = val_attr
        self.gain = 0
        self.childrenNodeColor = 'green'

    def addChildren(self, node):
        """Adds a child to the node
        Args:
            node ([Node]): [Node to be added]
        """
        self.children.append(node)
        
    def printTree(self, depth: int, graph, previous_node, name_previous_node: int, algorithm: str):
        """Prints the tree generated with graphviz

        Args:
            depth (int): intial depth of the tree
            graph ([Digraph]): graphviz Digraph object
            previous_node ([Node]): [description]
            name_previous_node (int): previous node identifier
            algorithm (str): chosen algorithm to print the tree (gain or gain ratio)
        """
        # If the chosen attribute for the current iteration is not an empty string, it creates a node with the chosen attribute for the class, and shows the gain of the node (gain or gain ratio)
        if self.chosen_att != '':
            graph.node(name = str(self.id_node),label = f'Clase: {self.chosen_att} \n Gain: {round(self.gain,3)}')
        else:
            #If the leaf node has more than one value of the class (inpure), it sets the node color to orange
            if len(self.data.cases[self.data.class_column_name].value_counts())>1: 
                self.childrenNodeColor = 'orange'
            else:
                #If the leaf node has only one value of the class (pure), it sets the node color to green
                self.childrenNodeColor = 'green'
            #We create the leaf node with the previous assigned color, and show the gain and amount of cases for each class attribute the node has
            graph.node(name = str(self.id_node), label= f'Clase: {self.curr_class} \n Gain: {round(self.gain,3)} \n [{self.data.cases[self.data.class_column_name].value_counts().to_string()}]',color=self.childrenNodeColor,style='filled')
        # We create the edge between the current node and the previous node
        if depth != 0:
            graph.edge(str(name_previous_node), str(self.id_node),label=str(self.val_attr),splines='line')
        name_previous_node+=1

        for item in self.children:
            # We append the current generated graph to the graph array, so as to keep each step made in the tree
            if algorithm == 'gain':
                graph_array.append(graph.copy())
            else:
                graph_array_ratio.append(graph.copy())
            item.printTree(depth+1, graph, self, self.id_node, algorithm)
        