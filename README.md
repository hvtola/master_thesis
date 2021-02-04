# Using Random Forest to predict avalanche runout
04.02.2021 - Håvard Toft Larsen

## Table of contents
* [Introduction](#introduction)
* [Data preparation](#data-preparation)
* [Random Forest](#random-forest)

## Introduction
Using the random forest algorithm, we developed four models for predicting alpha-angle runout from topographic parameters.

### To redo data preparation, the following data is needed:
#### Switzerland
* Avalanche dataset from Switzerland, contact Yves Bühler at SLF.
* SwissALTI3D_5m from SwissTopo for all of Switzerland

#### Norway
* Avalanche dataset from Norway, contact Markus Eckerstorfer at NORCE.
* National 10m DEM of Norway (https://hoydedata.no/LaserInnsyn/)
	
## Data preparation
### Switzerland
* Calculate the centerline of each avalanche using **calculate_centerline.py** (ESRI software is needed).
* Use ESRI ArcMap tool *Generate Points Along Lines* to generate a point every 5 meter of each avalanche centerline. Each point must include avalanche reference ID and elevation.
* Resample the data to 100 z-values for each avalanche using **centerline_to_array.ipynb**.
Calculate topographic parameters
* y'' can be calculated using **point_calculate_second_derivative**
* R, T and D can be calulcated using **calculate_avalanche_confinement.py** (ESRI software is needed).
* alpha, beta, theta can be calculated using **array_calculate_alpha_beta.ipynb**.
* path_type can be calculated using **array_KMeans_clustering.ipynb**.
* L_flow/linear, P, H, aspect, d_size, alt_min/max, is either given in the avalanche dataset or can be extracted using simple GIS tools.
* Hy'' and P/L_flow can be calculated from the topographic parameters above.
### Norway
* Calculate potential release areas (PRA, https://github.com/jocha81/Avalanche-release)
* Use the TauDEM to model the alpha angle for each PRA (https://hydrology.usu.edu/taudem/taudem5/)
* Use **calculate_percentiles.py** to calculate the 5th percentile lowest alpha angle within the avalanche runout polygon.
	
## Random Forest
* The whole model including training and target data is available. The model is available as a Jupyter Notebook or Google Colab: **Thesis_main.ipynp**, input data is **main_data.csv**
