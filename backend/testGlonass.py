import json

from matplotlib import pyplot as plt
import numpy as np
import gnsstoolbox.orbits as orbits
import pandas as pd

# # Opprett en instans av Orbit-klassen
# orb = orbits.orbit()
# dataframe = pd.read_csv(f"DataFrames/2025/100/structured_dataR.csv")
# gv = dataframe.iloc[0]
# #"2025-04-10T00:30:00"
# # Legg til GLONASS-navigasjonsdata
# def datetime_to_mjd(dt):
#     JD = dt.toordinal() + 1721424.5 + (dt.hour + dt.minute / 60 + dt.second / 3600) / 24
#     return JD - 2400000.5

# #gv['Datetime'] = pd.to_datetime(gv['Datetime'])
# orb.NAV_dataR.append({
#     'PRN': gv['satelite_id'],
#     'epoch': pd.to_datetime(gv['Datetime']),
#     'X': gv['X'],                      # ECEF PZ-90.11 (meter)
#     'Y': gv['Y'],                      # ECEF PZ-90.11 (meter)
#     'Z': gv['Z'],                      # ECEF PZ-90.11 (meter)
#     'X_dot': gv['Vx'],                    # ECEF PZ-90.11 (m/s)
#     'Y_dot': gv['Vy'],                    # ECEF PZ-90.11 (m/s)
#     'Z_dot': gv['Vz'], 
#     'MS_X_acc': gv['ax'],                # ECEF PZ-90.11 (m/s²)    
#     'MS_Y_acc': gv['ay'],                # ECEF PZ-90.11 (m/s²)
#     'MS_Z_acc': gv['az'],                # ECEF PZ-90.11 (m/s²)
#     'SV_clock_offset': gv['a0'],                # Klokkeavvik (sekunder)
#     'SV_relat_freq_offset': gv['a1'],            # Frekvensavvik (dimensjonsløs)
#     'Message_frame_time': gv['a2'],                    # Referansetidspunkt for ephemeride (sekunder siden ukestart)                   # Tidspunkt for klokkeparametere (sekunder siden ukestart)
#     'sv_health': gv['Health'],
#     'freq_num': gv['Frequency number'],   
#     'age_op_inf': gv['Age of operation'], # Alder på informasjonen (sekunder)          
# })
# # Beregn satellittposisjon på ønsket tidspunkt

# mjd = datetime_to_mjd(pd.to_datetime('2025-04-10T00:29:00'))
# X, Y, Z, dte = orb.calcSatCoord('R',gv['satelite_id'],pd.to_datetime('2025-04-10T00:14:00'),None)
# print(X, Y, Z, dte)
# print(orb.NAV_dataR)
# print('MJD:', mjd)
all_data = []
gps_data = []
gpsGalileo_data = []
gpsGalileoBeidou_data = []
gpsGalieoGlonass_data = []
with open('dop_dataAll.json', 'r') as f:
    data = json.load(f)
    all_data = data
    f.close()
with open('dop_dataGPS.json', 'r') as f:
    data = json.load(f)
    gps_data = data
    f.close()
with open('dop_dataGPSGal.json', 'r') as f:
    data = json.load(f)
    gpsGalileo_data = data
    f.close()
with open('dop_dataGPSGalBei.json', 'r') as f:
    data = json.load(f)
    gpsGalileoBeidou_data = data
    f.close()
with open('dop_dataGPSGalGlon.json', 'r') as f:
    data = json.load(f)
    gpsGalieoGlonass_data = data
    f.close()

x_labels = np.linspace(0, 22600, 227)

# plt.plot(x_labels, all_data, label='All GNSS', color='#1f77b4')        # Soft blå
# plt.plot(x_labels, gps_data, label='GPS', color='#ff7f0e')             # Oransje
# plt.plot(x_labels, gpsGalileo_data, label='GPS + Galileo', color='#2ca02c')  # Myk grønn
plt.plot(x_labels, gpsGalileoBeidou_data, label='GPS + Galileo + BeiDou', color='#d62728') # Dempet rød
plt.plot(x_labels, gpsGalieoGlonass_data, label='GPS + Galileo + GLONASS', color='#9467bd') # Lilla

plt.gca().set_facecolor('#faf9f6')   # Bakgrunn inni selve plot-området
plt.gcf().set_facecolor('#faf9f6')   # Bakgrunn utenfor plot-området (hele figuren)
plt.xticks(rotation=45)
plt.title('PDOP values along the road segment with Different constellations')
plt.xlabel('Distance along the road (m)')
plt.ylabel('PDOP value')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()