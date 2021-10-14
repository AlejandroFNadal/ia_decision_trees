import pandas as pd
import graphviz
from src.setCases.setCases import SetCases
from src.node.Node import Node
from src.decisionTree.DecisionTree import decisionTree
from src.predictions.Predictions import predict_cases
from config.config import name_counter
from src.split.split import split_dataset
from src.train.train import train
from src.preprocessing.preprocessing import remove_continuous_columns,impute_with_mode


df = pd.read_csv('data/mushrooms.csv')
target = 'class'
removed_continuous = remove_continuous_columns(df)
df = removed_continuous[1]
removed_columns = removed_continuous[0]

df = impute_with_mode(df)

df_train, df_test = split_dataset(df,0.7,target)
print(df_train.shape)
print(df_test.shape)
""" #graph = graphviz.Digraph()
classValues = list(df[target].value_counts().index) 

set_init = SetCases(df,len(df),target,classValues)
root_node = Node(set_init, 0)
decisionTree(set_init, set_init.get_attributes(),root_node,0,classValues)
 """
tree = train(df_train, target)
df_test['test_result'] = predict_cases(df_test,tree)
print(df_test[[target,'test_result']])
df_test['correct_prediction'] = df_test[['test_result',target]].apply(lambda x: 1 if x['test_result'] == x[target] else 0, axis=1)
print(df_test)
print(df_test[df_test['correct_prediction']==1]['correct_prediction'].count())
print(len(df_test))
print('Accuracy',df_test[df_test['correct_prediction']==1]['correct_prediction'].count()/len(df_test))
print(pd.crosstab(df_test['class'],df_test['test_result']))