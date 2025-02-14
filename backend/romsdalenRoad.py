import json
from pyproj import Transformer
from shapely.wkt import loads
from downloadfile import downloadRoad
import requests
import requests
import concurrent.futures
from itertools import chain

from shapely.geometry import LineString, Point



transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)
transformerToEN = Transformer.from_crs("EPSG:4326","EPSG:25833", always_xy=True)
def linestring_to_coordinates(linestring):
    wkt_string = linestring.replace("LINESTRING Z(", "").replace(")", "")
    points = [tuple(map(float, p.split())) for p in wkt_string.split(", ")]  # Parse E, N values 
    converted_points = [[transformer.transform(e, n)[0], transformer.transform(e, n)[1]] for e, n,h in points]
    return converted_points

def convert_coordinates(wgs84_coords):
    #wgs84_coords = wgs84_coords
    #points = [tuple(map(float, p.split())) for p in wkt_string.split(", ")]  # Parse E, N values 
    converted_points = [[transformerToEN.transform(lng, lat)[0], transformerToEN.transform(lng, lat)[1]] for lng,lat in wgs84_coords]
    return converted_points



def sort_road(total_road):
    sorted_road = sorted(total_road, key=lambda segment: segment["geometry"]["coordinates"][0])
    return sorted_road



def get_road(startpoint,sluttpoint):
    print('in get_road')
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
    
    i = 0
    total_vegsegment_wgs84=[]
    for veglenke in segmenter:
        if (
                veglenke['type'] == 'HOVED' 
                and veglenke['typeVeg_sosi'] == 'enkelBilveg' 
            ):
          
                converted = linestring_to_coordinates(veglenke['geometri']['wkt'])
                geojson_feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": converted
                    },
                    "properties": {"name": "RoadSegment ", "id": i}
                }

                total_vegsegment_wgs84.append(geojson_feature)
                i += 1

    total_veg_sorted = sort_road(total_vegsegment_wgs84)

    # geojson_output = {
    #     "type": "FeatureCollection",
    #     "features": total_veg_sorted
    # }
    # with open("merged_road.geojson", "w") as f:
    #     json.dump(geojson_output, f, indent=4)
    return total_veg_sorted


road = get_road([124429.61,6957703.95], [193547.58,6896803.47])



def find_points(line, avstand):
    distance= 0
    left_distance = 0
    points = []
    for feature in line:
        coords = feature["geometry"]["coordinates"]
        coords = convert_coordinates(coords)
   
        line = LineString(coords)
        length = line.length

        if distance < length:
            while distance < length:
                left_distance = length-distance
                point = line.interpolate(distance)
                points.append(point)
                distance += avstand
            distance -= left_distance
        else:
            distance -= length
        

    #converter tilbake til 
    geoJson_points_list = []
    for point in points:
        point_converted = transformer.transform(point.x, point.y)
        point_geojson = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [point_converted[0], point_converted[1]]
            },
            "properties": {"name": "Point"}
        }
        geoJson_points_list.append(point_geojson)
    return geoJson_points_list



#https://nvdbapiles-v3.atlas.vegvesen.no/beta/vegnett/rute?start=124429.61,6957703.95&slutt=193547.58,6896803.47&maks_avstand=3&omkrets=5&konnekteringslenker=true&pretty=true&kortform=true&srid=utm33&vegsystemreferanse=EV136&trafikantgruppe=K