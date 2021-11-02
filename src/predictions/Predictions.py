from src.node.Node import Node

def predict_case(case, node: Node):
    """ predicts a single case

    Args:
        case (Pandas Series): a single row of a dataset
        node (Node): starts with root node, traverses tree looking for those that match the case given

    Returns:
        str: class predicted for given case 
    """    
    while node.children:
        #width first
        flag = False
        node_att = node.chosen_att
        case_att = case[node_att]
        for child in node.children:
            if case_att == child.val_attr:
                flag = True
                node = child
                break
        if not flag:
            return node.data.most_frequent_class()
            
    return node.curr_class

def predict_cases(cases,node:Node):
    """Predicts a set of cases

    Args:
        cases (Pandas Series): A pandas series with the cases to predict
        node (Node): root node at start

    Returns:
        list: classes predicted for each given case
    """    
    predictions = []
    for item,value in cases.iterrows():
        aux = node
        predictions.append(predict_case(value, aux))
    return predictions