import numpy as np
import math
from skyfield.api import load
from skyfield.api import EarthSatellite

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

# compute the position of the Sun
sun = planets['sun'].at(time).position.km

# compute the Sun vector in the ECI coordinate system
sun_vector = sun - eci

# compute the orbital plane normal vector
velocity = satellite.at(time).velocity.km_per_s
normal_vector = np.cross(eci, velocity)

# compute the beta angle
cos_beta = np.dot(normal_vector, sun_vector) / (np.linalg.norm(normal_vector) * np.linalg.norm(sun_vector))
beta = math.acos(cos_beta)
print(beta)
