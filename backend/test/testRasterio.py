# import rasterio
# from rasterio.merge import merge
# from rasterio.io import MemoryFile
import os
import pandas as pd
import rasterio
from rasterio.plot import show
from pyproj import Proj
import matplotlib.pyplot as plt
from rasterio.merge import merge
# #Mappe som inneholder rasterfiler
folder_path = "data/DOM10_UTM33_20250117/"

#lager CSV fil med alle lagene

# # Finn alle TIF-filer i mappen
# raster_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".tif")]
# print(f"Fant {len(raster_files)} rasterfiler")
# # Les rasterfilene

# file_data = pd.DataFrame(columns=['filename','lat', 'lon'])
# for file in raster_files:

#     img = rasterio.open(file)
#     #print koordinatene til midtpunktet i bilet
#     midtpunkt = img.xy(img.height//2, img.width//2)
#     #transform x and y to lat and lng using CRS = epsg:25833
#     p2 = Proj(init=img.crs, proj="utm", zone=33)
#     lon, lat = p2(midtpunkt[0],midtpunkt[1],inverse=True)
#     #print(file[26:32], lat, lon)
#     file_data.loc[len(file_data)] = {'filename': file[26:32], 'lat': lat, 'lon': lon}

# file_data.to_csv('data/csv/midtpunkt_coordinates.csv', index=False)
pandas_dataframe = pd.read_csv('data/csv/midtpunkt_coordinates.csv')
sorted_pandas = pandas_dataframe.sort_values(by=['lat', 'lon'])
#finn alle raser i dataframen som har lng values mellom 7.2 og 9.7 og lat values mellom 61.7 og 62.7
filtered_pandas = sorted_pandas[(sorted_pandas['lon'] > 5) & (sorted_pandas['lon'] < 13) & (sorted_pandas['lat'] > 61) & (sorted_pandas['lat'] < 63)]
alle_filnavn = filtered_pandas['filename']
print(f"Fant {len(alle_filnavn)} rasterfiler")
filnavn_ende = '_10m_z33.tif'

gjeldeneFilnavn = []
for filename in alle_filnavn:
    gjeldeneFilnavn.append(folder_path+filename+filnavn_ende)

src = rasterio.open(gjeldeneFilnavn[0])
print(src.shape)

# src_files_to_mosaic = [rasterio.open(file) for file in gjeldeneFilnavn]
# mosaic, out_transform = merge(src_files_to_mosaic)
# out_meta = src_files_to_mosaic[0].meta.copy()

# Oppdater metadata for mosaikken
# out_meta.update({
#     "driver": "GTiff",
#     "height": mosaic.shape[1],
#     "width": mosaic.shape[2],
#     "transform": out_transform
# })

# # Lagre den sammenslåtte rasterfilen
# output_path = os.path.join(folder_path, "mosaic_output.tif")
# with rasterio.open(output_path, "w", **out_meta) as dest:
#     dest.write(mosaic)

# # Vis den sammenslåtte rasteren
# with rasterio.open(output_path) as src:
#     show(src, title="Sammenslått raster uten overlapping")



# with rasterio.open(folder_path+alle_filnavn[119]+filnavn_ende) as src:
    
#     #ta et utsnitt av bildet
#     src_liten = src
#     #src_liten = src.read(window=((0, 100), (0, 100)))
#     x = src_liten.bounds.right - 10
#     y = src_liten.bounds.top - 10
#     #src_liten.sample()
#     p2 = Proj(init=src_liten.crs, proj="utm", zone=33)
#     lon, lat = p2(x,y,inverse=True)
#     print(lon, lat)
#     for val in src_liten.sample([(x, y)]): 
#         print(val)
#     show(src)