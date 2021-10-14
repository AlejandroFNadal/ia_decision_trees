from src.node.Node import Node
import time
def predict_case(case, node: Node):
    print("Predicting case: ", case)
    while node.children:
        flag = False
        #sleep execution
        #time.sleep(0.5)
        print(f'CHOSEN ATT {node.chosen_att}')
        #print(f'VAL ATTR {node.val_attr}')
        node_att = node.chosen_att
        case_att = case[node_att]
        for child in node.children:
            print(f'VAL ATTR {child.val_attr}')
            if case_att == child.val_attr:
                flag = True
                node = child
                break
        if not flag:
            print("No child found")
            return node.data.most_frequent_class()
            
    return node.curr_class

def predict_cases(cases,node:Node):
    predictions = []
    for item,value in cases.iterrows():
        aux = node
        predictions.append(predict_case(value, aux))
    return predictions