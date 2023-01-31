# Designed to take telemetry from a file and output it back like it was being generated in real time
# Author: Jeff Schloemer
# Date: 01/30/2023

# pip install pandas

import argparse
import json
import pandas as pd

# Define the command line arguments
parser = argparse.ArgumentParser(description='Take telemetry data and output it in realtime')
parser.add_argument('input', help='a json file of timestamped telemetry data')

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

# Print the first 5 rows of the DataFrame
print(tf.head(25))
