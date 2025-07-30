import numpy as np
from pyproj import Transformer
import requests
from shapely.geometry import LineString
import config
import re

from time import perf_counter_ns

# Set up coordinate transformers between UTM and WGS84
transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)
transformerToEN = Transformer.from_crs("EPSG:4326","EPSG:25833", always_xy=True)

def linestring_to_coordinates(linestring: str) -> list[list[float]]:
    """
    Convert WKT LINESTRING Z to coordinate list in UTM33.
    Ignores elevation data.
    """
    linestring_stripped = linestring.replace('(', ',') # Remove openeing bracket to simplify regex
    east_north_pattern = '(?<=,)\s?\d+\.?\d*\s\d+\.?\d*'
    # Pattern matches two sequential floating point numbers after a '(' or ','
    # If 'linestring' was "LINESTRING Z ,116327.967 6953139.812 7.083,116321.16 6953161.844)"  (note opening bracket '(' is replaced with ',' above.)
    # then match will be:               "116327.967 6953139.812"     "116321.16 6953161.844"
    east_north_strings = re.findall(east_north_pattern, linestring_stripped)
    points_without_height = list([list(map(float, pos.split())) for pos in east_north_strings])
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
    Ignores elevation data.
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle_rad = np.atan2(dx, dy)
    angle_deg = np.degrees(angle_rad)
    return (angle_deg + 360) % 360

def calculate_distance(p1: list[float], p2: list[float]) -> float:
    """
    Distance between two points on a plane.
    Ignores elevation.
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return np.sqrt(dx**2 + dy**2)


def get_closest_roadsequence(startpoint: list[float], endpoint: list[float]) -> tuple[str, str]:
    """
    Gets the point on the road that is closes to the startpoint and to the endpoint.
    """
    MAX_SEARCH_DISTANCE = 200 # meters
    start_pos_url = f'https://nvdbapiles.atlas.vegvesen.no/posisjon?maks_avstand={MAX_SEARCH_DISTANCE}&ost={startpoint[0]}&nord={startpoint[1]}'
    end_pos_url   = f'https://nvdbapiles.atlas.vegvesen.no/posisjon?maks_avstand={MAX_SEARCH_DISTANCE}&ost={endpoint[0]}&nord={endpoint[1]}'
    try:
        start_kortform = requests.get(start_pos_url).json()[0]["veglenkesekvens"]["kortform"]
        end_kortform   = requests.get(end_pos_url).json()[0]["veglenkesekvens"]["kortform"]
        return start_kortform, end_kortform
    except Exception as e:
        print(f'Error in GET request, no valid car-road within {MAX_SEARCH_DISTANCE} meter from the startpoint or endpoint.\n'
              f'Error from "get_closest_roadsequence": {e}')
        raise  # let Flask catch and handle this



def get_road(startpoint: list[float], endpoint: list[float]) -> list[list[list[float]]]:
    start_kortform, end_kortform = get_closest_roadsequence(startpoint, endpoint)
    url = (
            f'https://nvdbapiles-v3.utv.atlas.vegvesen.no/beta/vegnett/rute'
            f'?start={start_kortform}'
            f'&slutt={end_kortform}'
            f'&maks_avstand=100&omkrets=1000'
            f'&konnekteringslenker=true&detaljerte_lenker=false'
            f'&trafikantgruppe=K&behold_trafikantgruppe=true'
        )

    response = requests.get(url, headers=config.HEADERS)
    if response.status_code != 200:
        raise Exception(f"Error from NVDB API: {response.status_code} {response.text}")

    data = response.json()
    road_segment_objects = data.get('vegnettsrutesegmenter', [])
    if not road_segment_objects:
        raise IndexError("No valid route found between startpoint and endpoint.")
    
    road_segments_linestrings = [segm['geometri']['wkt'] for segm in road_segment_objects]
    road_segments_coords = list(map(linestring_to_coordinates, road_segments_linestrings))

    print('road_segments_coords', road_segments_coords)

    start = perf_counter_ns()
    # print("timing createNewRaster (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))

    return road_segments_coords
    


def get_road_and_speedlimits(startpoint: list[float], endpoint: list[float]) -> tuple[ list[list[list[float]]], list[int] ]:
    try:
        start_kortform, end_kortform = get_closest_roadsequence(startpoint, endpoint)
        url = (
                f'https://nvdbapiles-v3.utv.atlas.vegvesen.no/beta/vegnett/rute'
                f'?start={start_kortform}'
                f'&slutt={end_kortform}'
                f'&maks_avstand=100&omkrets=1000'
                f'&konnekteringslenker=true&detaljerte_lenker=false'
                f'&trafikantgruppe=K&behold_trafikantgruppe=true'
            )

        response = requests.get(url, headers=config.HEADERS)
        if response.status_code != 200:
            raise Exception(f"Error from NVDB API: {response.status_code} {response.text}")

        data = response.json()
        if data['metadata']['status_tekst'] == 'IKKE_FUNNET_RUTE':
            raise ValueError('No rode route found between point A and B')
        road_segments = data.get('vegnettsrutesegmenter', [])
        if not road_segments:
            raise IndexError("No valid route found between startpoint and endpoint.")
        
        SPEEDLIMITS_OBJ_ID = 105
        speedlimits = []
        
        # Find the speedlimits for each segment.
        for segment in road_segments:
            url = (
                f'https://nvdbapiles.atlas.vegvesen.no/vegobjekter/api/v4/vegobjekter/{SPEEDLIMITS_OBJ_ID}?'
                f'&veglenkesekvens={segment['kortform']}'
            )
            speedlimit = None
            try:
                response = requests.get(url, headers=config.HEADERS)
                if response.status_code != 200:
                    raise Exception(f"Error from NVDB API: {response.status_code} {response.text}")
                
                data = response.json()
                json_data = data.get('objekter', [])
                href_speed_limits = json_data[0]['href']
                response = requests.get(href_speed_limits, headers=config.HEADERS)
                if response.status_code != 200:
                    raise Exception(f"Error from NVDB API: {response.status_code} {response.text}")
                
                data = response.json()
                # Not consistent where the speedlimit value is placed, try both places.
                try:
                    speedlimit = data['egenskaper'][1]['verdi']
                except IndexError:
                    speedlimit = data['egenskaper'][0]['verdi']
            except:
                # Speedlimit may be missing on remote roads, and no speedlimit on ferry crossingings
                speedlimit = config.DEFAULT_SPEEDLIMIT

            speedlimits.append(speedlimit)
    
        road_segments_linestring = [segm['geometri']['wkt'] for segm in road_segments]
        road_segments_coords = list(map(linestring_to_coordinates, road_segments_linestring))
        return road_segments_coords, speedlimits
        """
            # Delete merged raster if exists
            if os.path.exists("data/merged_raster.tif"):
                os.remove("data/merged_raster.tif")
            start = perf_counter_ns()
            create_new_raster(startpoint, endpoint)
            # print("timing createNewRaster (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
        
        # Original code gives buggy behaviour for:
        # (Basically didnt work for anything but the default EV136 route.)

        # Start (E,N) = 124657.85,6957624.16
        # End   (E,N) = 193510.27,6896504.01
        # Distance = 1000

        # Start (E,N) = 124657.85,6957624.16
        # End   (E,N) = 193510.27,6896504.01
        # Distance = 1000

        # Start (E,N) = 124657.85,6957624.16
        # End   (E,N) = 193510.27,6896504.01
        # Distance = 1000
            
        """
    except Exception as e:
        print(f"Error in get_road_and_speedlimits: {e}")
        raise  # let Flask catch and handle this


def segment_in_wrong_direction(prev_segment_endpoint: list[float] | None, curr_segment_startpoint: list[float], curr_segment_endpoint: list[float], startpoint: list[float]) -> bool:
    """
    Check if the coordinates in the segment is oriented in the travel-direction.
    """
    #First point on route, chose orientation based on proximity to start
    if prev_segment_endpoint is None:
        start2segment_beginning = calculate_distance(startpoint, curr_segment_startpoint)
        start2segment_end = calculate_distance(startpoint, curr_segment_endpoint)
        return start2segment_beginning > start2segment_end
    return prev_segment_endpoint != curr_segment_startpoint


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


def connect_total_road_segments(road_segments: list[list[list[float]]], startpoint: list[float], speedlimits: list[int] = []) -> tuple[list[dict], list[dict]]:
    """
    Returns UTM and WGS84 lists of roadsegments dictionaries, in which the coordinates in the dictionary is oriented wowards the travel length.
    """
    
    total_vegsegment_wgs84 = []
    total_vegsegment_utm = []
    i = 0
    prev_segment_endpoint = None
    for segment_utm_coords in road_segments:
        speedlimit = speedlimits[i] if speedlimits else config.DEFAULT_SPEEDLIMIT # If DEFAULT_SPEEDLIMIT was np.inf: Travel instantly, time dont pass along route.
        if segment_in_wrong_direction(prev_segment_endpoint, segment_utm_coords[0], segment_utm_coords[-1], startpoint):
            segment_utm_coords.reverse()

        wgs_coordinates = convert_coordinates(segment_utm_coords)
        
        geojson_feature_wgs = {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": wgs_coordinates},
            "properties": {"name": "RoadSegment", "id": i, "fartsgrense": speedlimit}
        }

        geojson_feature_utm = {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": segment_utm_coords},
            "properties": {"name": "RoadSegment", "id": i, "fartsgrense": speedlimit}
        }

        total_vegsegment_wgs84.append(geojson_feature_wgs)
        total_vegsegment_utm.append(geojson_feature_utm)
        prev_segment_endpoint = segment_utm_coords[-1]
        i += 1

    total_vegsegment_utm.append(geojson_feature_utm)
    total_vegsegment_wgs84.append(geojson_feature_wgs)

    connected_utm = connect_road(total_vegsegment_utm)
    connected_wgs = connect_road(total_vegsegment_wgs84)
    return connected_utm, connected_wgs


def extract_points_at_interval(road_segments: list[dict], spacing: float) -> list[dict]:
    """
    Finds the points (dictionaries) along the 'road_segments' with interval equal to 'distance'.
    The points dictionaries include calculated traveltime.
    """
    points_geojson     = []
    total_time         = 0  
    total_distance     = 0
    remaining_distance = 0 

    transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)  

    for segment in road_segments:
        coords = segment["geometry"]["coordinates"] 
        line = LineString(coords) 
        length = line.length
        speedlimit = segment["properties"]["fartsgrense"] / 3.6 # Convert speedlimit (Fartsgrense) from km/h to m/s
        
        distance = remaining_distance
        
        while distance < length:
            point = line.interpolate(distance)
            next_point = line.interpolate(distance + 1)
            point_latlng = transformer.transform(point.x, point.y)
            azimuth = calculate_travel_direction([point.x, point.y], [next_point.x, next_point.y])
            travel_time = distance / speedlimit
            
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

            distance += spacing

        remaining_distance = distance - length 
        total_distance += length  
        total_time += length / speedlimit

    return points_geojson