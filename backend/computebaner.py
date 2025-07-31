import pandas as pd
import numpy as np
from pyproj import Transformer
from sortDataNew import sortData
from datetime import datetime, timedelta
#from computeDOP import DOP_at_epochs
from satellitePositions import get_satellite_positions
from generateElevationMask import satellite__is_in_sight, check_satellite_sight_2
from common_variables import wgs
import rasterio

from time import perf_counter_ns
from itertools import repeat

# Set up coordinate transformers: EPSG:4326 = WGS84, EPSG:25833 = UTM zone 33N
transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)
transformerToEN = Transformer.from_crs("EPSG:4326","EPSG:25833", always_xy=True)


def Cartesian(phi: float, lam: float, h: float) -> list[float]:
    """
    Convert geodetic coordinates to ECEF (Earth-Centered, Earth-Fixed).
    """
    N = (wgs.a**2)/np.sqrt(wgs.a**2*(np.cos(phi))**2 + wgs.b**2*(np.sin(phi))**2)
    X = (N+h)*np.cos(phi)*np.cos(lam)
    Y = (N+h)*np.cos(phi)*np.sin(lam)
    Z = (((wgs.b**2)/(wgs.a**2))*N + h)*np.sin(phi)
    return [X,Y,Z]


def CartesianToGeodetic(X: float, Y: float, Z: float, a: float, b: float) -> list[float]:
    """
    Convert ECEF back to geodetic coordinates.
    """
    # Calculate the first eccentricity squared
    e2 = 1 - (b**2 / a**2)
    lam = np.arctan2(Y, X)
    p = np.sqrt(X**2 + Y**2)
    phi = np.arctan2(Z, p * (1 - e2))

    phi_prev = 0
    h = 0
    
    while phi != phi_prev:
        phi_prev = phi
        N = a / np.sqrt(1 - e2 * np.sin(phi)**2)
        h = p / np.cos(phi) - N
        phi = np.arctan2(Z, p * (1 - e2 * N / (N + h)))
    
    phi_deg = np.degrees(phi)
    lam_deg = np.degrees(lam)
    
    return [phi_deg, lam_deg, h]


def getDayNumber(date: datetime) -> int:
    """
    Get day number of year from date, adjust if today.
    """
    #print('in getDayNumber', date)
    first_day_of_year = datetime(date.year, 1, 1)
    days_difference = (date - first_day_of_year).days + 1
    if date.date() == datetime.now().date():
        days_difference -= 1
        date = date - timedelta(days=1)

    daynumber = f"{days_difference:03d}"
    
    start = perf_counter_ns()
    sortData(daynumber, date)
    print("timing sortData (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
    return daynumber


def get_gnss(daynumber: int, year: int) -> dict[str, pd.DataFrame]:
    """
    Load structured GNSS data for a specific day/year.
    """
    gnss_mapping = {
        'GPS'    : pd.read_csv(f"DataFrames/{year}/{daynumber}/structured_dataG.csv"),
        'GLONASS': pd.read_csv(f"DataFrames/{year}/{daynumber}/structured_dataR.csv"),
        'Galileo': pd.read_csv(f"DataFrames/{year}/{daynumber}/structured_dataE.csv"),
        'QZSS'   : pd.read_csv(f"DataFrames/{year}/{daynumber}/structured_dataJ.csv"),
        'BeiDou' : pd.read_csv(f"DataFrames/{year}/{daynumber}/structured_dataC.csv"),
        'NavIC'  : pd.read_csv(f"DataFrames/{year}/{daynumber}/structured_dataI.csv"),
        'SBAS'   : pd.read_csv(f"DataFrames/{year}/{daynumber}/structured_dataS.csv")
    }
    return gnss_mapping


def create_observers(src: rasterio.io.DatasetReader, dem_data: np.ndarray[float], points: dict) -> tuple[ np.ndarray[float], np.ndarray[float]] :
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
        
        # Convert to cartesian coordinates
        obs_cartesian = Cartesian(observation_point_latlng[1]* np.pi/180, observation_point_latlng[0]* np.pi/180, observation_height)
        observers_cartesian[step,:] = obs_cartesian
        observer = [observation_point_EN[0], observation_point_EN[1], observation_height]
        observers[step,:] = observer
    return observers, observers_cartesian


def visual_satellites_xyz(satellites: pd.DataFrame,
                          observer_cartesian: np.ndarray[float],
                          observer: np.ndarray[float],
                          observation_lnglat: tuple[float],
                          elevation_mask: float,
                          dem_data: np.ndarray[float],
                          E_lower: float,
                          N_upper: float
                          ) -> list[list[float]]:
    """
    Return list of the XYZ (ECEF) position for each satellite visible from the observer,
    with consideration to dem_data and elevation_mask.
    """
    visual_satellites = []

    phi = observation_lnglat[1]*np.pi/180
    lam =  observation_lnglat[0]*np.pi/180
    T = np.matrix([
        [-np.sin(phi)*np.cos(lam),-np.sin(phi)*np.sin(lam), np.cos(phi)], 
        [            -np.sin(lam),             np.cos(lam),      0     ],
        [ np.cos(phi)*np.cos(lam), np.cos(phi)*np.sin(lam), np.sin(phi)]
        ])

    for _, sat in satellites.iterrows():
        deltaCTRS = np.array([sat["X"]-observer_cartesian[0],
                              sat["Y"]-observer_cartesian[1],
                              sat["Z"]-observer_cartesian[2]])
        
        xyzLG = T @ deltaCTRS.T
        xyzLG = np.array(xyzLG).flatten() 
        #calculate angles
        Ss = np.sqrt((xyzLG[0]**2 + xyzLG[1]**2 + xyzLG[2]**2))
        azimuth = np.arctan2(xyzLG[1], xyzLG[0]) * 180/np.pi
        zenith  = np.arccos(xyzLG[2]/Ss)         * 180/np.pi
        elevation = 90 - abs(zenith)

        if azimuth < 0:
            azimuth += 360

        if satellite_is_in_sight(observer, dem_data, E_lower, N_upper, elevation, elevation_mask, azimuth):
            visual_satellites.append([sat["X"],sat["Y"],sat["Z"]])

    return visual_satellites


def satellites_visible_from_point(gnss_mapping: dict[str, pd.DataFrame],
                                  gnss_list: list[str],
                                  given_date: datetime,
                                  obs_cartesian: np.ndarray[float],
                                  observer: np.ndarray[float],
                                  elevation_angle: str,
                                  dem_data: np.ndarray[float],
                                  E_lower: float, 
                                  N_upper: float
                                  ) -> list[list[float]]:

    elevation_mask = float(elevation_angle)
    observation_lnglat = transformer.transform(observer[0], observer[1])

    final_list = []
    for gnss in gnss_list:
        satellites = get_satellite_positions(gnss_mapping[gnss],gnss,given_date)
        visual_satellites = visual_satellites_xyz(satellites, obs_cartesian, observer,observation_lnglat, elevation_mask, dem_data,E_lower, N_upper)
        final_list.extend(visual_satellites)
    
    return final_list


def visual_satellites_data(satellites: pd.DataFrame,
                           observer_cartesian: np.ndarray[float],
                           observer: np.ndarray[float],
                           observation_lnglat: tuple[float],
                           elevation_mask: str,
                           dem_data: np.ndarray[float],
                           E_lower: float,
                           N_upper: float) -> pd.DataFrame:
    """
    Return list of the "satelite_id", "time", "X", "Y", "Z" for each satellite visible from the observer,
    with consideration to dem_data and elevation_mask.
    """
    visual_satellites = []

    phi = observation_lnglat[1] * np.pi/180
    lam =  observation_lnglat[0] * np.pi/180
    T = np.matrix([[-np.sin(phi)*np.cos(lam),-np.sin(phi)*np.sin(lam) , np.cos(phi)], 
            [-np.sin(lam), np.cos(lam), 0],
            [np.cos(phi)*np.cos(lam), np.cos(phi)*np.sin(lam), np.sin(phi)]])

    for _, sat in satellites.iterrows():
        deltaCTRS = np.array([sat["X"]-observer_cartesian[0],
                              sat["Y"]-observer_cartesian[1],
                              sat["Z"]-observer_cartesian[2]])
        
        xyzLG = T @ deltaCTRS.T
        xyzLG = np.array(xyzLG).flatten() 
        #calculate angles
        Ss = np.sqrt(xyzLG[0]**2 + xyzLG[1]**2 + xyzLG[2]**2)
        azimuth = np.arctan2(xyzLG[1],xyzLG[0]) * 180/np.pi
        zenith  = np.arccos(xyzLG[2]/Ss)        * 180/np.pi
        elevation = 90- abs(zenith)

        if azimuth < 0:
            azimuth = 360 + azimuth
    
        if satellite_is_in_sight(observer, dem_data, E_lower, N_upper, elevation, elevation_mask,azimuth):
            visual_satellites.append([sat["satelite_id"],sat["time"],sat["X"],sat["Y"],sat["Z"], azimuth,zenith])

    df = pd.DataFrame(visual_satellites, columns = ["Satelitenumber","time", "X","Y","Z", "azimuth", "zenith"])
    return df


def data_from_epoch(gnss_list: list[str],
                    elevation_mask_str: str,
                    start_time: datetime,
                    epoch: int,
                    frequency: int,
                    observation_lnglat: tuple[float]
                    ) -> tuple[ list[list[dict]],
                                list[str],
                                list[list[pd.DataFrame]],
                                list[float] ]:
    """
    A wrapper function for getting DOP and satellite count on a point during a specified epoch.
    Returns "visible_sats_data_for_timesteps" which is data regarding each satellite with
    LOS (line of sight) from that point.
    "visible_sats_pos_for_timesteps" and "observation_cartesian" is returned to calculate DOP outside
    this function.
    """
    elevation_cutoffs = []
    visible_sats_data_for_timesteps = []
    visible_sats_pos_for_timesteps = []

    elevation_mask = float(elevation_mask_str)
    observation_EN = transformerToEN.transform(observation_lnglat[0], observation_lnglat[1])
    given_date = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%f")
    start = perf_counter_ns()
    daynumber = getDayNumber(given_date)
    print("timing getDaynumber_runData_check_sight (ms):\t", round((perf_counter_ns()-start)/1_000_000,3))
    gnss_mapping = get_gnss(daynumber, given_date.year )
    
    with rasterio.open("data/merged_raster.tif") as src:
        dem_data = src.read(1)
        E_lower = src.bounds[0]
        N_upper = src.bounds[3]
        observer_height = dem_data[src.index(observation_EN[0], observation_EN[1])]
        observation_cartesian = Cartesian(observation_lnglat[1]* np.pi/180, observation_lnglat[0]*np.pi/180, observer_height)
        observation_end = [observation_EN[0], observation_EN[1], observer_height]

        calculations = epoch * int((60/frequency))+1
        for i in range(calculations):
         
            time = pd.to_datetime(start_time)+ pd.Timedelta(minutes=i*frequency)
            sats_data_dfs = []
            sats_pos_dfs = []

            for gnss in gnss_list:

                positions = get_satellite_positions(gnss_mapping[gnss], gnss, time)
                data = visual_satellites_data(positions, observation_cartesian, observation_end, observation_lnglat, elevation_mask, dem_data, E_lower, N_upper)
                if data.empty: continue

                sats_data_dfs.append(data)
                sats_pos_dfs.extend(data[['X', 'Y', 'Z']].values.tolist())

            visible_sats_pos_for_timesteps.append(sats_pos_dfs)
            visible_sats_data_for_timesteps.append([df.to_dict() for df in sats_data_dfs])

        elevation_cutoffs = list(map(check_satellite_sight_2, repeat(observation_end), repeat(dem_data), repeat(E_lower), repeat(N_upper), repeat(elevation_mask), range(0,360,1)))
        elevation_cutoffs = [str(elevation) for elevation in elevation_cutoffs]

    return visible_sats_data_for_timesteps, elevation_cutoffs, visible_sats_pos_for_timesteps, observation_cartesian
