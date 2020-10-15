# Ternary Decomposer
This was built for the Geological Survey of Brazil. 
The application takes as input a 16 million RGB geotiff file and decomposes it in 27 layers (check image files for references). The georeferencing of the output files is the same as the input. It also produces shapefiles (shp) of the tiff files.
 
##Dependencies (C++)
* Qt 5
* GDAL 3

## Dependencies (Python)
* GDAL/OSR/OGR (and libgdal-dev)
* Numpy
* PyQt

## Usage
Clone the repository and use `python main.py`.
The compiled version C++ is located at the Releases.

## Notes
* When importing to ArcGIS, it's necessary to disable some statistical calculation automatically does or the images will be badly displayed. This is solvable by simply disabling the ‘gamma stretch’ and the equalization to ‘none’ (properties tab of the raster). . 
* This application is expected to freeze for large files (however, just leave it open as it's doing the processing).
* You can bundle it through `pyinstaller -F main.py`.
