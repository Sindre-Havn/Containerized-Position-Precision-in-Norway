from datetime import timedelta
import numpy as np
from pyproj import Transformer
from computebaner import Cartesian, satellites_visible_from_point
from common_variables import phi,lam
import rasterio

from time import perf_counter_ns

# Set up coordinate transformers between UTM and WGS84
transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)
transformerToEN = Transformer.from_crs("EPSG:4326","EPSG:25833", always_xy=True)

def R2(theta):
    """
    Rotation matrix about Y-axis (used in coordinate transformation).
    """
    return np.array([[np.cos(theta),0,-np.sin(theta)],
                    [0,            1,           0],
                    [np.sin(theta),0,np.cos(theta)]])

def R3(theta):
    """
    Rotation matrix about Z-axis.
    """
    return np.array([[np.cos(theta),np.sin(theta),0],
                    [-np.sin(theta),np.cos(theta),0],
                    [0,             0,             1]])

def P2():
    """
    Mirror/reflection matrix"""
    return np.array([[1,0,0],[0,-1,0],[0,0,1]])

def geometric_range(sat_pos, rec_pos):
    """
    Calculates Euclidean distance between satellite and receiver
    """
    return np.sqrt((sat_pos[0] - rec_pos[0])**2 +
                   (sat_pos[1] - rec_pos[1])**2 +
                   (sat_pos[2] - rec_pos[2])**2)

def DOPvalues(satellites: list[list], receiver_pos: list[float]) -> list[float]:
    """
    Calculates DOP from a location (point) given a list of satellites with line of sight (LOS).
    """
    LOS_sat_cnt = len(satellites)
    if LOS_sat_cnt < 4:
        # Not enough satellites
        GDOP = PDOP = TDOP = HDOP = VDOP = 0
        return GDOP,PDOP,TDOP,HDOP,VDOP
    
    # Construct A matrix for least-squares
    A = np.zeros((LOS_sat_cnt, 4))
    Qxx = np.zeros((4, 4))
    i = 0
    for satellite in satellites:
        rho_i = geometric_range([satellite[2], satellite[3], satellite[4]], receiver_pos)

        A[i][0] = -((satellite[2] - receiver_pos[0]) / rho_i)
        A[i][1] = -((satellite[3] - receiver_pos[1]) / rho_i)
        A[i][2] = -((satellite[4] - receiver_pos[2] ) / rho_i)
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


def DOP_at_epochs(satellites_at_epochs, receiver_pos: list[float]) -> list[float]:
    """
    Computes DOP values over a list of time steps at a point "receiver_pos".
    """
    DOP_at_epochs = []
    for satellites_at_epoch in satellites_at_epochs:
        satellites_array = []
        for satellitedf in satellites_at_epoch:
            satellites_array.extend(satellitedf.values.tolist())
        if len(satellites_array) >= 4:
            DOP_at_epochs.append( DOPvalues(satellites_array, receiver_pos) )
        else:
            DOP_at_epochs.append( [0,0,0,0,0] )
    return DOP_at_epochs

def create_observers(src: rasterio.io.DatasetReader, dem_data, points) -> np.ndarray[3, np.float32]:
    """
    Return lat, long, heigth for every point. Coordinates in Easting/Norting.
    """
    # Convert observation point to EN-coordinates and find height from DEM
    observers = np.empty((len(points),3), dtype=np.float32)
    observers_cartesian = np.empty((len(points),3), dtype=np.float32)
    transformerToEN = Transformer.from_crs("EPSG:4326","EPSG:25833", always_xy=True)
    for step in range(len(points)):
        observation_point_latlng = points[step]['geometry']['coordinates']
        observation_point_EN = transformerToEN.transform(observation_point_latlng[0], observation_point_latlng[1])  
        observation_height = dem_data[src.index(observation_point_EN[0], observation_point_EN[1])]
        #print('observation_height', observation_height, type(observation_height))
        
        # Convert to cartesian coordinates
        obs_cartesian = Cartesian(observation_point_latlng[1]* np.pi/180, observation_point_latlng[0]* np.pi/180, observation_height)
        observers_cartesian[step,:] = obs_cartesian
        observer = [observation_point_EN[0], observation_point_EN[1], observation_height]
        observers[step,:] = observer
    return observers, observers_cartesian


def find_dop_on_point(dem_data, gnss_mapping, gnss, time, point, observer, obs_cartesian, elevation_angle, E_lower, N_upper,step):
    """
    Computes DOP at a specific point in time and location (point).
    """
    # Offset time by current point's offset
    timeNow = time + timedelta(seconds=point['properties']['time_from_start'])

    #start = perf_counter_ns()
    visible_satellites = satellites_visible_from_point(gnss_mapping,gnss, timeNow, obs_cartesian, observer, elevation_angle, dem_data,E_lower, N_upper, step)
    #print("timing satellites_visible_from_point (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
    
    if len(visible_satellites) < 4: return [0, 0, 0, 0, 0]
    return DOPvalues(visible_satellites, obs_cartesian)