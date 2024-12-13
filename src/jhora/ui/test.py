from jhora.panchanga import drik
from jhora import const, utils

# Function to calculate the planet position using drik
def calculate_planet_position(jd, place, planet):
    if planet == 'L':
        sla = drik.ascendant(jd, place)
        return sla[0] * 30 + sla[1]
    else:
        return drik.sidereal_longitude(jd, planet)

# Lagrange Inverse Interpolation
def lagrange_inverse_interpolation(x, y, x_val):
    n = len(x)
    y_val = 0
    for i in range(n):
        term = y[i]
        for j in range(n):
            if i != j:
                term *= (x_val - x[j]) / (x[i] - x[j])
        y_val += term
    return y_val

# Function to find the conjunction time
def find_conjunction(planet1, planet2, jd, place, max_days=365*20, tolerance=1.0, tuning_factor=0.9):
    # Calculate initial positions
    lon1 = calculate_planet_position(jd, place, planet1)
    lon2 = calculate_planet_position(jd, place, planet2)
    print('initial longs', lon1, lon2)
    # Calculate initial longitude difference
    initial_diff = abs(lon1 - lon2)
    
    # Get planet velocities
    velocity1 = planet_speeds[planet1]
    velocity2 = planet_speeds[planet2]
    # Estimate time to close the gap
    differential_velocity = abs(velocity1 - velocity2)
    if differential_velocity == 0:
        return None  # Conjunction cannot be found if velocities are equal
    
    estimated_time = initial_diff / differential_velocity*tuning_factor
    jd += estimated_time  # Move time forward by the estimated time
    print(velocity1, velocity2, 'estimated starting date/time', utils.jd_to_gregorian(jd))
    
    # Start precise iterations from the new estimate
    time_step = 1.0 / 24.0 / 60.0 if planet1 == 'L' or planet2 == 'L' else 0.01
    for _ in range(int(max_days / (time_step ))):
        lon1 = calculate_planet_position(jd, place, planet1)
        lon2 = calculate_planet_position(jd, place, planet2)
        lon_diff = abs(lon1 - lon2)
        if lon_diff < tolerance:
            print(lon1, lon2, utils.jd_to_gregorian(jd))
            jd_list = [jd+t*time_step for t in range(-10,10)]
            long_diff_list = []
            for jdt in jd_list:
                p1_long = calculate_planet_position(jdt, place, planet1)
                p2_long = calculate_planet_position(jdt, place, planet2)
                #print(jd,jdt,planet1,p1_long,planet2,p2_long)
                long_diff_list.append((p1_long-p2_long))
            #print(jd_list)
            #print(long_diff_list)
            refined_jd = utils.inverse_lagrange(jd_list, long_diff_list, 0.0)
            refined_lon1 = calculate_planet_position(refined_jd, place, planet1)
            refined_lon2 = calculate_planet_position(refined_jd, place, planet2)
            print(refined_jd,utils.jd_to_gregorian(refined_jd),refined_lon1,refined_lon2)
            return refined_jd,refined_lon1

        jd += time_step

    return None  # Conjunction not found within max days

planet_speeds = {
    'L': 360, const._SUN: 1.0, const._MOON: 13.0, const._MARS: 0.4, 
    const._MERCURY: 1.4, const._JUPITER: 0.2, const._VENUS: 1.2, 
    const._SATURN: 0.008, const._RAHU: -0.05, const._KETU: -0.05
}
utils.set_ephemeris_data_path()
# Example usage
planet1 = const._JUPITER
planet2 = const._SUN
dob = drik.Date(1996, 12, 7)
tob = (10, 34, 0)
jd = utils.julian_day_number(dob, tob)
place = drik.Place('Chennai, India', 13.0878, 80.2785, 5.5)

conjunction_results = find_conjunction(planet1, planet2, jd, place)
if conjunction_results:
    conjunction_jd,conjunction_longitude = conjunction_results
    #conjunction_jd = conjunction_results
    cy,cm,cd,cfh = utils.jd_to_gregorian(conjunction_jd)
    print(planet1, planet2, "Conjunction will occur at:", (cy,cm,cd),utils.to_dms(cfh),utils.to_dms(conjunction_longitude,is_lat_long='plong'))
else:
    print(planet1, planet2, "Conjunction not found within the given time frame.")
