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

def MainFunction(df,threshold):

    target = df.columns[-1]
    removed_continuous = remove_continuous_columns(df)
    df = removed_continuous[1]

    df = impute_with_mode(df)
    print(df.head())

    df_train, df_test = split_dataset(df,0.7,target)
    print(df_train.shape)
    print(df_test.shape)
    graph = graphviz.Digraph()
    """ 
    classValues = list(df[target].value_counts().index) 

    set_init = SetCases(df,len(df),target,classValues)
    root_node = Node(set_init, 0)
    decisionTree(set_init, set_init.get_attributes(),root_node,0,classValues)
    """
    tree_gain = train(df_train, target,threshold,'gain',separator)
    tree_gain_ratio = train(df_train,target,threshold,'gain_ratio',separator)

    #tree_gain_ratio.printTree(0, graph, tree_gain_ratio,name_counter)

    #graph.view()

    df_test['test_result_gain'] = predict_cases(df_test,tree_gain)
    df_test['correct_prediction_gain'] = df_test[['test_result_gain',target]].apply(lambda x: 1 if x['test_result_gain'] == x[target] else 0, axis=1)



    df_test['test_result_gain_ratio'] = predict_cases(df_test,tree_gain_ratio)
    df_test['correct_prediction_gain_ratio'] = df_test[['test_result_gain_ratio',target]].apply(lambda x: 1 if x['test_result_gain_ratio'] == x[target] else 0, axis=1)

    print('---------------------GAIN--------------------------------')
    print('Accuracy',df_test[df_test['correct_prediction_gain']==1]['correct_prediction_gain'].count()/len(df_test))
    print(pd.crosstab(df_test[target],df_test['test_result_gain']))

    print('---------------------GAIN RATIO--------------------------------')
    print('Accuracy',df_test[df_test['correct_prediction_gain_ratio']==1]['correct_prediction_gain_ratio'].count()/len(df_test))
    print(pd.crosstab(df_test[target],df_test['test_result_gain_ratio']))


