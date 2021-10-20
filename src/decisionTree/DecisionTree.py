from src.setCases.setCases import SetCases
from config.config import name_counter
from src.node.Node import Node

def decisionTree(D : SetCases, A : list, T : Node, guide_int : int,classValues : list, threshold : float, gain_ratio:bool):
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
            gain = D.gain2()[0]
        if gain[1] < threshold:
            class_name = D.most_frequent_class()
            T.curr_class = class_name
        else:
            T.chosen_att = gain[0]
            A1 = [item for item in A if item != gain[0]]
            subsets = D.separate_data(gain[0])
            for subset in subsets:
                elem = SetCases(subset[1], len(subset[1]), D.class_column_name,classValues)
                T.gain = round(gain[1],2)
                new_node = Node(elem, name_counter, subset[0])
                name_counter+=1
                T.addChildren(new_node)
                decisionTree(elem, A1, new_node, guide_int+1,classValues,threshold,gain_ratio)