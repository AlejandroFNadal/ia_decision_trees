import streamlit as st
from io import StringIO
import pandas as pd
import numpy as np
#pip install openpyxl
#pip install xlrd

uploaded_file = st.file_uploader("Choose a file (CSV, Text or Excel File)",  accept_multiple_files=False, type = ['csv','txt','xlsx'])
button = st.button('Cargar Archivo')

if button == True:
    if uploaded_file is not None:
        st.write("Resumen de los datos:")
        if (uploaded_file.name).split('.')[1] == 'csv': # Aca usamos la funcion de acuerdo al tipo de archivo
            dataframe = pd.read_csv(uploaded_file)
            st.write(dataframe.head())

        elif (uploaded_file.name).split('.')[1] == 'xlsx':
            dataframe = pd.read_excel(uploaded_file, index_col=0,  engine='openpyxl')
            st.write(dataframe.head())

        elif (uploaded_file.name).split('.')[1] == 'txt':
            delimiter = st.text_input('Delimitador', max_chars=1, autocomplete=',')
            button = st.button('Cargar Delimitador')
            if button == True:
                if delimiter != '':
                    st.write(delimiter)
                    dataframe = pd.read_csv('output_list.txt', sep=delimiter, header=None)
                    st.write(dataframe.head())
                else:
                    st.write('Por favor, inserte un delimitador')

    elif uploaded_file is None:
        st.write('Cargue un Archivo')

        
    