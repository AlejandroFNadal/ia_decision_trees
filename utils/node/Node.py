from config.config import name_counter
from utils.setCases.setCases import SetCases

class Node:
    def __init__(self, data: SetCases, id_node: int , val_attr = None):
        self.data = data
        self.children = []
        self.curr_class = ''
        self.chosen_att = ''
        self.id_node = id_node
        self.val_attr = val_attr
        self.gain = 0

    def addChildren(self, node):
        self.children.append(node)
        
    def printTree(self, depth: int, graph, previous_node, name_previous_node: int):
        print('###############################################')
        print(f"Depth {depth}")
        print(self.curr_class)
        if self.chosen_att != '':
            print(f'Created node with name {self.id_node} and label {self.chosen_att}')
            graph.node(name = str(self.id_node),label = f'{self.chosen_att} \n Gain: {self.gain}')
        else:
            print(f'Created node with name {self.id_node} and label {self.curr_class}')
            print(self.data.cases[self.data.class_column_name].value_counts())
            graph.node(name = str(self.id_node), label= f'{self.curr_class} \n Gain: {self.gain} \n {self.data.cases[self.data.class_column_name].value_counts().values}',color='green')
        if depth != 0:
            print(f'Created edge between {name_previous_node} and {self.id_node}')
            graph.edge(str(name_previous_node), str(self.id_node),label=self.val_attr)
        #name_counter+=1
        name_previous_node+=1
        for item in self.children:
            item.printTree(depth+1, graph, self, self.id_node)
        