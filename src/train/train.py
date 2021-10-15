from src.node.Node import Node
from src.decisionTree.DecisionTree import decisionTree
from src.setCases.setCases import SetCases

def train(df, class_name, threshold, method) -> Node:
    classValues = list(df[class_name].value_counts().index)
    set_init = SetCases(df,len(df),class_name,classValues)
    root_node = Node(set_init, 0)
    if method == 'gain':
        decisionTree(set_init, set_init.get_attributes(),root_node,0,classValues,threshold,False)
    else:
        decisionTree(set_init, set_init.get_attributes(),root_node,0,classValues,threshold,True)
    return root_node