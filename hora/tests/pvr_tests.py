from hora.panchanga import panchanga 
from hora.horoscope.chart import house
" Chapter 1"
def chapter_one_tests():
    """ Exercise 1 - Jupiter is at 94°19'. Mercury is at 5s 17° 45'. Venus is at 25 Li 31. For each of these
planets, find (a) the rasi occupied and (b) the advancement from the start of the rasi
occupied."""
    print('Ex-1:',panchanga.dasavarga_from_long(longitude=94+19.0/60, sign_division_factor=1))
    print('Ex-1:',panchanga.dasavarga_from_long(longitude=5*30+17+45.0/60, sign_division_factor=1))
    print('Ex-1:',panchanga.dasavarga_from_long(longitude=6*30+25+31.0/60, sign_division_factor=1))
    """ Exercise 2:
(1) Lagna is in Cn, Sun is in Ar, Moon is in Ta and Mars is in Cp. Find the houses
occupied by Sun, Moon and Mars.
(2) Repeat the exercise, taking Moon as the reference point when finding houses."""
    print('Ex-2:',house.get_relative_house_of_planet(3,0))
    print('Ex-2:',house.get_relative_house_of_planet(3,1))
    print('Ex-2:',house.get_relative_house_of_planet(3,9))
    print('Ex-2:',house.get_relative_house_of_planet(1,0))
    print('Ex-2:',house.get_relative_house_of_planet(1,1))
    print('Ex-2:',house.get_relative_house_of_planet(1,9))
    """ Exercise 3: Moon is at 14°43' in Leo. Sun is at 28°13' in Capricorn. Find the running
tithi. """
    print('Ex 3',int( ( (4*30+12+45.0/60) - (9*30+28+13.0/60) + 360.0 ) %360 / 12)+1)
    """ Example 3: Suppose Sun is at 23°50' in Cp and Moon is at 17°20' in Li. Find yoga """
    print("Ex 4",int((9*30+23+50./60 + 6*30+17+20./60 - 360.0)/(13+20./60))+1)
    
if __name__ == "__main__":
    chapter_one_tests()
    