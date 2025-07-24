from datetime import timedelta, datetime
import pandas as pd
import numpy as np
from pyproj import Transformer
from computebaner import satellites_visible_from_point
from common_variables import phi,lam
import rasterio

from time import perf_counter_ns

def R2(theta: float) -> np.ndarray[float]:
    """
    Rotation matrix about Y-axis (used in coordinate transformation).
    """
    return np.array([[np.cos(theta),0,-np.sin(theta)],
                    [       0,      1,      0       ],
                    [np.sin(theta) ,0,np.cos(theta)]])

def R3(theta: float) -> np.ndarray[float]:
    """
    Rotation matrix about Z-axis.
    """
    return np.array([[np.cos(theta),np.sin(theta),0],
                    [-np.sin(theta),np.cos(theta),0],
                    [       0,            0,      1]])

def P2() -> np.ndarray[int]:
    """
    Mirror/reflection matrix"""
    return np.array([[1, 0, 0],
                     [0,-1, 0],
                     [0, 0, 1]])

def geometric_range(sat_pos: list[float], rec_pos: list[float]) -> float:
    """
    Calculates Euclidean distance between satellite and receiver
    """
    return np.sqrt((sat_pos[0] - rec_pos[0])**2 +
                   (sat_pos[1] - rec_pos[1])**2 +
                   (sat_pos[2] - rec_pos[2])**2)

def DOPvalues(satellites: list[list], receiver_pos: list[float]) -> list[float]:
    """
    Calculates DOP from a location (receiver_pos) and list of satellites with line of sight (LOS),
    given their respective ECEF coordinates.
    """
    LOS_sat_cnt = len(satellites)
    if LOS_sat_cnt < 4:
        # Not enough satellites
        GDOP = PDOP = TDOP = HDOP = VDOP = 0.0
        return GDOP,PDOP,TDOP,HDOP,VDOP
    
    # Construct A matrix for least-squares
    A = np.zeros((LOS_sat_cnt, 4))
    Qxx = np.zeros((4, 4))
    i = 0
    for satellite in satellites:
        #print(satellite) #xyz
        rho_i = geometric_range([satellite[0], satellite[1], satellite[2]], receiver_pos)

        A[i][0] = -((satellite[0] - receiver_pos[0]) / rho_i)
        A[i][1] = -((satellite[1] - receiver_pos[1]) / rho_i)
        A[i][2] = -((satellite[2] - receiver_pos[2] ) / rho_i)
        A[i][3] = -1
        i += 1
    # Compute covariance matrix Qxx
    Qxx = np.linalg.inv(A.T @ A)
    Qxx_local = Qxx[0:3,0:3]
    # Transform to local ENU coordinates
    T = P2()@R2(phi-np.pi/2)@R3(lam-np.pi)
    Qxx_local = T@Qxx_local@T.T
    # Calculate DOP metrics
    GDOP = np.sqrt(Qxx[0][0] + Qxx[1][1] + Qxx[2][2] + Qxx[3][3])
    PDOP = np.sqrt(Qxx[0][0] + Qxx[1][1] + Qxx[2][2])
    TDOP = np.sqrt(Qxx[3][3]) 
    HDOP = np.sqrt(Qxx_local[0][0]+Qxx_local[1][1])
    VDOP = np.sqrt(Qxx_local[2][2])
    return GDOP,PDOP,TDOP,HDOP,VDOP

def DOP_in_epoch(visible_sats_pos_for_timesteps: list[list[float]], receiver_pos: list[float]) -> list[float]:
    """
    Computes DOP values over a list of time steps at a point "receiver_pos".
    """
    DOP_at_intervals = []
    for satellites_positions in visible_sats_pos_for_timesteps:
        if len(satellites_positions) >= 4:
            DOP_at_intervals.append( DOPvalues(satellites_positions, receiver_pos) )
        else:
            DOP_at_intervals.append( [0.0, 0.0, 0.0, 0.0, 0.0] )
    return DOP_at_intervals


def find_dop_on_point(dem_data: np.ndarray[float], gnss_mapping: dict[str, pd.DataFrame], gnss: list[str], time: datetime, point: dict, observer: np.ndarray[float], obs_cartesian: np.ndarray[float], elevation_angle: str, E_lower: float, N_upper: float) -> list[list[float]]:
    """
    Computes DOP at a specific point in time and location (point).
    """
    # Offset time by current point's offset
    timeNow = time + timedelta(seconds=point['properties']['time_from_start'])

    #start = perf_counter_ns()
    visible_satellites = satellites_visible_from_point(gnss_mapping, gnss, timeNow, obs_cartesian, observer, elevation_angle, dem_data,E_lower, N_upper)
    #print("timing satellites_visible_from_point (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
    
    if len(visible_satellites) < 4: return [0.0, 0.0, 0.0, 0.0, 0.0]
    return DOPvalues(visible_satellites, obs_cartesian)


