import swisseph as swe
from collections import namedtuple as struct
from jhora import utils, const
_rise_flags = swe.BIT_HINDU_RISING | swe.FLG_TRUEPOS | swe.FLG_SPEED # V3.2.3 # Speed flag added for retrogression
_ayanamsa_value = None
Date = struct('Date', ['year', 'month', 'day'])
Place = struct('Place', ['Place','latitude', 'longitude', 'timezone'])
def normalize_angle(angle, start=0):
    """
    Normalize angle to be within the range from start to start + 360 degrees.
    """
    while angle >= start + 360:
        angle -= 360
    while angle < start:
        angle += 360
    return angle
def set_ayanamsa_mode(ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE,ayanamsa_value=None,jd=None):
    """
        Set Ayanamsa mode
        @param ayanamsa_mode - Default - Lahiri
            Other possible values: 
            FAGAN, KP, RAMAN, USHASHASHI, YUKTESHWAR, SURYASIDDHANTA, SURYASIDDHANTA_MSUN,ARYABHATA,ARYABHATA_MSUN,
            SS_CITRA, TRUE_CITRA, TRUE_REVATI, SS_REVATI, SENTHIL, SUNDAR_SS, SIDM_USER
        @param ayanamsa_value - Need to be supplied only in case of 'SIDM_USER'
        @param jd: Julian day number to be supplied only for ayanamsa modes: SENTHIL and SUNDAR_SS
        See 'available_ayanamsa_modes' for the list of available models
        @return None
    """
    global _ayanamsa_mode,_ayanamsa_value
    key = ayanamsa_mode.upper()
    #print('panchanga setting',key,ayanamsa_value,jd)
    if key in [am.upper() for am in const.available_ayanamsa_modes.keys()]:
        if key == "SIDM_USER":
            _ayanamsa_value = ayanamsa_value
            swe.set_sid_mode(swe.SIDM_USER,ayanamsa_value)
        else:
            swe.set_sid_mode(const.available_ayanamsa_modes[key])
    else:
        ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE
        swe.set_sid_mode(const.available_ayanamsa_modes[const._DEFAULT_AYANAMSA_MODE] )#swe.SIDM_LAHIRI)
    _ayanamsa_mode = ayanamsa_mode
    const._DEFAULT_AYANAMSA_MODE = _ayanamsa_mode
reset_ayanamsa_mode = lambda: swe.set_sid_mode(const.available_ayanamsa_modes[const._DEFAULT_AYANAMSA_MODE]) \
                      if const._DEFAULT_AYANAMSA_MODE not in ['SIDM_USER','SENTHIL','SUNDAR_SS','KP-SENTHIL'] else \
                      swe.set_sid_mode(swe.SIDM_LAHIRI)
def nakshatra_pada(longitude):
    """ 
        Gives nakshatra (1..27) and paada (1..4) in which given longitude lies
        @param longitude: longitude of the planet 
        @return [nakshathra index, paadham, longitude remainder in the nakshathra]
            Note: Nakshatra index [1..27], Paadha [1..4] reminder in float degrees 
    """
    # 27 nakshatras span 360°
    one_star = (360 / 27)  # = 13°20'
    # Each nakshatra has 4 padas, so 27 x 4 = 108 padas in 360°
    one_pada = (360 / 108) # = 3°20'
    quotient = int(longitude / one_star)
    #reminder = (longitude - quotient * one_star)
    reminder = longitude%one_star
    pada = int(reminder / one_pada)
    #  print (longitude,quotient,pada)
    # convert 0..26 to 1..27 and 0..3 to 1..4
    #print(longitude,quotient,reminder,pada)
    return [1 + quotient, 1 + pada,reminder]

def sidereal_longitude(jd, planet):
    """
        The sequence number of 0 to 8 for planets is not followed by swiss ephemeris
        Need to be sure we pass correct planet reference to swiss ephemeris
        Make sure to pass planets as const._SUN, const._MOON .. const._KETU etc
        For all other functions of this PyJHora libarary one can use 0 to 8 for Sun to Ketu and 9-11 for Urnaus to Pluto
        Computes nirayana (sidereal) longitude of given planet on jd
        Note: This is where the selected/default ayanamsa is adjusted to tropical longitude obtained from swiss ephimeride
        @param jd: Julian Day Number of the UTC date/time.
        NOTE: The julian day number supplied to this function must be UTC date/time.
              All other functions of this PyJHora library will require JD and not JD_UTC
              JD_UTC = JD - Place.TimeZoneInFloatHours
              For example for India JD_UTC = JD - 5.5. For wester time zone -5.0 it JD_UTC = JD - (-5.0)
        @param planet: index of the planet Use const._SUN, const._RAHU etc.
        @return: the sidereal longitude of the planet (0-360 degrees)
    """
    global _ayanamsa_mode,_ayanamsa_value
    if const._TROPICAL_MODE:
        flags = swe.FLG_SWIEPH
    else:
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | _rise_flags
        #set_ayanamsa_mode(_ayanamsa_mode,_ayanamsa_value,jd)
        set_ayanamsa_mode(const._DEFAULT_AYANAMSA_MODE,_ayanamsa_value,jd); _ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE
        #print('drik sidereal long ayanamsa',_ayanamsa_mode, const._DEFAULT_AYANAMSA_MODE)
    longi,flgs = swe.calc_ut(jd, planet, flags = flags)
    reset_ayanamsa_mode()
    return utils.norm360(longi[0]) # degrees
solar_longitude = lambda jd: sidereal_longitude(jd, const._SUN)
lunar_longitude = lambda jd: sidereal_longitude(jd, const._MOON)
def sunrise(jd, place):
    """
        Sunrise when centre of disc is at horizon for given date and place
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [sunrise time as local time in float hours, local time string, and sunrise julian number]
            e.g. [6.5,'06:30 AM',2450424.94]
    """
    # First convert jd to UTC
    y, m, d,_  = utils.jd_to_gregorian(jd)
    jd_utc = utils.gregorian_to_jd(Date(y, m, d))
    
    _,lat, lon, tz = place
    result = swe.rise_trans(jd_utc - tz/24, swe.SUN, geopos=(lon, lat,0.0), rsmi = _rise_flags + swe.CALC_RISE)
    rise_jd = result[1][0]  # julian-day number
    rise_local_time = (rise_jd - jd_utc) * 24 + tz
    """ ADDED THE FOLLOWING IN V2.5.2 TO RECALCULATE RISE_JD"""
    dob = (y,m,d)
    tob = tuple(utils.to_dms(rise_local_time, as_string=False))
    rise_jd = utils.julian_day_number(dob, tob)
    # Convert to local time
    return [rise_local_time, utils.to_dms(rise_local_time),rise_jd]

def extend_angle_range(angles, target):
    """
    Extend angles to cover a wider range if needed for interpolation.
    """
    extended_angles = angles[:]
    while max(extended_angles) - min(extended_angles) < target:
        extended_angles = extended_angles + [angle + 360 for angle in angles]
    return extended_angles

def _get_nakshathra(jd, place):
    tz = place.timezone
    y, m, d, _ = utils.jd_to_gregorian(jd)
    jd_ut = utils.gregorian_to_jd(Date(y, m, d))
    jd_utc = jd - place.timezone / 24.
    rise = sunrise(jd_utc, place)[2]
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [sidereal_longitude(rise + t, const._MOON) for t in offsets]
    unwrapped_longitudes = utils.unwrap_angles(longitudes)
    print("Unwrapped longitudes:", unwrapped_longitudes)

    # Extend angle range if needed
    extended_longitudes = extend_angle_range(unwrapped_longitudes, 360)
    x = offsets * (len(extended_longitudes) // len(unwrapped_longitudes))
    
    nirayana_long = lunar_longitude(jd_utc)
    nak_no, padam_no, _ = nakshatra_pada(nirayana_long)
    y_check = (nak_no * 360 / 27)

    # Normalize y_check to the same range as extended_longitudes
    y_check = normalize_angle(y_check, start=min(extended_longitudes))
    approx_end = utils.inverse_lagrange(x, extended_longitudes, y_check)
    print(x, extended_longitudes, y_check, approx_end)

    ends = (rise - jd_ut + approx_end) * 24 + tz
    answer = [nak_no, padam_no, ends]
    leap_nak = nak_no + 1
    y_check = (leap_nak * 360 / 27)
    y_check = normalize_angle(y_check, start=min(extended_longitudes))
    approx_end = utils.inverse_lagrange(x, extended_longitudes, y_check)
    ends = (rise - jd_utc + approx_end) * 24 + tz
    leap_nak = 1 if nak_no == 27 else leap_nak
    nak_no = int(leap_nak)
    answer += [nak_no, padam_no, ends]
    return answer
def nakshatra(jd,place):
    """
        returns the nakshathra at julian day/time
        @param jd: Julian Day Number of the date/time
        @param place: Place as struct ('Place',latitude,longitude,timezone)
        @return [nakshatra number, nakshatra starting time, nakshatra ending time, nakshatra fraction left, 
                 next nakshatra number, next nakshatra starting time, next nakshatra ending time, next nakshatra fraction left]
          next nakshatra index and next nakshatra time is additionally returned if two nakshatras on same day 
          nakshatra number = [1..27]  Aswini to Revathi
    """
    _nak = _get_nakshathra(jd, place)
    _nak_prev = _get_nakshathra(jd-1, place)
    _nak_no = _nak[0]; _pad_no = _nak[1]; _nak_start = _nak_prev[2]; _nak_end = _nak[2]
    if _nak_start < 24.0:
        _nak_start = -_nak_start #utils.to_dms(_tithi_start)+'(-1)'
    elif _nak_start > 24:
        _nak_start -= 24.0
    result = [_nak_no,_pad_no,_nak_start,_nak_end]+_nak[3:]
    return result
if __name__ == "__main__":
    utils.set_language('ta')
    dob = Date(2024,12,11); tob = (6,30,0); place = Place('Chennai,India',13.0878,80.2785,5.5)
    jd = utils.julian_day_number(dob, tob)
    nak = nakshatra(jd, place)
    print(nak)