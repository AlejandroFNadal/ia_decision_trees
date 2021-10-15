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

def _update_slider(value):
    st.session_state["test_slider"] = value
    st.graphviz_chart(graph_array[value])

uploaded_file = st.file_uploader("Ingrese un archivo (CSV, Text o Excel File):",  accept_multiple_files=False, type = ['csv','txt','xlsx'])
delimiter = st.radio("Seleccione un delimitador:",(',', ';', '-'))
threshold = st.slider('Seleccione el valor de Threshold a usar:', 0.0, 1.0, 0.1, 0.05)  # Minimo, Maximo, Default, Step
button = st.button('Cargar Archivo')

if button == True:
    if uploaded_file is not None:
        st.write("Resumen de los datos:")
        if (uploaded_file.name).split('.')[1] in ['csv','txt']:     # Aca usamos la funcion de acuerdo al tipo de archivo 
            dataframe = pd.read_csv(uploaded_file, sep=delimiter)   # CSV y TXT
            st.write(dataframe.head())

        elif (uploaded_file.name).split('.')[1] == 'xlsx':
            dataframe = pd.read_excel(uploaded_file, engine='openpyxl')     # EXCEL
            st.write(dataframe.head())
        
        function = 'gain'
        target = dataframe.columns[-1]
        graph = graphviz.Digraph()
        root_node = train(dataframe, target, threshold, function)
        root_node.printTree(0, graph, root_node, name_counter)
        
        i = 0
        exit = False
        siguiente = False 
        anterior = False
        print = False
        while exit == False:
            siguiente = st.button('Siguiente')
            anterior = st.button('Anterior')
            print = st.button('Mostrar')
            exit = st.button('Salir')
            if siguiente:
                ++i
                siguiente = False
            if anterior: 
                --i
                anterior = False
            if print:
                st.graphviz_chart(graph_array[i])

        # st.graphviz_chart(graph_array[graphs], kwargs={"value": graphs})

        # for graph in graph_array:  
            st.graphviz_chart(graph)

    elif uploaded_file is None:
        st.write('Por favor, ingrese un Archivo.')
        
    

        
    