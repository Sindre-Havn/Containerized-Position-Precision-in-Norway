import json
import math
import os
import numpy as np
from pyproj import Transformer
import requests
import pandas as pd
from shapely.geometry import LineString, Point
from downloadHoydedata import createNewRaster
import nvdbapiv3 
from flask import jsonify

from time import perf_counter_ns


# Set up coordinate transformers between UTM and WGS84
transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)
transformerToEN = Transformer.from_crs("EPSG:4326","EPSG:25833", always_xy=True)

# Convert WKT LINESTRING Z to coordinate array in UTM33
def linestring_to_coordinates(linestring: str) -> list[list[np.float64]]:
    wkt_string = linestring.replace("LINESTRING Z(", "").replace(")", "")
    points = np.array([list(map(float, p.split())) for p in wkt_string.split(", ")])
    points_without_height =[ [coord[0], coord[1]] for coord in points]
    return points_without_height

# Convert UTM coordinates to WGS84 coordinates
def convert_coordinates(utm_coords: list[list[np.float64]]) -> list[list[float]]:
    coords = np.array(utm_coords)
    transformed_points = np.column_stack(transformer.transform(coords[:, 0], coords[:, 1]))
    return transformed_points.tolist()

def calculate_travel_direction(p1: list[float], p2: list[float]) -> float:
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle_rad = math.atan2(dx, dy)
    angle_deg = math.degrees(angle_rad)
    return (angle_deg + 360) % 360

def calculate_distance(p1: list, p2: list) -> float:
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return abs(math.sqrt(dx**2 + dy**2))

def checkDirection(startpointRoad: list[float], startpoinSegment: list[np.float64], endpointSegment: list[np.float64]) -> str:
    distStart = calculate_distance(startpointRoad, startpoinSegment)
    distEnd = calculate_distance(startpointRoad, endpointSegment)
    if distStart > distEnd:
        return 'MOT'
    else:
        return 'MED'
    
# Connect all road segments and insert missing connectors if needed
def connect_road(total_road: list[dict]) -> dict:
    road_segments = total_road.copy()
    connected = [road_segments[0]]
    for i in range(1,len(road_segments)-1):
        prev_segment_end_point = road_segments[i-1]["geometry"]["coordinates"][-1]
        start_point = road_segments[i]["geometry"]["coordinates"][0]
        #print('start, prev', start_point, prev_segment_end_point)
        fartsgrense = road_segments[i]["properties"]["fartsgrense"]
        if prev_segment_end_point != start_point:
            geojson_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [prev_segment_end_point, start_point]
                },
                "properties": {"name": "RoadSegment ", "id": i, "fartsgrense":fartsgrense}
            } 
            connected.append(geojson_feature)  
        connected.append(road_segments[i])
    
    return connected


# Calculate position and time for measurement points along road segments
def calculate_travel_time(road_segments: list[dict], avstand: float) -> list[dict]:
    # print(len(road_segments), road_segments[0])
    points_geojson = []
    total_time = 0  
    total_distance = 0
    remaining_distance = 0 

    transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)  

    # print('avstand', avstand)
    for segment in road_segments:
        coords = segment["geometry"]["coordinates"] 
        line = LineString(coords) 
        length = line.length
        # print('line', line)
        # print('line.length', line.length)
        # input()
        fartsgrense = segment["properties"]["fartsgrense"] / 3.6 # Convert speedlimit (Fartsgrense) from km/h to m/s
        
        distance = remaining_distance
        
        while distance < length:
            # print(i)
            point = line.interpolate(distance) 
            next_point = line.interpolate(distance + 1)
            point_latlng = transformer.transform(point.x, point.y)
            azimuth = calculate_travel_direction([point.x,point.y], [next_point.x, next_point.y])
            travel_time = (distance) / fartsgrense
            
            points_geojson.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": point_latlng
                },
                "properties": {
                    "distance_from_start": total_distance + distance,
                    "time_from_start": total_time + travel_time,
                    "azimuth": azimuth,
                }
            })

            distance += avstand 
        # print('remaining_distance', remaining_distance)
        # print('total_distance', total_distance)
        remaining_distance = distance - length 
        total_distance += length  
        total_time += length / fartsgrense
        # print('remaining_distance', remaining_distance)
        # print('total_distance', total_distance)
        # input()
    
    # print('len', len(points_geojson))
    # input()

    return points_geojson

# Fetch one additional road segment beyond the given end
def add_last_segment(sisteVegsegment_id: int, sisteVegsegment_nr: int, vegsystemreferanse: str, fartsgrense_df: pd.DataFrame, retning: str, i: int) -> tuple[dict, dict]:
    rett = " ".join(vegsystemreferanse.split()[:2])
    vegnett = nvdbapiv3.nvdbVegnett()
    vegnett.filter({'vegsystemreferanse': rett})
    vegdata = vegnett.to_records()
    #print('length', len(vegdata))
    vegdata_df = pd.DataFrame(vegdata)
    dette_segmentet = vegdata_df[
        (vegdata_df['veglenkesekvensid'] == sisteVegsegment_id) & 
        (vegdata_df['veglenkenummer'] == sisteVegsegment_nr)
    ]  
    neste_index = dette_segmentet.index[0] +1
    neste_segment = vegdata_df.iloc[neste_index]


    fartsgrense_row = fartsgrense_df[fartsgrense_df['veglenkesekvensid'] == neste_segment['veglenkesekvensid']]['Fartsgrense']
    fartsgrense = float(fartsgrense_row.iloc[0]) if not fartsgrense_row.empty else 50.0

    utm_coordinates = linestring_to_coordinates(neste_segment['geometri'])
    
    if retning == 'MOT':
        utm_coordinates.reverse()

    wgs_coordinates = convert_coordinates(utm_coordinates)
    geojson_feature_wgs = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": wgs_coordinates
        },
        "properties": {"name": "RoadSegment ", "id": i, "fartsgrense":fartsgrense}
    }


    geojson_feature_utm = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": utm_coordinates
        },
        "properties": {"name": "RoadSegment ", "id": i, "fartsgrense":fartsgrense}
    }
    #print(neste_segment)
    return geojson_feature_utm, geojson_feature_wgs


# Main function to fetch road geometry and properties from NVDB API
def get_road_api(startpoint: list[float], sluttpoint: list[float], vegsystemreferanse: str) -> tuple[list[dict], pd.DataFrame, str]:
    try:
        # Fetch speed limits
        fartsgrenser = nvdbapiv3.nvdbFagdata(105)
        fartsgrenser.filter({'vegsystemreferanse': vegsystemreferanse})

        #print('start, slutt', startpoint, sluttpoint)

        url = (
            f'https://nvdbapiles-v3.utv.atlas.vegvesen.no/beta/vegnett/rute'
            f'?start={startpoint[0]},{startpoint[1]}'
            f'&slutt={sluttpoint[0]},{sluttpoint[1]}'
            f'&maks_avstand=1000&omkrets=10&konnekteringslenker=true'
            f'&detaljerte_lenker=false&behold_trafikantgruppe=false'
            f'&pretty=true&kortform=false&vegsystemreferanse={vegsystemreferanse}'
        )
        #print('url', url)

        headers = {
            "Accept": "application/json",
            "X-Client": "Masteroppgave-vegnett"
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Error from NVDB API: {response.status_code} {response.text}")

        data = response.json()
        segmenter = data.get('vegnettsrutesegmenter', [])
        if not segmenter:
            raise IndexError("No road segments found for the given input. Most likely you have to be more specific with the start and end point. Check that you have the correcr Road reference system.")

        df = pd.DataFrame(fartsgrenser.to_records()).query("typeVeg == 'Enkel bilveg'")

        # Delete merged raster if exists
        #print('lager raster')
        if os.path.exists("data/merged_raster.tif"):
            os.remove("data/merged_raster.tif")
        start = perf_counter_ns()
        createNewRaster(startpoint, sluttpoint)
        print("timing createNewRaster (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
        #print('utav lager raster')



        return segmenter, df, vegsystemreferanse

    except Exception as e:
        #print(f"Error in get_road_api: {e}")
        raise  # let Flask catch and handle this

def connect_total_road_segments(road_segments: list[dict], fartsgrense_df: dict, vegsystemreferanse: str, startpoint: list[float], sluttpoint: list[float]) -> tuple[list[dict], list[dict]]:
    i = 0
    total_vegsegment_wgs84 = []
    total_vegsegment_utm = []

    for veglenke in road_segments:
        if veglenke['typeVeg_sosi'] != 'enkelBilveg': continue

        fartsgrense_row = fartsgrense_df[fartsgrense_df['veglenkesekvensid'] == veglenke['veglenkesekvensid']]['Fartsgrense']
        fartsgrense = float(fartsgrense_row.iloc[0]) if not fartsgrense_row.empty else 50.0
        utm_coordinates = linestring_to_coordinates(veglenke['geometri']['wkt'])
        
        retningIveg = veglenke['vegsystemreferanse']['strekning']['retning']
        retning = checkDirection(startpoint,utm_coordinates[0], utm_coordinates[-1])

        #print(retning, retningIveg)
        
        if retning == 'MOT':
            utm_coordinates.reverse()
        wgs_coordinates = convert_coordinates(utm_coordinates)
        #print('startPoint in segment', utm_coordinates[0])
        geojson_feature_wgs = {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": wgs_coordinates},
            "properties": {"name": "RoadSegment", "id": i, "fartsgrense": fartsgrense}
        }

        
        geojson_feature_utm = {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": utm_coordinates},
            "properties": {"name": "RoadSegment", "id": i, "fartsgrense": fartsgrense}
        }

        total_vegsegment_wgs84.append(geojson_feature_wgs)
        total_vegsegment_utm.append(geojson_feature_utm)
        i += 1

    #sjekekr rekkefølgen på vegsegmenter
    segments_direction = checkDirection(startpoint, total_vegsegment_utm[0]['geometry']['coordinates'][0], total_vegsegment_utm[-1]['geometry']['coordinates'][-1])
    
    if segments_direction == 'MOT':
        total_vegsegment_utm.reverse()
        total_vegsegment_wgs84.reverse()

    sistesegment = road_segments[-1]
    #print('i sistesegment', sistesegment)
    
    geojson_feature_utm, geojson_feature_wgs = add_last_segment(
        sistesegment['veglenkesekvensid'],
        sistesegment['veglenkenummer'],
        sistesegment['vegsystemreferanse']['kortform'],
        fartsgrense_df,
        retning,
        i
    )

    #print('utav siste segment')

    total_vegsegment_utm.append(geojson_feature_utm)
    total_vegsegment_wgs84.append(geojson_feature_wgs)

    connected_utm = connect_road(total_vegsegment_utm)
    connected_wgs = connect_road(total_vegsegment_wgs84)

    #print('første segment', connected_utm[0]['geometry']['coordinates'][0])
    return connected_utm,connected_wgs

# eksempel url
# https://nvdbapiles-v3.utv.atlas.vegvesen.no/beta/vegnett/rute?start=131363.978346842,6943393.145821838&slutt=136419.9895830073,6941862.632362077&maks_avstand=1000&omkrets=10&konnekteringslenker=true&detaljerte_lenker=true&behold_trafikantgruppe=false&pretty=true&kortform=false&vegsystemreferanse=EV136
#test 
# https://nvdbapiles-v3.utv.atlas.vegvesen.no/vegnett?detaljnivå=Kjørefelt&vegsystemreferanse=EV136&segmentstart=131363.978346842,6943393.145821838&segmentslutt=136419.9895830073,6941862.632362077
# vegnett = nvdbapiv3.nvdbVegnett()
# vegnett.filter({'vegsystemreferanse': 'EV6 S54D1'})
# vegnett_liste = vegnett.to_records()
# print('vegnett',len(vegnett_liste))

# start=[131363.978346842,6943393.145821838]
# slutt=[136419.9895830073,6941862.632362077]
# startLL = [62.630977, 10.083656]
# sluttLL = [62.617177, 10.149317]
# veg = get_road_api(start,slutt, 'EV136')
# vegnett = nvdbapiv3.nvdbVegnett()
# vegnett.filter({'vegsystemreferanse': 'EV136'})
# vegdata = vegnett.to_records()
# vegdata_df = pd.DataFrame(vegdata)
# ny_geometri = []
# for i, row in vegdata_df.iterrows():
#     converted = linestring_to_coordinates(row['geometri'])
#     ny_geometri.append(converted)
    
# vegdata_df['geometri_ny'] = ny_geometri
# print(vegdata_df.columns)
# #finn alle veglenke nr og star og slutt pos for vegleneksekvens: 248939
# filtered = vegdata_df[vegdata_df['veglenkesekvensid'] == 248939]
# print(filtered[['veglenkenummer', 'type']])
# print(vegdata_df[['veglenkesekvensid', 'veglenkenummer', 'startposisjon', 'sluttposisjon']].head())
# print(vegdata_df['veglenkesekvensid'].unique)


# import time

#når vegen går mot ålesund(feil veg), er sluttniode først, men dette er det"første" segmentet som går i rikig veg, retning er mot
#når vegen går mot dombås, er første segment startnode, men geometrien går feil veg. retnign er mot

#     # Start tidtaking
# start_time = time.time()
# road_utm, road_wgs =  get_road_api(start, slutt, 'EV136')
# truncated_road = truncate_road_segment(road_utm, start)
# #sorted_road = sort_road_api(road_wgs)
# points = calculate_travel_time(road_utm, 100)
# end_time = time.time()

# # Beregn og skriv ut kjøretiden
# elapsed_time = end_time - start_time
# print(f"Kjøretid finn elevation: {elapsed_time:.2f} sekunder")
# points_geojson = {
#     "type": "FeatureCollection",
#     "features": points
# }
# Create a FeatureCollection manually
# geojson_object = {
#     "type": "FeatureCollection",
#     "features": road_wgs
# }



# # # Save it as a GeoJSON file
# with open("points.geojson", "w") as f:
#     json.dump(points_geojson, f, indent=4)
# print(filtered[['veglenkesekvensid','veglenkenummer', 'segmentnummer']])
# fart = nvdbapiv3.finnid(85288328, kunfagdata=True) # python-dict
# fartobj = nvdbapiv3.nvdbFagObjekt(fart)   # Objektorientert representasjon, se definisjonen nvdbFagobjekt
# veg = nvdbapiv3.finnid(1812388, kunvegnett=True)

# print(fart)
