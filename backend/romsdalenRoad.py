import json
from pyproj import Transformer
from shapely.wkt import loads
from downloadfile import downloadRoad
import requests


transformer = Transformer.from_crs("EPSG:32633", "EPSG:4326", always_xy=True)

def linestring_to_coordinates(linestring):
    wkt_string = linestring.replace("LINESTRING Z(", "").replace(")", "")
    points = [tuple(map(float, p.split())) for p in wkt_string.split(", ")]  # Parse E, N values 
    converted_points = [[transformer.transform(e, n)[0], transformer.transform(e, n)[1]] for e, n,h in points]
    return converted_points
def get_total_road(roadJson):
    # print(roadJson)
    total_road = []
    road = roadJson['objekter']
    num = 0
    for segment in road:
        segmentID = segment['veglenkesekvensid']
        veglenker = segment['veglenker']
        #sorterer porter etter relativ posisjon på en vegsekvens
        porter = sorted(segment['porter'], key=lambda x: x['relativPosisjon'])
        porter_list = [port['id'] for port in porter]
        port_index = {port: idx for idx, port in enumerate(porter_list)}
        sort_veglenker = sorted(veglenker, key=lambda x: port_index.get(x['startport'], float('inf')))
        #print portid sortert
        # print(porter_list)
        # print(port_index)
        # print(f'porter lengde:{len(porter)}, veglenker lengde:{len(veglenker)}')
        total_vegsegment = []
        for i in range(0,len(sort_veglenker)):
            veglenke = sort_veglenker[i]
            if(veglenke['type'] == 'HOVED'):
                #print(veglenke['startport'], veglenke['sluttport'])
                converted_points = linestring_to_coordinates(veglenke['geometri']['wkt'])
    
                # if (veglenke['startport'] == sort_veglenker[i-1]['startport']) and (veglenke['sluttport'] == sort_veglenker[i-1]['sluttport']):
                #     #choose the one with the newest måledato
                #     if (i >0) and (veglenke['startdato'] > sort_veglenker[i-1]['startdato']):
                #         total_vegsegment[len(total_vegsegment)-1] = converted_points
                # else:
                total_vegsegment.append(converted_points)
        
        total_veg_list = []
        for seg in total_vegsegment:
           for point in seg:
                total_veg_list.append(point)

        geojson_data = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": total_veg_list
            },
            "properties": {"name": "Road Segment", "id": segmentID}
        }
        total_road.append(geojson_data)
       
    return total_road


# data = downloadRoad('EV136')
# road = get_total_road(data)
# print(road)

# def get_road_between_points(startpoint, sluttpoint):

#     url = f"https://nvdbapiles-v3.atlas.vegvesen.no/beta/vegnett/rute?start={startpoint[0]},{startpoint[1]}&slutt={sluttpoint[0]},{sluttpoint[1]}&maks_avstand=10&omkrets=100&konnekteringslenker=true&detaljerte_lenker=true&behold_trafikantgruppe=false&pretty=true&kortform=true"
#     header = {
#         "Accept": "application/json",
#         "X-Client": "Masteroppgave-vegnett"
#         }
    
#     response = requests.get(url, headers=header)
#     total_road = []
#     if response.status_code == 200:
#         data = response.json()
#         segmenter = data['vegnettsrutesegmenter']
#         for vegnettrutesegment in segmenter:
#             segmentId = vegnettrutesegment['veglenkesekvensid']
#             url_veg = f"https://nvdbapiles-v3.atlas.vegvesen.no/vegnett/veglenkesekvenser/{segmentId}"
#             responseveg = requests.get(url_veg, headers=header)
#             segment = responseveg.json()
            
#             veglenker = segment['veglenker']
#             #sorterer porter etter relativ posisjon på en vegsekvens
#             porter = sorted(segment['porter'], key=lambda x: x['relativPosisjon'])
#             porter_list = [port['id'] for port in porter]
#             port_index = {port: idx for idx, port in enumerate(porter_list)}
#             sort_veglenker = sorted(veglenker, key=lambda x: port_index.get(x['startport'], float('inf')))
#             #print portid sortert
#             # print(porter_list)
#             # print(port_index)
#             # print(f'porter lengde:{len(porter)}, veglenker lengde:{len(veglenker)}')
#             total_vegsegment = []
#             for i in range(0,len(sort_veglenker)):
#                 veglenke = sort_veglenker[i]
#                 if(veglenke['type'] == 'HOVED'):
#                     #print(veglenke['startport'], veglenke['sluttport'])
#                     converted_points = linestring_to_coordinates(veglenke['geometri']['wkt'])
        
#                     # if (veglenke['startport'] == sort_veglenker[i-1]['startport']) and (veglenke['sluttport'] == sort_veglenker[i-1]['sluttport']):
#                     #     #choose the one with the newest måledato
#                     #     if (i >0) and (veglenke['startdato'] > sort_veglenker[i-1]['startdato']):
#                     #         total_vegsegment[len(total_vegsegment)-1] = converted_points
#                     # else:
#                     total_vegsegment.append(converted_points)
            
#                 total_veg_list = []
#                 for seg in total_vegsegment:
#                     for point in seg:
#                         total_veg_list.append(point)

#                 geojson_data = {
#                     "type": "Feature",
#                     "geometry": {
#                         "type": "LineString",
#                         "coordinates": total_veg_list
#                     },
#                     "properties": {"name": "Road Segment", "id": segmentId}
#                 }
#                 total_road.append(geojson_data)
#         return total_road
    

import requests
import concurrent.futures
from itertools import chain

def get_road_between_points(startpoint, sluttpoint):
    print('in get_road_between_points')
    url = f"https://nvdbapiles-v3.atlas.vegvesen.no/beta/vegnett/rute?start={startpoint[0]},{startpoint[1]}&slutt={sluttpoint[0]},{sluttpoint[1]}&maks_avstand=3&omkrets=5&konnekteringslenker=true&pretty=true&kortform=true&srid=utm33&vegsystemreferanse=EV136"
    
    headers = {
        "Accept": "application/json",
        "X-Client": "Masteroppgave-vegnett"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []  # Returnerer tom liste hvis feil i forespørselen
    
    data = response.json()
    segmenter = data.get('vegnettsrutesegmenter', [])
    
    segment_ids = [seg['veglenkesekvensid'] for seg in segmenter]
    
    total_road = []
    
    def fetch_segment(segment_id):
        """ Henter data for et enkelt segment parallelt. """
        url_veg = f"https://nvdbapiles-v3.atlas.vegvesen.no/vegnett/veglenkesekvenser/{segment_id}?srid=utm33"
        responseveg = requests.get(url_veg, headers=headers)
        
        if responseveg.status_code != 200:
            return None
        
        segment = responseveg.json()
        veglenker = segment.get('veglenker', [])
        porter = sorted(segment.get('porter', []), key=lambda x: x['relativPosisjon'])
        
        porter_list = [port['id'] for port in porter]
        port_index = {port: idx for idx, port in enumerate(porter_list)}
        
        sort_veglenker = sorted(veglenker, key=lambda x: port_index.get(x['startport'], float('inf')))
        print(veglenker[0]['geometri']['wkt'])
        
        total_vegsegment = [
            linestring_to_coordinates(veglenke['geometri']['wkt'])
            for veglenke in sort_veglenker if veglenke['type'] == 'HOVED'
        ]
        
        total_veg_list = list(chain.from_iterable(total_vegsegment))  # Unngå nested loops
        
        return {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": total_veg_list
            },
            "properties": {"name": "Road Segment", "id": segment_id}
        }
    
    # 🚀 Parallelliser API-kallene for segmentdetaljer
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch_segment, segment_ids))
    
    # Filter ut None-resultater
    total_road.extend(filter(None, results))
    
    return total_road

road = get_road_between_points([124429.61,6957703.95], [193547.58,6896803.47])
#print(road)

#https://nvdbapiles-v3.atlas.vegvesen.no/beta/vegnett/rute?start=124429.61,6957703.95&slutt=193547.58,6896803.47&maks_avstand=3&omkrets=5&konnekteringslenker=true&pretty=true&kortform=true&srid=utm33&vegsystemreferanse=EV136&trafikantgruppe=K