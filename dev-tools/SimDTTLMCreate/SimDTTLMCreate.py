# Designed to take telemetry from a file and output smoothed versions representing a digital twin and a low-fidelity simulator
# Author: Jeff Schloemer
# Date: 02/10/2023

# pip install pandas matplotlib scikit-learn

# Usage Example: python SimDTTLMCreate.py /Users/jeffreyschloemer/GitHub/satellite-data-repo/tmp/normalized_frames.json --SpaceWx /Users/jeffreyschloemer/GitHub/satellite-data-repo/SpaceWeather/F10.7Flux.json --PosData /Users/jeffreyschloemer/GitHub/satellite-data-repo/dev-tools/TLEProp/PosAndEventsData.json

import argparse
import json
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score,mean_squared_error
from sklearn import metrics
from tqdm import tqdm


# Define the command line arguments
parser = argparse.ArgumentParser(description='Take telemetry data and output it in realtime')
parser.add_argument('input', help='a json file of timestamped telemetry data')
parser.add_argument('--PosData', help='a json file of timestamped position and orbit events data')
parser.add_argument('--SpaceWx', help='a json file of timestamped space weather data for F10.7 Flux')

# debug
debug = False

# Parse the command-line arguments
args = parser.parse_args()
tf = []

if args.input.endswith('json'):
    # Load the JSON file into a pandas DataFrame
    data = json.load(open(args.input))
    tf = pd.DataFrame(data["frames"])
    df = pd.DataFrame(data["frames"])
else:
    print("Other sources not supported yet")
    exit()
    
if args.PosData.endswith('json'):
    # Load the JSON file into a pandas DataFrame
    data = json.load(open(args.PosData))
    posDf = pd.DataFrame(data)
    # transpose the DataFrame
    posDf = posDf.transpose()
    #print(posDf)
else:
    print("Other sources not supported yet")
    exit()
    
if args.SpaceWx.endswith('json'):
    # Load the JSON file into a pandas DataFrame
    data = json.load(open(args.SpaceWx))
    WxDf = pd.DataFrame(data["data"])
    WxDf[0] = pd.to_datetime(WxDf[0])
else:
    print("Other sources not supported yet")
    exit()

# replace every entry in "value" with the rounded average
# find all columns that contain the string "tmp"
dest_columns = [col for col in tf["fields"][0].keys() if "tmp" in col or "temp" in col or "curr" in col or "busv" in col or "volt" in col]

# iterate over the columns and compute the average of their values
for col in dest_columns:
    values = [item[col]['value'] for item in tf['fields']]
    average = round(pd.Series(values).mean(), 1)
    for i, item in enumerate(tf['fields']):
        tf['fields'][i][col]['value'] = average
        
# replace every entry in "value" with the rounded average
# find all columns that contain the string "tmp"
dest_columns = [col for col in tf["fields"][0].keys() if "callsign" in col or "ssidid" in col or "port" in col or "ctl" in col or "pid" in col or "addr" in col or "port" in col or "type" in col or "buffers" in col or "flags" in col or "type" in col or "status" in col or "fails" in col]

# iterate over the columns and assign all values the first entry
for col in dest_columns:
    values = [item[col]['value'] for item in tf['fields']]
    first = values[0]
    for i, item in enumerate(tf['fields']):
        tf['fields'][i][col]['value'] = first
        
# replace every entry in "value" with the rounded average
# find all columns that contain the string "tmp"
dest_columns = [col for col in tf["fields"][0].keys() if "College" in col or "Fredericksburg" in col or "Proton" in col or "Neutron" in col or "unspot" in col or "X-Ray" in col or "Solar" in col or "Optical" in col or "Radio" in col or "Regions" in col]

tf['time'] = pd.to_datetime(tf['time'])

# iterate over the columns and assign all values the first entry
for col in dest_columns:
    values = [item[col]['value'] for item in tf['fields']]
    max = pd.Series(values).max()
    if "unspot" in col:
        if debug:
            print(max)
    min = pd.Series(values).min()
    if "unspot" in col:
        if debug:
            print(min)
    avg = pd.Series(values).mean()
    if "unspot" in col:
        if debug:
            print(avg)
    amp = (max - (min - 1 * (max - avg)))/2
    if "unspot" in col:
        if debug:
            print(amp)
    mid = (max + min)/2 - (max - avg)/2
    if "unspot" in col:
        if debug:
            print(mid)
    for i, item in enumerate(tf['fields']):
        seconds = pd.to_datetime(tf['time'][i]).timestamp()
        negOK = False
        if min < 0:
            negOK = True
        tmp = amp * math.sin(2 * math.pi / 3153600 * seconds) + mid
        if negOK == False:
            if tmp < 0:
                tmp = 0
        tf['fields'][i][col]['value'] = tmp

# Export the data frame to a JSON file
tf.to_json('SimData.json', indent=4)

## Digital twin (from state) section

# Create an empty dataframe with columns for satellite tlm data
xcolumns = ['timestamp', "spacewx", 'latitude', 'longitude', 'altitude', 'eclipsed', 'beta_angle', 'sun2vel_angle']
xcoltelm = []
ycolumns = []
ecolumns = []

dest_columns = [col for col in df["fields"][0].keys()]

# Only copy attitude and rate data from the telemetry into the x columns
for col in dest_columns:
    if "_act" in col or "_rate" in col:
        xcolumns.append(col)
        xcoltelm.append(col)
    else:
        if str(df['fields'][0][col]['value']).isnumeric():
            ycolumns.append(col)
        else:
            ecolumns.append(col)

# Create x y and e dfs
xdf = pd.DataFrame(columns=xcolumns)
ydf = pd.DataFrame(columns=ycolumns)

rows = len(df)

# Iterate over the telemetry set
for index, row in tqdm(df.iterrows(), desc="Processing Telemetry", bar_format="{l_bar}{bar:50}{r_bar}", total=rows):
    values = []
    timestamp = pd.to_datetime(row['time']).timestamp()
    values.append(timestamp)
    spacewx = np.interp(timestamp, WxDf[0].astype(int), WxDf[1])
    values.append(spacewx)
    latitude = np.interp(timestamp, posDf['timestamp'].astype(int), posDf['latitude'].astype(float))
    values.append(latitude)
    longitude = np.interp(timestamp, posDf['timestamp'].astype(int), posDf['longitude'].astype(float))
    values.append(longitude)
    altitude = np.interp(timestamp, posDf['timestamp'].astype(int), posDf['altitude'].astype(float))
    values.append(altitude)
    
    # Eclipsed part - Using interp now due to uncertainty in interpolation
    eclipsed = np.interp(timestamp, posDf['timestamp'].astype(int), posDf['eclipsed'].astype(int))
    values.append(eclipsed)
    
    beta_angle = np.interp(timestamp, posDf['timestamp'].astype(int), posDf['beta_angle'].astype(float))
    values.append(beta_angle)
    sun2vel_angle = np.interp(timestamp, posDf['timestamp'].astype(int), posDf['sun2vel_angle'].astype(float))
    values.append(sun2vel_angle)
    for col in xcoltelm:
        tmp = row['fields'][col]['value']
        values.append(tmp)
    
    #print("=================")
    #print(str(len(xcolumns)))
    #print(str(len(values)))        
    result = {xcolumns[i]: values[i] for i in range(len(xcolumns))}
    tdf = pd.DataFrame(result, index=[0])
    
    # Concatenate the new row to the existing dataframe
    xdf = pd.concat([xdf, tdf], ignore_index=True)
    
    # Go over the y columns
    yval = []
    for col in ycolumns:
        tmp = row['fields'][col]['value']
        yval.append(tmp)
    
    #print("=================")
    #print(str(len(ycolumns)))
    #print(str(len(yval)))    
    result = {ycolumns[i]: yval[i] for i in range(len(ycolumns))}
    tdf = pd.DataFrame(result, index=[0])
    
    # Concatenate the new row to the existing dataframe
    ydf = pd.concat([ydf, tdf], ignore_index=True)
    
xdf.to_csv('xVals.csv', index=False)
ydf.to_csv('yVals.csv', index=False)

x_array = xdf.to_numpy()
y_array = xdf.to_numpy()

# Regression Time
print('Performing Regression')
modelControl = LinearRegression()
modelTest = RandomForestRegressor(n_estimators=200, random_state=42)

X_train, X_test, y_train, y_test = train_test_split(x_array, y_array, test_size=0.3)

modelControl.fit(X_train, y_train)
predictionsControl = modelControl.predict(X_test)
modelControl.score(X_test, y_test)
print("Control")
print(r2_score(y_test, predictionsControl))
print(mean_squared_error(y_test, predictionsControl))

modelTest.fit(X_train, y_train)
predictionsTest = modelTest.predict(X_test)
ResTest = modelTest.predict(X_train)
teacc = modelTest.score(X_train, y_train)
veacc = modelTest.score(X_test, y_test)
print("Test")
print(r2_score(y_test, predictionsTest))
print(mean_squared_error(y_test, predictionsTest))

print('Training Accuracy : ', teacc)
 
print('Validation Accuracy : ', veacc)
    
# Plots for debugging
# plt.plot(tf['time'], tf['fields'].apply(lambda x: x['SESC sunspot number']['value']))
# plt.xlabel('Time')
# plt.ylabel('Value')
# plt.show()


# "dest_callsign": "constant",
# "src_callsign": "constant",
# "src_ssid": "constant",
# "dest_ssid": "constant",
# "ctl": "constant",
# "pid": "constant",
# "src_ip_addr": "constant",
# "dst_ip_addr": "constant",
# "src_port": "constant",
# "dst_port": "constant",
# "type": "constant",
# "daughter_atmp": "variable",
# "daughter_btmp": "variable",
# "threev_pltmp": "variable",
# "rf_amptmp": "variable",
# "nx_tmp": "variable",
# "px_tmp": "variable",
# "ny_tmp": "variable",
# "py_tmp": "variable",
# "nz_tmp": "variable",
# "pz_tmp": "variable",
# "atmelpwrcurr": "variable",
# "atmelpwrbusv": "variable",
# "threev_pwrcurr": "variable",
# "threev_pwrbusv": "variable",
# "threev_plpwrcurr": "variable",
# "threev_plpwrbusv": "variable",
# "fivev_plpwrcurr": "variable",
# "fivev_plpwrbusv": "variable",
# "daughter_apwrcurr": "variable",
# "daughter_apwrbusv": "variable",
# "daughter_bpwrcurr": "constant",
# "daughter_bpwrbusv": "constant",
# "nx_intpwrcurr": "variable",
# "nx_intpwrbusv": "variable",
# "nx_extpwrcurr": "variable",
# "nx_extpwrbusv": "variable",
# "px_intpwrcurr": "variable",
# "px_intpwrbusv": "variable",
# "px_extpwrcurr": "variable",
# "px_extpwrbusv": "variable",
# "ny_intpwrcurr": "variable",
# "ny_intpwrbusv": "variable",
# "ny_extpwrcurr": "variable",
# "ny_extpwrbusv": "variable",
# "py_intpwrcurr": "variable",
# "py_intpwrbusv": "variable",
# "py_extpwrcurr": "variable",
# "py_extpwrbusv": "variable",
# "nz_extpwrcurr": "variable",
# "nz_extpwrbusv": "variable",
# "usercputime": "variable",
# "syscputime": "variable",
# "idlecputime": "variable",
# "processes": "variable",
# "memfree": "variable",
# "buffers": "constant",
# "cached": "variable",
# "datafree": "variable",
# "nanderasures": "variable",
# "beaconcnt": "variable",
# "time": "variable",
# "boottime": "variable",
# "long_dur_counter": "variable",
# "adcs_mode": "status",
# "flags": "status",
# "q0_act": "variable",
# "q1_act": "variable",
# "q2_act": "variable",
# "q3_act": "variable",
# "x_rate": "variable",
# "y_rate": "variable",
# "z_rate": "variable",
# "gyro_px": "variable",
# "gyro_py": "variable",
# "gyro_iz": "variable",
# "gyro_pz": "variable",
# "gyro_ix": "variable",
# "gyro_iy": "variable",
# "sol_nxx": "status",
# "sol_nxy": "status",
# "sol_nyx": "status",
# "sol_nyy": "status",
# "sol_nzx": "status",
# "sol_nzy": "status",
# "sol_pxx": "status",
# "sol_pxy": "status",
# "sol_pyx": "status",
# "sol_pyy": "status",
# "mag_nxx": "variable",
# "mag_nxy": "variable",
# "mag_nxz": "variable",
# "mag_pxz": "variable",
# "mag_pxx": "variable",
# "mag_pxy": "variable",
# "mag_nyz": "variable",
# "mag_pyz": "variable",
# "mag_pyx": "variable",
# "mag_pyy": "variable",
# "wheel_rpm": "variable",
# "cam0_status": "status",
# "cam0_temp": "variable",
# "cam0_last_contact": "variable",
# "cam0_pics_remaining": "status",
# "cam0_retry_fails": "status",
# "cam1_status": "status",
# "cam1_temp": "variable",
# "cam1_last_contact": "variable",
# "cam1_pics_remaining": "status",
# "cam1_retry_fails": "status",
# "torqx_pwrcurr": "variable",
# "torqx_pwrbusv": "variable",
# "torqy_pwrcurr": "variable",
# "torqy_pwrbusv": "variable",
# "torqz_pwrcurr": "variable",
# "torqz_pwrbusv": "variable",
# "motor_pwrcurr": "variable",
# "motor_pwrbusv": "constant",
# "pic_panel_flags": "status",
# "motor_cnt": "status",
# "motor_limit": "status",
# "bat0_curr": "variable",
# "bat0_volt": "variable",
# "bat0_temp": "variable",
# "bat0_flags": "status",
# "bat0_ctlflags": "status",
# "bat1_curr": "variable",
# "bat1_volt": "variable",
# "bat1_temp": "variable",
# "bat1_flags": "status",
# "bat1_ctlflags": "status",
# "bat2_curr": "variable",
# "bat2_volt": "variable",
# "bat2_temp": "variable",
# "bat2_flags": "status",
# "bat2_ctlflags": "status",
# "bat3_curr": "variable",
# "bat3_volt": "variable",
# "bat3_temp": "variable",
# "bat3_flags": "status",
# "bat3_ctlflags": "status",
# "bat4_curr": "variable",
# "bat4_volt": "variable",
# "bat4_temp": "variable",
# "bat4_flags": "status",
# "bat4_ctlflags": "status",
# "bat5_curr": "variable",
# "bat5_volt": "variable",
# "bat5_temp": "variable",
# "bat5_flags": "status",
# "bat5_ctlflags": "status",
# "bat6_curr": "variable",
# "bat6_volt": "variable",
# "bat6_temp": "variable",
# "bat6_flags": "status",
# "bat6_ctlflags": "status",
# "bat7_curr": "variable",
# "bat7_volt": "variable",
# "bat7_temp": "variable",
# "bat7_flags": "status",
# "bat7_ctlflags": "status",
# "comm_rxcount": "variable",
# "comm_txcount": "variable",
# "comm_rxbytes": "variable",
# "comm_txbytes": "variable",
# "Planetary K 12-15": "status",
# "College K 6-9": "variable",
# "Planetary K 18-21": "status",
# "College K 9-12": "variable",
# "College K 21-24": "variable",
# "Fredericksburg K 9-12": "variable",
# "Fredericksburg K 3-6": "variable",
# "College K 3-6": "variable",
# "Planetary A": "status",
# "Fredericksburg A": "variable",
# "Planetary K 21-24": "status",
# "Fredericksburg K 6-9": "variable",
# "College K 12-15": "variable",
# "College K 15-18": "variable",
# "Fredericksburg K 21-24": "variable",
# "College K 0-3": "variable",
# "Fredericksburg K 0-3": "variable",
# "Fredericksburg K 12-15": "variable",
# "Planetary K 9-12": "status",
# "College K 18-21": "variable",
# "Fredericksburg K 18-21": "variable",
# "Fredericksburg K 15-18": "variable",
# "Planetary K 15-18": "status",
# "Planetary K 3-6": "status",
# "College A": "variable",
# "Planetary K 0-3": "status",
# "Planetary K 6-9": "status",
# "Proton 100 MeV": "variable",
# "Electron 2 MeV": "variable",
# "Proton 1 MeV": "variable",
# "Proton 10 MeV": "variable",
# "Neutron": "constant",
# "Electron 800 KeV": "variable",
# "Sunspot Area": "variable",
# "X-Ray S": "status",
# "X-Ray X": "status",
# "SESC sunspot number": "status",
# "X-ray Background Flux": "variable",
# "Optical 3": "constant",
# "Optical 1": "status",
# "Optical 2": "constant",
# "X-Ray M": "status",
# "Solar Mean Field": "constant",
# "Radio Flux": "variable",
# "New Regions": "status",
# "X-Ray C": "status"