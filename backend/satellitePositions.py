import pandas as pd
import numpy as np
from datetime import timedelta, datetime
from common_variables import GM,we


def TK(t: float) -> float:
    """
    Time correction based on GPS week rollover.
    """
    tm = t
    if(t >302400):
        return tm-604800
    elif(t <-302400 ):
        return tm+604800
    else:
        return tm

def MK(M0: float, a: float, deltan: float, tk: float) -> float:
    """
    Mean anomaly computation.
    """
    return M0 + (np.sqrt(GM/a**3)+deltan)*tk


def EK(Mk: float, e: float, n: int) -> float:
    """
    Eccentric anomaly computation using iterative approach.
    """
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


def FK(e: float, Ek: float) -> float:
    """
    Converts eccentric anomaly (Ek) to true anomaly (fk) using eccentricity (e).
    """
    return 2 * np.arctan(np.sqrt((1 + e) / (1 - e)) * np.tan(Ek / 2))

def UK(w: float, fk: float, Cuc: float, Cus: float):
    """
    Computes the argument of latitude (uk) with corrections.
    """
    return w + fk + Cuc * (np.cos(2 * (w + fk))) + Cus * (np.sin(2 * (w + fk)))

def RK(a: float, e: float, w: float, Ek: float, fk: float, Crc: float, Crs: float) -> float:
    """
    Computes the corrected radius (rk).
    """
    return a * (1 - e * np.cos(Ek)) + Crc * (np.cos(2 * (w + fk))) + Crs * (np.sin(2 * (w + fk)))

def IK(i0: float, idot: float, tk: float, Cic: float, w: float, fk: float, Cis: float) -> float:
    """
    Computes the corrected inclination (ik).
    """
    return i0 + idot * tk + Cic * (np.cos(2 * (w + fk))) + Cis * (np.sin(2 * (w + fk)))

def LAMBDAK(lambda0: float, omegadot: float, we: float, tk: float, toe: float) -> float:
    """
    Computes corrected longitude of the ascending node (lambda_k).
    """
    return lambda0 + (omegadot - we) * tk - we * toe

def R1(theta: float) -> np.ndarray[float]:
    """
    Rotation matrix around X-axis (R1).
    """
    return np.array([
        [1,        0,            0       ],
        [0,  np.cos(theta), np.sin(theta)],
        [0, -np.sin(theta), np.cos(theta)]
    ])


def R3(theta: float) -> np.ndarray[float]:
    """
    Rotation matrix around Z-axis (R3).
    """
    return np.array([
        [ np.cos(theta), np.sin(theta), 0],
        [-np.sin(theta), np.cos(theta), 0],
        [       0,            0,        1]
    ])

def get_closest_row(data: pd.DataFrame, time: datetime) -> pd.DataFrame:
    """
    Finds the row in DataFrame closest in time to the given timestamp.
    """
    if data.empty:
        return None
    differences = (time - data["Datetime"]).abs()
    return data.loc[differences.idxmin()]


def cartesianA_list(data: pd.DataFrame, time: datetime) -> list[ str, str, float, float, float ]:
    """
    Computes satellite ECEF coordinates from broadcast ephemeris (for GPS, Galileo, BeiDou, QZSS, NavIC).
    """
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


def cartesianC_list(data: pd.DataFrame, time: datetime, is_today: bool) -> list[ str, str, float, float, float ]:
    """
    Computes satellite ECEF coordinates frombroadcast ephemeris  (GLONASS, SBAS).
    """
    if data.empty:
        return []

    # Adjust for data timestamp offset if needed
    timeBack = time - timedelta(hours=11, minutes=15, seconds=44) if is_today else time
    row = get_closest_row(data,timeBack)

    # Compute GMST
    #thetaG0 = gmst_at_midnight(time.year, time.month, time.day)
    #theta_Gc = thetaG0 + 0.7292115 * 10**(-4) * (row['a2'] - 3 * 3600)  # rad

    # Convert to meters and apply known hardware biases
    x = (row["X"]) * 1000 - 0.36
    y = (row["Y"]) * 1000 + 0.08
    z = (row["Z"]) * 1000 + 0.18

    return [row["satelite_id"], time.strftime("%Y-%m-%dT%H:%M:%S.%f"), x, y, z]


def get_satellite_positions(data: pd.DataFrame, gnss: str, time: datetime) -> pd.DataFrame:
    """
    Retrieves positions of all satellites at a given time.
    """
    if data.empty:
        return pd.DataFrame(columns=["satelite_id", "time", "X", "Y", "Z"])

    data["Datetime"] = pd.to_datetime(data["Datetime"])
    is_today = time.date() != data.iloc[0]["Datetime"].date()

    positions = []
    for _, group in data.groupby("satelite_id"):
        if gnss in {"GPS", "Galileo", "BeiDou", "QZSS", "NavIC"}:
            xyz = cartesianA_list(group, time)
        else:
            xyz = cartesianC_list(group, time, is_today)
        if xyz:
            positions.append(xyz)

    return pd.DataFrame(positions, columns=["satelite_id", "time", "X", "Y", "Z"])


# Testing
if __name__ == '__main__':

    def get_satellite_positiontest(data,gnss,time):
        data['Datetime'] = pd.to_datetime(data['Datetime'])
        dataGrouped = data.groupby("satelite_id")
        time = pd.to_datetime(time)
        positions = pd.DataFrame(columns = ["satelite_id","TOW", "X", "Y", "Z" ])
        is_today = time.date() != data.iloc[0]["Datetime"].date()
        if(gnss == "GPS") or (gnss == "Galileo"):
            for key, group in dataGrouped:
                if(cartesianA_list(group, time) != []):
                    positions.loc[len(positions)] = cartesianA_list(group, time)
        elif(gnss == "GLONASS") or (gnss == "SBAS"):
            for key, group in dataGrouped:
                if(cartesianC_list(group, time) != []):
                    positions.loc[len(positions)] = cartesianC_list(group, time, is_today)
        # elif(gnss == "BeiDou") or (gnss == "QZSS") or (gnss == "IRNSS"):
        #     for key, group in dataGrouped:
        #         if(cartesianB_list(group, time) != []):
        #             positions.loc[len(positions)] = cartesianB_list(group, time)
        # return positions

        GLONASSData = pd.read_csv('DataFrames/289/structured_dataR.csv')
        r01 = GLONASSData.loc[GLONASSData['satelite_id'] == 'R01']
        r01['Datetime'] = pd.to_datetime(r01['Datetime'] )
        cartesianC_list(r01, pd.to_datetime("2024-10-15T12:12:02.000"), True)