from src.setCases.setCases import SetCases
from config.config import graph_array, graph_array_ratio

class Node:
    def __init__(self, data: SetCases, id_node: int , val_attr = None):
        self.data = data
        self.children = []
        self.curr_class = ''
        self.chosen_att = ''
        self.id_node = id_node
        self.val_attr = val_attr
        self.gain = 0
        self.childrenNodeColor = 'green'

    def addChildren(self, node):
        self.children.append(node)
        
    def printTree(self, depth: int, graph, previous_node, name_previous_node: int, algorithm: str):
        if self.chosen_att != '':
            graph.node(name = str(self.id_node),label = f'Clase: {self.chosen_att} \n Gain: {round(self.gain,3)}')
        else:
            if len(self.data.cases[self.data.class_column_name].value_counts())>1: 
                self.childrenNodeColor = 'orange'
            else:
                self.childrenNodeColor = 'green'
            graph.node(name = str(self.id_node), label= f'Clase: {self.curr_class} \n Gain: {round(self.gain,3)} \n [{self.data.cases[self.data.class_column_name].value_counts().to_string()}]',color=self.childrenNodeColor,style='filled')
        if depth != 0:
            graph.edge(str(name_previous_node), str(self.id_node),label=str(self.val_attr),splines='line')
        name_previous_node+=1
        for item in self.children:
            if algorithm == 'gain':
                graph_array.append(graph.copy())
            else:
                graph_array_ratio.append(graph.copy())
            item.printTree(depth+1, graph, self, self.id_node, algorithm)
        