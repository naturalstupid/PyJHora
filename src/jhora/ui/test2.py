import datetime
#"""
def vaakya_tamil_month(year, month_number):
    """
        Ref: https://groups.google.com/g/mintamil/c/DSXP2KHvgRw - by Ravi Annaswamy
    """
    tamil_month_names = 'சித்திரை,வைகாசி,ஆனி,ஆடி,ஆவணி,புரட்டாசி,ஐப்பசி,கார்த்திகை,மார்கழி,தை,மாசி,பங்குனி'.split(',')

    tamil_month_start_days = \
    [0,
     30.925555,
     62.328888,
     93.939444,
     125.409444,
     156.445555,
     186.901666,
     216.803611,
     246.310277,
     275.658333,
     305.112777,
     334.919444]
    
    
    # Step 1: Calculate how many Kali years are over.
    # Kali yuga started 3101 B.C. when all planets were aligned on one
    # star on other side of earth, so invisible in India.
    kali_year_finished = year+3101
    #print('Year:', year, 'Finished kali:', kali_year_finished)
    
    # Step 2: Count the number of solar years in days
    kd_base = 365.25868055555554 * kali_year_finished
    
    # Step 3: Adjust for Kali arrival delay time. This count represents
    # absolute count of days for this year's new year day.
    kali_sudda_dinam = kd_base - 2.147569444444444
    
    # Step 4: Calculate month start by adding the start days of the month according to
    # Aryabhatiya approximation for average month lengths.
    month_start_kd = kali_sudda_dinam + tamil_month_start_days[month_number-1]
    
    # Step 5: If this happened after sunset, then make the next day 
    kddays=int(month_start_kd)
    kdhours=month_start_kd-kddays
    hours=int(kdhours*24)
    #print(hours)
    minutes=round(((kdhours*24)-hours)*60)
    #print(hours,minutes)
    if kdhours>0.5:
        kddays+=1
    #print(kddays)
    
    # Step 6: Find the day of the week
    weekday = 'வெள்ளி சனி ஞாயிறு திங்கள் செவ்வாய் புதன் வியாழன்'.split()[kddays%7]
    
    # Step 7: Convert to English date.
    # January 1st of 1900 was Kali yuga's 1826555'th day
    # See how many days have elapsed since and add to English date.
    diff=kddays-1826555
    month_birthday = datetime.datetime(1900,1,1,0,0,0)+datetime.timedelta(days=diff)
    
    # Step 8: To calculate how many days in this month, find next month start.
    if month_number < 12:
        next_mon_kd = kali_sudda_dinam + tamil_month_start_days[month_number]
    else:
        next_mon_kd = kali_sudda_dinam + 365.258680555
    if next_mon_kd - int(next_mon_kd)>0.5:
        next_mon_kd=int(next_mon_kd)+1
    else:
        next_mon_kd=int(next_mon_kd)
    next_mon_birthday = datetime.datetime(1900,1,1,0,0,0)+datetime.timedelta(days=next_mon_kd-1826555)
    num_days_in_this_month = (next_mon_birthday-month_birthday).days
    
    return tamil_month_names[month_number-1], datetime.datetime.strftime(month_birthday, '%d-%m-%Y'), weekday, num_days_in_this_month, month_start_kd

for month_number in range(1,13):
    print(vaakya_tamil_month(2024,month_number))
exit()
#"""
from jhora.panchanga import drik
from jhora import utils
def tamil_solar_month_and_date(panchanga_date,place):
    jd = utils.julian_day_number(panchanga_date, (10,0,0))
    jd_set = drik.sunset(jd, place)[2]
    jd_utc = jd_set - place.timezone/24
    sr = drik.solar_longitude(jd_utc)
    tamil_month = int(sr/30)
    daycount=1
    while True:
        if sr%30<1 and sr%30>0:
            break
        jd_utc -= 1
        sr = drik.solar_longitude(jd_utc)
        daycount+=1
    return tamil_month, daycount

dob = drik.Date(2025,1,1); tob = (10,34,0); place = drik.Place('Chennai,India',13.0878,80.2785,5.5)
jd = utils.julian_day_number(dob,tob)
for _ in range(365):
    year,month,day,_=utils.jd_to_gregorian(jd)
    print(year,month,day,tamil_solar_month_and_date(drik.Date(year,month,day), place))
    jd += 1
    