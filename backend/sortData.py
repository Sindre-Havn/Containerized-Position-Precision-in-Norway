
import math
import pandas as pd
import numpy as np
import re
import ahrs
from datetime import datetime
from dataframes import columnsG, columnsR, columnsE, columnsJ, columnsC, columnsI, columnsS
import os
import gzip
import shutil
from downloadfile import lastned

# G: GPS
# R: GLONASS
# E: Galileo
# J: QZSS
# C: BDS
# I: NavIC/IRNSS
# S: SBAS payload


def split_on_second_sign(s):
    signs = [m.start() for m in re.finditer(r'(?<![eE])[+-]', s)]
    if not signs:
        return s

    parts = []
    last_index = 0
    for idx in signs:
        parts.append(s[last_index:idx])  
        last_index = idx 
    parts.append(s[last_index:])
    
    return parts

def flatten(lst):
    flat_list = []
    for item in lst:
        if isinstance(item, (list, tuple)):
            flat_list.extend(item)  
        else:
            flat_list.append(item) 
    return flat_list

def strToFloat(inputstring):
    splittedString = inputstring.split("E")
    num = float(splittedString[0])
    potens = int(splittedString[1])
    return num * 10**potens



def GPSdata(df,satellitt_id,time, values_list, SV):
    df.loc[len(df)]  = [
        satellitt_id,
        time,
        SV[0],
        SV[1],
        SV[2],
        values_list[0],
        values_list[1],
        values_list[2],
        values_list[3],
        values_list[4],
        values_list[5],
        values_list[6],
        values_list[7],
        values_list[8],
        values_list[9],
        values_list[10],
        values_list[11],
        values_list[12],
        values_list[13],
        values_list[14],
        values_list[15],
        values_list[16],
        values_list[17],
        values_list[18],
        values_list[19],
        values_list[20],
        values_list[21],
        values_list[22],
        values_list[23],
        values_list[24],
        values_list[25]
    ]

def GLONASSdata(df,satellitt_id,time, values_list, SV):
    df.loc[len(df)] = [
        satellitt_id,
        time,
        SV[0],
        SV[1],
        SV[2],
        values_list[0],
        values_list[1],
        values_list[2],
        values_list[3],
        values_list[4],
        values_list[5],
        values_list[6],
        values_list[7],
        values_list[8],
        values_list[9],
        values_list[10],
        values_list[11]
    ]

def Galileiodata(df,satellitt_id,time, values_list, SV):
    df.loc[len(df)] = [
        satellitt_id,
        time,
        SV[0],
        SV[1],
        SV[2],
        values_list[0],
        values_list[1],
        values_list[2],
        values_list[3],
        values_list[4],
        values_list[5],
        values_list[6],
        values_list[7],
        values_list[8],
        values_list[9],
        values_list[10],
        values_list[11],
        values_list[12],
        values_list[13],
        values_list[14],
        values_list[15],
        values_list[16],
        values_list[17],
        values_list[18],
        values_list[20],
        values_list[21],
        values_list[22],
        values_list[23],
        values_list[24]
    ]

def QZSSdata(df,satellitt_id,time, values_list, SV):
    
    df.loc[len(df)] = [
        satellitt_id,
        time,
        SV[0],
        SV[1],
        SV[2],
        values_list[0],
        values_list[1],
        values_list[2],
        values_list[3],
        values_list[4],
        values_list[5],
        values_list[6],
        values_list[7],
        values_list[8],
        values_list[9],
        values_list[10],
        values_list[11],
        values_list[12],
        values_list[13],
        values_list[14],
        values_list[15],
        values_list[16],
        values_list[17],
        values_list[18],
        values_list[19],
        values_list[20],
        values_list[21],
        values_list[22],
        values_list[23],
        values_list[24],
        values_list[25]
    ]

def BeiDoudata(df,satellitt_id,time, values_list, SV):

    df.loc[len(df)] = [
        satellitt_id,
        time,
        SV[0],
        SV[1],
        SV[2],
        values_list[0],
        values_list[1],
        values_list[2],
        values_list[3],
        values_list[4],
        values_list[5],
        values_list[6],
        values_list[7],
        values_list[8],
        values_list[9],
        values_list[10],
        values_list[11],
        values_list[12],
        values_list[13],
        values_list[14],
        values_list[15],
        values_list[16],
        values_list[17],
        values_list[18],
        values_list[19],
        values_list[20],
        values_list[21],
        values_list[22],
        values_list[23],
        values_list[24],
        values_list[25]
    ]

def NavICdata(df,satellitt_id,time, values_list, SV):
    df.loc[len(df)] = [
        satellitt_id,
        time,
        SV[0],
        SV[1],
        SV[2],
        values_list[0],
        values_list[1],
        values_list[2],
        values_list[3],
        values_list[4],
        values_list[5],
        values_list[6],
        values_list[7],
        values_list[8],
        values_list[9],
        values_list[10],
        values_list[11],
        values_list[12],
        values_list[13],
        values_list[14],
        values_list[15],
        values_list[16],
        values_list[17],
        values_list[18],
        values_list[19],
        values_list[20],
        values_list[21],
        values_list[22],
        values_list[23],
        values_list[24]
    ]

def SBASdata(df,satellitt_id,time, values_list, SV):
    df.loc[len(df)] = [
        satellitt_id,
        time,
        SV[0],
        SV[1],
        SV[2],
        values_list[0],
        values_list[1],
        values_list[2],
        values_list[3],
        values_list[4],
        values_list[5],
        values_list[6],
        values_list[7],
        values_list[8],
        values_list[9],
        values_list[10],
        values_list[11]
    ]

def sortData(daynumber, date):
    if os.path.exists(f"backend/DataFrames/{daynumber}/structured_dataG.csv"):
        print(f"Data on day {daynumber} already sorted")
        return
    else:
        filename = f'backend/unzipped/BRDC00IGS_R_2024{daynumber}0000_01D_MN.rnx'
        lastned(daynumber)
        #current date
        current_date = date.date()
        #creates new dataFrames, based on the columns from Dataframes
        structured_dataG = pd.DataFrame(columns = columnsG)
        structured_dataR = pd.DataFrame(columns = columnsR) 
        structured_dataE = pd.DataFrame(columns = columnsE) 
        structured_dataJ = pd.DataFrame(columns = columnsJ) 
        structured_dataC = pd.DataFrame(columns = columnsC) 
        structured_dataI = pd.DataFrame(columns = columnsI) 
        structured_dataS = pd.DataFrame(columns = columnsS)
        content = []
        with open(filename, "r") as file:
            print(f"Reading file {filename}")
            content = file.read()

        split_index = content.index("END OF HEADER")
        header_part = content[:split_index] # baneinformasjon
        data_part = content[split_index+13:] #satelitt informasjon

        satellitt_data = re.split(r'(?=[GRJCIS])', data_part)[1:]
        data_for_Galileio = []
        for i in range(0,len(satellitt_data)):
            lines = satellitt_data[i].strip().splitlines()
            satellitt_id = lines[0].split(' ')[0]  # Første linje inneholder satellitt-ID (f.eks. G08)
            if ("R" in satellitt_id) and (len(lines) >4):
                Edata = lines[4:]
                lines = lines[:4]
                #data_for_Galileio += [[Edata[i:i + 8]] for i in range(0, len(Edata), 8)]
                for i in range(0, len(Edata), 8):
                    data_for_Galileio.append(Edata[i:i + 8])
        
            forsteLinje = lines[0].split()[1:]
            values_lines = lines[1:]

            flattened_forstelinje = flatten(list(map(split_on_second_sign, forsteLinje)))

            cleaned_forstelinje = [item for item in flattened_forstelinje if item != '']
            values_list = []
            for line in values_lines:
                flattenedLine = flatten(list(map(split_on_second_sign, line.split())))
                cleanedLine = [item for item in flattenedLine if item != '']
                while len(cleanedLine)<4:
                    cleanedLine.append(np.nan)
                values_list += cleanedLine

            time = datetime(int(cleaned_forstelinje[0]),int(cleaned_forstelinje[1]), int(cleaned_forstelinje[2]), int(cleaned_forstelinje[3]), int(cleaned_forstelinje[4]), int(cleaned_forstelinje[5]))
            
            #output_folder = cleaned_forstelinje[0] +'-'+ cleaned_forstelinje[1] +'-'+ cleaned_forstelinje[2]
            SV = cleaned_forstelinje[6:]

            for i in range(len(SV)):
                value = SV[i]
                floatNumber = strToFloat(value)
                SV[i] = floatNumber
            for j in range(len(values_list)):
                value = values_list[j]
                if isinstance(value, str):
                    floatNumber = strToFloat(value)
                    values_list[j] = floatNumber
            
            if time.date() == current_date:
                if "G" in satellitt_id:
                    GPSdata(structured_dataG,satellitt_id,time,values_list, SV)
                elif "R" in satellitt_id:
                    GLONASSdata(structured_dataR ,satellitt_id,time,values_list, SV)
                elif "J" in satellitt_id:
                    QZSSdata(structured_dataJ,satellitt_id,time,values_list, SV)
                elif "C" in satellitt_id:
                    BeiDoudata(structured_dataC,satellitt_id,time,values_list, SV)
                elif "I" in satellitt_id:
                    NavICdata(structured_dataI,satellitt_id,time,values_list, SV)
                elif "S" in satellitt_id:
                    SBASdata(structured_dataS,satellitt_id,time,values_list, SV)


        for i in range(0,len(data_for_Galileio)):
            lines = data_for_Galileio[i]
            satellitt_id = lines[0].split(' ')[0]  
            forsteLinje = lines[0].split()[1:]
            values_lines = lines[1:]

            flattened_forstelinje = flatten(list(map(split_on_second_sign, forsteLinje)))

            cleaned_forstelinje = [item for item in flattened_forstelinje if item != '']
            values_list = []
            for line in values_lines:
                flattenedLine = flatten(list(map(split_on_second_sign, line.split())))
                cleanedLine = [item for item in flattenedLine if item != '']
                while len(cleanedLine)<4:
                    cleanedLine.append(np.nan)
                values_list += cleanedLine

            time = datetime(int(cleaned_forstelinje[0]),int(cleaned_forstelinje[1]), int(cleaned_forstelinje[2]), int(cleaned_forstelinje[3]), int(cleaned_forstelinje[4]), int(cleaned_forstelinje[5]))
            
            SV = cleaned_forstelinje[6:]

            for i in range(len(SV)):
                value = SV[i]
                floatNumber = strToFloat(value)
                SV[i] = floatNumber
            for j in range(len(values_list)):
                value = values_list[j]
                if isinstance(value, str):
                    floatNumber = strToFloat(value)
                    values_list[j] = floatNumber
            if time.date() == current_date:
                Galileiodata(structured_dataE,satellitt_id,time,values_list, SV)

        print(f"Processing at {time}")
        output_folder = "backend/DataFrames/"+daynumber
        os.makedirs(output_folder, exist_ok=True)
        file_pathG = os.path.join(output_folder, "structured_dataG.csv")
        structured_dataG.to_csv(file_pathG, index=False)
        file_pathR = os.path.join(output_folder, "structured_dataR.csv")
        structured_dataR.to_csv(file_pathR, index=False)
        file_pathE = os.path.join(output_folder, "structured_dataE.csv")
        structured_dataE.to_csv(file_pathE, index=False)
        file_pathJ = os.path.join(output_folder, "structured_dataJ.csv")
        structured_dataJ.to_csv(file_pathJ, index=False)
        file_pathC = os.path.join(output_folder, "structured_dataC.csv")
        structured_dataC.to_csv(file_pathC, index=False)
        file_pathI = os.path.join(output_folder, "structured_dataI.csv")
        structured_dataI.to_csv(file_pathI, index=False)
        file_pathS = os.path.join(output_folder, "structured_dataS.csv")
        structured_dataS.to_csv(file_pathS, index=False)


    
