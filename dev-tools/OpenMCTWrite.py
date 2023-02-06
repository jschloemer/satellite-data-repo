# Test script for OpenMCT write
# Author: Jeff Schloemer
# Date: 02/05/2023

import requests
import json

# Define the API endpoint for OpenMCT
openmct_endpoint = "http://localhost:8080/telemetry"

# Define the telemetry data to send
telemetry_data = {
    "key1": 10.0,
    "key2": 20.0,
    "key3": 30.0
}

# Send the telemetry data to OpenMCT
response = requests.post(openmct_endpoint, json=telemetry_data)

# Check the response to see if the data was sent successfully
if response.status_code == 200:
    print("Telemetry data sent successfully")
    print(response)
else:
    print("Failed to send telemetry data")
