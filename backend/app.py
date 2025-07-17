import json
from flask import Flask, Response, jsonify, request, stream_with_context
from computebaner import  get_gnss, getDayNumber, runData_check_sight
from computeDOP import best, find_dop_on_point
from flask_cors import CORS
from datetime import datetime
from romsdalenRoad import calculate_travel_time, connect_total_road_segments, get_road_api
import rasterio

from time import perf_counter_ns
import multiprocessing
import functools
import concurrent.futures
import pickle
import numpy as np
from pyproj import Transformer
from computeDOP import create_observers

distance = None
points = None

app = Flask(__name__)
CORS(app, resources={r"/satellites": {"origins": "http://localhost:3000"}}, supports_credentials=True)
CORS(app, resources={r"/dopvalues": {"origins": "http://localhost:3000"}})

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
    epoch = data.get('epoch')
    frequency = int(data.get('epochFrequency'))
    point = data.get('point')
    #print(f'point: {point}')
    
    is_processing = True
    start = perf_counter_ns()
    list, df,elevation_cutoffs, obs_cartesian = runData_check_sight(gnss, elevation_angle, time, epoch,frequency, point) 
    print("timing runData_check_sight (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
    elevation_strings = [str(elevation) for elevation in elevation_cutoffs]
    DOPvalues = best(df, obs_cartesian)

    is_processing = False
    print("timing satellites (ms):\t", round((perf_counter_ns()-start_satellites)/1_000_000,3))
    if not is_processing:
        response = jsonify({'message': 'Data processed successfully', 'data': list, 'DOP': DOPvalues,   'elevation_cutoffs': elevation_strings})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")  
        return response, 200
    else:
        response = jsonify({"data": "Data is not ready"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")  
        return response, 202


from flask import Flask, request, jsonify
import traceback

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
        vegReferanse = request.json.get('vegReferanse')
        startPoint = request.json.get('startPoint')
        endPoint = request.json.get('endPoint')
        distance = request.json.get('distance')

        # Validate input
        if not vegReferanse or not startPoint or not endPoint or not distance:
            response = jsonify({'error': 'Missing input parameters.', 'message': 'Please provide startPoint, endPoint, distance and vegReferanse.'})
            response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
            return response, 400

        # Get road data
        segmenter, df, vegsystemreferanse= get_road_api(startPoint, endPoint, vegReferanse)
        start = perf_counter_ns()
        road_utm, road_wgs = connect_total_road_segments(segmenter,df, vegsystemreferanse, startPoint, endPoint)
        print("timing connect_total_road_segments (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))

        # Calculate points
        start = perf_counter_ns()
        points = calculate_travel_time(road_utm, float(distance))
        print('COUNT',len(points))
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
    

def prin(points):
    for i in points:
        yield int(i)

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
    dop_list = []
    #PDOP_list = []
    start = perf_counter_ns()
    daynumber = getDayNumber(time)
    print("timing getDaynumber_dopValues (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
    gnss_mapping = get_gnss(daynumber, time.year)
    total_steps = len(points) + 1
    
    """
    def generate():
        start = perf_counter_ns()
        find_dop_on_point_partial = functools.partial(find_dop_on_point,
                                                        gnss_mapping=gnss_mapping, time=time, elevation_angle=elevation_angle)
        def inner_generate(points):
            print("Entered INNER")
            with rasterio.open("data/merged_raster.tif") as src:
                dem_data = src.read(1)
                print(gnss_mapping, time, elevation_angle, points, dem_data, src, type(dem_data), type(src))
                print("ENTER INNER")
                for step, point in enumerate(points, start=1):
                    print(step)
                    #start = perf_counter_ns()
                    dop_point = find_dop_on_point_partial(point=point, step=step, dem_data=dem_data, src=src)
                    #print("timing find_dop_on_point (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
                    dop_list.append(dop_point)
                    #PDOP_list.append(dop_point[0][1])
                    yield f"{int((step / total_steps) * 100)}\n\n"
        
        

        print("BEFORE MULTI PROCESS")
        #args = (dem_data, src, gnss_mapping, gnss, time, points[1:], elevation_angle, steps)
        items = [1,2,3]
        if __name__ == '__main__':
            with multiprocessing.Pool(processes=max(1,multiprocessing.cpu_count()-1)) as pool: #multiprocessing.Pool(processes=max(1,multiprocessing.cpu_count()-1), maxtasksperchild=1) as pool:
                print(pool)
                for result_generator in pool.imap(prin, items): # find_dop_on_point_partial, points
                    yield from result_generator
        #p = multiprocessing.Process(target=inner_generate, args=args)
        #p.start()

        # Når prosessen er ferdig
        print("timing generate (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
        print("timing dopValues (ms):\t", round((perf_counter_ns()-start_dopValues)/1_000_000,3))
        yield f"{json.dumps(dop_list)}\n\n"
    """
    
    def generate():
        start = perf_counter_ns()
        with rasterio.open("data/merged_raster.tif") as src:
            dem_data = src.read(1)

            observers, observers_cartesian = create_observers(src, dem_data, points)
            
            E_lower = src.bounds[0]
            N_upper = src.bounds[3]
            print(dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper)
            pickle_data = [dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper]
            with open('multiprocessing_test.pkl', 'wb') as out:
                idx = 0
                for d in pickle_data:
                    print(idx)
                    idx += 1
                    pickle.dump(d, out ,pickle.HIGHEST_PROTOCOL)
            input()
            
            for step in range(1,len(points)):
                #start = perf_counter_ns()
                dop_point = find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, step, E_lower, N_upper)
                #print("timing find_dop_on_point (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
                dop_list.append(dop_point)
                #PDOP_list.append(dop_point[0][1])

                yield f"{int((step / total_steps) * 100)}\n\n"

        # Når prosessen er ferdig
        print("timing generate (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
        print("timing dopValues (ms):\t", round((perf_counter_ns()-start_dopValues)/1_000_000,3))
        yield f"{json.dumps(dop_list)}\n\n"

    response = Response(stream_with_context(generate()), content_type='text/event-stream')
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
    return response


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True, threaded=False, processes=10)

