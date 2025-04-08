from pyubx2 import UBXReader
import datetime
import numpy as np

print(np.sin(180))
print(np.sin(np.pi))
# Åpne en .ubx-fil i binær lesemodus
# with open("data/bilinnsamling/NedRomsdalen.ubx", "rb") as ubx_file:
#     ubr = UBXReader(ubx_file)
#     messages = []
#     for (raw_data, parsed_data) in ubr:
#         # Bare fortsett hvis det er en kjent melding
#         if parsed_data.identity:
#             messages.append(parsed_data.identity)
#             # print(f"Parsed Data: {parsed_data}")
#             # print("---")

#             # # Eksempel: hente tid og posisjon fra NAV-PVT-meldinger
#             # if parsed_data.identity == "NAV-PVT":
#             #     timestamp = datetime.datetime(
#             #         parsed_data.year, parsed_data.month, parsed_data.day,
#             #         parsed_data.hour, parsed_data.min, parsed_data.second
#             #     )
#             #     lat = parsed_data.lat / 1e7  # grader
#             #     lon = parsed_data.lon / 1e7  # grader
#             #     alt = parsed_data.hMSL / 1000  # meter

#             #     #print(f"Time: {timestamp} | Lat: {lat}, Lon: {lon}, Alt: {alt}")

#             # if parsed_data.identity == "NAV-DOP":
#             #     iTOW = parsed_data.iTOW #GPS time of weak (ms)
#             #     gDOP = parsed_data.gDOP / 100.0
#             #     pDOP = parsed_data.pDOP / 100.0
#             #     tDOP = parsed_data.tDOP / 100.0
#             #     vDOP = parsed_data.vDOP / 100.0
#             #     hDOP = parsed_data.hDOP / 100.0
#             #     nDOP = parsed_data.nDOP / 100.0
#             #     eDOP = parsed_data.eDOP / 100.0
#             #     print(f'iTOW: {iTOW}, gDOP: {gDOP}, pDOP: {pDOP}, tDOP: {tDOP}, vDOP: {vDOP}, hDOP: {hDOP}, nDOP: {nDOP}, eDOP: {eDOP}')
#             #     print("---")

#     print(f"Type meldinger: {set(messages)}")          # Unique message types
#     print(f"Antall meldinger: {len(messages)}") 
