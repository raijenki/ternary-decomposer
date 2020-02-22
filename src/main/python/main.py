import sys
import os
import gdal, osr
import gdalnumeric
import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QFileDialog, QProgressBar
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize
from fbs_runtime.application_context.PyQt5 import ApplicationContext


# Ternary Decomposer
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(350, 170))    
        self.setWindowTitle("Ternary Decomposer") 

        # Main button
        fileBtn = QPushButton('Start decomposition!', self)
        fileBtn.clicked.connect(self.fileDialog)
        fileBtn.resize(200, 30)
        fileBtn.move(64, 70)

        # Label
        self.processWarn = QLabel(self)
        self.processWarn.setWordWrap(True)
        self.processWarn.setText('<i>The processing will start automatically after the file selection.</i>')
        self.processWarn.resize(300,60)
        self.processWarn.move(20, 100)

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

    # File Dialog
    def fileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"Ternary File", "","Geotiff Files (*.tif)", options=options)
        options |= QFileDialog.DontUseNativeDialog
        if fileName:
            self.raster2array(fileName)
    
    # Decompose
    def raster2array(self, filename):
        self.processStatus.setText('Loading bands...')
        self.progressBar.setValue(5)
        # Get file, open with GDAL and separate rasters
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        source = gdal.Open(filename)
        K = np.array(source.GetRasterBand(1).ReadAsArray())
        Th = np.array(source.GetRasterBand(2).ReadAsArray())
        U = np.array(source.GetRasterBand(3).ReadAsArray())

        # Create rasters for K element on low, mid, high
        K_low = np.zeros(K.shape, dtype=np.uint8)
        K_mid = np.zeros(K.shape, dtype=np.uint8)
        K_high = np.zeros(K.shape, dtype=np.uint8)

        self.processStatus.setText('Decomposing potassium...')
        self.progressBar.setValue(15)

        # Actual separation loop
        for i, j in np.ndindex(K.shape):
            if(K[i, j] <= 85):
                K_low[i, j] = 1
            if(K[i, j] > 85 and K[i, j] <= 170):
                K_mid[i, j] = 128 
            if(K[i, j] > 170):
                K_high[i, j] = 255        

        self.processStatus.setText('Decomposing thorium...')
        self.progressBar.setValue(25)

        # Create rasters for Th element on low, mid, high
        Th_low = np.zeros(Th.shape, dtype=np.uint8)
        Th_mid = np.zeros(Th.shape, dtype=np.uint8)
        Th_high = np.zeros(Th.shape, dtype=np.uint8)
        
        # Actual separation loop
        for i, j in np.ndindex(Th.shape):
            if(Th[i, j] <= 85):
                Th_low[i, j] = 1
            if(Th[i, j] > 85 and Th[i, j] <= 170):
                Th_mid[i, j] = 128 
            if(Th[i, j] > 170):
                Th_high[i, j] = 255  

        self.processStatus.setText('Decomposing uranium...')
        self.progressBar.setValue(35)

        # Create rasters for U element on low, mid, high
        U_low = np.zeros(U.shape, dtype=np.uint8)
        U_mid = np.zeros(U.shape, dtype=np.uint8)
        U_high = np.zeros(U.shape, dtype=np.uint8)

        # Actual separation loop
        for i, j in np.ndindex(U.shape):
            if(U[i, j] <= 85):
                U_low[i, j] = 1
            if(U[i, j] > 85 and U[i, j] <= 170):
                U_mid[i, j] = 128 
            if(U[i, j] > 170):
                U_high[i, j] = 255        

        self.processStatus.setText('Exporting 1/27...')
        self.progressBar.setValue(38)

        # 111
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_low[i, j] == 1 and Th_low[i, j] == 1 and U_low[i, j] == 1 ):
                R[i, j] = 1
                G[i, j] = 1
                B[i, j] = 1

        # Gotta do this way or TIFF problem
        outputPath = os.path.join(fileDir, '111.tif' )
        # Create Gtiff driver with RGB Opts   
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
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

        self.processStatus.setText('Exporting 2/27...')
        self.progressBar.setValue(40)

        # Repeat - 112
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_low[i, j] == 1 and Th_low[i, j] == 1 and U_mid[i, j] == 128 ):
                R[i, j] = 1
                G[i, j] = 1
                B[i, j] = 128

        outputPath = os.path.join(fileDir, '112.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        self.processStatus.setText('Exporting 3/27...')
        self.progressBar.setValue(43)
        # 113
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_low[i, j] == 1 and Th_low[i, j] == 1 and U_high[i, j] == 255 ):
                R[i, j] = 1
                G[i, j] = 1
                B[i, j] = 255
        outputPath = os.path.join(fileDir, '113.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        self.processStatus.setText('Exporting 4/27...')
        self.progressBar.setValue(46)
        # 121
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_low[i, j] == 1 and Th_mid[i, j] == 128 and U_low[i, j] == 1 ):
                R[i, j] = 1
                G[i, j] = 128
                B[i, j] = 1
        outputPath = os.path.join(fileDir, '121.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        # 122
        self.processStatus.setText('Exporting 5/27...')
        self.progressBar.setValue(49)
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_low[i, j] == 1 and Th_mid[i, j] == 128 and U_mid[i, j] == 128 ):
                R[i, j] = 1
                G[i, j] = 128
                B[i, j] = 128
        outputPath = os.path.join(fileDir, '122.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        self.processStatus.setText('Exporting 6/27...')
        self.progressBar.setValue(52)
        # 123
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_low[i, j] == 1 and Th_mid[i, j] == 128 and U_high[i, j] == 255 ):
                R[i, j] = 1
                G[i, j] = 128
                B[i, j] = 255
        outputPath = os.path.join(fileDir, '123.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        self.processStatus.setText('Exporting 7/27...')
        self.progressBar.setValue(55)
        # 131
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_low[i, j] == 1 and Th_high[i, j] == 255 and U_low[i, j] == 1 ):
                R[i, j] = 1
                G[i, j] = 255
                B[i, j] = 1
        outputPath = os.path.join(fileDir, '131.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()
        self.processStatus.setText('Exporting 8/27...')
        self.progressBar.setValue(58)
        # 132
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_low[i, j] == 1 and Th_high[i, j] == 255 and U_mid[i, j] == 128 ):
                R[i, j] = 1
                G[i, j] = 255
                B[i, j] = 128
        outputPath = os.path.join(fileDir, '132.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        self.processStatus.setText('Exporting 9/27...')
        self.progressBar.setValue(61)
        # 133
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_low[i, j] == 1 and Th_high[i, j] == 255 and U_high[i, j] == 255 ):
                R[i, j] = 1
                G[i, j] = 255
                B[i, j] = 255
        outputPath = os.path.join(fileDir, '133.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        self.processStatus.setText('Exporting 10/27...')
        self.progressBar.setValue(64)
        # 211
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_mid[i, j] == 128 and Th_low[i, j] == 1 and U_low[i, j] == 1 ):
                R[i, j] = 128
                G[i, j] = 1
                B[i, j] = 1
        outputPath = os.path.join(fileDir, '211.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        self.processStatus.setText('Exporting 11/27...')
        self.progressBar.setValue(67)
        # 212
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_mid[i, j] == 128 and Th_low[i, j] == 1 and U_mid[i, j] == 128 ):
                R[i, j] = 128
                G[i, j] = 1
                B[i, j] = 128
        outputPath = os.path.join(fileDir, '212.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        self.processStatus.setText('Exporting 12/27...')
        self.progressBar.setValue(70)
        # 213
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_mid[i, j] == 128 and Th_low[i, j] == 1 and U_high[i, j] == 255 ):
                R[i, j] = 128
                G[i, j] = 1
                B[i, j] = 255
        outputPath = os.path.join(fileDir, '213.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        self.processStatus.setText('Exporting 13/27...')
        self.progressBar.setValue(73)
        # 221
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_mid[i, j] == 128 and Th_mid[i, j] == 128 and U_low[i, j] == 1 ):
                R[i, j] = 128
                G[i, j] = 128
                B[i, j] = 1
        outputPath = os.path.join(fileDir, '221.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()
        self.processStatus.setText('Exporting 14/27...')
        self.progressBar.setValue(76)
        # 222
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_mid[i, j] == 128 and Th_mid[i, j] == 128 and U_mid[i, j] == 128 ):
                R[i, j] = 128
                G[i, j] = 128
                B[i, j] = 128
        outputPath = os.path.join(fileDir, '222.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        self.processStatus.setText('Exporting 15/27...')
        self.progressBar.setValue(78)
        # 223
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_mid[i, j] == 128 and Th_mid[i, j] == 128 and U_high[i, j] == 255 ):
                R[i, j] = 128
                G[i, j] = 128
                B[i, j] = 255
        outputPath = os.path.join(fileDir, '223.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        self.processStatus.setText('Exporting 16/27...')
        self.progressBar.setValue(80)
        # 231
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_mid[i, j] == 128 and Th_high[i, j] == 255 and U_low[i, j] == 1 ):
                R[i, j] = 128
                G[i, j] = 255
                B[i, j] = 1
        outputPath = os.path.join(fileDir, '231.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        self.processStatus.setText('Exporting 17/27...')
        self.progressBar.setValue(82)
        # 232
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_mid[i, j] == 128 and Th_high[i, j] == 255 and U_mid[i, j] == 128 ):
                R[i, j] = 128
                G[i, j] = 255
                B[i, j] = 128
        outputPath = os.path.join(fileDir, '232.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        self.processStatus.setText('Exporting 18/27...')
        self.progressBar.setValue(84)
        # 233
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_mid[i, j] == 128 and Th_high[i, j] == 255 and U_high[i, j] == 255 ):
                R[i, j] = 128
                G[i, j] = 255
                B[i, j] = 255
        outputPath = os.path.join(fileDir, '233.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()
        self.processStatus.setText('Exporting 19/27...')
        self.progressBar.setValue(86)
        # 311
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_high[i, j] == 255 and Th_low[i, j] == 1 and U_low[i, j] == 1 ):
                R[i, j] = 255
                G[i, j] = 1
                B[i, j] = 1
        outputPath = os.path.join(fileDir, '311.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        self.processStatus.setText('Exporting 20/27...')
        self.progressBar.setValue(88)
        # 312
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_high[i, j] == 255 and Th_low[i, j] == 1 and U_mid[i, j] == 128 ):
                R[i, j] = 255
                G[i, j] = 1
                B[i, j] = 128
        outputPath = os.path.join(fileDir, '312.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        self.processStatus.setText('Exporting 21/27...')
        self.progressBar.setValue(88)
        # 313
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_high[i, j] == 255 and Th_low[i, j] == 1 and U_high[i, j] == 255 ):
                R[i, j] = 255
                G[i, j] = 1
                B[i, j] = 255
        outputPath = os.path.join(fileDir, '313.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()
        self.processStatus.setText('Exporting 22/27...')
        self.progressBar.setValue(90)
        # 321
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_high[i, j] == 255 and Th_mid[i, j] == 128 and U_low[i, j] == 1 ):
                R[i, j] = 255
                G[i, j] = 128
                B[i, j] = 1
        outputPath = os.path.join(fileDir, '321.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()
        self.processStatus.setText('Exporting 23/27...')
        self.progressBar.setValue(92)
        # 322
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_high[i, j] == 255 and Th_mid[i, j] == 128 and U_mid[i, j] == 128 ):
                R[i, j] = 255
                G[i, j] = 128
                B[i, j] = 128
        outputPath = os.path.join(fileDir, '322.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()
        self.processStatus.setText('Exporting 24/27...')
        self.progressBar.setValue(94)
        # 323
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_high[i, j] == 255 and Th_mid[i, j] == 128 and U_high[i, j] == 255 ):
                R[i, j] = 255
                G[i, j] = 128
                B[i, j] = 255
        outputPath = os.path.join(fileDir, '323.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()
        self.processStatus.setText('Exporting 25/27...')
        self.progressBar.setValue(96)
        # 331
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_high[i, j] == 255 and Th_high[i, j] == 255 and U_low[i, j] == 1 ):
                R[i, j] = 255
                G[i, j] = 255
                B[i, j] = 1
        outputPath = os.path.join(fileDir, '331.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()
        self.processStatus.setText('Exporting 26/27...')
        self.progressBar.setValue(98)
        # 332
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_high[i, j] == 255 and Th_high[i, j] == 255 and U_mid[i, j] == 128 ):
                R[i, j] = 255
                G[i, j] = 255
                B[i, j] = 128
        outputPath = os.path.join(fileDir, '332.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()
        self.processStatus.setText('Exporting 27/27...')
        self.progressBar.setValue(99)
        # 333
        R = np.zeros(K.shape, dtype=np.uint8)
        G = np.zeros(K.shape, dtype=np.uint8)
        B = np.zeros(K.shape, dtype=np.uint8)

        for i, j in np.ndindex(K.shape):
            if(K_high[i, j] == 255 and Th_high[i, j] == 255 and U_high[i, j] == 255 ):
                R[i, j] = 255
                G[i, j] = 255
                B[i, j] = 255
        outputPath = os.path.join(fileDir, '333.tif' )  
        dst_ds = gdal.GetDriverByName('GTiff').Create(outputPath, K.shape[1], K.shape[0], 3, gdal.GDT_UInt16, options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF',])
        gdalnumeric.CopyDatasetInfo(source, dst_ds)
        dst_ds.GetRasterBand(1).WriteArray(R)
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(2).WriteArray(G)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.FlushCache()
        dst_ds.GetRasterBand(3).WriteArray(B)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.FlushCache()

        self.processStatus.setText('')
        self.progressBar.setValue(100)
        alert = QMessageBox()
        alert.setText('Finished!')

# Init Qt Window
if __name__ == "__main__":
    appctxt = ApplicationContext()
    #app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
