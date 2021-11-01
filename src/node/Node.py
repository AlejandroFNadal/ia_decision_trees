from config.config import name_counter
from src.setCases.setCases import SetCases
from config.config import graph_array, tree_gain_data, current_test_is_gain, tree_gain_ratio_data

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
        
    def printTree(self, depth: int, graph, previous_node, name_previous_node: int, gain_ratio:bool):
        global current_test_is_gain
        global tree_gain_ratio_data
        global tree_gain_data
        print('###############################################')
        print(f"Depth {depth}")
        print(self.curr_class)
        print(f'Current Test is gain: {current_test_is_gain}')
        if gain_ratio:
            tree_gain_ratio_data['node_counter'] += 1
        else:
            tree_gain_data['node_counter'] += 1
        if self.chosen_att != '':
            print(f'Created node with name {self.id_node} and label {self.chosen_att}')
            if gain_ratio:
                tree_gain_ratio_data['node_c_decision'] +=1
            else:
                tree_gain_data['node_c_decision'] +=1
            graph.node(name = str(self.id_node),label = f'{self.chosen_att} \n Gain: {self.gain}')
        else:
            print(f'Created node with name {self.id_node} and label {self.curr_class}')
            print(self.data.cases[self.data.class_column_name].value_counts())
            if gain_ratio:
                tree_gain_ratio_data['node_c_leaf'] +=1
            else:
                tree_gain_data['node_c_leaf'] +=1
            graph.node(name = str(self.id_node), label= f'{self.curr_class} \n Gain: {self.gain} \n {self.data.cases[self.data.class_column_name].value_counts().values}',color='green')
        if depth != 0:
            print(f'Created edge between {name_previous_node} and {self.id_node}')
            #graph.edge with straight spline
            graph.edge(str(name_previous_node), str(self.id_node),label=str(self.val_attr),splines='line')
        #name_counter+=1
        name_previous_node+=1
        if gain_ratio:
            tree_gain_ratio_data['avg_children'] += len(self.children)
        else:
            tree_gain_data['avg_children'] += len(self.children)
        for item in self.children:
            graph_array.append(graph.copy())
            item.printTree(depth+1, graph, self, self.id_node, gain_ratio)
        