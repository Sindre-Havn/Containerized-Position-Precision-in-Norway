import math
import os
import pandas as pd
import numpy as np
import rasterio
from rasterio.plot import show
from pyproj import Proj
import matplotlib.pyplot as plt
from rasterio.merge import merge
import math
import rasterio
from rasterio.mask import mask
from shapely.geometry import Point, Polygon, mapping
import geopandas as gpd


#først må en laste ned daten fra hoydedata.no over området en ønsker data fra
#legg mappen med data inn i prosjektet

#Mappe som inneholder rasterfiler
folder_path = "data/dom10/data/"


tif_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".tif")]

raster_list = []
#raster_midtpunkt = []
raster_midtpunkt_NE = []
for file in tif_files:
    raster = rasterio.open(file)
    midtpunkt = raster.xy(raster.width//2, raster.height//2)
    # p2 = Proj(init=raster.crs, proj="utm", zone=33)
    # lng, lat = p2(midtpunkt[0],midtpunkt[1],inverse=True)
    raster_list.append(raster)
    raster_midtpunkt_NE.append([midtpunkt[0],midtpunkt[1]])
    #raster_midtpunkt.append([lng,lat])


#lage en stor raster med alle filene samlet
raster_list = []
for file in tif_files:
    raster = rasterio.open(file)
    raster_list.append(raster)
mosaic, out_transform = merge(raster_list)
# Hent metadata fra den første rasterfilen
out_meta = raster_list[0].meta.copy()
out_meta.update({
    "driver": "GTiff",
    "height": mosaic.shape[1],
    "width": mosaic.shape[2],
    "transform": out_transform
})

# # Lagre mosaikken til en midlertidig fil
output_path = f"data/merged_raster_romsdalen_10.tif"
with rasterio.open(output_path, "w", **out_meta) as dest:
    dest.write(mosaic)


# Sjekke informasjon om rasterfilen
with rasterio.open("data/merged_raster_romsdalen_10.tif") as src:
    print(f"Raster nodata value: {src.nodata}")
    
    # Read the first band and print min/max values
    data = src.read(1)
    print(f"Raster min/max values: {data.min()}, {data.max()}")

    # Unpack the affine transform correctly
    a, b, c, d, e, f = src.transform.to_gdal()
    print(f"Affine transform: {src.transform}")
    
    # Upper-left corner
    print(f"Raster upper-left corner: (a.{a}, b {b}, c:{c}, d:{d}, e:{e}, f: {f})")

    # Get raster index for a specific coordinate (East, North)
    x, y = 124388.06, 6957735.68  # Coordinate to look up
    row, col = src.index(x, y)
    print(f"Raster index (row, col) for ({x}, {y}): ({row}, {col})")

    # Get the height/elevation value at this point
    elevation_value = data[row, col]
    print(f"Elevation at ({x}, {y}): {elevation_value}")
