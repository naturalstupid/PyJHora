import swisseph as swe
from hora.panchanga import panchanga
from hora.horoscope.chart import charts
" Rajiv Gandhi"
dob = (1944,8,20)
tob = (7,11,40)
lat = 18.0+59.0/60
lon = 72.0+49.0/60
tz = 5.5
tob_in_hours = tob[0]+tob[1]/60.0+tob[2]/3600.0
place = panchanga.Place('unknown',lat,lon,tz)
#jd = panchanga.julian_day_number(dob,tob)
jd = swe.julday(dob[0],dob[1],dob[2], tob_in_hours)
cht = charts.divisional_chart(jd,place)
print(cht)
