from src.node.Node import Node
from src.decisionTree.DecisionTree import decisionTree
from src.setCases.setCases import SetCases

def train(df, class_name) -> Node:
    classValues = list(df[class_name].value_counts().index)
    set_init = SetCases(df,len(df),class_name,classValues)
    root_node = Node(set_init, 0)
    decisionTree(set_init, set_init.get_attributes(),root_node,0,classValues)
    return root_node