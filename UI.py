from re import I
import streamlit as st
from io import StringIO
import pandas as pd
import numpy as np
#pip install openpyxl
#pip install xlrd
import pandas as pd
import graphviz
from src.setCases.setCases import SetCases
from src.node.Node import Node
from src.decisionTree.DecisionTree import decisionTree
from src.predictions.Predictions import predict_cases
from config.config import name_counter,graph_array
from src.train.train import train
from src.split.split import split_dataset
from src.preprocessing.preprocessing import remove_continuous_columns,impute_with_mode

if 'count' not in st.session_state:
    st.session_state['count'] = 0
else:
    st.session_state['count'] = 0

uploaded_file = st.file_uploader("Ingrese un archivo (CSV, Text o Excel File):",  accept_multiple_files=False, type = ['csv','txt','xlsx'])
delimiter = st.radio("Seleccione un delimitador:",(',', ';', '-'))
threshold = st.slider('Seleccione el valor de Threshold a usar:', 0.0, 1.0, 0.1, 0.05)  # Minimo, Maximo, Default, Step
button = st.button('Cargar Archivo', key= "add")

if button == True:
    if uploaded_file is not None:
        st.write("Resumen de los datos:")
        if (uploaded_file.name).split('.')[1] in ['csv','txt']:     # Aca usamos la funcion de acuerdo al tipo de archivo 
            dataframe = pd.read_csv(uploaded_file, sep=delimiter)   # CSV y TXT
            st.write(dataframe.head())
            Tree = 0

        elif (uploaded_file.name).split('.')[1] == 'xlsx':
            dataframe = pd.read_excel(uploaded_file, engine='openpyxl')     # EXCEL
            st.write(dataframe.head())
            Tree = 0
        
        function = 'gain'
        target = dataframe.columns[-1]
        removed_continuous = remove_continuous_columns(dataframe)
        dataframe = removed_continuous[1]
        df_train, df_test = split_dataset(dataframe,0.7,target)

        graph = graphviz.Digraph()

        Tree = train(df_train, target, threshold, function)
        Tree.printTree(0, graph, Tree, name_counter)
        
        df_test['Test Result'] = predict_cases(df_test,Tree)
        df_test['Correct Prediction'] = df_test[['Test Result',target]].apply(lambda x: 1 if x['Test Result'] == x[target] else 0, axis=1)
        print('---------------------ACURRACY--------------------------------')
        print('Accuracy value:',df_test[df_test['Correct Prediction']==1]['Correct Prediction'].count()/len(df_test))
        #print(pd.crosstab(df_test[target],df_test['Test Result:']))



        print("Mira cuantas cosas hay aca", len(graph_array))
        
        for graph in graph_array:  
            st.graphviz_chart(graph)
        if 'count' not in st.session_state:
            st.session_state['count'] = 0
        else:
            st.session_state['count'] = 0
    elif uploaded_file is None:
        st.write('Por favor, ingrese un Archivo.')
        
    

        
    