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
        #print('Depth ' + str(guide_int))
        #gain = D.gain()
        if gain_ratio:
            #print('VOY A USAR GAIN RATIO')
            gain = D.gain_ratio()
        else:
            #print('VOY A USAR GAIN')
            gain = D.gain2()[0]
        #gain = D.gain_ratio()
        #gain = D.gain2()[0]
        #print('Attribute chosen ', gain[0])
        #print("ACA ESTA LA GANANCIA",gain[1])
        if gain[1] < threshold:
            class_name = D.most_frequent_class()
            T.curr_class = class_name
        else:
            T.chosen_att = gain[0]
            A1 = [item for item in A if item != gain[0]]
            subsets = D.separate_data(gain[0])
            #print(f'Cantidad de subsets{len(subsets)}')
            for subset in subsets:
                elem = SetCases(subset[1], len(subset[1]), D.class_column_name,classValues)
                #print(f'Name_counter {name_counter} Size {subset[1].shape}')
                T.gain = round(gain[1],2)
                new_node = Node(elem, name_counter, subset[0])
                name_counter+=1
                T.addChildren(new_node)
                decisionTree(elem, A1, new_node, guide_int+1,classValues,threshold,gain_ratio)