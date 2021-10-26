import sys
import pandas as pd
import graphviz
import pydot
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PIL import Image
from src.predictions.Predictions import predict_cases
from config.config import name_counter, graph_array, graph_array_ratio
from src.split.split import split_dataset
from src.train.train import train
from src.preprocessing.preprocessing import remove_continuous_columns,impute_with_mode

class App(QMainWindow): 
    def __init__(self):
        super().__init__()
        uic.loadUi('./UI.ui',self)
        self.setWindowTitle('Arbol de Decision - Grupo 7')
        self.gainImage = 0
        self.gainRatioImage = 0
        self.target = ''
        self.fileName = ''
        self.df = ''
        self.fileNameText.setText("Nombre del archivo:")
        self.generarArbolButton.setEnabled(False)
        self.cargarDatosButton.setEnabled(False)
        self.tabShowTrees.setEnabled(False)
        self.prevImagenGain.setEnabled(False)
        self.thresholdSelector2.setEnabled(False)

        self.cargarArchivoButton.setStyleSheet('font: bold')
        self.cargarArchivoButton.clicked.connect(self.openFile) #Una vez cargado el archivo, se habilita el boton de generar el arbol
        self.cargarDatosButton.clicked.connect(self.generateDataset)
        self.generarArbolButton.clicked.connect(self.executeMainFunction)

        self.sigImagenGain.clicked.connect(self.nextGain)
        self.prevImagenGain.clicked.connect(self.prevGain)
        self.sigImagenGainRatio.clicked.connect(self.nextGainRatio)
        self.prevImagenGainRatio.clicked.connect(self.prevGainRatio)

        self.firstImageGain.clicked.connect(self.showFirstGain)
        self.lastImageGain.clicked.connect(self.showLastGain)
        self.firstImageGainRatio.clicked.connect(self.showFirstGainRatio)
        self.lastImageGainRatio.clicked.connect(self.showLastGainRatio)

        self.twoThresholdsCheckbox.stateChanged.connect(self.twoThresholds)

        self.viewImageSystemGain.clicked.connect(self.showInSystemApp)
        self.viewImageSystemGainRatio.clicked.connect(self.showInSystemAppRatio)
            

    def twoThresholds(self):
        if  self.twoThresholdsCheckbox.isChecked():
            self.thresholdSelector2.setEnabled(True)
        else: 
            self.thresholdSelector2.setEnabled(False)

    def openFile(self):
        options = QFileDialog.Options()
        file = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Files (*.txt *.csv *.xlsx);;All Files (*)", options=options)
        if file:
            self.fileName, _ = file
            self.fileNameText.setText("Nombre del archivo: " + (self.fileName).split('/')[-1]) # Muestra el nombre del archivo cargado
            self.cargarDatosButton.setEnabled(True)
            self.cargarDatosButton.setStyleSheet('font: bold;color: #000000;background-color : #94C973')
        else:
            print("error")
    
    def generateDataset(self):
        #Resetea qpixmap y graph of self.imageGain
        self.imageGain.clear()
        self.imageGainRatio.clear()
        if (self.fileName).split('.')[-1] in ['csv','txt']:     # Aca usamos la funcion de acuerdo al tipo de archivo 
                self.df = pd.read_csv(self.fileName, sep=(self.separatorSelector.currentText()))   # CSV y TXT
        elif (self.fileName).split('.')[-1] == 'xlsx':
            self.df = pd.read_excel(self.fileName, engine='openpyxl')     # EXCEL
        print(self.df.head())

        removed_continuous = remove_continuous_columns(self.df, self.maxValuesAllowed.value())     # Se seleccionan y eliminan las columnas continuas
        self.df = removed_continuous[1]
        self.deletedColumnsLabel.setText('Columnas eliminadas (variables continuas): ' + ', '.join(map(str,removed_continuous[0])))
        
        self.model = TableModel(self.df.head()) # Aca se cargan los datos en el resumen de los datos
        self.tableView.setModel(self.model)
        self.generarArbolButton.setEnabled(True)
        self.generarArbolButton.setStyleSheet('font: bold;color: #000000;background-color : #94C973')
        
    def executeMainFunction(self): # Aca se ejecuta el algoritmo de generacion del arbol
        graph_array.clear()
        graph_array_ratio.clear()
        self.target = self.df.columns[-1]       # Se selecciona la CLASE
        df = self.df
        threshold = self.thresholdSelector.value()   
        if self.twoThresholdsCheckbox.isChecked():
            threshold2 = self.thresholdSelector2.value()  
        splitValue = self.spinBoxTrainTest.value() / 100

        df = impute_with_mode(df, self.nullValue.text()) 

        df_train, df_test = split_dataset(df,splitValue,self.target) # Se separan los valores para Train y Test
        graph = graphviz.Digraph()
        graph_ratio = graphviz.Digraph()

        # Se generan los arboles para ambos algoritmos
        tree_gain = train(df_train, self.target,threshold,'gain')
        if self.twoThresholdsCheckbox.isChecked():
            print("HERE IS THE THRESHOLD 2", threshold2)
            tree_gain_ratio = train(df_train,self.target,threshold2,'gain_ratio')
        else:
            tree_gain_ratio = train(df_train,self.target,threshold,'gain_ratio')

        self.treeGainImage = tree_gain.printTree(0, graph, tree_gain,name_counter,'gain')
        self.treeGainRatioImage = tree_gain_ratio.printTree(0, graph_ratio, tree_gain_ratio,name_counter,'gain_ratio')
        
        self.tabShowTrees.setEnabled(True) # Habilita las tabs para ver los arboles

        # Aca se llama a la funcion para mostrar la imagen del arbol
        graph_array.append(graph.copy())
        graph_array_ratio.append(graph_ratio.copy())

        self.showTreeGain(graph_array[self.gainImage], self.target)
        self.showTreeGainRatio(graph_array_ratio[self.gainRatioImage], self.target)
        
        # Esto genera las matrices de confusion
        if not (df_test.empty):
            df_test['test_result_gain'] = predict_cases(df_test,tree_gain)
            df_test['correct_prediction_gain'] = df_test[['test_result_gain',self.target]].apply(lambda x: 1 if x['test_result_gain'] == x[self.target] else 0, axis=1)

            df_test['test_result_gain_ratio'] = predict_cases(df_test,tree_gain_ratio)
            df_test['correct_prediction_gain_ratio'] = df_test[['test_result_gain_ratio',self.target]].apply(lambda x: 1 if x['test_result_gain_ratio'] == x[self.target] else 0, axis=1)

            self.showAccuracy(df_test, self.target)

    def nextGain(self):
        self.gainImage = self.gainImage + 1
        self.prevImagenGain.setEnabled(True)
        if (self.gainImage < len(graph_array)):
            self.showTreeGain(graph_array[self.gainImage], self.target)
            if (self.gainImage >= len(graph_array)):
                self.sigImagenGain.setEnabled(False)
        else: 
            self.sigImagenGain.setEnabled(False)
    
    def prevGain(self):
        if self.gainImage > 0:
            self.gainImage = self.gainImage - 1 
            self.showTreeGain(graph_array[self.gainImage], self.target)
            if self.gainImage <= 0:
                self.prevImagenGain.setEnabled(False)
        else: 
            self.prevImagenGain.setEnabled(False)

    def nextGainRatio(self):
        self.prevImagenGainRatio.setEnabled(True)
        self.gainRatioImage = self.gainRatioImage + 1
        if (self.gainRatioImage < len(graph_array_ratio)):
            self.showTreeGainRatio(graph_array_ratio[self.gainRatioImage], self.target)
            if (self.gainRatioImage >= len(graph_array_ratio)):
                self.sigImagenGainRatio.setEnabled(False)
        else: 
            self.sigImagenGainRatio.setEnabled(False)
    
    def prevGainRatio(self):
        if self.gainRatioImage > 0:
            self.gainRatioImage = self.gainRatioImage - 1 
            self.showTreeGainRatio(graph_array_ratio[self.gainRatioImage], self.target)
            if self.gainRatioImage <= 0:
                self.prevImagenGainRatio.setEnabled(False)
        else: 
            self.prevImagenGainRatio.setEnabled(False)

    def showFirstGain(self):
        self.gainImage = 0
        self.showTreeGain(graph_array[0], self.target)
        self.sigImagenGain.setEnabled(True)
        self.prevImagenGain.setEnabled(False)

    def showLastGain(self):
        self.gainImage = len(graph_array) - 1
        self.showTreeGain(graph_array[len(graph_array)-1], self.target)
        self.sigImagenGain.setEnabled(False)
        self.prevImagenGain.setEnabled(True)

    def showFirstGainRatio(self):
        self.gainRatioImage = 0
        self.showTreeGainRatio(graph_array_ratio[0], self.target)
        self.sigImagenGainRatio.setEnabled(True)
        self.prevImagenGainRatio.setEnabled(False)

    def showLastGainRatio(self):
        self.gainRatioImage = len(graph_array_ratio)-1
        self.showTreeGainRatio(graph_array_ratio[len(graph_array_ratio)-1], self.target)
        self.sigImagenGainRatio.setEnabled(False)
        self.prevImagenGainRatio.setEnabled(True)

    def showTreeGain(self, grafico, target):
        grafico.render(f'test_output/gain.dot')
        (grafico,) = pydot.graph_from_dot_file(f'test_output/gain.dot')
        grafico.write_png(f'test_output/gain.png')

        test = QPixmap(f'test_output/gain.png')
        self.imageGain.setPixmap(test)
            
    def showTreeGainRatio(self, grafico, target):
        grafico.render(f'test_output/gain_ratio.dot')
        (grafico,) = pydot.graph_from_dot_file(f'test_output/gain_ratio.dot')
        grafico.write_png(f'test_output/gain_ratio.png')
        
        test_ratio = QPixmap(f'test_output/gain_ratio.png')
        self.imageGainRatio.setPixmap(test_ratio)
    
    def showAccuracy(self, df_test, target):
        # ---------------------GAIN--------------------------------'
        self.accuracyGainLabel.setText('Accuracy: ' + str(df_test[df_test['correct_prediction_gain']==1]['correct_prediction_gain'].count()/len(df_test)))
        self.gainConfusionMatrix = TableModel(pd.crosstab(df_test[target],df_test['test_result_gain'])) # Aca se cargan los datos en el resumen de los datos
        self.confusionMatrixGainTab.setModel(self.gainConfusionMatrix)
        # ---------------------GAIN RATIO--------------------------------
        self.accuracyGainRatioLabel.setText('Accuracy: ' + str(df_test[df_test['correct_prediction_gain_ratio']==1]['correct_prediction_gain_ratio'].count()/len(df_test)))
        self.gainRatioConfusionMatrix = TableModel(pd.crosstab(df_test[target],df_test['test_result_gain_ratio'])) # Aca se cargan los datos en el resumen de los datos
        self.confusionMatrixGainRatioTab.setModel(self.gainRatioConfusionMatrix)

    def showInSystemApp(self):
        with Image.open('test_output/gain.png') as img:
            img.show()

    def showInSystemAppRatio(self):
        with Image.open('test_output/gain_ratio.png') as img:
            img.show()

class TableModel(QtCore.QAbstractTableModel): # Esta clase es para generar las tablas (Preview de datos y matrices de confusion)
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role): # Obtiene los valores
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role): # Obtiene los nombres de las columnas y/o filas 
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = App()
    GUI.showMaximized()
    sys.exit(app.exec_())