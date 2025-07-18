
from dataclasses import dataclass
import multiprocessing
from time import perf_counter_ns
import config
from computeDOP import find_dop_on_point
import json

from pyproj import Transformer
from datetime import datetime, timedelta
from computebaner import getDayNumber, get_gnss, Cartesian, get_satellite_positions, visualCheck_3, check_satellite_sight_2
import rasterio
import numpy as np
import pandas as pd
from itertools import repeat, chain

"""
Provides a multiprocess alternative to for
"find_dop_on_point" and "runData_check_sight" in app.py.


This module is tested using 7 processes on a 8 core CPU, but only resulted in
a 2-3x runtime speed up compared to single process.
The "Read_Only" dataclass is shared (not duplicated) among the child processes.
It is though the slowdown comes from not bypass the GIL.
Using "Manager" from multiprocessing also is little help as it acts as
a proxy server and using it to distribute large data trough "pipes" are slow and
ends up duplicating RAM usage.
To get true shared  memory (without GIL slowdown) the
multiprocessing.sharedctypes module seems like the only options,
but this may only be used for values and arrays of primitive types.
(No dictionary, dataframe, etc)
"""



def get_dopvalues(step):
    #dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper = RO.data
    #return find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    return find_dop_on_point(ROD.dem_data, ROD.gnss_mapping, ROD.gnss, ROD.time, ROD.points[step], ROD.observers[step], ROD.observers_cartesian[step], ROD.elevation_angle, ROD.E_lower, ROD.N_upper, step)

def get_dopvalues_concurrently(data):
    """
    Benchmarked as 2-3x faster at 105 road points compared to single process.
    Tests performed 16GB RAM and Intel® Core™ i5-10310U × 8.
    """
    start = perf_counter_ns()
    @dataclass(frozen=True)
    class Read_Only_Dop:
        dem_data = data[0]
        gnss_mapping = data[1]
        gnss = data[2]
        time = data[3]
        points = data[4]
        observers = data[5]
        observers_cartesian = data[6]
        elevation_angle = data[7]
        E_lower = data[8]
        N_upper = data[9]
    global ROD
    ROD = Read_Only_Dop()
    step = 0
    dop_list = []
    with multiprocessing.Pool(processes=config.PROCESSES_COUNT_DOPVALUES) as pool:
        steps = [i for i in range(1,105)]
        total_steps = len(steps)-1
        result_generator = pool.imap(get_dopvalues, steps, chunksize=1)
        for r in result_generator:
            dop_list.append(r)
            step += 1
            yield f"{int((step / total_steps) * 100)}\n\n"
    #dt = (perf_counter_ns()-start)/10**9/60
    #print(f'{int(dt)}:{int((dt-int(dt))*60)}')
    print("timing generate (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
    yield f"{json.dumps(dop_list)}\n\n"






def find_visual_satellites(i):
    time2 = pd.to_datetime(ROS.t)+ pd.Timedelta(minutes=i*ROS.frequency)
        
    LGDF_df = []
    for gnss in ROS.gnss_list:

        positions = get_satellite_positions(ROS.gnss_mapping[gnss],gnss,time2)
    
        data = visualCheck_3(positions, ROS.observation_cartesian, ROS.observation_end, ROS.observation_lngLat, ROS.elevation_mask, ROS.dem_data, ROS.E_lower, ROS.N_upper)
        
        if not data.empty:
            LGDF_df += [data]
    return LGDF_df

def runData_check_sight_concurrently(gnss, elevationstring, time, epoch, freq, observation_lng_lat):
    """
    Benchmarked as 10-15% faster on 3 epochs, and 40-50% faster on 61 epochs, compared to single process.
    Tests performed 16GB RAM and Intel® Core™ i5-10310U × 8.
    """
    transformerToEN = Transformer.from_crs("EPSG:4326","EPSG:25833", always_xy=True)
    observation_EN = transformerToEN.transform(observation_lng_lat[0], observation_lng_lat[1])
    given_date = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f")
    start = perf_counter_ns()
    daynumber = getDayNumber(given_date)
    print("timing getDaynumber_runData_check_sight (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
    
    with rasterio.open("data/merged_raster.tif") as src:
        dem_data_temp = src.read(1)
        observer_height = dem_data_temp[src.index(observation_EN[0], observation_EN[1])]
        start = perf_counter_ns()
        @dataclass(frozen=True)
        class Read_Only_Sat:
            t = time
            frequency = freq
            gnss_list = gnss
            gnss_mapping = get_gnss(daynumber,given_date.year)
            observation_cartesian = Cartesian(observation_lng_lat[1]* np.pi/180, observation_lng_lat[0]* np.pi/180, observer_height)
            observation_end = [observation_EN[0], observation_EN[1], observer_height]
            observation_lngLat = observation_lng_lat
            elevation_mask = float(elevationstring)
            dem_data = dem_data_temp
            E_lower = src.bounds[0]
            N_upper = src.bounds[3]
        global ROS
        ROS = Read_Only_Sat()
        #print('finds visual satellites')
        LGDF_DFs = None
        with multiprocessing.Pool(processes=config.PROCESSES_COUNT_SATELLITE) as pool:
            calc_count = int(epoch)* int((60/ROS.frequency))+1
            steps = [i for i in range(calc_count)]
            LGDF_DFs = pool.map(find_visual_satellites, steps, chunksize=1)
        final_listdf = LGDF_DFs
        #print('final_listdf', type(final_listdf), type(final_listdf[0]), len(final_listdf), len(final_listdf[0]))
        #print('LGDF_DFs', type(LGDF_DFs), type(LGDF_DFs[0]), len(LGDF_DFs), len(LGDF_DFs[0]))
        #final_list = [df.to_dict() for df in final_listdf]
        final_list = [[df.to_dict()] for epoch in LGDF_DFs for df in epoch]
        elevationCutoffs = list(map(check_satellite_sight_2, repeat(ROS.observation_end), repeat(ROS.dem_data), repeat(src), repeat(5000), repeat(ROS.elevation_mask), range(0,360,1)))
        return final_list, final_listdf, elevationCutoffs, ROS.observation_cartesian


if __name__ == '__main__':
    """
    Expects a "multiprocessing_dop_testdata.pkl" file built with expected input parameters of find_dop_on_point, for all steps along road: 

    pickle_data = [dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper]
    with open('multiprocessing_test.pkl', 'wb') as out:
        for d in pickle_data:
            pickle.dump(d, out, pickle.HIGHEST_PROTOCOL)
    """
    import pickle
    dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_dop_testdata.pkl', 'rb') as inp:
        dem_data = pickle.load(inp)
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        points = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    data = (dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper)
    
    for r in get_dopvalues_concurrently(data):
        print(r)