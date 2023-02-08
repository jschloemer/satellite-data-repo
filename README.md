# satellite-data-repo
Holds access tools and data sources for public satellite telemetry, state and space weather data. Used specifically for the development and test of Astri. 

# License
Each data source has their own usage and licensing agreements that should be consulted.

# TLEProp
Usage Example: python TLEProp.py ../../tmp/LightSail_2_TLE.json '2019-07-16 16:02:00' '2019-07-16 16:08:39'

Here tmp holds the unzipped TLE data stored in the Lightsail-2 folder
The two quoted time stamps are the time periods that the propegator runs on.

The output is two json files:
EpochTLEData.json contains a dataframe to json output of the TLE data epoch used to create the propegation with columns epoch, tle_line_1 and tle_line_2
PosAndEventsData.json contains lat, lon, alt information on a per minute basis for the entire set of epoch contained within the TLE data (note that it will return values outside of the input time) as well as a bool for if the satellite is eclipsed, current beta angle and current sun to velocity angle (both in radians)