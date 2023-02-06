# Test script for OpenMCT read
# Author: Jeff Schloemer
# Date: 02/05/2023

import requests

# The URL of the OpenMCT API endpoint
url = "http://localhost:8080/telemetry/path"

# Make a GET request to the API endpoint
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON data from the response
    data = response.json()
    # Do something with the data
    print(data)
else:
    # Handle the error
    print("Error:", response.status_code)
