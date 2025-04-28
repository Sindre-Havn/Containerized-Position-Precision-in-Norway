import gnsstoolbox.orbits as orbits
import pandas as pd

# Opprett en instans av Orbit-klassen
orb = orbits.orbit()
dataframe = pd.read_csv(f"DataFrames/2025/100/structured_dataR.csv")
gv = dataframe.iloc[0]
#"2025-04-10T00:30:00"
# Legg til GLONASS-navigasjonsdata
def datetime_to_mjd(dt):
    JD = dt.toordinal() + 1721424.5 + (dt.hour + dt.minute / 60 + dt.second / 3600) / 24
    return JD - 2400000.5

#gv['Datetime'] = pd.to_datetime(gv['Datetime'])
orb.NAV_dataR.append({
    'PRN': gv['satelite_id'],
    'epoch': pd.to_datetime(gv['Datetime']),
    'X': gv['X'],                      # ECEF PZ-90.11 (meter)
    'Y': gv['Y'],                      # ECEF PZ-90.11 (meter)
    'Z': gv['Z'],                      # ECEF PZ-90.11 (meter)
    'X_dot': gv['Vx'],                    # ECEF PZ-90.11 (m/s)
    'Y_dot': gv['Vy'],                    # ECEF PZ-90.11 (m/s)
    'Z_dot': gv['Vz'], 
    'MS_X_acc': gv['ax'],                # ECEF PZ-90.11 (m/s²)    
    'MS_Y_acc': gv['ay'],                # ECEF PZ-90.11 (m/s²)
    'MS_Z_acc': gv['az'],                # ECEF PZ-90.11 (m/s²)
    'SV_clock_offset': gv['a0'],                # Klokkeavvik (sekunder)
    'SV_relat_freq_offset': gv['a1'],            # Frekvensavvik (dimensjonsløs)
    'Message_frame_time': gv['a2'],                    # Referansetidspunkt for ephemeride (sekunder siden ukestart)                   # Tidspunkt for klokkeparametere (sekunder siden ukestart)
    'sv_health': gv['Health'],
    'freq_num': gv['Frequency number'],   
    'age_op_inf': gv['Age of operation'], # Alder på informasjonen (sekunder)          
})
# Beregn satellittposisjon på ønsket tidspunkt

mjd = datetime_to_mjd(pd.to_datetime('2025-04-10T00:29:00'))
X, Y, Z, dte = orb.calcSatCoord('R',gv['satelite_id'],pd.to_datetime('2025-04-10T00:14:00'),None)
print(X, Y, Z, dte)
print(orb.NAV_dataR)
print('MJD:', mjd)
