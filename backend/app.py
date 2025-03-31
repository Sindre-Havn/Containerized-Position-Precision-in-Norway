import json
from flask import Flask, Response, jsonify, request, stream_with_context
from computebaner import  get_gnss, getDayNumber, runData_check_sight
from computeDOP import best, find_dop_on_point
from flask_cors import CORS
from datetime import datetime
from romsdalenRoad import calculate_travel_time, get_road_api
import rasterio


distance = None
points = None

app = Flask(__name__)
CORS(app, resources={r"/satellites": {"origins": "http://localhost:3000"}}, supports_credentials=True)
CORS(app, resources={r"/dopvalues": {"origins": "http://localhost:3000"}})

@app.route('/satellites', methods=['POST', 'OPTIONS'])
def satellites():
    if request.method == 'OPTIONS':
        # Handle the preflight request with necessary headers
        response = jsonify({'status': 'Preflight request passed'})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response, 200

    # Main POST request handling
    data = request.json  
    time = data.get('time').strip('Z')
    elevation_angle = data.get('elevationAngle')
    gnss = data.get('GNSS')
    epoch = data.get('epoch')
    point = data.get('point')
    #print(f'point: {point}')
    
    is_processing = True
    list, df,elevation_cutoffs, obs_cartesian = runData_check_sight(gnss, elevation_angle, time, epoch, point) 
    elevation_strings = [str(elevation) for elevation in elevation_cutoffs]
    DOPvalues = best(df, obs_cartesian)

    is_processing = False
    
    if not is_processing:
        response = jsonify({'message': 'Data processed successfully', 'data': list, 'DOP': DOPvalues,   'elevation_cutoffs': elevation_strings})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")  
        return response, 200
    else:
        response = jsonify({"data": "Data is not ready"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")  
        return response, 202

@app.route('/road', methods=['POST','OPTIONS'])
def road():
    if request.method == 'OPTIONS':
        # Handle the preflight request with necessary headers
        response = jsonify({'status': 'Preflight request passed'})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response, 200


    is_processing = True
    vegReferanse = request.json.get('vegReferanse')
    startPoint = request.json.get('startPoint')
    endPoint = request.json.get('endPoint')
    #(request.json)
    distance = request.json.get('distance')
    road_utm,road_wgs =  get_road_api(startPoint, endPoint,vegReferanse)
    points = calculate_travel_time(road_utm, float(distance))
    is_processing = False
    
    if not is_processing:
        response = jsonify({'message': 'Data processed successfully', 'road': road_wgs, 'points': points})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")  
        return response, 200
    else:
        response = jsonify({"data": "Data is not ready"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")  
        return response, 202
    
@app.route('/dopvalues', methods=['POST', 'OPTIONS'])
def dopValues():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'Preflight request passed'})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Cache-Control")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        return response, 200

    # Main POST request handling
    try:
        data = request.get_json()
        time_str = data.get('time').strip('Z')
        elevation_angle = data.get('elevationAngle')
        gnss = data.get('GNSS')
        points = data.get('points')
    except Exception as e:
        return jsonify({"error": f"Invalid data format: {e}"}), 400

    time = datetime.fromisoformat(time_str)

    dop_list = []
    daynumber = getDayNumber(time)
    gnss_mapping = get_gnss(daynumber, time.year)
    total_steps = len(points) + 1

    def generate():
        with rasterio.open("data/merged_raster_romsdalen_10.tif") as src:
            dem_data = src.read(1)

            for step, point in enumerate(points, start=1):
                dop_point = find_dop_on_point(dem_data, src, gnss_mapping, gnss, time, point, elevation_angle, step)
                dop_list.append(dop_point)

                yield f"{int((step / total_steps) * 100)}\n\n"

        # Når prosessen er ferdig
        yield f"{json.dumps(dop_list)}\n\n"

    response = Response(stream_with_context(generate()), content_type='text/event-stream')
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
    return response


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)