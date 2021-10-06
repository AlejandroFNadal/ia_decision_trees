import streamlit as st
from io import StringIO
import pandas as pd
import numpy as np
#pip install openpyxl
#pip install xlrd

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

    elif uploaded_file is None:
        st.write('Por favor, ingrese un Archivo.')

        
    