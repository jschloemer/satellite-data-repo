import numpy as np
from skyfield.api import load
from skyfield.api import EarthSatellite
import math



# load the TLE data
planets = load('de421.bsp')
ts = load.timescale()

# extract the TLE data for the satellite
line1 = '1 44420U 19036AC  19189.19929602  .00000238  00000-0  66072-5 0  9998'
line2 = '2 44420  24.0039 123.5944 0010951 339.2037 161.8097 14.52524232    18'
satellite = EarthSatellite(line1, line2, 'LightSail-2', ts)

# compute the position of the satellite
time = ts.utc(2023, 2, 7, 12, 0, 0)
eci = satellite.at(time).position.km
print(eci)

# compute the position of the Sun
sun = planets['sun'].at(time).position.km
print(sun)

# compute the orbital plane normal vector
velocity = satellite.at(time).velocity.km_per_s
print(velocity)

# compute the Sun vector in the ECI coordinate system
sun_vector = sun - eci
print(sun_vector)

# compute the sun to velocity vector angle
cos_ang = np.dot(velocity, sun_vector) / (np.linalg.norm(velocity * np.linalg.norm(sun_vector)))
sun_ang = math.acos(cos_ang)
print(sun_ang)