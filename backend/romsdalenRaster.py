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
# #Mappe som inneholder rasterfiler
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

#print(raster_midtpunkt)
#print(raster_midtpunkt_NE)

romsdalen_punkter = [[124388.06,6957735.68],[127961.24,6948183.94], 
                     [138548.08,6941022.55], [146207,6922500.21], [159073.8,6916291.06], 
                     [173885.23,6904139.84], [	183291.02,6902250.15], [193562.71, 6896761.87]]

def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

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

# Lagre mosaikken til en midlertidig fil
output_path = f"data/merged_raster_romsdalen_10.tif"
with rasterio.open(output_path, "w", **out_meta) as dest:
    dest.write(mosaic)


# Sjekke informasjon om rasterfilen
# with rasterio.open("data/merged_raster_romsdalen_10.tif") as src:
#     print(f"Raster nodata value: {src.nodata}")
    
#     # Read the first band and print min/max values
#     data = src.read(1)
#     print(f"Raster min/max values: {data.min()}, {data.max()}")

#     # Unpack the affine transform correctly
#     a, b, c, d, e, f = src.transform.to_gdal()
#     print(f"Affine transform: {src.transform}")
    
#     # Upper-left corner
#     print(f"Raster upper-left corner: (a.{a}, b {b}, c:{c}, d:{d}, e:{e}, f: {f})")

#     # Get raster index for a specific coordinate (East, North)
#     x, y = 124388.06, 6957735.68  # Coordinate to look up
#     row, col = src.index(x, y)
#     print(f"Raster index (row, col) for ({x}, {y}): ({row}, {col})")

#     # Get the height/elevation value at this point
#     elevation_value = data[row, col]
#     print(f"Elevation at ({x}, {y}): {elevation_value}")

def generate_triangles(center, radius, step=1):
    """Generer punkter i en sirkel rundt et senterpunkt for hver grad."""
    polygons = []
    
    for angle in range(0, 360, step):
        # Calculate endpoints for the two angles
        x_end_first = center[0] + radius * math.cos(math.radians(angle))
        y_end_first = center[1] + radius * math.sin(math.radians(angle))

        x_end_second = center[0] + radius * math.cos(math.radians(angle + step))
        y_end_second = center[1] + radius * math.sin(math.radians(angle + step))
        
        # Define the polygon (triangle-like sector)
        polygon_coords = [
            center,  # Center point
            (x_end_first, y_end_first),  # First edge point
            (x_end_second, y_end_second),  # Second edge point
            center  # Close the polygon
        ]
        polygon = Polygon(polygon_coords)
        geojson_polygon = [mapping(polygon)]
        # Create the polygon and add to the list
        polygons.append(geojson_polygon)
    
    return polygons

def find_highest_elevation_triangle(raster_path, center,center_height, radius_km):
    """Finn høyeste punkt innenfor en radius for hver 5. grad rundt senter."""
    #radius_deg = radius_km / 111  # 1 grad ≈ 111 km
    polygons = generate_triangles(center, radius_km*1000)
    #print(polygons)
    with rasterio.open(raster_path) as src:
        highest_points = []
        
        for polygon in polygons:             
            out_image, out_transform = mask(src, polygon, crop=True, nodata=src.nodata)
            out_data = out_image[0]  # Hent første bånd  
            highest_elevation = 0
            best_height = None
            best_point = None   
            # # Finn høyeste verdi i masken
            if out_data.size > 0:
           
                #iterate through all cells that do not have the nodata value
                for i in range(out_data.shape[0]):
                    for j in range(out_data.shape[1]):
                        if out_data[i][j] != src.nodata:
                            x, y = rasterio.transform.xy(out_transform, i, j)
                            height = out_data[i, j]
                            elevation = np.rad2deg(np.arctan((height - center_height)/ calculate_distance(center, (x, y))))
                            if elevation > highest_elevation:
                                highest_elevation = elevation
                                best_point = (x, y)
                                best_height = height
            
            highest_points.append((best_point, best_height))        
        
        return highest_points



def find_obstruction(dem, transform, observer, max_distance, angle_step=1):
    """
    Finner nærmeste punkt som blokkerer sikten i ulike retninger fra observer.
    """
    obstructed_points = []  # Store (x, y, elevation) of sight-blocking points
    
    observer_x, observer_y = observer
    observer_row, observer_col = src.index(observer_x, observer_y)
    observer_elevation = dem[observer_row, observer_col]
    
    for angle in range(0, 360, angle_step):
        angle_rad = math.radians(angle)
        x_offset = math.cos(angle_rad)
        y_offset = math.sin(angle_rad)
        highest_elevation = 0
        obstructing_height = None
        obstructing_point = None
        # Search along a line up to max_distance
        #targets = []
        for dist in range(1, max_distance, 10):
            target_x = observer_x + dist *x_offset
            target_y = observer_y + dist *y_offset
            try:
                row, col = src.index(target_x, target_y)
                
                # Get elevation at the target point
                target_height = dem[row, col]
                target_elevation = np.rad2deg(np.arctan((target_height - observer_elevation)/ dist))
                #targets.append(target_elevation)
                # Check if elevation blocks sight
                if target_elevation > highest_elevation: 
                    highest_elevation = target_elevation
                    obstructing_point = (target_x, target_y)
                    obstructing_height = target_height
                    
                    #break  # Stop searching in this direction
                
            except IndexError:
                break  # Stop if we go outside raster bounds

        obstructed_points.append((obstructing_point, obstructing_height))

        # print(f"heighest by function : {highest_elevation}")
        # print(f"heighest not by function : {max(targets)}")
   
    return obstructed_points


# def plot_obstructions(observer, obstructions):
#     """
#     Plots the observer and obstructions in a circular layout.
#     """
#     fig, ax = plt.subplots(figsize=(8, 8))

#     # Extract data
#     angles = np.arange(0,360,1)
#     distances = [calculate_distance(observer,obs[0]) for obs in obstructions]  # Distances from observer
#     elevations = [obs[1] for obs in obstructions]  # Elevations

#     # Convert to Cartesian coordinates for plotting
#     x_coords = [d * math.cos(a) for d, a in zip(distances, np.deg2rad(angles))]
#     y_coords = [d * math.sin(a) for d, a in zip(distances, np.deg2rad(angles))]

#     # Plot observer at (0,0)
#     ax.scatter(0, 0, color='red', label="Observer", s=100, marker='*')

#     # Plot obstruction points
#     scatter = ax.scatter(x_coords, y_coords, c=elevations, cmap='terrain', label="Obstruction Points", edgecolor='black')

#     # Add colorbar
#     cbar = plt.colorbar(scatter, ax=ax)
#     cbar.set_label("Elevation (m)")

#     # Connect observer to each obstruction
#     for x, y in zip(x_coords, y_coords):
#         ax.plot([0, x], [0, y], color='gray', linestyle='dashed', linewidth=1)

#     # Set labels and title
#     ax.set_xlabel("Distance East (m)")
#     ax.set_ylabel("Distance North (m)")
#     ax.set_title("Obstruction Points Around Observer")
#     ax.legend()
    
#     # Make the plot circular
#     ax.set_aspect('equal', adjustable='datalim')
#     plt.grid(True)
#     plt.show()

# def plot_sight(observer, obstructions, observer_height):
#     angles = np.arange(0, 360, 1)
#     distances = [calculate_distance(observer, obs[0]) for obs in obstructions]
#     heights = [obs[1] for obs in obstructions]
#     elevations = np.arctan2(heights - observer_height, distances)  # Elevations
#     sight = 90 - np.degrees(elevations)  # Sight angles

#     fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))
    
#     # Convert angles to radians for polar plot
#     angles_rad = np.deg2rad(angles)
    
#     # Plot the sight angles
#     ax.plot(angles_rad, 90-np.rad2deg(elevations), label="Sight Elevation")
    
#     # Set labels and title
#     ax.set_theta_zero_location('E')
#     ax.set_theta_direction(-1)
#     ax.set_rlabel_position(0)
#     ax.set_title("Sight Elevation in Each Direction")
#     ax.set_ylabel("Elevation Angle (degrees)")
    
#     plt.legend()
#     plt.show()

def plotCirle(observer, obstructions_lines, obstructions_triangles, observer_height, title):
    angles = np.arange(0, 360, 1)
    distances_lines = [calculate_distance(observer, obs[0]) for obs in obstructions_lines]
    heights_lines = [obs[1] for obs in obstructions_lines]
    elevations_lines = np.arctan2(heights_lines - observer_height, distances_lines)  # Elevations
    
    distances_triangles = [calculate_distance(observer, obs[0]) for obs in obstructions_triangles]
    heights_triangles = [obs[1] for obs in obstructions_triangles]
    elevations_triangles = np.arctan2(heights_triangles - observer_height, distances_triangles)  # Elevations
    #print(elevations)
    points_x_lines = []
    points_y_lines = []
    points_x_triangles = []
    points_y_triangles = []

    for angle, elevation_line, elevation_triangle in zip(angles, elevations_lines, elevations_triangles):
        distance_line = (1- (np.rad2deg(elevation_line))/90)*90
        distance_triangle = (1- (np.rad2deg(elevation_triangle))/90)*90
        x_line = distance_line * math.cos(math.radians(angle))
        y_line = distance_line * math.sin(math.radians(angle))
        x_triangle = distance_triangle * math.cos(math.radians(angle))
        y_triangle = distance_triangle * math.sin(math.radians(angle))
        points_x_lines.append(x_line)
        points_y_lines.append(y_line)
        points_x_triangles.append(x_triangle)
        points_y_triangles.append(y_triangle)

    deg0_x = [90* math.cos(math.radians(angle))  for angle in range(0, 360, 1)]
    deg0_y = [90* math.sin(math.radians(angle))  for angle in range(0, 360, 1)]
    deg20_x = [ (1- (20)/90)*90* math.cos(math.radians(angle))  for angle in range(0, 360, 1)]
    deg20_y = [(1- (20)/90)*90* math.sin(math.radians(angle))  for angle in range(0, 360, 1)]
    deg40_x = [ (1- (40)/90)*90* math.cos(math.radians(angle))  for angle in range(0, 360, 1)]
    deg40_y = [(1- (40)/90)*90* math.sin(math.radians(angle))  for angle in range(0, 360, 1)]
    deg60_x = [ (1- (60)/90)*90* math.cos(math.radians(angle))  for angle in range(0, 360, 1)]
    deg60_y = [(1- (60)/90)*90* math.sin(math.radians(angle))  for angle in range(0, 360, 1)]
    fig, ax = plt.subplots(figsize=(8, 8))
    
    ax.plot(0, 0, label="Observer Position", marker='o', color='red')
    ax.plot(deg0_x, deg0_y, color='black')
    ax.plot(deg20_x, deg20_y,color='black')
    ax.plot(deg40_x, deg40_y,color='black')
    ax.plot(deg60_x, deg60_y, color='black')
    ax.plot(points_x_lines, points_y_lines, label="Cut off angle Lines", color='blue')
    ax.plot(points_x_triangles, points_y_triangles, label="Cut off angle Triangles", color='green')
    ax.text(deg0_x[-1], deg0_y[-1], "0°", fontsize=12, color='black', verticalalignment='bottom')
    ax.text(deg20_x[-1], deg20_y[-1], "20°", fontsize=12, color='black', verticalalignment='bottom')
    ax.text(deg40_x[-1], deg40_y[-1], "40°", fontsize=12, color='black', verticalalignment='bottom')
    ax.text(deg60_x[-1], deg60_y[-1], "60°", fontsize=12, color='black', verticalalignment='bottom')
    ax.set_title(title)
    plt.legend()
    plt.show()
	
	

# Åpne DEM-data
with rasterio.open("data/merged_raster_romsdalen_10.tif") as src:
    dem_data = src.read(1)
    transform = src.transform


observer = romsdalen_punkter[1]  # Observatørposisjon
observer_height = dem_data[src.index(observer[0], observer[1])]  # Høyde på observatørposisjonen
blocked_points = find_obstruction(dem_data, transform, observer, 5000) #sjekker med radius 5km
blocked_points_triangles = find_highest_elevation_triangle("data/merged_raster_romsdalen_10.tif", observer, observer_height, 5)

# plot_obstructions(observer, blocked_points)
#plot_sight(observer, blocked_points, observer_height)
plotCirle(observer, blocked_points, blocked_points_triangles, observer_height, f'Cut off angle for observer at {observer}') 




