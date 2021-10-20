import sys
import pandas as pd
import graphviz
import pydot

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QVBoxLayout, QLabel, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# from main import MainFunction
from src.predictions.Predictions import predict_cases
from config.config import name_counter, graph_array
from src.split.split import split_dataset
from src.train.train import train
from src.preprocessing.preprocessing import remove_continuous_columns,impute_with_mode

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('./UI.ui',self)
        self.setWindowTitle('Arbol de Decision - Grupo 7')

        self.fileName = ''
        self.df = ''
        self.fileNameText.setText("Nombre del archivo:")
        self.generarArbolButton.setEnabled(False)
        self.cargarDatosButton.setEnabled(False)
        self.tabShowTrees.setEnabled(False)

        self.cargarArchivoButton.clicked.connect(self.openFile) #Una vez cargado el archivo, se habilita el boton de generar el arbol
        self.cargarDatosButton.clicked.connect(self.generateDataset)
        self.generarArbolButton.clicked.connect(self.executeMainFunction)
    
    def openFile(self):
        options = QFileDialog.Options()
        file = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Files (*.txt *.csv *.xlsx);;All Files (*)", options=options)
        if file:
            self.fileName, _ = file
            self.fileNameText.setText("Nombre del archivo: " + (self.fileName).split('/')[-1]) # Muestra el nombre del archivo cargado
            self.cargarDatosButton.setEnabled(True)
        else:
            print("error")
    
    def generateDataset(self):
        if (self.fileName).split('.')[-1] in ['csv','txt']:     # Aca usamos la funcion de acuerdo al tipo de archivo 
                self.df = pd.read_csv(self.fileName, sep=(self.separatorSelector.currentText()))   # CSV y TXT
        elif (self.fileName).split('.')[-1] == 'xlsx':
            self.df = pd.read_excel(self.fileName, engine='openpyxl')     # EXCEL
        print(self.df.head())
        
        self.model = TableModel(self.df.head()) # Aca se cargan los datos en el resumen de los datos
        self.tableView.setModel(self.model)
        self.generarArbolButton.setEnabled(True)
        
    def executeMainFunction(self): # Aca se ejecuta el algoritmo de generacion del arbol
        target = self.df.columns[-1]
        removed_continuous = remove_continuous_columns(self.df)
        df = removed_continuous[1]
        threshold = self.thresholdSelector.value()
        splitValue = self.spinBoxTrainTest.value() / 100
        print(splitValue)

        df = impute_with_mode(df)

        df_train, df_test = split_dataset(df,splitValue,target)
        graph = graphviz.Digraph()
        graph_ratio = graphviz.Digraph()

        tree_gain = train(df_train, target,threshold,'gain')
        tree_gain_ratio = train(df_train,target,threshold,'gain_ratio')

        self.treeGainImage = tree_gain.printTree(0, graph, tree_gain_ratio,name_counter)
        self.treeGainRatioImage = tree_gain_ratio.printTree(0, graph, tree_gain_ratio,name_counter)
        
        self.tabShowTrees.setEnabled(True)

        print("HERE SOMETHING", len(graph_array))
        print("HERE SOMETHING", type(graph))

        # Aca se llama a la funcion para mostrar la imagen del arbol
        self.showTreeGain(graph, target)
        
        # TODO: pasar esto a la GUI
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

    def showTreeGain(self, grafico, target):
        grafico.render(f'test_output/{target}.dot')
        (grafico,) = pydot.graph_from_dot_file(target)
        grafico.write_png(f'test_output/{target}.png')

        #test = QPixmap(grafico)
        #pixmap = QPixmap("icecreamstore.jpg")
        #self.imageGain.setPixmap(test)
        #self.imageGainRatio.setPixmap(pixmap)
        # self.graphicsView.setValue(graph.view())
            
    def showTreeGainRatio(self):
        print('show')

class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = App()
    GUI.show()
    sys.exit(app.exec_())