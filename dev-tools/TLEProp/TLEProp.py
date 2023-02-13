# Designed to take telemetry a list of TLEs and propegrate position data
# Author: Jeff Schloemer
# Date: 02/06/2023

# pip install pandas pyorbital pyephem pyorbital skyfield

import pandas as pd
import numpy as np
import math
import argparse
import json
import pyorbital.orbital
from pyorbital import astronomy
import datetime
import ephem
from skyfield.api import load
from skyfield.api import EarthSatellite


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

# load the TLE data
planets = load('de421.bsp')
ts = load.timescale()

desired_columns = ['EPOCH', 'TLE_LINE1', 'TLE_LINE2']
df = in_df[desired_columns]

i = 0
lastTime = df.index[-1]

# Create an empty dataframe with columns for position data
columns = ['timestamp', 'latitude', 'longitude', 'altitude', 'eclipsed', 'beta_angle', 'sun2vel_angle']
tf = pd.DataFrame(columns=columns)
tf['eclipsed'] = tf['eclipsed'].astype(bool)

# Create empty dataframe with columns for TLE data
columns = ['epoch', 'tle_line_1', 'tle_line_2']
gf = pd.DataFrame(columns=columns)

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
    
    # Add usage to gf dataframe
    # Create a new row with the data
    ent = pd.DataFrame({'epoch': [date], 'tle_line_1': [line1], 'tle_line_2': [line2]})

    # Concatenate the new row to the existing dataframe
    gf = pd.concat([gf, ent], ignore_index=True)
    
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
        
        # Compute Sun info
        sat = EarthSatellite(line1, line2, 'LightSail-2', ts)
        # create a Time object from the datetime variable
        time2 = ts.utc(*time.timetuple()[:6])
        eci = sat.at(time2).position.km
        # compute the position of the Sun
        sun = planets['sun'].at(time2).position.km
        # compute the Sun vector in the ECI coordinate system
        sun_vector = sun - eci

        # compute the orbital plane normal vector
        velocity = sat.at(time2).velocity.km_per_s
        normal_vector = np.cross(eci, velocity)

        # compute the beta angle
        cos_beta = np.dot(normal_vector, sun_vector) / (np.linalg.norm(normal_vector) * np.linalg.norm(sun_vector))
        beta = math.acos(cos_beta)

        # compute the sun to velocity vector angle
        cos_ang = np.dot(velocity, sun_vector) / (np.linalg.norm(velocity * np.linalg.norm(sun_vector)))
        sun_ang = math.acos(cos_ang)
        
        # Create a new row with the data
        row = pd.DataFrame({'timestamp': [time], 'latitude': [lat], 'longitude': [lon], 'altitude': [alt], 'eclipsed': [ecl], 'beta_angle': [beta], 'sun2vel_angle': [sun_ang]})

        # Concatenate the new row to the existing dataframe
        tf = pd.concat([tf, row], ignore_index=True)

        # Propegate Time
        time = time + datetime.timedelta(minutes=1)
    
# Print the first 25 rows of the DataFrame
#print(df.head(25))

# Export the data frame to a JSON file
gf.to_json('EpochTLEData.json', orient='index')

# Print the first 25 rows of the DataFrame
#print(tf.head(90))
#print(tf.tail(5))

# Export the data frame to a JSON file
tf.to_json('PosAndEventsData.json', orient='index')