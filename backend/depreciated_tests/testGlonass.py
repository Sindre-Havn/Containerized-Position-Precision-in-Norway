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

#sammenligne konstellasjoner
# all_data = []
# gps_data = []
# gpsGalileo_data = []
# gpsGalileoBeidou_data = []
# gpsGalieoGlonass_data = []
# with open('dop_dataAll.json', 'r') as f:
#     data = json.load(f)
#     all_data = data
#     f.close()
# with open('dop_dataGPS.json', 'r') as f:
#     data = json.load(f)
#     gps_data = data
#     f.close()
# with open('dop_dataGPSGal.json', 'r') as f:
#     data = json.load(f)
#     gpsGalileo_data = data
#     f.close()
# with open('dop_dataGPSGalBei.json', 'r') as f:
#     data = json.load(f)
#     gpsGalileoBeidou_data = data
#     f.close()
# with open('dop_dataGPSGalGlon.json', 'r') as f:
#     data = json.load(f)
#     gpsGalieoGlonass_data = data
#     f.close()

# x_labels = np.linspace(0, 22600, 227)

# plt.plot(x_labels, all_data, label='All GNSS', color='#1f77b4')        # Soft blå
# plt.plot(x_labels, gps_data, label='GPS', color='#ff7f0e')             # Oransje
# plt.plot(x_labels, gpsGalileo_data, label='GPS + Galileo', color='#2ca02c')  # Myk grønn
# plt.plot(x_labels, gpsGalileoBeidou_data, label='GPS + Galileo + BeiDou', color='#d62728') # Dempet rød
# plt.plot(x_labels, gpsGalieoGlonass_data, label='GPS + Galileo + GLONASS', color='#9467bd') # Lilla

# plt.gca().set_facecolor('#faf9f6')   # Bakgrunn inni selve plot-området
# plt.gcf().set_facecolor('#faf9f6')   # Bakgrunn utenfor plot-området (hele figuren)
# plt.xticks(rotation=45)
# plt.title('PDOP values along the road segment when using constellations')
# plt.xlabel('Distance along the road (m)')
# plt.ylabel('PDOP value')
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()


#sammenligne med og uten terreng
# PDOP_w = []
# PDOP_wout = []

# with open('PDOP_wTerrain.json', 'r') as f:
#     data = json.load(f)
#     onluDop = []
#     for i in data:
#         onluDop.append(i[0][1])
#     PDOP_w = onluDop
#     f.close()
# with open('PDOP_wOutTerrain.json', 'r') as f:
#     data = json.load(f)
#     onluDop = []
#     for i in data:
#         onluDop.append(i[0][1])
#     PDOP_wout = onluDop
#     f.close()


# x_labels = np.linspace(0, 48000, 105)
# diff = []
# for i in range(len(PDOP_w)):
#     diff.append(PDOP_w[i] - PDOP_wout[i])

# plt.plot(x_labels, PDOP_w, label='With Terrain Obstruction', color='#1f77b4')        # Soft blå
# plt.plot(x_labels, PDOP_wout, label='Without Terrain Obstruction', color='#ff7f0e')             # Oransje
# plt.plot(x_labels, diff, label='Difference in DOP', color='#2ca02c')  # Myk grønn

# plt.gca().set_facecolor('#faf9f6')   # Bakgrunn inni selve plot-området
# plt.gcf().set_facecolor('#faf9f6')   # Bakgrunn utenfor plot-området (hele figuren)
# plt.xticks(rotation=45)
# plt.title('PDOP Values With and Without Terrain in Romsdalen')
# plt.xlabel('Distance along the road (m)')
# plt.ylabel('PDOP value')
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()

#sammenligne  sør og nord
# PDOP_sør = []
# PDOP_nord = []

# with open('PDOP_nord.json', 'r') as f:
#     data = json.load(f)
#     PDOP_sør = data
#     f.close()
# with open('PDOP_sør.json', 'r') as f:
#     data = json.load(f)
#     PDOP_nord = data
#     f.close()


# x_labels = np.linspace(0, 7100, 72)

# plt.plot(x_labels, PDOP_nord, label='Northern Norway', color='#d62728')        # Soft blå
# plt.plot(x_labels, PDOP_sør[:72], label='Southern Norway ', color='#9467bd')             # Oransje

# plt.gca().set_facecolor('#faf9f6')   # Bakgrunn inni selve plot-området
# plt.gcf().set_facecolor('#faf9f6')   # Bakgrunn utenfor plot-området (hele figuren)
# plt.xticks(rotation=45)
# plt.title('PDOP Values in South vs North Norway')
# plt.xlabel('Points along the road (m)')
# plt.ylabel('PDOP value')
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()

#sammenligne iløpet av døgnet
# p1 = []
# p2 = []
# p3 = []

# with open('pdop33.json', 'r') as f:
#     data = json.load(f)
#     p1 = data[0]
#     p2 = data[1]
#     p3 = data[2]
#     f.close()



# x_labels = np.linspace(0, 24, 25)

# plt.plot(x_labels, p1, label='Point 1', color='#1f77b4')   # Blå (moderne)
# plt.plot(x_labels, p2, label='Point 2', color='#ff7f0e')   # Oransje (myk)
# plt.plot(x_labels, p3, label='Point 3', color='#2ca02c')   # Grønn

# plt.gca().set_facecolor('#faf9f6')   # Bakgrunn inni selve plot-området
# plt.gcf().set_facecolor('#faf9f6')   # Bakgrunn utenfor plot-området (hele figuren)
# plt.xticks(x_labels)  # 👈 VIKTIG: vis ALLE x-ticks!
# plt.xticks(rotation=45)
# plt.title('PDOP Values Throuth the Day')
# plt.xlabel('Time of Day (hours)')
# plt.ylabel('PDOP value')
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()

import rasterio

with rasterio.open("data/dom10/landsdekkende/64m1_1_10m_z33.tif") as src:
    bounds = src.bounds
    print("Venstre:", bounds.left)
    print("Høyre:", bounds.right)
    print("Nedre:", bounds.bottom)
    print("Øvre:", bounds.top)

    width = bounds.right - bounds.left
    height = bounds.top - bounds.bottom
    print("Bredde (m):", width)
    print("Høyde (m):", height)
    print("Areal (km²):", (width * height) / 1e6)
