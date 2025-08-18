import pandas as pd
import numpy as np
import re
from datetime import datetime
import os
from download_rinex import download_rinex

"""
This module reads a rinex (version 4 / BRD4 file),
and sorts the relevant ephemeris data into csv files for each GNSS.

"""


# G: GPS
# R: GLONASS
# E: Galileo
# J: QZSS
# C: BDS
# I: NavIC/IRNSS
# S: SBAS payload
columnsG = [
    "type",
    "satelite_id",
    "Datetime",
    "C_rs",
    "Delta n0",
    "M0",
    "C_uc",
    "e",
    "C_us",
    "sqrt(A)",
    "T_oe",
    "C_ic",
    "OMEGA0",
    "C_is",
    "i0",
    "C_rc",
    "omega",
    "OMEGA DOT",
    "IDOT",
    "t_tm",
]

def GPSdata(df: pd.DataFrame, satellitt_id: str, time: datetime, values_list: list[float], clk_corr: list[float], nav_msg_type: str) -> list:
    if nav_msg_type == 'LNAV':
        df.loc[len(df)]  = [
            nav_msg_type,
            satellitt_id,
            time,
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
            values_list[24],
        ]
    # if nav_msg_type == 'CNAV':
    #     df.loc[len(df)]  = [
    #         nav_msg_type,
    #         satellitt_id,
    #         time,
    #         values_list[1],
    #         values_list[2],
    #         values_list[3],
    #         values_list[4],
    #         values_list[5],
    #         values_list[6],
    #         values_list[7],
    #         values_list[8],
    #         values_list[9],
    #         values_list[10],
    #         values_list[11],
    #         values_list[12],
    #         values_list[13],
    #         values_list[14],
    #         values_list[15],
    #         values_list[16],
    #         values_list[28],
    #     ]
    # elif nav_msg_type == 'CNV2':
    #     df.loc[len(df)]  = [
    #         nav_msg_type,
    #         satellitt_id,
    #         time,
    #         values_list[1],
    #         values_list[2],
    #         values_list[3],
    #         values_list[4],
    #         values_list[5],
    #         values_list[6],
    #         values_list[7],
    #         values_list[8],
    #         values_list[9],
    #         values_list[10],
    #         values_list[11],
    #         values_list[12],
    #         values_list[13],
    #         values_list[14],
    #         values_list[15],
    #         values_list[16],
    #         values_list[30],
    #     ]

columnsR = [
    "satelite_id",
    "Datetime",
    "a0",
    "a1",
    "a2",
    "X",
    "Vx",
    "ax",
    "Health",
    "Y",
    "Vy",
    "ay",
    "Frequency number",
    "Z",
    "Vz",
    "az",
    "Age of operation",
]

def GLONASSdata(df: pd.DataFrame, satellitt_id: str, time: datetime, values_list: list[float], clk_corr: list[float], nav_msg_type: str) -> list:
    df.loc[len(df)] = [
        satellitt_id,
        time,
        clk_corr[0],
        clk_corr[1],
        clk_corr[2],
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
columnsE = [
    "satelite_id",
    "Datetime",
    "C_rs",
    "Delta n0",
    "M0",
    "C_uc",
    "e",
    "C_us",
    "sqrt(A)",
    "T_oe",
    "C_ic",
    "OMEGA0",
    "C_is",
    "i0",
    "C_rc",
    "omega",
    "OMEGA DOT",
    "IDOT",
    "Data source",
    "GAL Week",
    "SISA signal",
    "clk_corr health",
    "BGDa",
    "BGDb",
    "t_tm"
]

def Galileiodata(df: pd.DataFrame, satellitt_id: str, time: datetime, values_list: list[float], clk_corr: list[float], nav_msg_type: str) -> list:
    df.loc[len(df)] = [
        satellitt_id,
        time,
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
columnsJ = [
    "type",
    "satelite_id",
    "Datetime",
    "C_rs",
    "Delta n0",
    "M0",
    "C_uc",
    "e",
    "C_us",
    "sqrt(A)",
    "T_oe",
    "C_ic",
    "OMEGA0",
    "C_is",
    "i0",
    "C_rc",
    "omega",
    "OMEGA DOT",
    "IDOT",
    "t_tm",
]
def QZSSdata(df: pd.DataFrame, satellitt_id: str, time: datetime, values_list: list[float], clk_corr: list[float], nav_msg_type: str) -> list:
    if nav_msg_type == 'LNAV':
        df.loc[len(df)] = [
            nav_msg_type,
            satellitt_id,
            time,
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
            values_list[24],
        ]
    elif nav_msg_type == 'CNAV':
        df.loc[len(df)] = [
            nav_msg_type,
            satellitt_id,
            time,
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
            values_list[28],
        ]
    elif nav_msg_type == 'CNV2':
        df.loc[len(df)] = [
            nav_msg_type,
            satellitt_id,
            time,
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
            values_list[30],
        ]
columnsC = [
    "type",
    "satelite_id",
    "Datetime",
    "C_rs",
    "Delta n0",
    "M0",
    "C_uc",
    "e",
    "C_us",
    "sqrt(A)",
    "T_oe",
    "C_ic",
    "OMEGA0",
    "C_is",
    "i0",
    "C_rc",
    "omega",
    "OMEGA DOT",
    "IDOT",
    "t_tm",

]
def BeiDoudata(df: pd.DataFrame, satellitt_id: str, time: datetime, values_list: list[float], clk_corr: list[float], nav_msg_type: str) -> list:
    if nav_msg_type == 'D1' or nav_msg_type == 'D2':
        df.loc[len(df)] = [
            nav_msg_type,
            satellitt_id,
            time,
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
            values_list[16],#idot
            values_list[24],#tm

        ]
    elif nav_msg_type == 'CNV1' or nav_msg_type == 'CNV2':
        df.loc[len(df)] = [
            nav_msg_type,
            satellitt_id,
            time,
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
            values_list[16],#idot
            values_list[31],
        ]
    elif nav_msg_type == 'CNV3':
        df.loc[len(df)] = [
            nav_msg_type,
            satellitt_id,
            time,
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
            values_list[16],#idot
            values_list[28],
        ]
columnsI = [
    "satelite_id",
    "Datetime",
    "a0",
    "a1",
    "a2",
    "IODEC",
    "C_rs",
    "Delta n0",
    "M0",
    "C_uc",
    "e",
    "C_us",
    "sqrt(A)",
    "T_oe",
    "C_ic",
    "OMEGA0",
    "C_is",
    "i0",
    "C_rc",
    "omega",
    "OMEGA DOT",
    "IDOT",
    "Spare1",
    "IRN Week",
    "Spare2",
    "User Range accurracy",
    "Health",
    "TGD",
    "Spare3",
    "t_tm"
]
def NavICdata(df: pd.DataFrame, satellitt_id: str, time: datetime, values_list: list[float], clk_corr: list[float], nav_msg_type: str) -> list:
    df.loc[len(df)] = [
        satellitt_id,
        time,
        clk_corr[0],
        clk_corr[1],
        clk_corr[2],
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
columnsS = [
    "satelite_id",
    "Datetime",
    "a0",
    "a1",
    "a2",
    "X",
    "Vx",
    "ax",
    "Health",
    "Y",
    "Vy",
    "ay",
    "Accurracy code",
    "Z",
    "Vz",
    "az",
    "IODN"
]
def SBASdata(df: pd.DataFrame, satellitt_id: str, time: datetime, values_list: list[float], clk_corr: list[float], nav_msg_type: str) -> list:
    df.loc[len(df)] = [
        satellitt_id,
        time,
        clk_corr[0],
        clk_corr[1],
        clk_corr[2],
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

def split_on_second_sign(s: str) -> str | list[str]:
    """
    Split up string where there is not a scientific number-notation.
    Used to seperate adjacent numbers packet to close together in the rinex file.
    """
    signs = [m.start() for m in re.finditer(r'(?<![eE])[+-]', s)] # Regex equivalent to: match any + or - after anything except e or E.
    if not signs:
        return s

    parts = []
    last_index = 0
    for idx in signs:
        parts.append(s[last_index:idx])  
        last_index = idx 
    parts.append(s[last_index:])
    
    return parts

def flatten(lst: list) -> list:
    """
    Flattens lists or tuples inside list.
    """
    flat_list = []
    for item in lst:
        if isinstance(item, (list, tuple)):
            flat_list.extend(item)  
        else:
            flat_list.append(item) 
    return flat_list

def str2float(inputstring: str) -> float:
    """
    Converts from scientific notation to python float.
    """
    splittedString = inputstring.split("e")
    num = float(splittedString[0])
    potens = int(splittedString[1])
    return num * 10**potens

def update_navigation_message_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    Update the navigation message type for each satellite ID to the last type encountered.
    """
    result_list = []
    for _, sat_group in df.groupby('satelite_id'): # _= sat_id
        last_type = sat_group['type'].iloc[-1]
        # Get the last type for each satellite ID
        filtered = sat_group[sat_group['type'] == last_type]
        result_list.append(filtered)
        
    new_df = pd.concat(result_list, ignore_index=True)
    return new_df


def sort_rinex(daynumber: str, date: datetime) -> None:
    """
    Extracts ephemeris data from rinex file, and store it in a csv file to their
    corresponding GNSS.
    """
  
    if os.path.exists(f'ephemeris/{date.year}_{daynumber}/structured_dataG.csv'):
        #print(f"Data on day {daynumber} already sorted")
        return
    
    rinex_path = download_rinex(daynumber, date.year)
    content = []
    with open(rinex_path, "r") as file:
        content = file.read()

    split_index = content.index("END OF HEADER")
    # header_part = content[:split_index]  # orbit information
    data_part = content[split_index+13:] # satellite information

    current_date = date.date()
    satellitt_data = re.split(r'\s*> EPH\s*', data_part)
    
    # Creates empty dataFrames, based on the columns from Dataframes
    structured_dataG = pd.DataFrame(columns = columnsG)
    structured_dataR = pd.DataFrame(columns = columnsR) 
    structured_dataE = pd.DataFrame(columns = columnsE) 
    structured_dataJ = pd.DataFrame(columns = columnsJ) 
    structured_dataC = pd.DataFrame(columns = columnsC) 
    structured_dataI = pd.DataFrame(columns = columnsI) 
    structured_dataS = pd.DataFrame(columns = columnsS)

    # Build DataFrames for each GNSS
    for i in range(1,len(satellitt_data)-1):
        lines = satellitt_data[i].strip().splitlines()
        satellitt_id = lines[0].split(' ')[0] 
        nav_msg_type = lines[0].split()[1]
    
        flattened_firstline = flatten(list(map(split_on_second_sign, lines[1].split()[1:])))
        cleaned_firstline = [item for item in flattened_firstline if item != '']
        
        values_lines = lines[2:]
        values_list = []
        for line in values_lines:
            flattenedLine = flatten(list(map(split_on_second_sign, line.split())))
            cleaned_line = [item for item in flattenedLine if item != '']
            while len(cleaned_line) < 4:
                cleaned_line.append(np.nan)
            values_list += cleaned_line

        time = datetime(int(cleaned_firstline[0]),int(cleaned_firstline[1]), int(cleaned_firstline[2]), int(cleaned_firstline[3]), int(cleaned_firstline[4]), int(cleaned_firstline[5]))
        
        clk_corr = cleaned_firstline[6:]
        for i in range(len(clk_corr)):
            value = clk_corr[i]
            floatNumber = str2float(value)
            clk_corr[i] = floatNumber
        for j in range(len(values_list)):
            value = values_list[j]
            if isinstance(value, str):
                floatNumber = str2float(value)
                values_list[j] = floatNumber
        
        if time.date() == current_date:
            if "G" in satellitt_id:
                GPSdata(    structured_dataG,satellitt_id,time,values_list, clk_corr, nav_msg_type)
            elif "R" in satellitt_id:
                GLONASSdata(structured_dataR,satellitt_id,time,values_list, clk_corr, nav_msg_type)
            elif "J" in satellitt_id:
                QZSSdata(   structured_dataJ,satellitt_id,time,values_list, clk_corr, nav_msg_type)
            elif "C" in satellitt_id:
                BeiDoudata( structured_dataC,satellitt_id,time,values_list, clk_corr, nav_msg_type)
            elif "I" in satellitt_id:
                NavICdata(  structured_dataI,satellitt_id,time,values_list, clk_corr, nav_msg_type)
            elif "S" in satellitt_id:
                SBASdata(   structured_dataS,satellitt_id,time,values_list, clk_corr, nav_msg_type)
            elif "E" in satellitt_id:
                Galileiodata(structured_dataE,satellitt_id,time,values_list, clk_corr, nav_msg_type)

    # Update navigation message type for GNSS's with multiple navigation message types.
    #structured_dataG = update_navigation_message_type(structured_dataG)
    structured_dataJ = update_navigation_message_type(structured_dataJ)
    structured_dataC = update_navigation_message_type(structured_dataC)

    # Save GNSS datafranes to csv.
    output_folder = f'ephemeris/{date.year}_{daynumber}/'
    os.makedirs(output_folder, exist_ok=True)
    file_pathG = os.path.join(output_folder, "structured_dataG.csv")
    structured_dataG = structured_dataG.sort_values(by=['satelite_id', 'Datetime'])
    structured_dataG.to_csv(file_pathG, index=False)
    file_pathR = os.path.join(output_folder, "structured_dataR.csv")
    structured_dataR = structured_dataR.sort_values(by=['satelite_id', 'Datetime'])
    structured_dataR.to_csv(file_pathR, index=False)
    file_pathE = os.path.join(output_folder, "structured_dataE.csv")
    structured_dataE = structured_dataE.sort_values(by=['satelite_id', 'Datetime'])
    structured_dataE.to_csv(file_pathE, index=False)
    file_pathJ = os.path.join(output_folder, "structured_dataJ.csv")
    structured_dataJ = structured_dataJ.sort_values(by=['satelite_id', 'Datetime'])
    structured_dataJ.to_csv(file_pathJ, index=False)
    file_pathC = os.path.join(output_folder, "structured_dataC.csv")
    structured_dataC = structured_dataC.sort_values(by=['satelite_id', 'Datetime'])
    structured_dataC.to_csv(file_pathC, index=False)
    file_pathI = os.path.join(output_folder, "structured_dataI.csv")
    structured_dataI = structured_dataI.sort_values(by=['satelite_id', 'Datetime'])
    structured_dataI.to_csv(file_pathI, index=False)
    file_pathS = os.path.join(output_folder, "structured_dataS.csv")
    structured_dataS = structured_dataS.sort_values(by=['satelite_id', 'Datetime'])
    structured_dataS.to_csv(file_pathS, index=False)