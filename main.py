import pandas as pd
import graphviz
from src.setCases.setCases import SetCases
from src.node.Node import Node
from src.decisionTree.DecisionTree import decisionTree
from src.predictions.Predictions import predict_cases
from config.config import name_counter


df = pd.read_csv('data/automoviles.csv').head(10)
target = 'AltaGama'
#graph = graphviz.Digraph()
classValues = list(df[target].value_counts().index) 

set_init = SetCases(df,len(df),target,classValues)
root_node = Node(set_init, 0)
decisionTree(set_init, set_init.get_attributes(),root_node,0,classValues)

df['test_result'] = predict_cases(df,root_node)
print(df[[target,'test_result']])
