from src.setCases.setCases import SetCases
from config.config import name_counter
from src.node.Node import Node

def decisionTree(D : SetCases, A : list, T : Node, guide_int : int,classValues : list, threshold : float, gain_ratio:bool):
    """recursive function that creates a tree out of a set of values, using gain or gain ratio

    Args:
        D (SetCases): Object that represent a set of data
        A (list): attributes of dataset
        T (Node): Initial node of the tree, 
        guide_int (int): recursive measurement guide value
        classValues (list): possible values for class
        threshold (float): minimum possible value for gain or gain ratio before stopping recursion
        gain_ratio (bool): if True, gain ratio is used, else, gain is used
    """    
    global name_counter
    if D.is_pure():
        class_name = D.most_frequent_class()
        T.curr_class = class_name
    elif not A:
        class_name = D.most_frequent_class()
        T.curr_class = class_name
    else:
        if gain_ratio:
            gain = D.gain_ratio()
        else:
            #gain2 returns all gain values for each attribute ordered from biggest to smallest and that is why we take the first
            gain = D.gain2()[0]
        if gain[1] < threshold:
            T.gain = gain[1]
            class_name = D.most_frequent_class()
            T.curr_class = class_name
        else:
            T.chosen_att = gain[0]
            # A1 contains all attributes except the one that had the biggest gain or gain_ratio
            A1 = [item for item in A if item != gain[0]]
            subsets = D.separate_data(gain[0])
            #creation of every subset basing the set division on the chosen attribute
            for subset in subsets:
                # creation of object setcases that contains one of the new subsets
                elem = SetCases(subset[1], len(subset[1]), D.class_column_name,classValues)
                T.gain = round(gain[1],2)
                # creation of the new node that will contain the new subset
                new_node = Node(elem, name_counter, subset[0])
                name_counter+=1
                # adding new node to the parent
                T.addChildren(new_node)
                # recursive call
                decisionTree(elem, A1, new_node, guide_int+1,classValues,threshold,gain_ratio)