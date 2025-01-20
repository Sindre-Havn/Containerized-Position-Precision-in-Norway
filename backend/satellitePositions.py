import math
import pandas as pd
import numpy as np
import re
import ahrs
from datetime import timedelta
#common functions

GM = 3.986005*10**14
we = 7.2921151467 * 10**(-5) 
c = 299792458


def TK(t):
    tm = t
    if(t >302400):
        return tm-604800
    elif(t <-302400 ):
        return tm+604800
    else:
        return tm

def MK(M0, a,deltan, tk):
    return M0 + (np.sqrt(GM/a**3)+deltan)*tk

def EK(Mk,e, n):
    E = [Mk]
    i = 1
    if i==1:
        Enew = E[i-1] + ((Mk-E[i-1]+e*np.sin(E[i-1]))/(1-e*np.cos(E[i-1])))
        E.append(Enew)
        i += 1
    else:
        while abs(E[-1] - E[-2]) > 10**(-n):
            Enew = E[i-1] + ((Mk-E[i-1]+e*np.sin(E[i-1]))/(1-e*np.cos(E[i-1])))
            E.append(Enew)
            i += 1
    return Mk + e*np.sin(E[-1])

def FK(e,Ek):
    return 2*np.arctan(np.sqrt((1+e)/(1-e))*np.tan(Ek/2))

def UK(w,fk,Cuc,Cus):
    return w+ fk + Cuc*(np.cos(2*(w+fk))) + Cus*(np.sin(2*(w+fk)))

def RK(a,e,w,Ek,fk,Crc,Crs):
    return a*(1-e*np.cos(Ek)) + Crc*(np.cos(2*(w+fk))) + Crs*(np.sin(2*(w+fk)))

def IK(i0,idot,tk,Cic,w,fk,Cis):
    return i0+ idot*tk + Cic*(np.cos(2*(w+fk))) + Cis*(np.sin(2*(w+fk)))

def LAMBDAK(lambda0,omegadot,we,tk,toe):
    return lambda0 + (omegadot-we)*tk - we*toe


def R1(theta):
    return np.array([[1,0,0],[0,np.cos(theta),np.sin(theta)],[0,-np.sin(theta),np.cos(theta)]])
def R3(theta):
    return np.array([[np.cos(theta),np.sin(theta),0],[-np.sin(theta),np.cos(theta),0],[0,0,1]])



def julian_date(year, month, day):
    # Julian Date calculation
    if month <= 2:
        year -= 1
        month += 12
    A = math.floor(year / 100)
    B = 2 - A + math.floor(A / 4)
    JD = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + B - 1524.5
    return JD

def gmst_at_midnight(year, month, day):
    J2000 = 2451545.0  # Julian Date of J2000 epoch
    DAYS_PER_CENTURY = 36525.0 # Days in a Julian century
    JD = julian_date(year, month, day)
    T = (JD - J2000) / DAYS_PER_CENTURY
    GMST = 100.46061837 + 36000.770053608 * T + 0.000387933 * T**2 - (T**3 / 38710000.0)
    GMST = GMST % 360.0
    GMST_rad = math.radians(GMST)
    
    return GMST_rad


def cartesianA_list(data, time):
    diff = 720100000000#high start number
    theIndex = 0
    i = 0
    for index, row in data.iterrows():
        if (row["Datetime"] <= time) and ((time-row["Datetime"]).total_seconds() <= diff):
            theIndex = i
            diff = (time-row["Datetime"]).total_seconds()
        i += 1
    
    tk = TK(diff)
    row = data.iloc[theIndex]
    satelite_id = row["satelite_id"]
    Mk = MK(row["M0"],row["sqrt(A)"]**2, row["Delta n0"], tk)
    Ek = EK(Mk,row["e"],6)
    fk = FK(row["e"],Ek)
    uk = UK(row["omega"], fk,row["C_uc"],row["C_us"])
    rk = RK(row["sqrt(A)"]**2, row["e"], row["omega"], Ek,fk, row["C_rc"],row["C_us"])
    ik = IK(row["i0"],row["IDOT"],tk,row["C_ic"],row["omega"],fk,row["C_is"])
    lambdak= LAMBDAK(row["OMEGA0"],row["OMEGA DOT"], we,tk,row["T_oe"])

    rkM = np.array([rk,0,0]).transpose()
    coordinates = R3(-lambdak)@R1(-ik)@R3(-uk)@rkM
    return [satelite_id,time.strftime("%Y-%m-%dT%H:%M:%S.%f"), coordinates[0], coordinates[1],coordinates[2]]

def cartesianC_list(data, time, today, i):
    diff = 18000000000000
    prevRow = []
    endRow = []
    time = time #UTC to GLONASS time - timedelta(hours=3)
    if not today:#vanlig
        if not data.empty:
            for index, row in data.iterrows():
                if (row["Datetime"] <= time) and ((time-row["Datetime"]).total_seconds() <= diff):
                    diff = (time-row["Datetime"]).total_seconds()
                    row["Datetime"] = row["Datetime"]
                    midnight = pd.Timestamp(row["Datetime"].year, row["Datetime"].month, row["Datetime"].day)
                    te = (row["Datetime"] - midnight).total_seconds()
                    #print(f"newTime: {newTime}, te: {te}, diff: {diff}")
                    thetaG0 = gmst_at_midnight(time.year, time.month, time.day) #rad
                    theta_Gc = thetaG0 + 0.7292115*10**(-4) *(row['a2']-3*3600)#rad
                    # x = (row["X"] * np.cos(theta_Gc)  - row["Y"] * np.sin(theta_Gc))*1000 -0.36
                    # y = (row["X"] * np.sin(theta_Gc) + row["Y"] * np.cos(theta_Gc))*1000 + 0.08
                    # z = (row["Z"])*1000 + 0.18
                    x = (row["X"])*1000 - 0.36
                    y = (row["Y"])*1000 + 0.08
                    z = (row["Z"])*1000 + 0.18
                    endRow = [row["satelite_id"],time.strftime("%Y-%m-%dT%H:%M:%S.%f"), x, y,z]
    else:#today

        timeBack = time - timedelta(hours= 11, minutes = 15 , seconds=44)
        if not data.empty:
            for index, row in data.iterrows():
                if (row["Datetime"] <= timeBack) and ((timeBack-row["Datetime"]).total_seconds() <= diff):
                    diff = (time-row["Datetime"]).total_seconds()
                    row["Datetime"] = row["Datetime"] 
                    midnight = pd.Timestamp(row["Datetime"].year, row["Datetime"].month, row["Datetime"].day)
                    te = (row["Datetime"] - midnight).total_seconds()
                    #print(f"newTime: {newTime}, te: {te}, diff: {diff}")

                    thetaG0 = gmst_at_midnight(time.year, time.month, time.day) #rad
                    theta_Gc = thetaG0 + 0.7292115*10**(-4) *(row['a2']- 3*3600)#rad

                    # x = (row["X"] * np.cos(theta_Gc)  - row["Y"] * np.sin(theta_Gc))*1000 -0.36
                    # y = (row["X"] * np.sin(theta_Gc) + row["Y"] * np.cos(theta_Gc))*1000 + 0.08
                    # z = (row["Z"])*1000 + 0.18
                    x = (row["X"])*1000 -0.36
                    y = (row["Y"])*1000 + 0.08
                    z = (row["Z"])*1000 + 0.18
                    endRow = [row["satelite_id"],time.strftime("%Y-%m-%dT%H:%M:%S.%f"), x, y,z]
    
    return endRow

def BeiDou(data, time,usedrows):
    diff = 720100000000
    theIndex = 0
    i = 0
    for index, row in data.iterrows():
        if (row["Datetime"] <= time) and ((time-row["Datetime"]).total_seconds() <= diff):
            theIndex = i
            diff = (time-row["Datetime"]).total_seconds()
        i += 1
    
    tk = TK(diff)
    row = data.iloc[theIndex]
  
    satelite_id = row["satelite_id"]
    Mk = MK(row["M0"],row["sqrt(A)"]**2, row["Delta n0"], tk)
    Ek = EK(Mk,row["e"],6)
    fk = FK(row["e"],Ek)
    uk = UK(row["omega"], fk,row["C_uc"],row["C_us"])
    rk = RK(row["sqrt(A)"]**2, row["e"], row["omega"], Ek,fk, row["C_rc"],row["C_us"])
    ik = IK(row["i0"],row["IDOT"],tk,row["C_ic"],row["omega"],fk,row["C_is"])
    lambdak= LAMBDAK(row["OMEGA0"],row["OMEGA DOT"], we,tk,row["T_oe"])

    rkM = np.array([rk,0,0]).transpose()
    coordinates = R3(-lambdak)@R1(-ik)@R3(-uk)@rkM

    usedrows.loc[len(usedrows)] = [row["satelite_id"],row["Datetime"],time.strftime("%Y-%m-%dT%H:%M:%S.%f"),diff,tk,coordinates[0], coordinates[1],coordinates[2]]
    return [satelite_id,time.strftime("%Y-%m-%dT%H:%M:%S.%f"), coordinates[0], coordinates[1],coordinates[2]]

#kommer annenhver time 7200 sek
# def cartesianB_list(data, time, today):
#     #obs = pd.read_csv("test/test1.csv")
#     diff = 7201000000
#     theIndex = 0
#     i = 0
#     #find the Datetime that is closes to time, but the datetime has to beback in time compared to time
#     for index, row in data.iterrows():
#         if (row["Datetime"] < time) and ((time-row["Datetime"]).total_seconds() < diff):
#             theIndex = i
#             diff = (time-row["Datetime"]).total_seconds()
#         i += 1
#     row = data.iloc[theIndex]
#     satelite_id = row["satelite_id"]
#     #sjekk om denne satelittiden eksisterer i obs
#     # if satelite_id in obs['Satellitenumber'].values:
#     #     obsRow = obs.loc[obs['Satellitenumber'] == satelite_id]
#     #     diffe = float(diff - (obsRow['P']/c) + obsRow['dt'])
        
#     #     tk = TK(diffe)
#     # else:
#     #     tk = TK(diff)
#     tk = TK(diff )
#     Mk = MK(row["M0"],row["sqrt(A)"]**2, row["Delta n0"], tk)
#     Ek = EK(Mk,row["e"],3)
#     fk = FK(row["e"],Ek)
#     uk = UK(row["omega"], fk,row["C_uc"],row["C_us"])
#     rk = RK(row["sqrt(A)"]**2, row["e"], row["omega"], Ek,fk, row["C_rc"],row["C_us"])
#     ik = IK(row["i0"],row["IDOT"],tk,row["C_ic"],row["omega"],fk,row["C_is"])
#     lambdak= LAMBDAK(row["OMEGA0"],row["OMEGA DOT"], we,tk,row["T_oe"])
#     rkM = np.array([rk,0,0]).transpose()
#     coordinates = R3(-lambdak)@R1(-ik)@R3(-uk)@rkM 


#     return [satelite_id, time.strftime("%Y-%m-%dT%H:%M:%S.%f") , coordinates[0], coordinates[1],coordinates[2]] 

def get_satellite_positions(data,gnss,time):
    data['Datetime'] = pd.to_datetime(data['Datetime'])
    #chech if time is the same day as data[datetime]
    if not data.empty:
        today = (time.date() != data.iloc[0]['Datetime'].date())
    else:
        today = False
    days = 0

    if(today):
        days = (time.date() - data.iloc[0]['Datetime'].date()).days
    dataGrouped = data.groupby("satelite_id")
    positions = pd.DataFrame(columns = ["satelite_id","time", "X", "Y", "Z" ])
    if(gnss == "GPS") or (gnss == "Galileo") or(gnss == "BeiDou") or (gnss == "QZSS") or (gnss == "NavIC"):
        for key, group in dataGrouped:
            xyz = cartesianA_list(group, time)
            if(xyz != []):
                positions.loc[len(positions)] = xyz
    elif(gnss == "GLONASS") or (gnss == "SBAS"):
        for key, group in dataGrouped:
            xyz = cartesianC_list(group, time, today, days)
            if(xyz != []):
                positions.loc[len(positions)] = xyz


    return positions

#testing

# def get_satellite_positiontest(data,gnss,time):
#     data['Datetime'] = pd.to_datetime(data['Datetime'])
#     dataGrouped = data.groupby("satelite_id")
#     time = pd.to_datetime(time)
#     positions = pd.DataFrame(columns = ["satelite_id","TOW", "X", "Y", "Z" ])
#     if(gnss == "GPS") or (gnss == "Galileo"):
#         for key, group in dataGrouped:
#             if(cartesianA_list(group, time) != []):
#                 positions.loc[len(positions)] = cartesianA_list(group, time)
#     elif(gnss == "GLONASS") or (gnss == "SBAS"):
#         for key, group in dataGrouped:
#             if(cartesianC_list(group, time) != []):
#                 positions.loc[len(positions)] = cartesianC_list(group, time)
#     elif(gnss == "BeiDou") or (gnss == "QZSS") or (gnss == "IRNSS"):
#         for key, group in dataGrouped:
#             if(cartesianB_list(group, time) != []):
#                 positions.loc[len(positions)] = cartesianB_list(group, time)
#     return positions

# GLONASSData = pd.read_csv('DataFrames/289/structured_dataR.csv')
# r01 = GLONASSData.loc[GLONASSData['satelite_id'] == 'R01']
# r01['Datetime'] = pd.to_datetime(r01['Datetime'] )
# cartesianC_list(r01, pd.to_datetime("2024-10-15T12:12:02.000"), True)