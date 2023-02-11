# Designed to take telemetry from a file and output a 
# Author: Jeff Schloemer
# Date: 02/10/2023

# pip install pandas

import argparse
import json
import pandas as pd
import numpy as np

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
    
namespace = 'lightsail-2.taxonomy'
type = 'lightsail-2.telemetry'
range = 1
domain = 1
