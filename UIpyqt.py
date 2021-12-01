import sys
import pandas as pd
import graphviz
import pydot
from PyQt5 import QtCore, uic, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QDialog, QLabel, QVBoxLayout, QMessageBox
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
        self.imageGain.setScaledContents(True)
        self.imageGainRatio.setScaledContents(True)
        self.predictBox.setEnabled(False)
        screen_resolution = app.desktop().screenGeometry()
        widthwindow, heightwindow = screen_resolution.width(), screen_resolution.height()
        self.setMaximumWidth(widthwindow*0.9)
        self.setMaximumHeight(heightwindow*0.9)

        self.cargarArchivoButton.setStyleSheet('font: bold')
        self.cargarArchivoButton.clicked.connect(self.openFile) 
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

        self.predictButton.clicked.connect(self.predictData)
            
    def twoThresholds(self):
        if  self.twoThresholdsCheckbox.isChecked():
            self.thresholdSelector2.setEnabled(True)
        else: 
            self.thresholdSelector2.setEnabled(False)

    def openFile(self):
        """
        Opens the file to use with the system file navegator tool
        """        
        options = QFileDialog.Options()
        file = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Files (*.txt *.csv);;All Files (*)", options=options)
        if file:
            self.fileName, _ = file
            self.fileNameText.setText("Nombre del archivo: " + (self.fileName).split('/')[-1]) # Shows the file name
            self.cargarDatosButton.setEnabled(True)
            self.cargarDatosButton.setStyleSheet('font: bold;color: #000000;background-color : #94C973')
            self.predictBox.setEnabled(False)
        else:
            pass
    
    def generateDataset(self):
        """
        Creates a dataset from the datafile. Just are accepted text and csv files
        Remove the continous columns, shows it those column names on the interface
        And enable the Generate Tree's tab
        """        
        # Reset qpixmap y graph of self.imageGain
        self.imageGain.clear()
        self.imageGainRatio.clear()
        if (self.fileName).split('.')[-1] in ['csv','txt']:     # here we load the file as a dataframe 
                self.df = pd.read_csv(self.fileName, sep=(self.separatorSelector.currentText()))   # CSV y TXT


        removed_continuous = remove_continuous_columns(self.df, self.maxValuesAllowed.value())     # Select and delete the continous columns
        self.df = removed_continuous[1]
        self.deletedColumnsLabel.setText('Columnas eliminadas (variables continuas): ' + ', '.join(map(str,removed_continuous[0])))
        
        #This alert to the user that a column looks like an id
        posibles_id = []
        for col in self.df:
            cardinality = self.df[col].nunique()
            if cardinality == len(self.df):
                posibles_id.append(col)
        
        if posibles_id != []:
            self.showAlert(posibles_id)

        self.model = TableModel(self.df.head()) # Aca se cargan los datos en el resumen de los datos
        self.tableView.setModel(self.model)
        

        if len(self.df.columns) < 2:
            self.control1column.setText("Se ha detectado una sola columna. El programa requiere de al menos 2 para funcionar. Revise el delimitador o que su archivo posea al menos 2 columnas")
            self.control1column.setStyleSheet("color: red")
            self.generarArbolButton.setEnabled(False)
            self.generarArbolButton.setStyleSheet('font: bold;color: #777777;background-color : #cccccc')
        else:
            self.control1column.setText("")
            self.generarArbolButton.setEnabled(True)
            self.generarArbolButton.setStyleSheet('font: bold;color: #000000;background-color : #94C973')

    def showAlert(self, posibles_id):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("AVISO!")
        dlg.setText("Se ha detectado que la/s siguiente/s columna/s pueden ser consideradas como IDs, por lo que esto podria generar un arbol que no generalice de manera correcta: \n" + str(posibles_id))
        dlg.exec()

    def executeMainFunction(self): 
        """
        This is the main function, where the values are reseted, threshold and split values are defined, trees are generated and calulate accuracy values
        """        
        self.creatingTreeAlert.setText("El arbol se esta generando... Espere por favor.")
        self.creatingTreeAlert.setStyleSheet('font: bold;color: #777777;background-color : #cccccc')
        self.generarArbolButton.setEnabled(False) # Once the generation in inicialized, we desable the button

        self.gainImage = 0 # Index for accessing the tree step
        self.gainRatioImage = 0
        graph_array.clear()
        graph_array_ratio.clear()
        self.target = self.df.columns[-1]       # We select the class as the las column
        df = self.df
        threshold = self.thresholdSelector.value()   
        if self.twoThresholdsCheckbox.isChecked():
            threshold2 = self.thresholdSelector2.value()  
        splitValue = self.spinBoxTrainTest.value() / 100

        if self.modaCheck.isChecked():
            df = impute_with_mode(df, self.nullValue.text()) 

        df_train, df_test = split_dataset(df,splitValue,self.target) # Train and test split
        graph = graphviz.Digraph()
        graph_ratio = graphviz.Digraph()

        # Here the trees are generated. Gain and Gain ratio with the same or different threshold
        tree_gain = train(df_train, self.target,threshold,'gain')
        if self.twoThresholdsCheckbox.isChecked():
            tree_gain_ratio = train(df_train,self.target,threshold2,'gain_ratio')
        else:
            tree_gain_ratio = train(df_train,self.target,threshold,'gain_ratio')

        if self.detailsCheckbox.isChecked():
            self.treeGainImage = tree_gain.printTree(0, graph, tree_gain,name_counter,'gain')
            self.treeGainRatioImage = tree_gain_ratio.printTree(0, graph_ratio, tree_gain_ratio,name_counter,'gain_ratio')
        else: 
            self.treeGainImage = tree_gain.printTreeWithoutDetails(0, graph, tree_gain,name_counter,'gain')
            self.treeGainRatioImage = tree_gain_ratio.printTreeWithoutDetails(0, graph_ratio, tree_gain_ratio,name_counter,'gain_ratio')

        self.tabShowTrees.setEnabled(True) # Enanable the tab to see the trees

        # Here we call the functions to show the trees
        graph_array.append(graph.copy())
        graph_array_ratio.append(graph_ratio.copy())
        self.showTreeGain(graph_array[self.gainImage], self.target)
        self.showTreeGainRatio(graph_array_ratio[self.gainRatioImage], self.target)
        
        # Generate the confusion matrix
        if not (df_test.empty):
            df_test['test_result_gain'] = predict_cases(df_test,tree_gain)
            df_test['correct_prediction_gain'] = df_test[['test_result_gain',self.target]].apply(lambda x: 1 if x['test_result_gain'] == x[self.target] else 0, axis=1)

            df_test['test_result_gain_ratio'] = predict_cases(df_test,tree_gain_ratio)
            df_test['correct_prediction_gain_ratio'] = df_test[['test_result_gain_ratio',self.target]].apply(lambda x: 1 if x['test_result_gain_ratio'] == x[self.target] else 0, axis=1)

            self.showAccuracy(df_test, self.target)
        else:
            self.accuracyGainLabel.setText('Accuracy: ')
            self.confusionMatrixGainTab.setModel(TableModel(pd.DataFrame([])))
            self.accuracyGainRatioLabel.setText('Accuracy: ')
            self.confusionMatrixGainRatioTab.setModel(TableModel(pd.DataFrame([])))
        
        self.predictBox.setEnabled(True)
        self.nodoRaiz = tree_gain
        self.nodoRaizRatio = tree_gain_ratio
        self.creatingTreeAlert.setText("")
        self.generarArbolButton.setEnabled(True)
        self.createPredictTable(self.df.columns.drop(self.target))

    def nextGain(self):
        """ Show the next step of the gain tree
        """        
        self.gainImage = self.gainImage + 1
        self.prevImagenGain.setEnabled(True)
        if (self.gainImage < len(graph_array)):
            self.showTreeGain(graph_array[self.gainImage], self.target)
            if (self.gainImage >= len(graph_array)):
                self.sigImagenGain.setEnabled(False)
        else: 
            self.sigImagenGain.setEnabled(False)
    
    def prevGain(self):
        """ Show the previous step of the gain tree
        """   
        if self.gainImage > 0:
            self.gainImage = self.gainImage - 1 
            self.showTreeGain(graph_array[self.gainImage], self.target)
            self.sigImagenGain.setEnabled(True)
            if self.gainImage <= 0:
                self.prevImagenGain.setEnabled(False)
        else: 
            self.prevImagenGain.setEnabled(False)

    def nextGainRatio(self):
        """ Show the next step of the gain ratio tree
        """   
        self.prevImagenGainRatio.setEnabled(True)
        self.gainRatioImage = self.gainRatioImage + 1
        if (self.gainRatioImage < len(graph_array_ratio)):
            self.showTreeGainRatio(graph_array_ratio[self.gainRatioImage], self.target)
            if (self.gainRatioImage >= len(graph_array_ratio)):
                self.sigImagenGainRatio.setEnabled(False)
        else: 
            self.sigImagenGainRatio.setEnabled(False)
    
    def prevGainRatio(self):
        """ Show the previous step of the gain ratio tree
        """  
        if self.gainRatioImage > 0:
            self.gainRatioImage = self.gainRatioImage - 1 
            self.showTreeGainRatio(graph_array_ratio[self.gainRatioImage], self.target)
            self.sigImagenGainRatio.setEnabled(True)
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
        """
        Shows a step of the gain tree

        Args:
            grafico ([dot]): [step of the gain tree selected in the interface]
            target ([string]): [class to predict]
        """        
        grafico.render(f'test_output/gain.dot')
        (grafico,) = pydot.graph_from_dot_file(f'test_output/gain.dot')
        grafico.write_png(f'test_output/gain.png')

        test = QPixmap(f'test_output/gain.png')
        self.imageGain.setPixmap(test)
        self.imageGain.adjustSize()
        # test resize(w,h)
            
    def showTreeGainRatio(self, grafico, target):
        """
        Shows a step of the gain ratio tree

        Args:
            grafico ([dot]): [step of the gain ratio tree selected in the interface]
            target ([string]): [class to predict]
        """ 
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

    def createPredictTable(self,columns):
        """
        Creates an empty table with the column names acording to the tree generated
        This table has a single empty row to recibe the values to predict the class

        Args:
            columns ([dataframe]): [column names of the dataframe used to generated the trees]
        """        
        self.tableToPredict.setColumnCount(len(columns))
        self.tableToPredict.setRowCount(1)
        self.tableToPredict.setHorizontalHeaderLabels(columns.tolist())
        self.tableToPredict.setVerticalHeaderLabels(['Ingrese sus datos aqui:'])

    def predictData(self):
        """
        Takes the row values to predict and call the predict_cases function with both trees (gain and gain ratio)
        After that, show the predict values of each tree
        """        
        row = []
        for column in range(0,len(self.df.columns.difference([self.target]))):
            row.append(self.tableToPredict.item(0, column).text())
        dfToPredict = pd.DataFrame([row], columns = self.df.columns.drop(self.target).tolist())
        prediccion = predict_cases(dfToPredict, self.nodoRaiz)
        self.predictedLabel.setText(f"{self.target}: {prediccion[0]}")

        row = []
        for column in range(0,len(self.df.columns.difference([self.target]))):
            row.append(self.tableToPredict.item(0, column).text())
        dfToPredict = pd.DataFrame([row], columns = self.df.columns.drop(self.target).tolist())
        prediccion = predict_cases(dfToPredict, self.nodoRaizRatio)
        self.predictedLabelRatio.setText(f"{self.target}: {prediccion[0]}")

class TableModel(QtCore.QAbstractTableModel): # This class is for generate the tables in the UI (data preview and confusion matrix)
    """
    Create a table with the atributes recived. 

    Args:
        QtCore ([module]): [module that has the table model class generator]
    """    
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role): # Obtain the values
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role): # Obtain the column names and row names
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
    