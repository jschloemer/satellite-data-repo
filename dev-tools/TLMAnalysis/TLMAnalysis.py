# Designed to take telemetry from a file and output anaylsis statistics
# Author: Jeff Schloemer
# Date: 01/30/2023

# pip install pandas

import argparse
import json
import pandas as pd

# Global checks
max_time = 22
max_frames = 0
startStamp = ""
endStamp = ""

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

# Sort the data frame by the index
tf.sort_index(inplace=True)

# Find the duplicate index values
duplicates = tf.index.duplicated(keep='first')

# Select only the non-duplicate values
tf = tf[~duplicates]

# Calculate the time difference between consecutive indices
time_diffs = tf.index.to_series().diff().dt.total_seconds()

# Create a cumulative sum of the time differences
cumulative_sum = (time_diffs > max_time).cumsum()

# Find the start and end indices of each group of indices separated by less than the maximum time in seconds
group_starts = cumulative_sum != cumulative_sum.shift()
group_ends = cumulative_sum != cumulative_sum.shift(-1)
start_indices = cumulative_sum[group_starts].index
end_indices = cumulative_sum[group_ends].index

# Create a list of tuples containing the start and end indices of each group
groups = [(start, end) for start, end in zip(start_indices, end_indices)]
# Iterate over the groups to access the corresponding data in the DataFrame
for start, end in groups: 
    loc1 = tf.index.get_loc(start)
    loc2 = tf.index.get_loc(end)
    frames = loc2 - loc1 + 1
    if frames > max_frames:
        startStamp = start
        endStamp = end
        max_frames = frames

group_data = tf.loc[startStamp:endStamp]


# Print the first 5 rows of the DataFrame
print(group_data.head(25))

print("Maximum frames = " + str(max_frames))
print("Start time = " + str(startStamp))
print("End time = " + str(endStamp))
