# Designed to take telemetry from a file and output it back like it was being generated in real time
# Author: Jeff Schloemer
# Date: 01/30/2023

# pip install pandas

import argparse
import json
import pandas as pd
import time
import requests

# Define the command line arguments
parser = argparse.ArgumentParser(description='Take telemetry data and output it in realtime')
parser.add_argument('input', help='a json file of timestamped telemetry data')
parser.add_argument('index', help='the starting index to start from in the json file')

# Parse the command-line arguments
args = parser.parse_args()
tf = []

if args.input.endswith('json'):
    # Load the JSON file into a pandas DataFrame
    data = json.load(open(args.input))
    tf = pd.DataFrame(data["frames"])
else:
    print("Other sources not supported yet")
    exit()

# Convert the timestamps to a pandas datetime format
tf['time'] = pd.to_datetime(tf['time'])

# Set the timestamp as the index of the DataFrame
tf = tf.set_index('time')

# Sort the data frame by the index
tf.sort_index(inplace=True)

# Find the duplicate index values
duplicates = tf.index.duplicated(keep='first')

# Select only the non-duplicate values
tf = tf[~duplicates]

# Print the first 5 rows of the DataFrame
#print(tf.head(25))

# Set the start time
start_time = time.time()

# Define the API endpoint for OpenMCT
openmct_endpoint = "http://localhost:8080/telemetry"
preTime = tf.index[int(args.index)]

# Create an empty dataframe with columns for position data
columns = ['measurand', 'value']
df = pd.DataFrame(columns=columns)

# Iterate over the index values
for index, row in tf.iterrows():
    if (index - preTime).total_seconds() < 0:
        #print('Skipping this')
        continue
    # Calculate the elapsed time
    elapsed_time = time.time() - start_time
    deltaTime = (index - preTime).total_seconds()
    if elapsed_time < deltaTime:
        # Wait statement
        #print("Sleeping " + str(deltaTime - elapsed_time) + " seconds")
        time.sleep(deltaTime - elapsed_time + 0.002)
    
    elapsed_time = time.time() - start_time
    #print(str(elapsed_time))
    #print(str((index - tf.index[int(args.index)]).total_seconds()))
    
    # Create an empty dataframe with columns for position data
    columns = ['measurand', 'value']
    df = pd.DataFrame(columns=columns)

    # Check if the elapsed time is equal to the time between timestamped indexes
    if elapsed_time >= (index - tf.index[int(args.index)]).total_seconds():
        # Send the request.post
        # Send the telemetry data to OpenMCT
        telemetry_data = tf['fields'][index]
        #print(telemetry_data)
        for row in telemetry_data:
            value = telemetry_data[row]['value']
            row = pd.DataFrame({'measurand': [row], 'value': [value]})
            
            # Concatenate the new row to the existing dataframe
            df = pd.concat([df, row], ignore_index=True)
            #print(value)
        t_v = df[:]
        print(t_v)    
        print("Tick")
        
        #response = requests.post(openmct_endpoint, json=telemetry_data)

        # Check the response to see if the data was sent successfully
        #if response.status_code == 200:
        #    print("Telemetry data sent successfully")
        #    print(response)
        #else:
        #    print("Failed to send telemetry data")
        
    