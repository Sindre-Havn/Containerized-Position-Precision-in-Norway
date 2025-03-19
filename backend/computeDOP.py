from datetime import datetime, timedelta
import numpy as np
import rasterio
from pyproj import Transformer
from computebaner import Cartesian, get_gnss, getDayNumber, runData, satellites_at_point_2
from common_variables import wgs, phi,lam, h

transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)
transformerToEN = Transformer.from_crs("EPSG:4326","EPSG:25833", always_xy=True)


def R2(theta):
    return np.array([[np.cos(theta),0,-np.sin(theta)],
                    [0,            1,           0],
                    [np.sin(theta),0,np.cos(theta)]])

def R3(theta):
    return np.array([[np.cos(theta),np.sin(theta),0],
                    [-np.sin(theta),np.cos(theta),0],
                    [0,             0,             1]])

def P2():
    return np.array([[1,0,0],[0,-1,0],[0,0,1]])

def geometric_range(sat_pos, rec_pos):
    return np.sqrt((sat_pos[0] - rec_pos[0])**2 +
                   (sat_pos[1] - rec_pos[1])**2 +
                   (sat_pos[2] - rec_pos[2])**2)

def DOPvalues(satellites, recieverPos0):
    size = len(satellites)
    A = np.zeros((size, 4))  
    Qxx =np.zeros((4, 4)) 
    if(size >= 4):
        #creates the A matrix
        i = 0
        for satellite in satellites:
            rho_i = geometric_range([satellite[2], satellite[3], satellite[4]], recieverPos0)

            A[i][0] = -((satellite[2]-recieverPos0[0]) / rho_i)
            A[i][1] = -((satellite[3] - recieverPos0[1]) / rho_i)
            A[i][2] = -((satellite[4] - recieverPos0[2] ) / rho_i)
            A[i][3] = -1
            i +=1
        
        AT = A.T
        ATA = AT@A
        Qxx = np.linalg.inv(ATA)
        Qxx_local = Qxx[0:3,0:3]
        T = P2()@R2(phi-np.pi/2)@R3(lam-np.pi)
        Qxx_local = T@Qxx_local@T.T
        GDOP = np.sqrt(Qxx[0][0] + Qxx[1][1] + Qxx[2][2] + Qxx[3][3])
        PDOP = np.sqrt(Qxx[0][0] + Qxx[1][1] + Qxx[2][2])
        TDOP = np.sqrt(Qxx[3][3])
        HDOP = np.sqrt(Qxx_local[0][0]+Qxx_local[1][1])
        VDOP = np.sqrt(Qxx_local[2][2])
    else:
        GDOP = 0
        PDOP = 0
        TDOP = 0
        HDOP = 0
        VDOP = 0
    return GDOP,PDOP,TDOP,HDOP,VDOP

def best(satellites, recieverPos0):

    final_DOP_values = []
    for satelitedf in satellites:
        satellites_array = []
        for satellitedf in satelitedf:
            for index,row in satellitedf.iterrows():
                satellites_array += [[row["Satelitenumber"],row["time"], row["X"],row["Y"], row["Z"]]]
        if(len(satellites_array) > 0):
            GDOP, PDOP, TDOP,HDOP,VDOP = DOPvalues(satellites_array, recieverPos0)
            final_DOP_values.append([GDOP, PDOP, TDOP, HDOP, VDOP])
        else:
            final_DOP_values.append([0, 0, 0, 0, 0])
    
    return final_DOP_values


def DOPvalues_2(satellites, recieverPos0):
    size = len(satellites)
    A = np.zeros((size, 4))  
    Qxx =np.zeros((4, 4)) 
    if(size >= 4):
        #creates the A matrix
        i = 0
        for satellite in satellites:
            rho_i = geometric_range([satellite[0], satellite[1], satellite[2]], recieverPos0)

            A[i][0] = -((satellite[0]-recieverPos0[0]) / rho_i)
            A[i][1] = -((satellite[1] - recieverPos0[1]) / rho_i)
            A[i][2] = -((satellite[2] - recieverPos0[2] ) / rho_i)
            A[i][3] = -1
            i +=1
        
        AT = A.T
        ATA = AT@A
        Qxx = np.linalg.inv(ATA)
        Qxx_local = Qxx[0:3,0:3]
        T = P2()@R2(phi-np.pi/2)@R3(lam-np.pi)
        Qxx_local = T@Qxx_local@T.T
        GDOP = np.sqrt(Qxx[0][0] + Qxx[1][1] + Qxx[2][2] + Qxx[3][3])
        PDOP = np.sqrt(Qxx[0][0] + Qxx[1][1] + Qxx[2][2])
        TDOP = np.sqrt(Qxx[3][3])
        HDOP = np.sqrt(Qxx_local[0][0]+Qxx_local[1][1])
        VDOP = np.sqrt(Qxx_local[2][2])
    else:
        GDOP = 0
        PDOP = 0
        TDOP = 0
        HDOP = 0
        VDOP = 0
    return GDOP,PDOP,TDOP,HDOP,VDOP


def best_2(satellites, observer):
    final_DOP_values = []
    if(len(satellites) > 0):
        GDOP, PDOP, TDOP,HDOP,VDOP = DOPvalues_2(satellites, observer)
        final_DOP_values.append([GDOP, PDOP, TDOP, HDOP, VDOP])
    else:
        final_DOP_values.append([0, 0, 0, 0, 0])

    return final_DOP_values


def find_dop_along_road(points, time, gnss, elevation_angle):
    dop_list = [] 

    daynumber = getDayNumber(time)
    gnss_mapping = get_gnss(daynumber,time.year )
    print('gnss_', gnss)
    with rasterio.open("data/merged_raster_romsdalen_10.tif") as src:
        dem_data = src.read(1)   
        #for hvert punkt finn alle satelliters posisjon som er i gnss, og som er innenfor sight
        for point in points:
            observation_point_latlng = point['geometry']['coordinates']
            observation_point_EN = transformerToEN.transform(observation_point_latlng[0], observation_point_latlng[1])
            observation_height = dem_data[src.index(observation_point_EN[0], observation_point_EN[1])]
            obs_cartesian = Cartesian(observation_point_latlng[1], observation_point_latlng[0], observation_height)

            observer = [observation_point_EN[0], observation_point_EN[1], observation_height]

            timeNow = time + timedelta(seconds=point['properties']['time_from_start'])
            #fra computebaner.py
            satellites = satellites_at_point_2(gnss_mapping,gnss, timeNow, observer, elevation_angle, dem_data,src)
            
            #finn så dop
            dopvalues = best_2(satellites, obs_cartesian)
            dop_list.append(dopvalues)

    return dop_list

def find_dop_on_point(dem_data, src, gnss_mapping, gnss, time, point, elevation_angle):

    observation_point_latlng = point['geometry']['coordinates']
    observation_point_EN = transformerToEN.transform(observation_point_latlng[0], observation_point_latlng[1])  
    observation_height = dem_data[src.index(observation_point_EN[0], observation_point_EN[1])]

    obs_cartesian = Cartesian(observation_point_latlng[1], observation_point_latlng[0], observation_height)

    observer = [observation_point_EN[0], observation_point_EN[1], observation_height]

    timeNow = time + timedelta(seconds=point['properties']['time_from_start'])
    #fra computebaner.py
    satellites = satellites_at_point_2(gnss_mapping,gnss, timeNow, observer, elevation_angle, dem_data,src)
    
    #finn så dop
    dopvalues = best_2(satellites, obs_cartesian)
    
    return dopvalues

# point = {
#     "type": "Feature",
#     "geometry": {
#         "type": "Point",
#         "coordinates": [8.0552304, 62.3482632]
#     },
#     "properties": {"time_from_start": 0, "id": 1}
# }
# timedate = datetime.strptime( '2025-03-13T12:00:00.000', "%Y-%m-%dT%H:%M:%S.%f")
# doplist = find_dop_along_road([point],timedate, ['GPS', 'GLONASS', 'Galileo', 'BeiDou', 'QZSS'], '10')

# list, df, elevation_cutoffs, obs_cartesian = runData(['GPS', 'GLONASS', 'Galileo', 'BeiDou', 'QZSS'], '10', '2025-03-13T12:00:00.000', 1, point) 
# print(f'satellites2:, {list[0]}')
# print('doplist:', doplist)
# import time

# # Start tidtaking
# start_time = time.time()

# # Kjør funksjonen
# #sortData('042', datetime(2025, 2, 11, 0, 0))
# list, df, elevation_cutoffs ,observation_cartesian = runData(['GPS', 'GLONASS', 'Galileo'], '10','2025-03-13T12:00:00.000' , 1 ,point)

# dop = best(df,observation_cartesian)
# print('dop:', dop[0])

# # Stopp tidtaking
# end_time = time.time()

# # Beregn og skriv ut kjøretiden
# elapsed_time = end_time - start_time
# print(f"Kjøretid rundata: {elapsed_time:.2f} sekunder")

# start_time = time.time()

# # Kjør funksjonen
# #sortData('042', datetime(2025, 2, 11, 0, 0))
# #data, datadf = runData(['GPS', 'Galileo','GLONASS','Beidou' ], "10", "2025-02-11T04:00:00.000", "6")

# best(datadf)

# # Stopp tidtaking
# end_time = time.time()

# # Beregn og skriv ut kjøretiden
# elapsed_time = end_time - start_time
# print(f"Kjøretid best: {elapsed_time:.2f} sekunder")