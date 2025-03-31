import pandas as pd
import numpy as np
from datetime import timedelta
from common_variables import GM,we

# Time correction based on GPS week rollover
def TK(t):
    tm = t
    if(t >302400):
        return tm-604800
    elif(t <-302400 ):
        return tm+604800
    else:
        return tm
# Mean anomaly computation
def MK(M0, a,deltan, tk):
    return M0 + (np.sqrt(GM/a**3)+deltan)*tk
# Eccentric anomaly computation using iterative approach
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

# Converts eccentric anomaly (Ek) to true anomaly (fk) using eccentricity (e)
def FK(e, Ek):
    return 2 * np.arctan(np.sqrt((1 + e) / (1 - e)) * np.tan(Ek / 2))

# Computes the argument of latitude (uk) with corrections
def UK(w, fk, Cuc, Cus):
    return w + fk + Cuc * (np.cos(2 * (w + fk))) + Cus * (np.sin(2 * (w + fk)))

# Computes the corrected radius (rk)
def RK(a, e, w, Ek, fk, Crc, Crs):
    return a * (1 - e * np.cos(Ek)) + Crc * (np.cos(2 * (w + fk))) + Crs * (np.sin(2 * (w + fk)))

# Computes the corrected inclination (ik)
def IK(i0, idot, tk, Cic, w, fk, Cis):
    return i0 + idot * tk + Cic * (np.cos(2 * (w + fk))) + Cis * (np.sin(2 * (w + fk)))

# Computes corrected longitude of the ascending node (lambda_k)
def LAMBDAK(lambda0, omegadot, we, tk, toe):
    return lambda0 + (omegadot - we) * tk - we * toe

# Rotation matrix around X-axis (R1)
def R1(theta):
    return np.array([
        [1, 0, 0],
        [0, np.cos(theta), np.sin(theta)],
        [0, -np.sin(theta), np.cos(theta)]
    ])

# Rotation matrix around Z-axis (R3)
def R3(theta):
    return np.array([
        [np.cos(theta), np.sin(theta), 0],
        [-np.sin(theta), np.cos(theta), 0],
        [0, 0, 1]
    ])

# Finds the row in DataFrame closest in time to the given timestamp
def get_closest_row(data, time):
    if data.empty:
        return None
    differences = (time - data["Datetime"]).abs()
    return data.loc[differences.idxmin()]

# Computes satellite ECEF coordinates from broadcast ephemeris (for GPS, Galileo, BeiDou, QZSS, NavIC)
def cartesianA_list(data, time):
    row = get_closest_row(data, time)
    if row is None:
        return []

    tk = TK((time - row["Datetime"]).total_seconds())  # Time from ephemeris reference
    Mk = MK(row["M0"], row["sqrt(A)"]**2, row["Delta n0"], tk)  # Mean anomaly
    Ek = EK(Mk, row["e"], 6)  # Eccentric anomaly
    fk = FK(row["e"], Ek)  # True anomaly
    uk = UK(row["omega"], fk, row["C_uc"], row["C_us"])  # Argument of latitude
    rk = RK(row["sqrt(A)"]**2, row["e"], row["omega"], Ek, fk, row["C_rc"], row["C_us"])  # Radius
    ik = IK(row["i0"], row["IDOT"], tk, row["C_ic"], row["omega"], fk, row["C_is"])  # Inclination
    lambdak = LAMBDAK(row["OMEGA0"], row["OMEGA DOT"], we, tk, row["T_oe"])  # Longitude of ascending node

    # Position in orbital plane (X = r, Y = 0, Z = 0)
    rkM = np.array([rk, 0, 0]).transpose()

    # Rotate into ECEF frame
    coordinates = R3(-lambdak) @ R1(-ik) @ R3(-uk) @ rkM

    return [row["satelite_id"], time.strftime("%Y-%m-%dT%H:%M:%S.%f"), coordinates[0], coordinates[1], coordinates[2]]

# Computes satellite ECEF coordinates frombroadcast ephemeris  (GLONASS, SBAS)
def cartesianC_list(data, time, today, i):
    if data.empty:
        return []

    # Adjust for data timestamp offset if needed
    timeBack = time - timedelta(hours=11, minutes=15, seconds=44) if today else time
    row = get_closest_row(data,timeBack)

    # Compute GMST
    #thetaG0 = gmst_at_midnight(time.year, time.month, time.day)
    #theta_Gc = thetaG0 + 0.7292115 * 10**(-4) * (row['a2'] - 3 * 3600)  # rad

    # Convert to meters and apply known hardware biases
    x = (row["X"]) * 1000 - 0.36
    y = (row["Y"]) * 1000 + 0.08
    z = (row["Z"]) * 1000 + 0.18

    return [row["satelite_id"], time.strftime("%Y-%m-%dT%H:%M:%S.%f"), x, y, z]

# Retrieves positions of all satellites at a given time
def get_satellite_positions(data,gnss,time):
    if data.empty:
        return pd.DataFrame(columns=["satelite_id", "time", "X", "Y", "Z"])

    data["Datetime"] = pd.to_datetime(data["Datetime"])
    today = time.date() != data.iloc[0]["Datetime"].date()

    positions = []
    for _, group in data.groupby("satelite_id"):
        if gnss in {"GPS", "Galileo", "BeiDou", "QZSS", "NavIC"}:
            xyz = cartesianA_list(group, time)
        else:
            xyz = cartesianC_list(group, time, today,1)
        if xyz:
            positions.append(xyz)

    return pd.DataFrame(positions, columns=["satelite_id", "time", "X", "Y", "Z"])

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