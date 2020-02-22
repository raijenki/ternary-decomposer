# Ternary Decomposer
This was built for the Geological Survey of Brazil. 
The application takes as input a 16 million RGB geotiff file and decomposes it in 27 layers. The georeferencing of the output files is the same as the input.
 
## Dependencies
* GDAL (and libgdal-dev)
* Numpy
* PyQt and fbs (for GUI and binary)

## Notes
The program may freeze during its operation due to the number of calculations. When exporting to GIS softwares such as ArcGIS, you should build pyramids with the JPEG compression.
