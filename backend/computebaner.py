from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import re
import ahrs
from sortDataNew import sortData
from datetime import datetime, timedelta
from satellitePositions import get_satellite_positions

T = 558000
GM = 3.986005*10**14
we = 7.2921151467 *10**(-5) 
c = 299792458

wgs = ahrs.utils.WGS()
#romsdalen
# phi = 62.42953 * np.pi/180
# lam = 7.94942* np.pi/180
# h = 117.5

#Parkeringsplass NTNU 20 grader
# phi = 63.41457900 * np.pi/180
# lam = 10.41045326 * np.pi/180
# h = 42.738

#Parkeringsplass NTNU 10 grader
phi = 63.41458293  * np.pi/180
lam = 10.41044691  * np.pi/180
h =39.689


def Cartesian(phi,lam, h):
    N = (wgs.a**2)/np.sqrt(wgs.a**2*(np.cos(phi))**2 + wgs.b**2*(np.sin(phi))**2)
    X = (N+h)*np.cos(phi)*np.cos(lam)
    Y = (N+h)*np.cos(phi)*np.sin(lam)
    Z = (((wgs.b**2)/(wgs.a**2))*N + h)*np.sin(phi)
    return [X,Y,Z]

#point 1 coordinates
recieverPos0 = Cartesian(phi,lam, h)

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

#get daynumber(for broadcasting ephemeris)
def getDayNumber(date):
    print('in getDayNumber', date)
    given_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
    start_date = datetime(given_date.year, 1, 1)
    days_difference = (given_date - start_date).days + 1
    if given_date.date() == datetime.now().date():
        days_difference -= 1
        given_date = given_date - timedelta(days=1)
    daynumber = f"{days_difference:03d}"

    print(daynumber, given_date)
    sortData(daynumber, given_date)
    return daynumber

def get_gnss(daynumber):
    print('in gnss_mapping')
    gnss_mapping = {
        'GPS': pd.read_csv(f"backend/DataFrames/{daynumber}/structured_dataG.csv"),
        'GLONASS': pd.read_csv(f"backend/DataFrames/{daynumber}/structured_dataR.csv"),
        'Galileo': pd.read_csv(f"backend/DataFrames/{daynumber}/structured_dataE.csv"),
        'QZSS': pd.read_csv(f"backend/DataFrames/{daynumber}/structured_dataJ.csv"),
        'BeiDou': pd.read_csv(f"backend/DataFrames/{daynumber}/structured_dataC.csv"),
        'NavIC': pd.read_csv(f"backend/DataFrames/{daynumber}/structured_dataI.csv"),
        'SBAS': pd.read_csv(f"backend/DataFrames/{daynumber}/structured_dataS.csv")
    }
    return gnss_mapping

#same as above but it return the values that are nececary for visualizing
def visualCheck(dataframe, recieverPos0, elevationInput):
    LGDF = pd.DataFrame(columns = ["Satelitenumber","time", "X","Y","Z", "azimuth", "zenith"])
    for index, row in dataframe.iterrows():
        deltax = row["X"]-recieverPos0[0]
        deltay = row["Y"]-recieverPos0[1]
        deltaz = row["Z"]-recieverPos0[2]
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
        if(elevation >=elevationInput):
            LGDF.loc[len(LGDF)] = [row["satelite_id"],row["time"],row["X"],row["Y"],row["Z"], azimuth,zenith]
    
    return LGDF


def runData(gnss_list, elevationstring, t, epoch):
    print('in runData')
    daynumber = getDayNumber(t)
    gnss_mapping =  get_gnss(daynumber)
    elevation = float(elevationstring)
    #create a list that contains the seconds for every halfhour in the epoch when epoch is hours
    final_list = []
    final_listdf = []
    print('finds visual satellites')
    for i in range(0, int(epoch)*2 + 1):
        time = pd.to_datetime(t)+ pd.Timedelta(minutes=i*30)
        LGDF_dict = []
        LGDF_df = []
        for gnss in gnss_list:
            positions = get_satellite_positions(gnss_mapping[gnss],gnss,time)
            data = visualCheck(positions, recieverPos0, elevation)
            if not data.empty:
                LGDF_dict += [data.to_dict()]  
                LGDF_df += [data]
        final_list.append(LGDF_dict)
        final_listdf.append(LGDF_df)
    return final_list, final_listdf

#test = runData(['GPS', 'Galileo', 'GLONASS', 'BeiDou'], '10', '2024-11-12T00:00:00.000', 4)
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
    

