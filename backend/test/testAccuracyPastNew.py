


import math
import pandas as pd
import numpy as np
import re
import ahrs
from datetime import datetime
from dataframes import structured_dataG, structured_dataR, structured_dataE, structured_dataJ, structured_dataC, structured_dataI, structured_dataS

from computebaner import runData2
from computeDOP import DOPvalues

data1,datadf1 = runData2("282",["GPS","GLONASS","BeiDou", "Galileo"], "10", "2024-10-9T20:00:00.000", "2")
data2,datadf2 = runData2("283",["GPS","GLONASS","BeiDou", "Galileo"], "10", "2024-10-9T20:00:00.000", "2")

# print(datadf1)

# print(datadf2)
i = 0
for data in datadf1:
    j= 0
    for df in data:
        for row, index in df.iterrows():
            print(row)
            print(index)
            print("")


