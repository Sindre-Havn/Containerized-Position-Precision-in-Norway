

import json
from flask import Flask, Response, jsonify, request
from computebaner import  runData, satellites_at_point
from computeDOP import find_dop_along_road
from flask_cors import CORS
from datetime import datetime, time, timedelta
from romsdalenRoad import calculate_travel_time, get_road_api

# Set up basic configuration for logging
#logging.basicConfig(level=logging.INFO)

distance = None
points = None

app = Flask(__name__)
CORS(app, resources={r"/satellites": {"origins": "http://localhost:3000"}}, supports_credentials=True)

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
    list, df, elevation_cutoffs = runData(gnss, elevation_angle, time, epoch, point) 
    elevation_strings = [str(elevation) for elevation in elevation_cutoffs]
    #DOPvalues = best(df)

    is_processing = False
    
    if not is_processing:
        response = jsonify({'message': 'Data processed successfully', 'data': list, 'elevation_cutoffs': elevation_strings})
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
        # Handle the preflight request with necessary headers
        response = jsonify({'status': 'Preflight request passed'})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response, 200

    # Main POST request handling
    data = request.json  
    time1 = data.get('time').strip('Z')
    elevation_angle = data.get('elevationAngle')
    gnss = data.get('GNSS')
    points = data.get('points')
    
    is_processing = True
    import time
    start = time.time()
    timeNow = datetime.strptime(time1, "%Y-%m-%dT%H:%M:%S.%f")
    dopvalues = find_dop_along_road(points, timeNow, gnss, int(elevation_angle))
    end = time.time()
    print(f"Kjøretid dop: {end-start} sekunder")
    is_processing = False
    
    if not is_processing:
        response = jsonify({'message': 'Data processed successfully','DOP': dopvalues})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")  
        return response, 200
    else:
        response = jsonify({"data": "Data is not ready"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")  
        return response, 202


@app.route('/submit-filter', methods=['POST'])
def submit_time():
    data = request.json  
    start_time = data.get('startTime')
    end_time = data.get('endTime')
    elevation_angle = data.get('elevationAngle')
    gnss = data.get('GNSS')
    stored_data = runData(gnss, elevation_angle, start_time, end_time)  # Long-running function
    return jsonify({'message': 'Data received successfully'}), 200


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)