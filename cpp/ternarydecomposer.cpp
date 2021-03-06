#include "ternarydecomposer.h"
#include "qstring.h"
#include "qfile.h"
#include "gdal_priv.h"
#include <qmessagebox.h>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>

using namespace std;
int vconversor(char rgb, uint16_t value);
bool colorchk(string comp, uint16_t k, uint16_t th, uint16_t u);

ternarydecomposer::ternarydecomposer(QWidget *parent) : QMainWindow(parent) {

	// Qt stuff
	QPushButton* fileSelector = new QPushButton("Select file and start!", this);
	fileSelector->resize(200, 30);
	fileSelector->move(64,60);
	connect(fileSelector, &QPushButton::clicked, this, &ternarydecomposer::flBtn_onClick);

	lbl = new QLabel("The processing will start after file selection.", this);
	lbl->resize(320, 60);
	lbl->move(20, 75);

	// TBD in future if necessary, GDAL documentation does not help at all
	//cbox = new QCheckBox("Produce shapefiles", this);
	//cbox->move(20, 60);
	//cbox->resize(320, 40);

	pBar = new QProgressBar(this);
	pBar->setGeometry(0, 0, 300, 25);
	pBar->setMaximum(100);
	pBar->move(50, 25);
}

void ternarydecomposer::flBtn_onClick() {
	int progress = 0;
	this->pBar->setValue(0);

	QString tiffFile = QFileDialog::getOpenFileName(this,
		tr("Select file"), "", tr("GeoTiff Files (*.tif)"));

	if (tiffFile.isEmpty()) {
		return;
	}
	else {
		// Sanity check 
		/*
		QFile file(tiffFile);
		if (!file.open(QIODevice::ReadOnly)) {
			QMessageBox::information(this, tr("Unable to open file"),
				file.errorString());
			return;
		}*/

		// Convert QString to const char
		QByteArray ba = tiffFile.toLocal8Bit();
		const char* fileLocation = ba.data();

		static vector<string> compositions;
		compositions = { "111", "112", "113", 
			"121", "122", "123",
			"131", "132", "133",
			"211", "212", "213",
			"221", "222", "223",
			"231", "232", "233",
			"311", "312", "313",
			"321", "322", "323",
			"331", "332", "333" };
		
		// Gdal stuff
		GDALAllRegister();
		GDALDataset* orig_ternary = (GDALDataset*)GDALOpen(fileLocation, GA_ReadOnly);
		const char* pszFormat = "GTiff";
		OGRSpatialReference oSRS;
		//oSRS = orig_ternary->GetSpatialRef();

		for (string composition : compositions) {
			this->pBar->setValue(progress);
			this->lbl->setText("Working...");
			GDALDataset* fused_bands;
			GDALDriver* tiffDriver;
			string filename = composition + ".tif";
			char k_pos = composition.at(0);
			char th_pos = composition.at(1);
			char u_pos = composition.at(2);

			// Get relevant data from original dataset
			int nRows = orig_ternary->GetRasterYSize();
			int nCols = orig_ternary->GetRasterXSize();
			
			//string wkt = proj = orig_ternary->GetProjectionRef();
			double noData = orig_ternary->GetRasterBand(1)->GetNoDataValue();
			
			//printf("Projection is `%s'\n", orig_ternary->GetProjectionRef());
			tiffDriver = GetGDALDriverManager()->GetDriverByName(pszFormat);

			char** papszOptions = NULL;
			papszOptions = CSLSetNameValue(papszOptions, "TILED", "NO");
			papszOptions = CSLSetNameValue(papszOptions, "COMPRESS", "PACKBITS");
			papszOptions = CSLSetNameValue(papszOptions, "PHOTOMETRIC", "RGB");
			papszOptions = CSLSetNameValue(papszOptions, "PROFILE", "GEOTIFF");
			//fused_bands = tiffDriver->CreateCopy(filename.c_str(), orig_ternary, FALSE, NULL, NULL, NULL);

			//fused_bands = tiffDriver->CreateCopy(filename.c_str(), orig_ternary, FALSE, papszOptions, GDALTermProgress, NULL);
			fused_bands = tiffDriver->Create(filename.c_str(), nCols, nRows, 3, GDT_Byte, papszOptions);
			GDALClose(fused_bands);
			fused_bands = (GDALDataset*)GDALOpen(filename.c_str(), GA_Update);
			fused_bands->GetRasterBand(1)->SetNoDataValue(0);
			fused_bands->GetRasterBand(2)->SetNoDataValue(0);
			fused_bands->GetRasterBand(3)->SetNoDataValue(0);

			// Allocate memory for row buffers
			uint16_t* k_Row = (uint16_t*)CPLMalloc(sizeof(uint16_t) * nCols);
			uint16_t* th_Row = (uint16_t*)CPLMalloc(sizeof(uint16_t) * nCols);
			uint16_t* u_Row = (uint16_t*)CPLMalloc(sizeof(uint16_t) * nCols);
			uint16_t* k_Row_new = (uint16_t*)CPLMalloc(sizeof(uint16_t) * nCols);
			uint16_t* th_Row_new = (uint16_t*)CPLMalloc(sizeof(uint16_t) * nCols);
			uint16_t* u_Row_new = (uint16_t*)CPLMalloc(sizeof(uint16_t) * nCols);

			// Decomposition
			for (auto i = 0; i < nRows; i++) {
				orig_ternary->GetRasterBand(1)->RasterIO(GF_Read, 0, i, nCols, 1, k_Row, nCols, 1, GDT_UInt16, 0, 0);
				orig_ternary->GetRasterBand(2)->RasterIO(GF_Read, 0, i, nCols, 1, th_Row, nCols, 1, GDT_UInt16, 0, 0);
				orig_ternary->GetRasterBand(3)->RasterIO(GF_Read, 0, i, nCols, 1, u_Row, nCols, 1, GDT_UInt16, 0, 0);
				for (auto j = 0; j < nCols; j++) {
					k_Row_new[j] = 0;
					u_Row_new[j] = 0;
					th_Row_new[j] = 0;

					// Sanity check
					if (colorchk(composition, vconversor(k_pos, k_Row[j]), vconversor(th_pos, th_Row[j]), vconversor(u_pos, u_Row[j]))) {
						k_Row_new[j] = vconversor(k_pos, k_Row[j]);;
						u_Row_new[j] = vconversor(u_pos, u_Row[j]);;
						th_Row_new[j] = vconversor(th_pos, th_Row[j]);
					}
				}
				GDALSetRasterColorInterpretation(fused_bands->GetRasterBand(1), GCI_RedBand);
				GDALSetRasterColorInterpretation(fused_bands->GetRasterBand(2), GCI_GreenBand);
				GDALSetRasterColorInterpretation(fused_bands->GetRasterBand(3), GCI_BlueBand);
				fused_bands->GetRasterBand(1)->RasterIO(GF_Write, 0, i, nCols, 1, k_Row_new, nCols, 1, GDT_UInt16, 0, 0);
				fused_bands->GetRasterBand(2)->RasterIO(GF_Write, 0, i, nCols, 1, th_Row_new, nCols, 1, GDT_UInt16, 0, 0);
				fused_bands->GetRasterBand(3)->RasterIO(GF_Write, 0, i, nCols, 1, u_Row_new, nCols, 1, GDT_UInt16, 0, 0);
				//fused_bands->SetProjection(orig_ternary->GetProjectionRef());
			}

			/* Will fix someday
			const char* pszDriverName = "ESRI Shapefile";
			string shpfilename = composition + ".shp";
			GDALDriver* shpDriver;
			GDALDataset* shpDS;
			OGRSpatialReference* shpproj = new OGRSpatialReference();
			shpproj->importFromWkt(proj);
			shpDriver = GetGDALDriverManager()->GetDriverByName(pszDriverName);
			shpDS = shpDriver->Create(shpfilename.c_str(), 0, 0, 0, GDT_Float32, NULL);
			OGRLayer* poLayer;
			poLayer = shpDS->CreateLayer(composition.c_str(), shpproj, wkbMultiPolygon, NULL);
			GDALFPolygonize(fused_bands->GetRasterBand(2), NULL, poLayer, -1, NULL, NULL, NULL);
			*/

			const char* pszProjection;
			pszProjection = orig_ternary->GetProjectionRef();
			double transform[6];
			const char* proj = orig_ternary->GetProjectionRef();
			orig_ternary->GetGeoTransform(transform);
			fused_bands->SetMetadata(orig_ternary->GetMetadata());
			if (!(transform[0] == 0 && transform[1] == 1 && transform[2] == 0 && transform[3] == 0 && transform[4] == 0 && transform[5] == 1)) {
				fused_bands->SetProjection(proj);
				fused_bands->SetGeoTransform(transform);
			}
			else if (orig_ternary->GetGCPCount() > 1) {
				fused_bands->SetGCPs(orig_ternary->GetGCPCount(), orig_ternary->GetGCPs(), orig_ternary->GetGCPProjection());
				
			}
			//fused_bands->SetSpatialRef(orig_ternary->GetSpatialRef());
			
			//fused_bands->SetGCPs(orig_ternary->GetGCPCount(), orig_ternary->GetGCPs(), orig_ternary->GetGCPSpatialRef());
			//fused_bands->FlushCache();
			GDALClose(fused_bands);
			progress = progress + 3.7;
			//GDALDestroyDriverManager(); // later

		}
		GDALClose(orig_ternary);
		this->pBar->setValue(100);
		QMessageBox processDone;
		processDone.setText("Processing is done!");
		processDone.exec();
		this->lbl->setText("The processing will start after file selection.");
		
	}

}


bool colorchk(string comp, uint16_t k, uint16_t th, uint16_t u) {
	
	int compvar = stoi(comp);
	if (compvar == 111 && k == 1 && th == 1 && u == 1) return true;
	else if (compvar == 112 && k == 1 && th == 1 && u == 128) return true;
	else if (compvar == 113 && k == 1 && th == 1 && u == 255) return true;
	else if (compvar == 121 && k == 1 && th == 128 && u == 1) return true;
	else if (compvar == 122 && k == 1 && th == 128 && u == 128) return true;
	else if (compvar == 123 && k == 1 && th == 128 && u == 255) return true;
	else if (compvar == 131 && k == 1 && th == 255 && u == 1) return true;
	else if (compvar == 132 && k == 1 && th == 255 && u == 128) return true;
	else if (compvar == 133 && k == 1 && th == 255 && u == 255) return true;
	else if (compvar == 211 && k == 128 && th == 1 && u == 1) return true;
	else if (compvar == 212 && k == 128 && th == 1 && u == 128) return true;
	else if (compvar == 213 && k == 128 && th == 1 && u == 255) return true;
	else if (compvar == 221 && k == 128 && th == 128 && u == 1) return true;
	else if (compvar == 222 && k == 128 && th == 128 && u == 128) return true;
	else if (compvar == 223 && k == 128 && th == 128 && u == 255) return true;
	else if (compvar == 231 && k == 128 && th == 255 && u == 1) return true;
	else if (compvar == 232 && k == 128 && th == 255 && u == 128) return true;
	else if (compvar == 233 && k == 128 && th == 255 && u == 255) return true;
	else if (compvar == 311 && k == 255 && th == 1 && u == 1) return true;
	else if (compvar == 312 && k == 255 && th == 1 && u == 128) return true;
	else if (compvar == 313 && k == 255 && th == 1 && u == 255) return true;
	else if (compvar == 321 && k == 255 && th == 128 && u == 1) return true;
	else if (compvar == 322 && k == 255 && th == 128 && u == 128) return true;
	else if (compvar == 323 && k == 255 && th == 128 && u == 255) return true;
	else if (compvar == 331 && k == 255 && th == 255 && u == 1) return true;
	else if (compvar == 332 && k == 255 && th == 255 && u == 128) return true;
	else if (compvar == 333 && k == 255 && th == 255 && u == 255) return true;
	return false;
}


int vconversor(char rgb, uint16_t value) {
	if (rgb == '1') {
		if (value <= 85) { return 1; }
		else { return 0; }
	}
	if (rgb == '2') {
		if (value > 85 && value < 170) { return 128; }
		else { return 0; }
	}
	if (rgb == '3') { 
		if (value >= 170) { return 255; }
		else { return 0; }
	}
}