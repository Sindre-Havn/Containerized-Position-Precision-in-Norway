import math

from shapely import LineString
from romsdalenRaster import find_highest_elevation_triangle, calculate_distance
import numpy as np
import rasterio


romsdalen_punkter = [[124388.06,6957735.68],[127961.24,6948183.94], 
                     [138548.08,6941022.55], [146207,6922500.21], [159073.8,6916291.06], 
                     [173885.23,6904139.84], [	183291.02,6902250.15], [193562.71, 6896761.87]]


def azimuth_to_unit_circle(azimuth):

    return (90 - azimuth) % 360

def sort_elevation_azimuth(elevation):
    elevation = elevation[::-1]
    last_part = elevation[271:]  # 90° til 360°

    elevation_azimuth = last_part + elevation[:271]

    return elevation_azimuth
#sjekker linjer
def check_satellite_sight(observer,dem_data,src, max_distance, elevation_satellite, elevation_mask, azimuth_satellite):

    degree = azimuth_to_unit_circle(azimuth_satellite)
    line = LineString([
            (observer[0] + d * np.cos(np.deg2rad(degree)), observer[1] + d * np.sin(np.deg2rad(degree)))
            for d in np.arange(1, max_distance, 5)
        ])
    coords = np.array(line.coords)

    rows = []
    cols = []
    for x, y in coords:
        try:
            row, col = src.index(x, y)
            rows.append(row)
            cols.append(col)
        except IndexError:
            break  # Hvis vi går utenfor rasteret, antar vi at sikten ikke er blokkert

    rows = np.array(rows)
    cols = np.array(cols)

    # Hent høyder fra DEM
    heights = dem_data[rows, cols]
    #print(f'høyder: {heights}') 
    # Beregn elevasjonsvinkel fra hvert punkt
    distances = np.linspace(1, max_distance, len(heights))
    target_elevations = np.rad2deg(np.arctan((heights - observer[2]) / distances))
    # print(f'distanser: {distances}')
    # print(f'elevasjoner: {target_elevations}')
    return max(target_elevations)
    # # Sjekk om noen punkter blokkerer sikten
    # if np.any((target_elevations > elevation_satellite) or (elevation_satellite < elevation_mask)):
    #     return False  # Sikt blokkert
    
    # return True  # Satellitten er synlig
    

#bruker trekanter
def find_elevation_cutoff(dem_data, src,observer, max_distance, elevation_mask):
    observer_height, heights_and_points = find_highest_elevation_triangle(dem_data,src, observer,max_distance, elevation_mask)

    elevation_azimuth = sort_elevation_azimuth(heights_and_points)
    return elevation_azimuth, observer_height

N = 6948183.94
E = 127961.24
#print(check_satellite_sight((E,N), 5000, 1.9,345.102093)
#find_elevation_cutoff((E,N), 5)

# observer = [140913.05,6932288.59]
# list_top = []
# with rasterio.open("data/merged_raster_romsdalen_10.tif") as src:
#     dem_data = src.read(1)
#     elevs, height = find_elevation_cutoff(dem_data, src,observer, 5, 10)
#     for i in range(0,360,1):
#         top = check_satellite_sight([observer[0], observer[1],height ],dem_data,src, 5000, 90, 10, i)
#         list_top.append(top)
        
# elev_new = [(90-elev) for elev in elevs]
# list_top_new = [int(top) for top in list_top]
# # print(f'360 med trekanter: {elev_new}')
# print(f'360 med linjer: {list_top}')


# import matplotlib.pyplot as plt
# azimuth = np.linspace(0, 2 * np.pi, 360)  # 0° til 359° i radianer

# # Plott
# plt.figure(figsize=(8, 8))
# ax = plt.subplot(1, 1, 1, polar=True)

# ax.plot(azimuth, elev_new, label='trekanter')
# ax.plot(azimuth, list_top_new, label='linjer')

# # Ekstra innstillinger for å gjøre det tydeligere
# ax.set_theta_zero_location("N")  # Starter i nord
# ax.set_theta_direction(-1)       # Går med klokken

# plt.title("Polarplott med elevasjonsvinkler")
# plt.legend()
# plt.show()