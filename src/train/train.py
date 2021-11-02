from src.node.Node import Node
from src.decisionTree.DecisionTree import decisionTree
from src.setCases.setCases import SetCases

def train(df, class_name, threshold, method) -> Node:
    """ Train the decision tree.

    Args:
        df ([DataFrame]): DataFrame with the training data
        class_name ([str]): Name of the class column
        threshold ([float]): Threshold to be used in decision Tree algorithm
        method ([str]): gain or gain ratio

    Returns:
        Node: returns the root node of the decision tree, from where all nodes can be accessed
    """    
    classValues = list(df[class_name].value_counts().index)
    #create a set of cases for the training data
    set_init = SetCases(df,len(df),class_name,classValues)
    #create the root node
    root_node = Node(set_init, 0)
    # Call the decision tree algorithm, with False as a parameter if the method is gain, otherwise, it is called with True (gain ratio)
    if method == 'gain':
        decisionTree(set_init, set_init.get_attributes(),root_node,0,classValues,threshold,False)
    else:
        decisionTree(set_init, set_init.get_attributes(),root_node,0,classValues,threshold,True)
    return root_node