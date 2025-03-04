import json
from pyproj import Transformer
from shapely.wkt import loads
from downloadfile import downloadRoad
import requests
import requests
import concurrent.futures
from itertools import chain
import pandas as pd
from shapely.geometry import LineString, Point
import nvdbapiv3 
import geopandas as gpd
from shapely import wkt
from shapely.geometry import mapping



transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)
transformerToEN = Transformer.from_crs("EPSG:4326","EPSG:25833", always_xy=True)
def linestring_to_coordinates(linestring):
    wkt_string = linestring.replace("LINESTRING Z(", "").replace(")", "")
    points = [tuple(map(float, p.split())) for p in wkt_string.split(", ")]  # Parse E, N values 
    converted_points = [[transformer.transform(e, n)[0], transformer.transform(e, n)[1]] for e, n,h in points]
    return converted_points

def convert_coordinates(wgs84_coords):

    converted_points = [[transformerToEN.transform(lng, lat)[0], transformerToEN.transform(lng, lat)[1]] for lng,lat in wgs84_coords]
    return converted_points

def connect_road(total_road):
    road_segments = total_road.copy()
    connected = [road_segments[0]]
    for i in range(1,len(road_segments)-1):
        prev_segment_end_point = road_segments[i-1]["geometry"]["coordinates"][-1]
        start_point = road_segments[i]["geometry"]["coordinates"][0]
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


def calculate_travel_time(road_segments, avstand):
    points_geojson = []
    total_time = 0  # Akkumulert tid fra startpunktet
    total_distance = 0  # Akkumulert distanse fra startpunktet
    remaining_distance = 0  # Restlengde fra forrige segment

    transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)  # UTM til WGS84 (Eksempel)

    for segment in road_segments:
        coords = segment["geometry"]["coordinates"] 
        line = LineString(coords) 
        length = line.length  # Lengden på segmentet
        fartsgrense = segment["properties"]["fartsgrense"] / 3.6  # Konverter km/t til m/s
        
        distance = remaining_distance  # Start med restlengde fra forrige segment
        while distance < length:
            point = line.interpolate(distance)  # Finner punkt på veien
            point_latlng = transformer.transform(point.x, point.y)  # Konverterer til WGS84
            
            # Tid til dette punktet
            travel_time = (distance) / fartsgrense  # Tid fra forrige punkt
            
            # Lagre punkt i GeoJSON-format
            points_geojson.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": point_latlng
                },
                "properties": {
                    "distance_from_start": total_distance + distance,
                    "time_from_start": total_time + travel_time
                }
            })

            distance += avstand  # Flytt til neste punkt

        remaining_distance = distance - length  # Hvor mye av neste steg må videreføres?
        total_distance += length  # Oppdater total distanse
        total_time += length / fartsgrense

    return points_geojson


def get_road_api(startpoint,sluttpoint, vegsystemreferanse):
    fartsgrenser = nvdbapiv3.nvdbFagdata(105)
    fartsgrenser.filter({'vegsystemreferanse':vegsystemreferanse})
    url =f'https://nvdbapiles-v3.utv.atlas.vegvesen.no/beta/vegnett/rute?start={startpoint[0]},{startpoint[1]}&slutt={sluttpoint[0]},{sluttpoint[1]}&maks_avstand=10&omkrets=100&konnekteringslenker=true&detaljerte_lenker=false&behold_trafikantgruppe=false&pretty=true&kortform=false&vegsystemreferanse=EV136'
    headers = {
        "Accept": "application/json",
        "X-Client": "Masteroppgave-vegnett"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []  # Returnerer tom liste hvis feil i forespørselen
    
    data = response.json()
    segmenter = data.get('vegnettsrutesegmenter', [])
    df = pd.DataFrame(fartsgrenser.to_records())
    df = df[(df['typeVeg'] == 'Enkel bilveg')]
    i = 0
    total_vegsegment_wgs84=[]
    total_vegsegment_utm = []
    for veglenke in segmenter:
        if (
                # veglenke['type'] == 'HOVED' and
                veglenke['typeVeg_sosi'] == 'enkelBilveg' 
            ):
                fartsgrense_row = df[df['veglenkesekvensid'] == veglenke['veglenkesekvensid']]['Fartsgrense']
                fartsgrense = float(fartsgrense_row.iloc[0]) if not fartsgrense_row.empty else None
                #print(fartsgrense)
                converted = linestring_to_coordinates(veglenke['geometri']['wkt'])
                if veglenke['vegsystemreferanse']['strekning']['retning'] == 'MOT':
                    print('reversing')
                    converted = converted[::-1]
                geojson_feature_wgs = {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": converted
                    },
                    "properties": {"name": "RoadSegment ", "id": i, "fartsgrense":fartsgrense}
                }
                utm_converted = convert_coordinates(converted)
                geojson_feature_utm = {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": utm_converted
                    },
                    "properties": {"name": "RoadSegment ", "id": i, "fartsgrense":fartsgrense}
                }
                total_vegsegment_wgs84.append(geojson_feature_wgs)
                total_vegsegment_utm.append(geojson_feature_utm)
                i += 1

    connected_utm = connect_road(total_vegsegment_utm)
    connected_wgs = connect_road(total_vegsegment_wgs84)
    return connected_utm, connected_wgs

# start = [136149.75, 6941757.94]
# slutt = [193547.58,6896803.47]
# import time

#     # Start tidtaking
# start_time = time.time()
# road_utm, road_wgs =  get_road_api(start, slutt, 'EV136')
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
