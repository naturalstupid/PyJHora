from jhora.panchanga import drik
from jhora import utils

def find_conjunction(dob, tob, place):
    # Initialize Julian Day number
    jd = utils.julian_day_number(dob, tob)
    # Define the number of planets (0 to 8)
    num_planets = 9
    # Define a large step size for initial iterations
    step_size = 0.1  # Step size in Julian days, can be adjusted
    
    while True:
        # Get the full longitudes of all planets
        planet_longitudes = []
        for planet in range(num_planets):
            planet_sign, planet_long = drik.sidereal_longitude(jd, planet)
            full_long = planet_sign * 30 + planet_long
            planet_longitudes.append(full_long)
        
        # Check for conjunctions
        for i in range(num_planets):
            for j in range(i + 1, num_planets):
                if abs(planet_longitudes[i] - planet_longitudes[j]) < 0.01:  # Allow small tolerance for precision
                    return jd, i, j
        
        # Update Julian Day number by step size
        jd += step_size

# Example usage
dob = drik.Date(1996, 12, 7)
tob = (10, 34, 0)
place = drik.Place('Chennai, India', 13.0878, 80.2785, 5.5)
jd_conjunction, planet1, planet2 = find_conjunction(dob, tob, place)
print(f'Conjunction found at JD {jd_conjunction} between planet {planet1} and planet {planet2}')
