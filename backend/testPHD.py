
import pandas as pd
import numpy as np
from computebaner import runData3
import scipy.io as sio



reciever = pd.read_csv("fromPHD/RN05345W1.csv")
recpos1 = reciever.iloc[0]
runData3(["GPS"], "15", "2023-12-11T10:13:34.000", 'test/test4', recpos1)


# recpos2 = reciever.iloc[1]
# runData3(["GPS"], "0", "2023-12-11T10:13:35.000", "test2", recpos2) 


# recpos3 = reciever.iloc[2]
# runData3(["GPS"], "0", "2023-12-11T10:13:36.000",'test3',recpos3)

#read the matlabfile and fine the variables rnx(51).xs{1,1}
fasit = sio.loadmat('fromPHD/RN05345W1_L12.mat')
fasit = fasit['rnx'][50]
fasit = fasit['xs'][0][0][0]

res = pd.read_csv('test/test4.csv')
i = 0
for index,row in res.iterrows():
    print(row)
    x = row['X'] - fasit[i][0]
    y = row['Y']- fasit[i][1]
    z = row['Z']- fasit[i][2]
    if not (row['Satellitenumber'] == "G08" or row['Satellitenumber'] == "G18" or row['Satellitenumber'] == "G23"):
        print(f"Difference to the PHD for {row['Satellitenumber']} \n X: {x} Y: {y} Z: {z}")
        i += 1

        
