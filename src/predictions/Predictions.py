from src.node.Node import Node

def predict_case(case, node: Node):
    while node.children:
        node_att = node.chosen_att
        case_att = case[node_att]
        for child in node.children:
            if case_att == child.val_attr:
                node = child
                break
    return node.curr_class

def predict_cases(cases,node:Node):
    predictions = []
    for item,value in cases.iterrows():
        aux = node
        predictions.append(predict_case(value, aux))
    return predictions