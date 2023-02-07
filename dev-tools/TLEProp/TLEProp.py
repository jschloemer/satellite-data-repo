# Designed to take telemetry a list of TLEs and propegrate position data
# Author: Jeff Schloemer
# Date: 02/06/2023

# pip install pandas pyorbital

import pandas as pd
import math
import argparse
import json
import pyorbital.orbital
from pyorbital import astronomy
import datetime
import ephem
from numpy import dot
from numpy.linalg import norm


# Define the command line arguments
parser = argparse.ArgumentParser(description='Take TLE data output position and orbital events')
parser.add_argument('input', help='a json file of timestamped TLE data')
parser.add_argument('startTime', help='epoch start to propegrate TLE between globally')
parser.add_argument('stopTime', help='epoch stop to propegrate TLE between globally')

# Parse the command-line arguments
args = parser.parse_args()
in_df = []

date_format = '%Y-%m-%d %H:%M:%S'
userStart = datetime.datetime.strptime(args.startTime, date_format)
userEnd = datetime.datetime.strptime(args.stopTime, date_format)

if args.input.endswith('json'):
    # Load the JSON file into a pandas DataFrame
    data = json.load(open(args.input))
    in_df = pd.DataFrame(data)
    # Convert the date column to a timestamp
    in_df['EPOCH'] = pd.to_datetime(in_df['EPOCH'], format='%Y-%m-%dT%H:%M:%S.%f')
else:
    print("Other sources not supported yet")
    exit()

desired_columns = ['EPOCH', 'TLE_LINE1', 'TLE_LINE2']
df = in_df[desired_columns]

i = 0
lastTime = df.index[-1]

# Create an empty dataframe with columns for position data
columns = ['timestamp', 'latitude', 'longitude', 'altitude', 'eclipsed']
tf = pd.DataFrame(columns=columns)
tf['eclipsed'] = tf['eclipsed'].astype(bool)

# Iterate over the index values
for index, row in df.iterrows():
    date = row['EPOCH']
    if date == lastTime:
        continue
    if date > userEnd:
        break
    #if i > 25:
    #    continue
    i = i + 1
    startTime = date
    stopTime = df['EPOCH'][i]
    if stopTime < userStart:
        continue
    line1 = row['TLE_LINE1']
    line2 = row['TLE_LINE2']
    
    satellite = pyorbital.orbital.Orbital('LightSail-2',line1=line1, line2=line2)
    tle = ('LightSail-2', line1, line2)
    eph = ephem.readtle(*tle)
    observer = ephem.Observer()
    
    # Define the Sun as a PyEphem body object
    sun = ephem.Sun()
    
    # Get the position information in 1 minute increments between the start and end times
    time = startTime
    while time < stopTime:
        lon, lat, alt = satellite.get_lonlatalt(time)
        [x, v] = satellite.get_position(time)
        
        #print("Time:", time, "Longitude:", lon, "Latitude:", lat, "Altitude:", alt)
        
        eph.compute(time)
        ecl = eph.eclipsed
        
        # Create an observer object for the current location on Earth
        obs = ephem.Observer()
        obs.lat = lat
        obs.lon = lon
        obs.elevation = alt
        obs.date = time
        
        # Compute the position of the Sun
        sun = ephem.Sun()
        sun.compute(obs)
        
        # Calculate the angle between the velocity vector of the satellite and the Sun
        #sunAngle = math.acos(v.dot(sun.vector) / (v.length() * sun.vector.length()))
        
        # Create a new row with the data
        row = pd.DataFrame({'timestamp': [time], 'latitude': [lat], 'longitude': [lon], 'altitude': [alt], 'eclipsed': [ecl]})

        # Concatenate the new row to the existing dataframe
        tf = pd.concat([tf, row], ignore_index=True)

        # Propegate Time
        time = time + datetime.timedelta(minutes=1)
    
# Print the first 25 rows of the DataFrame
print(df.head(25))

# Export the data frame to a JSON file
df.to_json('EpochTLEData.json', orient='index')

# Print the first 25 rows of the DataFrame
print(tf.head(90))
print(tf.tail(5))

# Export the data frame to a JSON file
tf.to_json('PosAndEventsData.json', orient='index')