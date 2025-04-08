import numpy as np
from pyproj import Transformer
import requests
import pandas as pd
from shapely.geometry import LineString, Point
import nvdbapiv3 



# Set up coordinate transformers between UTM and WGS84
transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)
transformerToEN = Transformer.from_crs("EPSG:4326","EPSG:25833", always_xy=True)

# Convert WKT LINESTRING Z to coordinate array in WGS84
def linestring_to_coordinates(linestring):
    wkt_string = linestring.replace("LINESTRING Z(", "").replace(")", "")
    points = np.array([list(map(float, p.split())) for p in wkt_string.split(", ")])
    transformed_points = np.column_stack(transformer.transform(points[:, 0], points[:, 1]))
    return transformed_points.tolist()

# Convert WGS84 coordinates to UTM
def convert_coordinates(wgs84_coords):
    coords = np.array(wgs84_coords)
    transformed_points = np.column_stack(transformerToEN.transform(coords[:, 0], coords[:, 1]))
    return transformed_points.tolist()

# Connect all road segments and insert missing connectors if needed
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

# Calculate position and time for measurement points along road segments
def calculate_travel_time(road_segments, avstand):
    points_geojson = []
    total_time = 0  
    total_distance = 0  
    remaining_distance = 0 

    transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)  

    for segment in road_segments:
        coords = segment["geometry"]["coordinates"] 
        line = LineString(coords) 
        length = line.length 
        fartsgrense = segment["properties"]["fartsgrense"] / 3.6 # Fartsgrense i m/s
        
        distance = remaining_distance  
        while distance < length:
            point = line.interpolate(distance) 
            point_latlng = transformer.transform(point.x, point.y)
            
            travel_time = (distance) / fartsgrense
            
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

            distance += avstand 

        remaining_distance = distance - length 
        total_distance += length  
        total_time += length / fartsgrense

    return points_geojson

# Fetch one additional road segment beyond the given end
def add_last_segment(sisteVegsegment_id, sisteVegsegment_nr, vegsystemreferanse, fartsgrense_df, retning, i):
    vegnett = nvdbapiv3.nvdbVegnett()
    vegnett.filter({'vegsystemreferanse': vegsystemreferanse})
    vegdata = vegnett.to_records()
    vegdata_df = pd.DataFrame(vegdata)
    dette_segmentet = vegdata_df[
        (vegdata_df['veglenkesekvensid'] == sisteVegsegment_id) & 
        (vegdata_df['veglenkenummer'] == sisteVegsegment_nr)
    ]  
    neste_index = dette_segmentet.index[0] +1
    neste_segment = vegdata_df.iloc[neste_index]


    fartsgrense_row = fartsgrense_df[fartsgrense_df['veglenkesekvensid'] == neste_segment['veglenkesekvensid']]['Fartsgrense']
    fartsgrense = float(fartsgrense_row.iloc[0]) if not fartsgrense_row.empty else None

    converted = linestring_to_coordinates(neste_segment['geometri'])
    
    if retning == 'MOT':
        converted.reverse()

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
    print(neste_segment)
    return geojson_feature_utm, geojson_feature_wgs


# Main function to fetch road geometry and properties from NVDB API
def get_road_api(startpoint,sluttpoint, vegsystemreferanse):
    fartsgrenser = nvdbapiv3.nvdbFagdata(105)
    fartsgrenser.filter({'vegsystemreferanse': vegsystemreferanse})

    url = (
        f'https://nvdbapiles-v3.utv.atlas.vegvesen.no/beta/vegnett/rute'
        f'?start={startpoint[0]},{startpoint[1]}'
        f'&slutt={sluttpoint[0]},{sluttpoint[1]}'
        f'&maks_avstand=1000&omkrets=10&konnekteringslenker=true'
        f'&detaljerte_lenker=false&behold_trafikantgruppe=false'
        f'&pretty=true&kortform=false&vegsystemreferanse={vegsystemreferanse}'
    )

    headers = {
        "Accept": "application/json",
        "X-Client": "Masteroppgave-vegnett"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    
    data = response.json()
    segmenter = data.get('vegnettsrutesegmenter', [])

    startveg = segmenter[0]

    df = pd.DataFrame(fartsgrenser.to_records()).query("typeVeg == 'Enkel bilveg'")
    i = 0
    retning = 'MED'
    # Finding the correct direction of the road
    if 'sluttnode' in startveg:
        retning = 'MED'
    if 'startnode' in startveg:
        retning = 'MOT'
    
    total_vegsegment_wgs84=[]
    total_vegsegment_utm = []
    for veglenke in segmenter:
        if (
                veglenke['typeVeg_sosi'] == 'enkelBilveg' 
            ):
                fartsgrense_row = df[df['veglenkesekvensid'] == veglenke['veglenkesekvensid']]['Fartsgrense']
                fartsgrense = float(fartsgrense_row.iloc[0]) if not fartsgrense_row.empty else None
                converted = linestring_to_coordinates(veglenke['geometri']['wkt'])
                
                if retning == 'MOT':
                    converted.reverse()
                    
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
    sistesegment = segmenter[-1]
    geojson_feature_utm, geojson_feature_wgs = add_last_segment(sistesegment['veglenkesekvensid'], sistesegment['veglenkenummer'], vegsystemreferanse, df, retning, i)
    total_vegsegment_utm.append(geojson_feature_utm)
    total_vegsegment_wgs84.append(geojson_feature_wgs)
    connected_utm = connect_road(total_vegsegment_utm)
    connected_wgs = connect_road(total_vegsegment_wgs84)
    return connected_utm, connected_wgs

# eksempel url
# https://nvdbapiles-v3.utv.atlas.vegvesen.no/beta/vegnett/rute?start=131363.978346842,6943393.145821838&slutt=136419.9895830073,6941862.632362077&maks_avstand=1000&omkrets=10&konnekteringslenker=true&detaljerte_lenker=true&behold_trafikantgruppe=false&pretty=true&kortform=false&vegsystemreferanse=EV136
#test 
# https://nvdbapiles-v3.utv.atlas.vegvesen.no/vegnett?detaljnivå=Kjørefelt&vegsystemreferanse=EV136&segmentstart=131363.978346842,6943393.145821838&segmentslutt=136419.9895830073,6941862.632362077


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
