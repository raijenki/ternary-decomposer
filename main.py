import sys
import os
import ogr, osr
import gdal, gdalnumeric
import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QFileDialog, QProgressBar
from PyQt5.QtWidgets import QPushButton, QMessageBox, QCheckBox
from PyQt5.QtCore import QSize


# Ternary Decomposer
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(350, 220))    
        self.setWindowTitle("Ternary Decomposer") 
        
        # Main button
        fileBtn = QPushButton('Start decomposition!', self)
        fileBtn.clicked.connect(self.fileDialog)
        fileBtn.resize(200, 30)
        fileBtn.move(64, 100)

        cbox = QCheckBox("Produce Shapefiles", self)
        cbox.setChecked(False)
        cbox.move(20,60)
        cbox.resize(320,40)
        cbox.stateChanged.connect(self.clickBox)
        self.checkedBox = 0

        # Label
        self.processWarn = QLabel(self)
        self.processWarn.setWordWrap(True)
        self.processWarn.setText('<i>The processing will start automatically after the file selection.</i>')
        self.processWarn.resize(300,60)
        self.processWarn.move(20, 130)

        # PBar
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(0, 0, 300, 25)
        self.progressBar.setMaximum(100)
        self.progressBar.move(50, 25)

        # Process Status
        self.processStatus = QLabel(self)
        self.processStatus.setText('Waiting for file selection...')
        self.processStatus.resize(350,60)
        self.processStatus.move(90, 6)

    def clickBox(self, state):
        if state == QtCore.Qt.Checked:
            self.checkedBox = 1
            print(self.checkedBox)
        else:
            self.checkedBox = 0

    # File Dialog
    def fileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"Ternary File", "","Geotiff Files (*.tif)", options=options)
        options |= QFileDialog.DontUseNativeDialog
        if fileName:
            self.raster2array(fileName)

    # Decompose
    def raster2array(self, filename):

        decomposition = [ '111', '112', '113', '121', '122', '123', '131', '132', '133', '211', '212', '213', '221', '222', '223', '231', '232', '233', '311', '312', '313', '321', '322', '323', '331', '332', '333']

        self.processStatus.setText('Loading bands...')
        self.progressBar.setValue(5)
        # Get file, open with GDAL and separate rasters
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        source = gdal.Open(filename)
        K = np.array(source.GetRasterBand(1).ReadAsArray())
        Th = np.array(source.GetRasterBand(2).ReadAsArray())
        U = np.array(source.GetRasterBand(3).ReadAsArray())

        # Create zeros for all elements on low, mid, high
        K_ref = np.zeros(K.shape, dtype=np.uint8)
        Th_ref = np.zeros(Th.shape, dtype=np.uint8)
        U_ref = np.zeros(U.shape, dtype=np.uint8)

        self.processStatus.setText('Decomposing potassium...')
        self.progressBar.setValue(15)

        # Actual separation loop
        for i, j in np.ndindex(K.shape):
            if(K[i, j] <= 85):
                K_ref[i, j] = 1
            if(K[i, j] > 85 and K[i, j] <= 170):
                K_ref[i, j] = 128 
            if(K[i, j] > 170):
                K_ref[i, j] = 255        
        
        self.processStatus.setText('Decomposing thorium...')
        self.progressBar.setValue(25)

        
        # Actual separation loop
        for i, j in np.ndindex(Th.shape):
            if(Th[i, j] <= 85):
                Th_ref[i, j] = 1
            if(Th[i, j] > 85 and Th[i, j] <= 170):
                Th_ref[i, j] = 128 
            if(Th[i, j] > 170):
                Th_ref[i, j] = 255
        del Th

        self.processStatus.setText('Decomposing uranium...')
        self.progressBar.setValue(35)

        # Actual separation loop
        for i, j in np.ndindex(U.shape):
            if(U[i, j] <= 85):
                U_ref[i, j] = 1
            if(U[i, j] > 85 and U[i, j] <= 170):
                U_ref[i, j] = 128 
            if(U[i, j] > 170):
                U_ref[i, j] = 255        
        del U

        progressNumber = 1
        self.processStatus.setText('Exporting 1/27...')
    

        for i in decomposition:
            progressValue = 35 + 2.4
            outputName = filename + '_' + i  + '.tif'
            outputPath = os.path.join(fileDir, outputName)
            self.progressBar.setValue(progressValue)
            R = np.zeros(K.shape, dtype=np.uint8)
            G = np.zeros(K.shape, dtype=np.uint8)
            B = np.zeros(K.shape, dtype=np.uint8)
            progressText = 'Exporting' + str(progressNumber) + '/27...'

            for w, x in np.ndindex(K.shape):
                if(K_ref[w, x] == self.colortransform(i[0]) and Th_ref[w, x] == self.colortransform(i[1]) and U_ref[w, x] == self.colortransform(i[2])):
                    R[w, x] = self.colortransform(i[0])
                    G[w, x] = self.colortransform(i[1])
                    B[w, x] = self.colortransform(i[2])
            # Create Gtiff driver with RGB Opts   
            dst_ds = gdal.GetDriverByName('GTiff').Create(outputName, K.shape[1], K.shape[0], 3, gdal.GDT_Byte, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
            # Copy georeferencing info
            gdalnumeric.CopyDatasetInfo(source, dst_ds)
            # Write arrays
            dst_ds.GetRasterBand(1).WriteArray(R)
            dst_ds.GetRasterBand(1).SetNoDataValue(0)
            dst_ds.FlushCache()
            dst_ds.GetRasterBand(2).WriteArray(G)
            dst_ds.GetRasterBand(2).SetNoDataValue(0)
            dst_ds.FlushCache()
            dst_ds.GetRasterBand(3).WriteArray(B)
            dst_ds.GetRasterBand(3).SetNoDataValue(0)
            dst_ds.FlushCache()

            if(self.checkedBox == 1):
                src_ds = dst_ds
                proj = osr.SpatialReference(wkt=src_ds.GetProjection())
                srcband = src_ds.GetRasterBand(2)
                dst_layername = i
                drv = ogr.GetDriverByName("ESRI Shapefile")
                dst_ds = drv.CreateDataSource( dst_layername + ".shp" )
                #gdalnumeric.CopyDatasetInfo(src_ds, dst_ds)
                dst_layer = dst_ds.CreateLayer(dst_layername, proj )
                gdal.Polygonize( srcband, None, dst_layer, -1, [], callback=None )
                dst_ds.FlushCache()
                
            dst_ds = None
        self.processStatus.setText('')
        self.progressBar.setValue(100)
        QMessageBox.about(self, "Ternary Decomposer", "It's done!")

    def colortransform(self, indexcolor):
        if (int(indexcolor) == 1):
            return 1
        if (int(indexcolor) == 2):
            return 128
        if (int(indexcolor) == 3):
            return 255

# Init Qt Window
if __name__ == "__main__":
    #appctxt = ApplicationContext()
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
