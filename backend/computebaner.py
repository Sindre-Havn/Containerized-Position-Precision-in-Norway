from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import re
import ahrs
from sortDataNew import sortData
from datetime import datetime, timedelta
from satellitePositions import get_satellite_positions
from generateElevationMask import check_satellite_sight, find_elevation_cutoff
from common_variables import wgs, phi,lam, h, E, N

def Cartesian(phi,lam, h):
    N = (wgs.a**2)/np.sqrt(wgs.a**2*(np.cos(phi))**2 + wgs.b**2*(np.sin(phi))**2)
    X = (N+h)*np.cos(phi)*np.cos(lam)
    Y = (N+h)*np.cos(phi)*np.sin(lam)
    Z = (((wgs.b**2)/(wgs.a**2))*N + h)*np.sin(phi)
    return [X,Y,Z]

#calculate LG
T = np.matrix([[-np.sin(phi)*np.cos(lam),-np.sin(phi)*np.sin(lam) , np.cos(phi)], 
            [-np.sin(lam), np.cos(lam), 0],
            [np.cos(phi)*np.cos(lam), np.cos(phi)*np.sin(lam), np.sin(phi)]])

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


def getDayNumber(date):
    print('in getDayNumber', date)
    start_date = datetime(date.year, 1, 1)
    days_difference = (date - start_date).days + 1
    if date.date() == datetime.now().date():
        days_difference -= 1
        date = date - timedelta(days=1)
    daynumber = f"{days_difference:03d}"

    #print(daynumber, date)
    sortData(daynumber, date)
    return daynumber

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

#same as above but it return the values that are nececary for visualizing
def visualCheck(dataframe,observation_cartesian, observation_en, elevation_cutoffs, elevation_mask):
    #print('in visual check')
    LGDF = pd.DataFrame(columns = ["Satelitenumber","time", "X","Y","Z", "azimuth", "zenith"])
    nb = 0
    length = len(dataframe)
    for index, row in dataframe.iterrows():
        deltax = row["X"]-observation_cartesian[0]
        deltay = row["Y"]-observation_cartesian[1]
        deltaz = row["Z"]-observation_cartesian[2]
        deltaCTRS = np.array([deltax,deltay,deltaz])
        
        xyzLG = T @ deltaCTRS.T
        xyzLG = np.array(xyzLG).flatten() 
        #calculate angles
        Ss = (xyzLG[0]**2 + xyzLG[1]**2 + xyzLG[2]**2)**(0.5)
        Sh = (xyzLG[0]**2 + xyzLG[1]**2 )**(0.5)
        azimuth = np.arctan2(xyzLG[1],xyzLG[0]) *180/np.pi
        zenith = np.arccos(xyzLG[2]/Ss)* 180/np.pi
        elevation = 90- abs(zenith)
        if azimuth < 0:
            azimuth = 360 + azimuth
        minElev = elevation_cutoffs[int(round(azimuth))]
        #if check_satellite_sight((observation_en[0], observation_en[1]), 5000, elevation, azimuth):
        if elevation > minElev and elevation > elevation_mask:
            LGDF.loc[len(LGDF)] = [row["satelite_id"],row["time"],row["X"],row["Y"],row["Z"], azimuth,zenith]
        #print(f"{nb} /{length}")
        nb +=1
    return LGDF


def runData(gnss_list, elevationstring, t, epoch):
    print(f"gnss_list:{gnss_list}")
    observation_Cartesian = Cartesian(phi,lam, h)
    observation_en = (E, N)
    elevation_cutoffs = find_elevation_cutoff(observation_en, 5)
    #elevation_cutoff = []
    print('in runData')
    given_date = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%f")
    daynumber = getDayNumber(given_date)
    gnss_mapping =  get_gnss(daynumber,given_date.year )
    elevation = float(elevationstring)
    #create a list that contains the seconds for every halfhour in the epoch when epoch is hours
    final_list = []
    final_listdf = []
    #print('finds visual satellites')
    for i in range(0, int(epoch)*2 + 1):
        print(f"{i}/{int(epoch)*2 + 1}")
        time = pd.to_datetime(t)+ pd.Timedelta(minutes=i*30)
        LGDF_dict = []
        LGDF_df = []
        for gnss in gnss_list:
            print(gnss)
            positions = get_satellite_positions(gnss_mapping[gnss],gnss,time)
            data = visualCheck(positions,observation_Cartesian, observation_en, elevation_cutoffs, elevation_mask)
            if not data.empty:
                LGDF_dict += [data.to_dict()]  
                LGDF_df += [data]
        final_list.append(LGDF_dict)
        final_listdf.append(LGDF_df)
    return final_list, final_listdf

# test_f,test = runData(['GPS', 'Galileo', 'GLONASS', 'BeiDou'], '10', '2025-01-30T12:00:00.000',1)
# print(test)
# test funksjoner
# def visualCheck2(dataframe, recieverPos0, elevationInput):
#     LGDF = pd.DataFrame(columns = ["satelite_id","time", "X","Y","Z", "azimuth", "zenith"])
#     for index, row in dataframe.iterrows():
#         deltax = row["X"]-recieverPos0[0]
#         deltay = row["Y"]-recieverPos0[1]
#         deltaz = row["Z"]-recieverPos0[2]
#         deltaCTRS = np.array([deltax,deltay,deltaz])
        
#         xyzLG = T @ deltaCTRS.T
#         xyzLG = np.array(xyzLG).flatten() 
#         #calculate angles
#         Ss = (xyzLG[0]**2 + xyzLG[1]**2 + xyzLG[2]**2)**(0.5)
#         Sh = (xyzLG[0]**2 + xyzLG[1]**2 )**(0.5)
#         azimuth = np.arctan2(xyzLG[1],xyzLG[0]) *180/np.pi
#         zenith = np.arccos(xyzLG[2]/Ss)* 180/np.pi
#         elevation = 90- abs(zenith)
#         print(elevation, elevationInput)
#         if azimuth < 0:
#             azimuth = 360 + azimuth
#         if(elevation >=elevationInput):
#             LGDF.loc[len(LGDF)] = [row["satelite_id"],row["time"],row["X"],row["Y"],row["Z"], azimuth,zenith]
    
#     return LGDF



# def runData3(gnss_list, elevationstring, t, str, recpos):
#     daynumber = "345"    
#     gnss_mapping = {
#         'GPS': pd.read_csv(f"DataFrames/{daynumber}/structured_dataG.csv"),
#         'Galileo': pd.read_csv(f"DataFrames/{daynumber}/structured_dataE.csv"),
#         'GLONASS': pd.read_csv(f"DataFrames/{daynumber}/structured_dataR.csv"),
#         'BeiDou': pd.read_csv(f"DataFrames/{daynumber}/structured_dataC.csv"),

#     }
#     elevation = float(elevationstring)
#     #create a list that contains the seconds for every halfhour in the epoch when epoch is hours
#     with open (f'{str}.csv','w') as f:
#         f.write(f"Satellitenumber,time,X,Y,Z,zenith, azimuth\n")
#         for i in range(0, 1):
#             time = pd.to_datetime(t)+ pd.Timedelta(seconds=i)
    
#             for gnss in gnss_list:
#                 positions = get_satellite_positions(gnss_mapping[gnss],gnss,time)

#                 if not positions.empty:
#                     visual = visualCheck2(positions, recpos, 10)
#                     for index, row in visual.iterrows():
                        
#                         f.write(f"{row['satelite_id']}, {row['time']}, {row['X']}, {row['Y']}, {row['Z']} ,{row['zenith']}, {row['azimuth']}\n")
            
#         f.close() 
    

