import sys
import pandas as pd
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtCore import Qt
from main import MainFunction

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
        self.cargarArchivoButton.clicked.connect(self.openFile) #Una vez cargado el archivo, se habilita el boton de generar el arbol
        self.cargarDatosButton.clicked.connect(self.generateDataset)
        self.generarArbolButton.clicked.connect(self.executeMainFunction)
    
    def openFile(self):
        options = QFileDialog.Options()
        file = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Files (*.txt *.csv *.xlsx);;All Files (*)", options=options)
        if file:
            self.fileName, _ = file
            print("MIRA ACA",self.separatorSelector.currentText())
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
        print("Algo")
        #MainFunction(df,self.thresholdSelector.value())

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