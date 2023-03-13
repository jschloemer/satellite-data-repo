# Designed to take telemetry from a file and output a 
# Author: Jeff Schloemer
# Date: 02/10/2023

# pip install pandas

import argparse
import json
import pandas as pd
import numpy as np

def add_measurement(data, measurement_name, values):
    new_measurement = {
        "name": measurement_name,
        "key": measurement_name.lower().replace(" ", "."),
        "values": values
    }
    data["measurements"].append(new_measurement)
    return data

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
    
namespace = 'lightsail-2'

data = {
    "name": namespace,
    "key": "sc",
    "measurements": [
    ]
}

dest_columns = [col for col in tf["fields"][0].keys()]
# iterate over the columns and assign all values the first entry
for col in dest_columns:
    values = [item[col]['value'] for item in tf['fields']]
    units = [item[col]['unit'] for item in tf['fields']]
    unit = first_unit = units[0]  # get the first entry from the units list
    min = pd.Series(values).min()
    max = pd.Series(values).max()
    
    value_type = type(tf['fields'][col]['value'])
    format = ""
    if value_type == int:
        # do something with integer value
        format = 'integer'
    elif value_type == float:
        # do something with float value
        format = 'float'
    elif value_type == str:
        # do something with string value
        format = 'enum'
    else:
        # handle other types if needed
        format = 'string'

    new_measurement_name = col
    new_measurement_values = [
        {
            "key": "value",
            "name": "Value",
            "units": unit,
            "format": format,
            "min": min,
            "max": max,
            "hints": {
                "range": 1
            }
        },
        {
            "key": "utc",
            "source": "timestamp",
            "name": "Timestamp",
            "format": "utc",
            "hints": {
                "domain": 1
            }
        }
    ]

    data = add_measurement(data, new_measurement_name, new_measurement_values)


with open('dictionary.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)
