
from dataclasses import dataclass
import multiprocessing
from time import perf_counter_ns
import config
from computeDOP import find_dop_on_point
import json
from pyproj import Transformer
from datetime import datetime
from computebaner import getDayNumber, get_gnss, Cartesian, get_satellite_positions, visual_satellites_data, check_satellite_sight_2
import rasterio
import numpy as np
import pandas as pd
from itertools import repeat
from typing import Iterator

"""
Provides a multiprocess alternative to for
"find_dop_on_point" and "data_from_epoch" in app.py.


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



def get_dopvalues(step: int) -> list[list[float]]:
    """
    Concurrency wrapper for "find_dop_on_point" function.
    """
    return find_dop_on_point(ROD.dem_data, ROD.gnss_mapping, ROD.gnss, ROD.time, ROD.points[step], ROD.observers[step], ROD.observers_cartesian[step], ROD.elevation_angle, ROD.E_lower, ROD.N_upper)


def get_dopvalues_concurrently(data: tuple[ np.ndarray[float],
                                           dict[str, pd.DataFrame],
                                           list[str], datetime,
                                           list[dict],
                                           list[np.ndarray[float]],
                                           list[np.ndarray[float]],
                                           str,
                                           float,
                                           float
                                           ] ) -> Iterator[str]:
    """
    Calculates DOP for every point.
    All input data is packed inside a "data" tuple. This is done to 
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
        steps = [i for i in range(len(ROD.points))]
        total_steps = len(ROD.points)+1
        result_generator = pool.imap(get_dopvalues, steps, chunksize=1)
        for r in result_generator:
            dop_list.append([r]) # Frontend expects "double-wrapped lists"
            step += 1
            yield f"{int(((step+1) / total_steps) * 100)}\n\n"
    #dt = (perf_counter_ns()-start)/10**9/60
    #print(f'{int(dt)}:{int((dt-int(dt))*60)}')
    print("timing generate (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
    yield f"{json.dumps(dop_list)}\n\n"




def data_from_timestep(step: int) -> list[pd.DataFrame]:
    """
    Concurrency wrapper for inner-loop for "data_from_epoch" function.
    Is similar to innerloop of "computerbaner.py->data_from_epoch" function.
    """
    time = pd.to_datetime(ROS.start_time)+ pd.Timedelta(minutes=step*ROS.frequency)
    df_list = []
    for gnss in ROS.gnss_list:

        positions = get_satellite_positions(ROS.gnss_mapping[gnss], gnss,time)
        data = visual_satellites_data(positions, ROS.observation_cartesian, ROS.observation_end, ROS.observation_lnglat, ROS.elevation_mask, ROS.dem_data, ROS.E_lower, ROS.N_upper)
    
        if data.empty: continue
        df_list.append(data)

    return df_list

def data_from_epoch(gnss: list[str],
                    elevationstring: str,
                    t: datetime,
                    epoch: int,
                    freq: int,
                    observation_lng_lat: list[float]
                    ) -> tuple[ list[list[dict]],
                                list[str],
                                list[list[pd.DataFrame]],
                                list[float] ]:
    """
    A wrapper function for getting DOP and satellite count on a point during a specified epoch.
    Returns "visible_sats_data_for_timesteps" which is data regarding each satellite visual from that point.
    This data is structured in a two layer list: top layer is timesteps, second layer is gnss.
    "visible_sats_pos_for_timesteps" and "observation_cartesian" is returned to calculate DOP outside
    this function.
    Benchmarked as 10-15% faster on 3 timesteps, and 40-50% faster on 61 timesteps, compared to single process.
    Tests performed 16GB RAM and Intel® Core™ i5-10310U × 8.
    """
    transformerToEN = Transformer.from_crs("EPSG:4326","EPSG:25833", always_xy=True)
    observation_EN = transformerToEN.transform(observation_lng_lat[0], observation_lng_lat[1])
    given_date = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%f")
    start = perf_counter_ns()
    daynumber = getDayNumber(given_date)
    print("timing getDaynumber_runData_check_sight (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
    
    with rasterio.open("data/merged_raster.tif") as src:
        dem_data_temp = src.read(1)
        observer_height = dem_data_temp[src.index(observation_EN[0], observation_EN[1])]
        start = perf_counter_ns()

        @dataclass(frozen=True)
        class Read_Only_Sat:
            start_time = t
            frequency = freq
            gnss_list = gnss
            gnss_mapping = get_gnss(daynumber,given_date.year)
            observation_cartesian = Cartesian(observation_lng_lat[1]* np.pi/180, observation_lng_lat[0]* np.pi/180, observer_height)
            observation_end = [observation_EN[0], observation_EN[1], observer_height]
            observation_lnglat = observation_lng_lat
            elevation_mask = float(elevationstring)
            dem_data = dem_data_temp
            E_lower = src.bounds[0]
            N_upper = src.bounds[3]
        global ROS
        ROS = Read_Only_Sat()

        DFs_in_2d_list = None
        with multiprocessing.Pool(processes=config.PROCESSES_COUNT_SATELLITE) as pool:
            calc_count = epoch * int((60/ROS.frequency))+1
            steps = [i for i in range(calc_count)]
            DFs_in_2d_list = pool.map(data_from_timestep, steps, chunksize=1)
            
        visible_sats_data_for_timesteps = [[df.to_dict() for df in timestep] for timestep in DFs_in_2d_list]
        
        # Extract positions of every satellites for each timestep
        visible_sats_pos_for_timesteps = []
        for timestep in DFs_in_2d_list:
            sats_pos_dfs = []
            for gnss_df in timestep:
                sats_pos_dfs.extend(gnss_df[['X', 'Y', 'Z']].values.tolist())
            visible_sats_pos_for_timesteps.append(sats_pos_dfs)
            
        elevation_cutoffs = list(map(check_satellite_sight_2, repeat(ROS.observation_end), repeat(ROS.dem_data), repeat(src), repeat(5000), repeat(ROS.elevation_mask), range(0,360,1)))
        elevation_cutoffs = [str(elevation) for elevation in elevation_cutoffs]
        return visible_sats_data_for_timesteps, elevation_cutoffs, visible_sats_pos_for_timesteps, ROS.observation_cartesian