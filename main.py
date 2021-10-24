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
    threshold = 0.03
    target = 'contraceptive'
    removed_continuous = remove_continuous_columns(df)
    df = removed_continuous[1]

    df = impute_with_mode(df)
    #print(df.head())

    df_train, df_test = split_dataset(df,0.9,target)
    print(df_train.shape)
    print(df_test.shape)
    graph = graphviz.Digraph()
    graph_ratio = graphviz.Digraph()
    """ 
    classValues = list(df[target].value_counts().index) 

    set_init = SetCases(df,len(df),target,classValues)
    root_node = Node(set_init, 0)
    decisionTree(set_init, set_init.get_attributes(),root_node,0,classValues)
    """
    separator = ','
    tree_gain = train(df_train, target,threshold,'gain')
    tree_gain_ratio = train(df_train,target,threshold,'gain_ratio')

    df_test['test_result_gain'] = predict_cases(df_test,tree_gain)
    df_test['correct_prediction_gain'] = df_test[['test_result_gain',target]].apply(lambda x: 1 if x['test_result_gain'] == x[target] else 0, axis=1)
    print('ENTREEEEEEEEEEEEEEEEEEEEEEEEEEEEEE----')


    df_test['test_result_gain_ratio'] = predict_cases(df_test,tree_gain_ratio)
    df_test['correct_prediction_gain_ratio'] = df_test[['test_result_gain_ratio',target]].apply(lambda x: 1 if x['test_result_gain_ratio'] == x[target] else 0, axis=1)

    print('---------------------GAIN--------------------------------')
    print('Accuracy',df_test[df_test['correct_prediction_gain']==1]['correct_prediction_gain'].count()/len(df_test))
    print(pd.crosstab(df_test[target],df_test['test_result_gain']))

    print('---------------------GAIN RATIO--------------------------------')
    print('Accuracy',df_test[df_test['correct_prediction_gain_ratio']==1]['correct_prediction_gain_ratio'].count()/len(df_test))
    print(pd.crosstab(df_test[target],df_test['test_result_gain_ratio']))
    tree_gain.printTree(0,graph,tree_gain,0)
    tree_gain_ratio.printTree(0, graph_ratio, tree_gain_ratio,0)
    
    graph.render(f'test_output/{target}.pdf')
    graph_ratio.render(f'test_output/{target}_ratio.pdf')


def SingleRun(df_train, df_test, threshold, gain_ratio:bool, target):
    print(f'Running with gain_ratio: {gain_ratio} and threshold {threshold}')
    if gain_ratio:
        func = 'gain_ratio'
    else:
        func = 'gain'
    tree_gain = train(df_train, target,threshold,func)
    df_test['test_result_gain'] = predict_cases(df_test,tree_gain)
    df_test['correct_prediction_gain'] = df_test[['test_result_gain',target]].apply(lambda x: 1 if x['test_result_gain'] == x[target] else 0, axis=1)
    return df_test[df_test['correct_prediction_gain']==1]['correct_prediction_gain'].count()/len(df_test)

def hiperpar():
    target = 'Clase'
    df = pd.read_csv('data/diabetes_dataset__2019sugar.csv')
    removed_continuous = remove_continuous_columns(df)
    df = removed_continuous[1]
    df = impute_with_mode(df)
    df_train, df_test = split_dataset(df,0.9,target)
    thresholds = [0.01, 0.02, 0.025, 0.03, 0.05, 0.07, 0.08, 0.09, 0.095, 0.1, 0.2, 0.3, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.4, 0.5]
    gain_results = []
    gain_ratio_results = []
    for elem in thresholds:
        val = SingleRun(df_train, df_test, elem, False, target)
        print(val)
        gain_results.append(val)
    for elem in thresholds:
        val = SingleRun(df_train, df_test, elem, True, target)
        print(val)
        gain_ratio_results.append(val)
    print('thresholds')
    print(thresholds)
    print('Gain')
    print(gain_results)
    print('Gain Ratio')
    print(gain_ratio_results)
    df = pd.DataFrame({"thresholds":thresholds, "gain": gain_results, "gain_ratio":gain_ratio_results})
    plot_result = df.plot('thresholds',['gain','gain_ratio'],figsize=(15,6),title='Ganancia vs Tasa de Ganancia')
    plot_fig = plot_result.get_figure()
    plot_fig.savefig('result.png')

hiperpar()