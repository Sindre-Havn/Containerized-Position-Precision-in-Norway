import json
from flask import Flask, Response, jsonify, request, stream_with_context
from visible_satellites import get_gnss, getDayNumber, data_from_epoch, create_observers
from compute_DOP import DOP_in_epoch, find_dop_on_point
from flask_cors import CORS
from datetime import datetime
from roads import extract_points_at_interval, connect_total_road_segments, get_road_and_speedlimits, get_road
import rasterio
import config
import concurrency
import os
import traceback
from merge_rasters import get_merged_raster_near_points

from time import perf_counter_ns

app = Flask(__name__)
CORS(app, resources={r"/satellites": {"origins": "http://localhost:3000"}}, supports_credentials=True)
CORS(app, resources={r"/dopvalues" : {"origins": "http://localhost:3000"}})


@app.route('/road', methods=['POST', 'OPTIONS'])
def road():
    if request.method == 'OPTIONS':
        # Handle the preflight request (CORS preflight)
        response = jsonify({'status': 'Preflight request passed'})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response, 200

    try:
        start_road = perf_counter_ns()
        veg_referanse = request.json.get('vegReferanse') # Not needed, depreciated
        startpoint = request.json.get('startPoint')
        endpoint = request.json.get('endPoint')
        distance = request.json.get('distance')

        # Validate input
        if not startpoint or not endpoint or not distance:
            response = jsonify({'error': 'Missing input parameters.', 'message': 'Please provide startPoint, endPoint, distance and vegReferanse.'})
            response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
            return response, 400

        # Get road data
        if config.USE_CORRECT_SPEEDLIMITS:
            road_segments, speedlimits = get_road_and_speedlimits(startpoint, endpoint)
        else:
            road_segments, speedlimits = get_road(startpoint, endpoint), []
        start = perf_counter_ns()
        road_utm, road_wgs = connect_total_road_segments(road_segments, startpoint, speedlimits) # startpoint should be road startpoint, not pin startpoint.
        print("timing connect_total_road_segments (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))

        # Calculate points
        start = perf_counter_ns()
        points = extract_points_at_interval(road_utm, float(distance))

        # The following lines regarding deleting/creating raster must be refactored.
        # It does not support multiple users requesting road routes for different
        # areas of the country.
        # Delete merged raster if exists

        print("timing calculate_travel_time (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))

        response = jsonify({'message': 'Data processed successfully', 'road': road_wgs, 'points': points})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        print("timing road (ms):\t", round((perf_counter_ns()-start_road)/1_000_000,3))
        return response, 200

    except IndexError as e:
        response = jsonify({
            'error': 'No road data found for the given input.',
            'details': str(e),
            'message': 'The road couldn’t be found. Please check all the input parameters and be more specific with the start and end markers.'
        })
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        return response, 400

    except Exception as e:
        # Log full error in backend
        print(traceback.format_exc())
        response = jsonify({
            'error': 'An unexpected error occurred.',
            'details': str(e),
            'message': 'An unexpected error occurred. Please try again later.'
        })
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        return response, 500
    

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

    start_dopValues = perf_counter_ns()
    time = datetime.fromisoformat(time_str)
    print('time', time)
    total_steps = len(points)+1
    start = perf_counter_ns()
    print("timing getDaynumber_dopValues (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
    
    daynumber = getDayNumber(time)
    gnss_mapping = get_gnss(daynumber, time.year)

    merged_raster = get_merged_raster_near_points(points)

    # Prepare data
    dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None
    with rasterio.open(merged_raster) as src:
            dem_data = src.read(1)

            observers, observers_cartesian = create_observers(src, dem_data, points)
            
            E_lower = src.bounds[0]
            N_upper = src.bounds[3]
    data = (dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper)
    
    dop_list = []

    def generate():
        start = perf_counter_ns()
        for step in range(len(points)):
            #start = perf_counter_ns()
            dop_point = find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper)
            #print("timing find_dop_on_point (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
            dop_list.append([dop_point]) # Frontend expects "double-wrapped dop_point lists"
            print(f"{int(((1+step) / total_steps) * 100)}\n\n")
            yield f"{int(((1+step) / total_steps) * 100)}\n\n"

        # Når prosessen er ferdig
        print("timing generate (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
        print("timing dopValues (ms):\t", round((perf_counter_ns()-start_dopValues)/1_000_000,3))
        print(f"{json.dumps(dop_list)}\n\n")
        yield f"{json.dumps(dop_list)}\n\n"
    
    generator = None
    if config.USE_CONCURRENCY_FOR_DOPVALUES:
        generator = concurrency.get_dopvalues_concurrently(data)
    else:
        generator = generate()
    response = Response(stream_with_context(generator), content_type='text/event-stream')
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
    return response


@app.route('/satellites', methods=['POST', 'OPTIONS'])
def satellites():
    start_satellites = perf_counter_ns()
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
    epoch = int(data.get('epoch'))
    frequency = int(data.get('epochFrequency'))
    point = data.get('point')

    is_processing = True
    start = perf_counter_ns()
    visible_sats_data_for_timesteps, DOPvalues, elevation_cutoffs = [], [], []
    if config.USE_CONCURRENCY_FOR_SATELLITE:
        visible_sats_data_for_timesteps, elevation_cutoffs, visible_sats_pos_for_timesteps, observation_cartesian = concurrency.data_from_epoch(gnss, elevation_angle, time, epoch,frequency, point)
    else:
        visible_sats_data_for_timesteps, elevation_cutoffs, visible_sats_pos_for_timesteps, observation_cartesian = data_from_epoch(gnss, elevation_angle, time, epoch,frequency, point)
    print("timing runData_check_sight (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
    DOPvalues = DOP_in_epoch(visible_sats_pos_for_timesteps, observation_cartesian)
    is_processing = False
    print("timing satellites (ms):\t", round((perf_counter_ns()-start_satellites)/1_000_000,3))
    if not is_processing:
        response = jsonify({'message': 'Data processed successfully', 'data': visible_sats_data_for_timesteps, 'DOP': DOPvalues, 'elevation_cutoffs': elevation_cutoffs})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")  
        return response, 200
    else:
        response = jsonify({"data": "Data is not ready"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")  
        return response, 202
    

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True, threaded=False)

