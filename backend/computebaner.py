import pandas as pd
import numpy as np
from pyproj import Transformer
from sortDataNew import sortData
from datetime import datetime, timedelta
from satellitePositions import get_satellite_positions
from generateElevationMask import check_satellite_sight, check_satellite_sight_2
from common_variables import wgs
import rasterio

# Set up coordinate transformers
transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)
transformerToEN = Transformer.from_crs("EPSG:4326","EPSG:25833", always_xy=True)
# Convert geodetic coordinates to ECEF (Earth-Centered, Earth-Fixed)
def Cartesian(phi,lam, h):
    N = (wgs.a**2)/np.sqrt(wgs.a**2*(np.cos(phi))**2 + wgs.b**2*(np.sin(phi))**2)
    X = (N+h)*np.cos(phi)*np.cos(lam)
    Y = (N+h)*np.cos(phi)*np.sin(lam)
    Z = (((wgs.b**2)/(wgs.a**2))*N + h)*np.sin(phi)
    return [X,Y,Z]

# Convert ECEF back to geodetic coordinates
def CartesianToGeodetic(X, Y, Z, a, b):
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

# Get day number of year from date, adjust if today
def getDayNumber(date):
    print('in getDayNumber', date)
    start_date = datetime(date.year, 1, 1)
    days_difference = (date - start_date).days + 1
    if date.date() == datetime.now().date():
        days_difference -= 1
        date = date - timedelta(days=1)

    daynumber = f"{days_difference:03d}"
    sortData(daynumber, date)
    return daynumber

# Load structured GNSS data for a specific day/year
def get_gnss(daynumber,year):
    print('in gnss_mapping')
    gnss_mapping = {
        'GPS': pd.read_csv(f"DataFrames/{year}/{daynumber}/structured_dataG.csv"),
        'GLONASS': pd.read_csv(f"DataFrames/{year}/{daynumber}/structured_dataR.csv"),
        'Galileo': pd.read_csv(f"DataFrames/{year}/{daynumber}/structured_dataE.csv"),
        'QZSS': pd.read_csv(f"DataFrames/{year}/{daynumber}/structured_dataJ.csv"),
        'BeiDou': pd.read_csv(f"DataFrames/{year}/{daynumber}/structured_dataC.csv"),
        'NavIC': pd.read_csv(f"DataFrames/{year}/{daynumber}/structured_dataI.csv"),
        'SBAS': pd.read_csv(f"DataFrames/{year}/{daynumber}/structured_dataS.csv")
    }
    return gnss_mapping

# Used for calculating visual satellite positions along road segments
def visualCheck_2(satellites, obs_cartesian,observer,observation_lngLat, elevation_mask, dem_data, src,step):

    visual_satellites = []

    satellite_names = pd.DataFrame(columns = ["Satelitenumber","time", "X","Y","Z", "azimuth", "zenith"])
    phi = observation_lngLat[1]*np.pi/180
    lam =  observation_lngLat[0]*np.pi/180
    T = np.matrix([[-np.sin(phi)*np.cos(lam),-np.sin(phi)*np.sin(lam) , np.cos(phi)], 
            [-np.sin(lam), np.cos(lam), 0],
            [np.cos(phi)*np.cos(lam), np.cos(phi)*np.sin(lam), np.sin(phi)]])

  
    for index, row in satellites.iterrows():
        deltaCTRS = np.array([row["X"]-obs_cartesian[0],
                              row["Y"]-obs_cartesian[1],
                              row["Z"]-obs_cartesian[2]])
        
        xyzLG = T @ deltaCTRS.T
        xyzLG = np.array(xyzLG).flatten() 
        #calculate angles
        Ss = (xyzLG[0]**2 + xyzLG[1]**2 + xyzLG[2]**2)**(0.5)
        azimuth = np.arctan2(xyzLG[1],xyzLG[0]) *180/np.pi
        zenith = np.arccos(xyzLG[2]/Ss)* 180/np.pi
        elevation = 90- abs(zenith)

        if azimuth < 0:
            azimuth = 360 + azimuth
        #fra generateEvelationMask.py

        if check_satellite_sight(observer, dem_data,src, 5000, elevation, elevation_mask, azimuth):
            visual_satellites.append([row["X"],row["Y"],row["Z"]])
            satellite_names.loc[len(satellite_names)] = [row["satelite_id"],row['time'],row["X"],row["Y"],row["Z"], azimuth,zenith]
    if step == 1:
        print(f'visual_satellites road calc: {satellite_names}')     

    return visual_satellites


def satellites_at_point_2(gnss_mapping,gnss_list,given_date,obs_cartesian, observer, elevation_angle, dem_data,src,step):

    print('in satellites_at_point_2')

    elevation_mask = float(elevation_angle)
    observation_lngLat = transformer.transform(observer[0], observer[1])

    final_list = []

    for gnss in gnss_list:
        #fra satellitePositions.py
        satellites = get_satellite_positions(gnss_mapping[gnss],gnss,given_date)

        visual_satellites = visualCheck_2(satellites, obs_cartesian, observer,observation_lngLat, elevation_mask, dem_data,src,step)
        final_list = final_list + visual_satellites
    
    return final_list


# Check visible satellites for one point in time
# Used for visualization of skyplot
def visualCheck_3(satellites, observer_cartesian, observer, observation_lngLat, elevation_mask, dem_data, src):
    
    visual_satellites = []

    phi = observation_lngLat[1] *np.pi/180
    lam =  observation_lngLat[0] *np.pi/180
    T = np.matrix([[-np.sin(phi)*np.cos(lam),-np.sin(phi)*np.sin(lam) , np.cos(phi)], 
            [-np.sin(lam), np.cos(lam), 0],
            [np.cos(phi)*np.cos(lam), np.cos(phi)*np.sin(lam), np.sin(phi)]])

    for index, row in satellites.iterrows():
        deltaCTRS = np.array([row["X"]-observer_cartesian[0],
                              row["Y"]-observer_cartesian[1],
                              row["Z"]-observer_cartesian[2]])
        
        xyzLG = T @ deltaCTRS.T
        xyzLG = np.array(xyzLG).flatten() 
        #calculate angles
        Ss = (xyzLG[0]**2 + xyzLG[1]**2 + xyzLG[2]**2)**(0.5)
        azimuth = np.arctan2(xyzLG[1],xyzLG[0]) *180/np.pi
        zenith = np.arccos(xyzLG[2]/Ss)* 180/np.pi
        elevation = 90- abs(zenith)

        if azimuth < 0:
            azimuth = 360 + azimuth
        #fra generateEvelationMask.py
    
        if check_satellite_sight(observer, dem_data,src, 5000, elevation, elevation_mask,azimuth):
            visual_satellites.append([row["satelite_id"],row["time"],row["X"],row["Y"],row["Z"], azimuth,zenith])

    df = pd.DataFrame(visual_satellites, columns = ["Satelitenumber","time", "X","Y","Z", "azimuth", "zenith"])
    return df


# Wrapper-funksjon som brukes av frontend for å hente visuelle satellitter
# Returnerer både DataFrame og dictionary-format

def runData_check_sight(gnss_list, elevationstring, t, epoch, frequency,observation_lngLat):

    print('in runData_check_sight')


    elevation_mask = float(elevationstring)

    
    observation_EN = transformerToEN.transform(observation_lngLat[0], observation_lngLat[1])
    given_date = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%f")
    daynumber = getDayNumber(given_date)
    gnss_mapping = get_gnss(daynumber,given_date.year )
    
    with rasterio.open("data/merged_raster.tif") as src:
        dem_data = src.read(1)  

        observer_height = dem_data[src.index(observation_EN[0], observation_EN[1])]
        print(f'observer: {observation_lngLat}, {observer_height}')
        observation_cartesian = Cartesian(observation_lngLat[1]* np.pi/180, observation_lngLat[0]* np.pi/180, observer_height)
        observation_end = [observation_EN[0], observation_EN[1], observer_height]

        final_list = []
        final_listdf = []
        print('finds visual satellites')
        calculations = int(epoch)* int((60/frequency))+1
        for i in range(0, calculations):
         
            time2 = pd.to_datetime(t)+ pd.Timedelta(minutes=i*frequency)
        
            LGDF_df = []
            for gnss in gnss_list:

                positions = get_satellite_positions(gnss_mapping[gnss],gnss,time2)
            
                data = visualCheck_3(positions, observation_cartesian,observation_end, observation_lngLat, elevation_mask, dem_data, src)
                
                if not data.empty:
                    LGDF_df += [data]
            
            final_list.append([df.to_dict() for df in LGDF_df])
            final_listdf.append(LGDF_df)
       
        elevationCutoffs = []
        for i in range(0,360,1):
            top = check_satellite_sight_2(observation_end,dem_data,src, 5000, elevation_mask, i)
            elevationCutoffs.append(top)

    
    return final_list, final_listdf,elevationCutoffs,observation_cartesian



#gammel funksjon

#same as above but it return the values that are nececary for visualizing
# def visualCheck(dataframe, observation_lnglat, observation_cartesian, observation_en, elevation_cutoffs, elevation_mask):
#     #print('in visual check')
#     LGDF = pd.DataFrame(columns = ["Satelitenumber","time", "X","Y","Z", "azimuth", "zenith"])
#     nb = 0

#     phi = observation_lnglat[1]*np.pi/180
#     lam =  observation_lnglat[0]*np.pi/180
#     T = np.matrix([[-np.sin(phi)*np.cos(lam),-np.sin(phi)*np.sin(lam) , np.cos(phi)], 
#             [-np.sin(lam), np.cos(lam), 0],
#             [np.cos(phi)*np.cos(lam), np.cos(phi)*np.sin(lam), np.sin(phi)]])

#     # print('in visual check')
#     # print(f'elevation_cutoffs: {len(elevation_cutoffs)}')

#     for index, row in dataframe.iterrows():
#         deltaCTRS = np.array([row["X"]-observation_cartesian[0],
#                             row["Y"]-observation_cartesian[1],
#                             row["Z"]-observation_cartesian[2]])
        
#         xyzLG = T @ deltaCTRS.T
#         xyzLG = np.array(xyzLG).flatten() 
#         #calculate angles
#         Ss = (xyzLG[0]**2 + xyzLG[1]**2 + xyzLG[2]**2)**(0.5)
#         Sh = (xyzLG[0]**2 + xyzLG[1]**2 )**(0.5)
#         azimuth = np.arctan2(xyzLG[1],xyzLG[0]) *180/np.pi
#         zenith = np.arccos(xyzLG[2]/Ss)* 180/np.pi
#         elevation = 90- abs(zenith)

#         if azimuth < 0:
#             azimuth = 360 + azimuth

#         #print(f'azimuth: {int(round(azimuth) %360)}')
#         index = int(round(azimuth)) % 360
#         minElev = elevation_cutoffs[index] 
#         if isinstance(minElev, (list, np.ndarray)): # her må det fikses- finner ikke grunnen til at noen verdier er arrays
#             minElev = minElev[0]  
#         minElev = float(minElev)  
#         if  (elevation > elevation_mask) and (elevation > minElev):

#             LGDF.loc[len(LGDF)] = [row["satelite_id"],row["time"],row["X"],row["Y"],row["Z"], azimuth,zenith]
#         #print(f"{nb} /{length}")
#         nb +=1
#     return LGDF


# def runData(gnss_list, elevationstring, t, epoch, observation_lngLat):

#     print('in runData')

#     import time

#     # Start tidtaking
#     start_time = time.time()

#     # Kjør funksjonen
#     elevation_mask = float(elevationstring)

#     print(f'observation_lngLat: {observation_lngLat}')
#     observation_EN = transformerToEN.transform(observation_lngLat[0], observation_lngLat[1])

#     with rasterio.open("data/merged_raster_romsdalen_10.tif") as src:
#         dem_data = src.read(1)  
#         elevation_cutoff, observer_height = find_elevation_cutoff(dem_data, src, observation_EN, 5,elevation_mask)
#     #print(f'elevation_cutoffs: {elevation_cutoffs}')
#     elevation_cutoffs = elevation_cutoff.copy()
#     observation_cartesian = Cartesian(observation_lngLat[1] * np.pi/180, observation_lngLat[0]* np.pi/180, observer_height)
#     # Stopp tidtaking
#     end_time = time.time()

#     # Beregn og skriv ut kjøretiden
#     elapsed_time = end_time - start_time
#     print(f"Kjøretid finn elevation: {elapsed_time:.2f} sekunder")


#     given_date = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%f")
#     daynumber = getDayNumber(given_date)
#     gnss_mapping = get_gnss(daynumber,given_date.year )

 
#     #create a list that contains the seconds for every halfhour in the epoch when epoch is hours
#     final_list = []
#     final_listdf = []
#     print('finds visual satellites')
#     for i in range(0, int(epoch)*2 + 1):
#         # print(f"{i}/{int(epoch)*2 + 1}")
#         time2 = pd.to_datetime(t)+ pd.Timedelta(minutes=i*30)
#         #LGDF_dict = []
#         LGDF_df = []
#         for gnss in gnss_list:
#             # print(gnss)
            
#             positions = get_satellite_positions(gnss_mapping[gnss],gnss,time2)
           
#             data = visualCheck(positions,observation_lngLat,observation_cartesian, observation_EN, elevation_cutoffs, elevation_mask)
 
#             if not data.empty:
#                 #LGDF_dict += [data.to_dict()]  
#                 LGDF_df += [data]
#         final_list.append([df.to_dict() for df in LGDF_df])
#         final_listdf.append(LGDF_df)
#     return final_list, final_listdf, elevation_cutoffs,observation_cartesian



# point = {
#     "type": "Feature",
#     "geometry": {
#         "type": "Point",
#         "coordinates": [7.6866582, 62.5580949]
#     },
#     "properties": {"name": "Point", "id": 2}
# }
# list, df, elevation_cutoffs  = runData(['GPS', 'GLONASS', 'Galileo'], '10','2025-03-13T12:00:00.000' , 1 ,point)
# print(list[0])

