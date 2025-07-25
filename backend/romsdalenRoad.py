import json
import math
import os
import numpy as np
from pyproj import Transformer
import requests
import pandas as pd
from shapely.geometry import LineString, Point
from downloadHoydedata import create_new_raster
import nvdbapiv3 
from flask import jsonify

from time import perf_counter_ns


# Set up coordinate transformers between UTM and WGS84
transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)
transformerToEN = Transformer.from_crs("EPSG:4326","EPSG:25833", always_xy=True)

def linestring_to_coordinates(linestring: str) -> list[list[np.float64]]:
    """
    Convert WKT LINESTRING Z to coordinate array in UTM33.
    """
    wkt_string = linestring.replace("LINESTRING Z(", "").replace(")", "")
    points = np.array([list(map(float, p.split())) for p in wkt_string.split(", ")])
    points_without_height = [ [coord[0], coord[1]] for coord in points]
    return points_without_height

def convert_coordinates(utm_coords: list[list[np.float64]]) -> list[list[float]]:
    """
    Convert UTM coordinates to WGS84 coordinates.
    """
    coords = np.array(utm_coords)
    transformed_points = np.column_stack(transformer.transform(coords[:, 0], coords[:, 1]))
    return transformed_points.tolist()

def calculate_travel_direction(p1: list[float], p2: list[float]) -> float:
    """
    Return angel as plane azimuth.
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle_rad = math.atan2(dx, dy)
    angle_deg = math.degrees(angle_rad)
    return (angle_deg + 360) % 360

def calculate_distance(p1: list[float], p2: list[float]) -> float:
    """
    Distance between two points.
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx**2 + dy**2)

def in_wrong_direction(startpoint_road: list[float], startpoint_segment: list[np.float64], endpoint_segment: list[np.float64]) -> bool:
    """
    Check if the start_point is closer to beginning or end of a segment.
    IMPORTANT: May be erroneous for meandering road.
    """
    distance2start = calculate_distance(startpoint_road, startpoint_segment)
    distance2end   = calculate_distance(startpoint_road, endpoint_segment)
    return distance2start > distance2end


def connect_road(total_road: list[dict]) -> dict:
    """
    Connect all road segments and insert missing connectors if needed.
    """
    road_segments = total_road.copy()
    connected = [road_segments[0]]
    for i in range(1,len(road_segments)-1):
        prev_segment_end_point = road_segments[i-1]["geometry"]["coordinates"][-1]
        start_point = road_segments[i]["geometry"]["coordinates"][0]
        #print('start, prev', start_point, prev_segment_end_point)
        speedlimit = road_segments[i]["properties"]["fartsgrense"]
        if prev_segment_end_point != start_point:
            geojson_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [prev_segment_end_point, start_point]
                },
                "properties": {"name": "RoadSegment ", "id": i, "fartsgrense":speedlimit}
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
        speedlimit = segment["properties"]["fartsgrense"] / 3.6 # Convert speedlimit (Fartsgrense) from km/h to m/s
        
        distance = remaining_distance
        
        while distance < length:
            # print(i)
            point = line.interpolate(distance) 
            next_point = line.interpolate(distance + 1)
            point_latlng = transformer.transform(point.x, point.y)
            azimuth = calculate_travel_direction([point.x,point.y], [next_point.x, next_point.y])
            travel_time = (distance) / speedlimit
            
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
        total_time += length / speedlimit
        # print('remaining_distance', remaining_distance)
        # print('total_distance', total_distance)
        # input()
    
    # print('len', len(points_geojson))
    # input()

    return points_geojson

# Fetch one additional road segment beyond the given end
def add_last_segment(sisteVegsegment_id: int, sisteVegsegment_nr: int, vegsystemreferanse: str, speedlimit_df: pd.DataFrame, is_in_wrong_direction: bool, i: int) -> tuple[dict, dict]:
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


    speedlimit_row = speedlimit_df[speedlimit_df['veglenkesekvensid'] == neste_segment['veglenkesekvensid']]['Fartsgrense']
    speedlimit = float(speedlimit_row.iloc[0]) if not speedlimit_row.empty else 50.0

    utm_coordinates = linestring_to_coordinates(neste_segment['geometri'])
    
    if is_in_wrong_direction:
        utm_coordinates.reverse()

    wgs_coordinates = convert_coordinates(utm_coordinates)
    geojson_feature_wgs = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": wgs_coordinates
        },
        "properties": {"name": "RoadSegment ", "id": i, "fartsgrense":speedlimit}
    }


    geojson_feature_utm = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": utm_coordinates
        },
        "properties": {"name": "RoadSegment ", "id": i, "fartsgrense":speedlimit}
    }
    #print(neste_segment)
    return geojson_feature_utm, geojson_feature_wgs


# Main function to fetch road geometry and properties from NVDB API
def get_road_api(startpoint: list[float], endpoint: list[float], vegsystemreferanse: str) -> tuple[list[dict], pd.DataFrame, str]:
    """
    Trough testing, only seem to work on EV6 and EV136... no other roads.
    """
    try:

        print('vegsystemreferanse', vegsystemreferanse)
        # Fetch speed limits
        speedlimits = nvdbapiv3.nvdbFagdata(105)
        speedlimits.filter({'vegsystemreferanse': vegsystemreferanse})

        #print('start, slutt', startpoint, endpoint)

        headers = {
            "Accept": "application/json",
            "X-Client": "Masteroppgave-vegnett"
        }

        start_pos_url = f'https://nvdbapiles.atlas.vegvesen.no/posisjon?maks_avstand=200&nord={startpoint[1]}&ost={startpoint[0]}'
        end_pos_url = f'https://nvdbapiles.atlas.vegvesen.no/posisjon?maks_avstand=200&nord={endpoint[1]}&ost={endpoint[0]}'


        start_veglenkesekvens_kortform = requests.get(start_pos_url).json()[0]["veglenkesekvens"]["kortform"]
        end_veglenkesekvens_kortform = requests.get(end_pos_url).json()[0]["veglenkesekvens"]["kortform"]
        print('start_json', start_veglenkesekvens_kortform, end_veglenkesekvens_kortform)

        url = (
            f'https://nvdbapiles-v3.utv.atlas.vegvesen.no/beta/vegnett/rute'
            f'?start={start_veglenkesekvens_kortform}'
            f'&slutt={end_veglenkesekvens_kortform}'
            f'&maks_avstand=100&omkrets=1000&konnekteringslenker=true'
            f'&detaljerte_lenker=false&behold_trafikantgruppe=false'
            f'&pretty=true&kortform=false'
        )
        print("url", url)


        response = requests.get(url, headers=headers)
        # print('rrl:', url, 'headers', headers)
        print('respons text', response.text)
        if response.status_code != 200:
            raise Exception(f"Error from NVDB API: {response.status_code} {response.text}")

        data = response.json()
        segmenter = data.get('vegnettsrutesegmenter', [])
        if not segmenter:
            raise IndexError("No road segments found for the given input. Most likely you have to be more specific with the start and end point. Check that you have the correct Road reference system.")

        df = pd.DataFrame(speedlimits.to_records()).query("typeVeg == 'Enkel bilveg'")

        # Delete merged raster if exists
        #print('lager raster')
        if os.path.exists("data/merged_raster.tif"):
            os.remove("data/merged_raster.tif")
        start = perf_counter_ns()
        create_new_raster(startpoint, endpoint)
        # print("timing createNewRaster (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
        #print('utav lager raster')



        return segmenter, df, vegsystemreferanse

    except Exception as e:
        print(f"Error in get_road_api: {e}")
        raise  # let Flask catch and handle this

def connect_total_road_segments(road_segments: list[dict], speedlimit_df: dict, vegsystemreferanse: str, startpoint: list[float], endpoint: list[float]) -> tuple[list[dict], list[dict]]:
    i = 0
    total_vegsegment_wgs84 = []
    total_vegsegment_utm = []

    for veglenke in road_segments:
        if veglenke['typeVeg_sosi'] != 'enkelBilveg': continue

        speedlimit_row = speedlimit_df[speedlimit_df['veglenkesekvensid'] == veglenke['veglenkesekvensid']]['Fartsgrense']
        speedlimit = float(speedlimit_row.iloc[0]) if not speedlimit_row.empty else 50.0
        utm_coordinates = linestring_to_coordinates(veglenke['geometri']['wkt'])
        
        # retningIveg = veglenke['vegsystemreferanse']['strekning']['retning'] # Dont know why ignored.
        is_in_wrong_direction = in_wrong_direction(startpoint,utm_coordinates[0], utm_coordinates[-1])
        if is_in_wrong_direction:
            utm_coordinates.reverse()
        wgs_coordinates = convert_coordinates(utm_coordinates)
        #print('startPoint in segment', utm_coordinates[0])
        geojson_feature_wgs = {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": wgs_coordinates},
            "properties": {"name": "RoadSegment", "id": i, "fartsgrense": speedlimit}
        }

        geojson_feature_utm = {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": utm_coordinates},
            "properties": {"name": "RoadSegment", "id": i, "fartsgrense": speedlimit}
        }

        total_vegsegment_wgs84.append(geojson_feature_wgs)
        total_vegsegment_utm.append(geojson_feature_utm)
        i += 1

    if in_wrong_direction(startpoint, total_vegsegment_utm[0]['geometry']['coordinates'][0], total_vegsegment_utm[-1]['geometry']['coordinates'][-1]):
        total_vegsegment_utm.reverse()
        total_vegsegment_wgs84.reverse()

    last_segment = road_segments[-1]
    
    geojson_feature_utm, geojson_feature_wgs = add_last_segment(
        last_segment['veglenkesekvensid'],
        last_segment['veglenkenummer'],
        last_segment['vegsystemreferanse']['kortform'],
        speedlimit_df,
        is_in_wrong_direction,
        i
    )

    total_vegsegment_utm.append(geojson_feature_utm)
    total_vegsegment_wgs84.append(geojson_feature_wgs)

    connected_utm = connect_road(total_vegsegment_utm)
    connected_wgs = connect_road(total_vegsegment_wgs84)

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
