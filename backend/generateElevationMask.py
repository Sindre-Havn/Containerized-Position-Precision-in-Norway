import math
from romsdalenRaster import find_highest_elevation_triangle, calculate_distance
import numpy as np
import rasterio


romsdalen_punkter = [[124388.06,6957735.68],[127961.24,6948183.94], 
                     [138548.08,6941022.55], [146207,6922500.21], [159073.8,6916291.06], 
                     [173885.23,6904139.84], [	183291.02,6902250.15], [193562.71, 6896761.87]]


def azimuth_to_unit_circle(azimuth):
    """
    Konverterer azimutvinkel (0° = nord, med klokken) til grader i enhetssirkelen
    (0° = øst, mot klokken).
    
    :param azimuth: Vinkel i grader (0° = nord, 90° = øst, 180° = sør, 270° = vest)
    :return: Vinkel i grader i enhetssirkelen (0° = øst, 90° = nord, 180° = vest, 270° = sør)
    """
    return (90 - azimuth) % 360

def sort_elevation_azimuth(elevation):
    """
    Omorganiserer en liste sortert i enhetssirkelrekkefølge
    til å være i azimuth-rekkefølge.
    """
    # Finn hvor 90° er i listen (nord i azimuth)
    index_90 = len(elevation) // 4  # Antar lik fordeling av grader

    # Split listen i to deler:
    elevation = elevation[::-1]
    last_part = elevation[271:]  # 90° til 360°
    

    # Kombiner i riktig azimuth-rekkefølge
    elevation_azimuth = last_part + elevation[:271]

    return elevation_azimuth

def check_satellite_sight(observer, max_distance, elevation_satellite, azimuth_satellite):
    with rasterio.open("data/merged_raster_romsdalen_10.tif") as src:
        dem_data = src.read(1)
        observer_elevation = dem_data[src.index(observer[0], observer[1])]
    degree = azimuth_to_unit_circle(azimuth_satellite)

    sight = True
    for dist in range(1, max_distance, 10):
        target_x = observer[0] + dist * math.cos(np.deg2rad(degree))
        target_y = observer[1] + dist * math.sin(np.deg2rad(degree))
        try:
            row, col = src.index(target_x, target_y)
            target_height = dem_data[row, col]
            target_elevation = np.rad2deg(np.arctan((target_height - observer_elevation)/ dist))

            if target_elevation > elevation_satellite: 
                sight = False
                break
        except IndexError:
            break  # Stop if we go outside raster bounds
    return sight
    
def find_elevation_cutoff(observer, max_distance, elevation_mask):
    observer_height, heights_and_points = find_highest_elevation_triangle("data/merged_raster_romsdalen_10.tif", observer,max_distance)
    elevation = []
    #print(heights_and_points)
    for i in range(0,len(heights_and_points)):
        if heights_and_points[i][0] == None or heights_and_points[i][1] == None:
            elevation.append(elevation)
        else:
            height = heights_and_points[i][1]
            #print(observer, heights_and_points[i][0])
            distance = calculate_distance(observer, heights_and_points[i][0])
            elevation.append(np.rad2deg(np.arctan((height-observer_height)/distance)))
    
    elevation_azimuth = sort_elevation_azimuth(elevation)
    # print(f"elev deg: {elevation[180]}")
    # print(f"elev az : {elevation_azimuth[270]}")
    return elevation_azimuth, observer_height

N = 6948183.94
E = 127961.24
#print(check_satellite_sight((E,N), 5000, 1.9,345.102093)
#find_elevation_cutoff((E,N), 5)






