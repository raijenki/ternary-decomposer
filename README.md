# Ternary Decomposer
This was built for the Geological Survey of Brazil. 
The application takes as input a 16 million RGB geotiff file and decomposes it in 27 layers (check image files for references). The georeferencing of the output files is the same as the input.
 
## Dependencies
* GDAL/OSR/OGR (and libgdal-dev)
* Numpy
* PyQt

## Usage
Clone the repository and use `python main.py`.

## Notes
* The program may freeze during its operation due to the number of calculations. 
* This application is expected to freeze for large files (however, just leave it open as it's doing the processing).
* You can bundle it through `pyinstaller -F main.py`.