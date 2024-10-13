### Graha Dhasas:
#### Aayu Dhasa: jhora.horoscope.dhasa.graha.aayu
##### get\_dhasa\_antardhasa(jd,place,aayur\_type=None,include\_antardhasa=True,apply\_haranas=True):
    """
        provides Aayu dhasa bhukthi for a given date in julian day (includes birth time)
        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param aayur_type (0=Pindayu, 1=Nisargayu, 2=Amsayu, None=Automatically determine whichever is applicable)
        @param include_antardhasa: True (include) False (exclude) antardhasa 
        @param apply_haranas: (True/False) whether to or not to apply haranas (Default=True)
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start] if include_antardhasa=True
        @return: a list of [dhasa_lord,dhasa_start] if include_antardhasa=False
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Ashtottari Dhasa: jhora.horoscope.dhasa.graha.ashtottari
##### get\_ashtottari\_dhasa\_bhukthi(jd, place, divisional\_chart\_factor=1, star\_position\_from_moon=1, use\_tribhagi\_variation=False, include\_antardhasa=True, antardhasa\_option=1, dhasa\_starting\_planet=1, seed\_star=6)
    """
        provides Ashtottari dhasa bhukthi for a given date in julian day (includes birth time)
        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param include_antardhasa: True (include) False (exclude) antardhasa (Default=True)
        @param antardhasa_option: (Not applicable if use_rasi_bhukthi_variation=True)
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @param seed_star 1..27. Default = 6
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Buddhi Gathi Dhasa: jhora.horoscope.dhasa.graha.buddhi_gathi
##### get\_dhasa\_bhukthi(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardhasa=True)
    """
        provides Buddhi Gathi dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param years: Yearly chart. number of years from date of birth
        @param months: Monthly chart. number of months from date of birth
        @param sixty_hours: 60-hour chart. number of 60 hours from date of birth
        @param include_antardhasa: True (include) False (exclude) antardhasa (Default=True)
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start] if include_antardhasa=True
        @return: a list of [dhasa_lord,dhasa_start] if include_antardhasa=False
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Chathuraseethi Sama Dhasa: jhora.horoscope.dhasa.graha.chathuraaseethi_sama
##### get\_dhasa\_bhukthi(dob,tob,place,divisional\_chart\_factor=1,include\_antardhasa=True, star\_position\_from\_moon=1, use\_tribhagi\_variation=False, seed\_star=15,dhasa\_starting\_planet=1,antardhasa\_option=1):
    """
        returns a dictionary of all mahadashas and their start dates
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param include_antardhasa: True (include) False (exclude) antardhasa (Default=True)
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param seed_star 1..27. Default = 15
        @param antardhasa_option:
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Dwadasottari Dhasa: jhora.horoscope.dhasa.graha.dwadasottari
##### get\_dhasa\_bhukthi(dob,tob,place,divisional\_chart\_factor=1,include\_antardhasa=True, star\_position\_from\_moon=1, use\_tribhagi\_variation=False, seed\_star=27,dhasa\_starting\_planet=1,antardhasa\_option=1):
    """
        returns a dictionary of all mahadashas and their start dates
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param include_antardhasa: True (include) False (exclude) antardhasa (Default=True)
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param seed_star 1..27. Default = 27
        @param antardhasa_option:
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Dwisatpathi Dhasa: jhora.horoscope.dhasa.graha.dwisatpathi
##### get\_dhasa\_bhukthi(dob,tob,place,divisional\_chart\_factor=1,include\_antardhasa=True, star\_position\_from\_moon=1, use\_tribhagi\_variation=False, seed\_star=19,dhasa\_starting\_planet=1,antardhasa\_option=1):
    """
        returns a dictionary of all mahadashas and their start dates
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param include_antardhasa: True (include) False (exclude) antardhasa (Default=True)
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param seed_star 1..27. Default = 19
        @param antardhasa_option:
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Kaala Dhasa: jhora.horoscope.dhasa.graha.kaala
##### get\_dhasa\_antardhasa(dob,tob,place,years=1,months=1,sixty\_hours=1,include\_antardhasa=False)
    """
        provides kaala dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param years: Yearly chart. number of years from date of birth
        @param months: Monthly chart. number of months from date of birth
        @param sixty_hours: 60-hour chart. number of 60 hours from date of birth
        @param include_antardhasa: True (include) False (exclude) antardhasa (Default=True)
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start] if include_antardhasa=True
        @return: a list of [dhasa_lord,dhasa_start] if include_antardhasa=False
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Karaka Dhasa: jhora.horoscope.dhasa.graha.karaka
##### get\_dhasa\_antardhasa(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardhasa=True)
    """
        provides karaka dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param years: Yearly chart. number of years from date of birth
        @param months: Monthly chart. number of months from date of birth
        @param sixty_hours: 60-hour chart. number of 60 hours from date of birth
        @param include_antardhasa: True (include) False (exclude) antardhasa (Default=True)
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start] if include_antardhasa=True
        @return: a list of [dhasa_lord,dhasa_start] if include_antardhasa=False
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Karana Chathuraseethi Sama Dhasa: jhora.horoscope.dhasa.graha.karana_chathuraaseethi_sama
##### get\_dhasa\_bhukthi(dob,tob,place,include\_antardhasa=True,use\_tribhagi\_variation=False)
    """
        provides karana chathuraaseethi sama dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start] if include_antardhasa=True
        @return: a list of [dhasa_lord,dhasa_start] if include_antardhasa=False
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Naisargika Dhasa: jhora.horoscope.dhasa.graha.naisargika
##### get\_dhasa\_bhukthi(dob, tob, place, divisional\_chart\_factor=1, years=1, months=1, sixty\_hours=1, include\_antardhasa=True, mahadhasa\_lord\_has\_no\_antardhasa=True, antardhasa\_option1=False, antardhasa\_option2=False)
    """
        provides Naisargika dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone)
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param years: Yearly chart. number of years from date of birth
        @param months: Monthly chart. number of months from date of birth
        @param sixty_hours: 60-hour chart. number of 60 hours from date of birth
        @param include_antardhasa: True (include) False (exclude) antardhasa (Default=True)
        @param mahadhasa_lord_has_no_antardhasa=True => Mahadhasa lord has no antardhasa. Default=True
        @param antardhasa_option1=True => Planets in 3rd and 10th from dasa lord have no antardhasa. Default=False
        @param antardhasa_option2=True => Planets in 2nd,6th,11th and 12th from dasa lord have no antardhasa. Default=False
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start] if include_antardhasa=True
        @return: a list of [dhasa_lord,dhasa_start] if include_antardhasa=False
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Panchottari Dhasa: jhora.horoscope.dhasa.graha.panchottari
##### get\_dhasa\_bhukthi(dob,tob,place,divisional\_chart\_factor=1,include\_antardhasa=True, star\_position\_from\_moon=1, use\_tribhagi\_variation=False, seed\_star=17,dhasa\_starting\_planet=1,antardhasa\_option=1)
    """
        returns a dictionary of all mahadashas and their start dates
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param include_antardhasa: True (include) False (exclude) antardhasa (Default=True)
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param seed_star 1..27. Default = 17
        @param antardhasa_option:
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Saptharishi Nakshathra Dhasa jhora.horoscope.dhasa.graha.saptharishi_nakshathra
##### get\_dhasa\_bhukthi(dob, tob, place, divisional\_chart\_factor=1, include\_antardhasa=True, star\_position\_from\_moon=1, use\_tribhagi\_variation=False, dhasa\_starting\_planet=1,antardhasa\_option=1)
    """
        returns a dictionary of all mahadashas and their start dates
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param include_antardhasa: True (include) False (exclude) antardhasa (Default=True)
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param antardhasa_option: (Not applicable if use_rasi_bhukthi_variation=True)
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Sataatbika Dhasa jhora.horoscope.dhasa.graha.sataatbika
##### get\_dhasa\_bhukthi(dob,tob,place,divisional\_chart\_factor=1,include\_antardhasa=True, star\_position\_from\_moon=1, use\_tribhagi\_variation=False, seed\_star=27,dhasa\_starting\_planet=1,antardhasa\_option=1)
	"""
        returns a dictionary of all mahadashas and their start dates
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param include_antardhasa True/False. Default=True 
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param seed_star 1..27. Default = 27
        @param antardhasa_option:
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Shastihayani Dhasa (aka Shasti Sama) jhora.horoscope.dhasa.graha.shastihayani
##### get\_dhasa\_bhukthi(dob, tob, place,include\_antardhasa=True, star\_position\_from\_moon=1, use\_tribhagi\_variation=False, divisional\_chart\_factor=1, seed\_star=1, dhasa\_starting\_planet=1)
    """
        returns a dictionary of all mahadashas and their start dates
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param include_antardhasa True/False. Default=True 
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param seed_star 1..27. Default = 1
        @param antardhasa_option: (Not applicable if use_rasi_bhukthi_variation=True)
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Shattrimsa Sama Dhasa jhora.horoscope.dhasa.graha.shattrimsa_sama
##### get\_dhasa\_bhukthi(dob, tob, place, include\_antardhasa=True, star\_position\_from\_moon=1, use\_tribhagi\_variation=False, divisional\_chart\_factor=1, seed\_star=22, dhasa\_starting\_planet=1)
    """
        returns a dictionary of all mahadashas and their start dates
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param seed_star 1..27. Default = 22
        @param antardhasa_option: (Not applicable if use_rasi_bhukthi_variation=True)
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Shodasottari Dhasa jhora.horoscope.dhasa.graha.shodasottari
##### get\_dhasa\_bhukthi(dob, tob, place, include\_antardhasa=True, star\_position\_from\_moon=1, use\_tribhagi\_variation=False, divisional\_chart\_factor=1, seed\_star=8, dhasa\_starting\_planet=1)
    """
        returns a dictionary of all mahadashas and their start dates
        @param dob: Date Struct (year,month,day)
        @param tob: time tuple (h,m,s) 
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param seed_star 1..27. Default = 8
        @param antardhasa_option: (Not applicable if use_rasi_bhukthi_variation=True)
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Tara Dhasa jhora.horoscope.dhasa.graha.tara
##### get\_dhasa\_bhukthi(dob, tob, place, divisional\_chart\_factor=1, years=1, months=1, sixty\_hours=1, include\_antardasa=True):
    """
        provides Tara dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """
#### Tithi Ashtottari Dhasa jhora.horoscope.dhasa.graha.tithi_ashtottari
##### get\_ashtottari\_dhasa\_bhukthi(jd, place, use\_tribhagi\_variation=False, include\_antardhasa=True, tithi\_index=1)
    """
        provides Tithi Ashtottari dhasa bhukthi for a given date in julian day (includes birth time)
        This is Ashtottari Dhasa based on tithi instead of nakshathra
        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param include_antardhasa True/False. Default=True 
        @param tithi_index: 1=>Janma Tithi 2=>Dhana 3=>Bhratri, 4=>Matri 5=Putra 6=>Satru 7=>Kalatra 8=>Mrutyu 
                        9=>Bhagya 10=>Karma 11=>Laabha 12=>Vyaya 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Tithi Yogini Dhasa jhora.horoscope.dhasa.graha.tithi_yogini
##### get\_dhasa\_bhukthi(jd, place, use\_tribhagi\_variation=False, include\_antardhasa=True, tithi\_index=1)
    """
        provides Tithi Yogini dhasa bhukthi for a given date in julian day (includes birth time)
        This is Ashtottari Dhasa based on tithi instead of nakshathra
        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param include_antardhasa True/False. Default=True 
        @param tithi_index: 1=>Janma Tithi 2=>Dhana 3=>Bhratri, 4=>Matri 5=Putra 6=>Satru 7=>Kalatra 8=>Mrutyu 
                        9=>Bhagya 10=>Karma 11=>Laabha 12=>Vyaya 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Vimsottari Dhasa jhora.horoscope.dhasa.graha.vimsottari
##### get\_vimsottari\_dhasa\_bhukthi(jd, place, star\_position\_from\_moon=1, use\_tribhagi\_variation=False, use\_rasi\_bhukthi\_variation=False, include\_antardhasa=True, divisional\_chart\_factor=1, seed\_star=3, antardhasa\_option=1, dhasa\_starting\_planet=1)
    """
        provides Vimsottari dhasa bhukthi for a given date in julian day (includes birth time)
        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @param use_rasi_bhukthi_variation: Default False. True will give rasi bhukthi variation of vimosottari dasa
        @param include_antardhasa True/False. Default=True 
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param seed_star 1..27. Default = 3 
        @param antardhasa_option: (Not applicable if use_rasi_bhukthi_variation=True)
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start] if include_antardhasa=True
        @return: a list of [dhasa_lord,dhasa_start] if include_antardhasa=False
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Yoga Vimsottari Dhasa jhora.horoscope.dhasa.graha.yoga_vimsottari
##### get\_dhasa\_bhukthi(jd, place, use\_tribhagi\_variation=False)
    """
        provides Yoga Vimsottari dhasa bhukthi for a given date in julian day (includes birth time)
        This is vimsottari but based on yogam instead of nakshathra
        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start] if include_antardhasa=True
        @return: a list of [dhasa_lord,dhasa_start] if include_antardhasa=False
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Yogini Dhasa jhora.horoscope.dhasa.graha.yogini
##### get\_yogini\_dhasa\_bhukthi(dob,tob,place,include\_antardhasa=True):
    """
        provides Yogini dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """
### Rasi Dhasa
#### Narayana Dhasa jhora.horoscope.dhasa.raasi.narayana
##### narayana\_dhasa\_for\_divisional\_chart(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True):
    """
        calculate narayana dhasa for divisional charts / annual charts
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """
##### narayana\_dhasa\_for\_rasi\_chart(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True):
    """
        calculate narayana dhasa for Rasi chart / annual chart
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """
#### Lagna Kendraadhi Raasi Dhasa (Moola) jhora.horoscope.dhasa.raasi.moola
##### kendradhi\_rasi\_dhasa(dob,tob,place,divisional\_chart\_factor=1):
    """
        calculate Lagna Kendraadhi dhasa aka Moola Dhasa
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """
##### lagna\_kendradhi\_rasi\_dhasa(dob,tob,place,divisional_chart_factor=1):
	"""
		Calls kendradhi_rasi_dhasa(dob,tob,place,divisional_chart_factor=1):
	"""
##### kendradhi\_karaka\_dhasa(dob,tob,place,divisional\_chart\_factor=1):
    """
        calculate Kendraadhi Karaka dhasa aka Moola Dhasa
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """
#### Sudasa Dhasa jhora.horoscope.dhasa.raasi.sudasa
##### sudasa\_dhasa\_bhukthi(dob,tob,place,divisional\_chart\_factor=1):
    """
        calculate Sudasa Dhasa
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """
#### Drig Dhasa jhora.horoscope.dhasa.raasi.drig
##### drig\_dhasa\_bhukthi(dob,tob,place,divisional\_chart\_factor=1):
    """
        computes drig dhasa from the chart
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @return: list of drig dhasa from date of birth 
          Format: [ [dhasa_lord, dhasa_start_date, dhasa_end_date, [bhukthi_lord1, bhukthi_lord2...], dhasa_duration],...]
          Example: [[2, '1912-1-1', '1916-1-1', [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1], 4], 
                    [5, '1916-1-1', '1927-1-1', [5, 4, 3, 2, 1, 0, 11, 10, 9, 8, 7, 6], 11], ...]]
    """
#### Nirayana Shoola Dhasa jhora.horoscope.dhasa.raasi.nirayana
##### nirayana\_shoola\_dhasa\_bhukthi(dob,tob,place,divisional\_chart\_factor=1):
    """
        calculate Nirayana Shoola Dhasa
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """
#### Shoola Dhasa jhora.horoscope.dhasa.raasi.shoola
##### shoola\_dhasa\_bhukthi(dob,tob,place,divisional\_chart\_factor=1):
    """
        calculate Shoola Dhasa
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @return: 2D list of [dhasa_lord,dhasa_start,[Bhukthi_lord1,bhukthi_lord2,], dhasa_duraation
          Example: [ [7, '1993-6-1', '1996-6-1', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 3], ...]
    """
#### Chara Dhasa jhora.horoscope.dhasa.raasi.chara
##### get\_dhasa\_antardhasa(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True)
    """
        calculate Chara dhasa for Rasi chart / annual chart
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """    
#### Lagnamsaka Dhasa jhora.horoscope.dhasa.raasi.lagnamsaka
##### get\_dhasa\_antardhasa(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True)
    """
        calculate Lagnamsaka dhasa for Rasi chart / annual chart
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """    
#### Padhanadhamsa Dhasa jhora.horoscope.dhasa.raasi.padhanadhamsa
##### get\_dhasa\_antardhasa(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True)
    """
        calculate Padhanadhamsa dhasa for Rasi chart / annual chart
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """    
#### Mandooka Dhasa jhora.horoscope.dhasa.raasi.mandooka
##### get\_dhasa\_antardhasa(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True)
    """
        calculate Mandooka dhasa for Rasi chart / annual chart
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """    
#### Sthira Dhasa jhora.horoscope.dhasa.raasi.sthira
##### get\_dhasa\_antardhasa(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True)
    """
        calculate Sthira dhasa for Rasi chart / annual chart
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """    
#### Tara Lagna Dhasa jhora.horoscope.dhasa.raasi.tara_lagna
##### get\_dhasa\_antardhasa(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True)
    """
        calculate Tara Lagna dhasa for Rasi chart / annual chart
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """    
#### Brahma Dhasa jhora.horoscope.dhasa.raasi.brahma
##### get\_dhasa\_antardhasa(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True)
    """
        calculate Brahma dhasa for Rasi chart / annual chart
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """    
#### Varnada Dhasa jhora.horoscope.dhasa.raasi.varnada
##### get\_dhasa\_antardhasa(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True)
    """
        calculate Varnada dhasa for Rasi chart / annual chart
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """    
#### Yogardha Dhasa jhora.horoscope.dhasa.raasi.yogardha
##### get\_dhasa\_antardhasa(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True)
    """
        calculate Yogardha dhasa for Rasi chart / annual chart
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """    
#### Navamsa Dhasa jhora.horoscope.dhasa.raasi.navamsa
##### get\_dhasa\_antardhasa(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True)
    """
        calculate Navamsa dhasa for Rasi chart / annual chart
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """    
#### Paryaaya Dhasa jhora.horoscope.dhasa.raasi.paryaaya
##### get\_dhasa\_antardhasa(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True)
    """
        calculate Paryaaya dhasa for Rasi chart / annual chart
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """    
#### Trikona Dhasa jhora.horoscope.dhasa.raasi.trikona
##### get\_dhasa\_antardhasa(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True)
    """
        calculate Trikona dhasa for Rasi chart / annual chart
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """    
### Other Dhasa
#### Kalachakra Dhasa jhora.horoscope.dhasa.raasi.kalachakra
##### kalachakra\_dhasa(lunar\_longitude, dob)
    """
        Kalachara Dhasa calculation
        @param lunar_longitude: Longitude of moon at the time of date/time of birth as float
        	Note: one can get this from panchanga.lunar_longitude()
        @param dob: date of birth as tuple (year,month,day)
        @return: list of [dhasa_rasi,dhasa_rasi_start_date, dhasa_rasi_end_date,[abtadhasa_rasis],dhasa_rasi_duration]
        Example: [[7, '1946-12-2', '1955-12-2', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 9], [8, '1955-12-2', '1964-12-2', [8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7], 9], ...]
    """
#### Sudharsana Chakra Dhasa jhora.horoscope.dhasa.sudharsana_chakra
##### sudharsana\_chakra\_dhasa\_for\_divisional\_chart (jd\_at\_dob, place, dob, years\_from\_dob=0, divisional\_chart\_factor=1)
    """
        calculate sudharsana chakra dhasa for divisional charts / annual charts
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param jd_at_dob: Julian day for birthdate and birth time
        @param place: pancganga.Place Struct ('place_name',latitude,longitude,timezone)
        @param dob: Date of birth as a tuple e.g. (1999,12,31)  
        @param years_from_dob: # years of from year of birth
        @param divisional_chart_factor: integer of divisional chart 1=Rasi, 2=D2, 9=D9 etc 
        @return: [lagna_periods,moon_periods,sun_periods]
          Each dhasa period will have the following format:
          [planet index,(dhasa_start_year, month, date,longitude),dhasa duration],...
          [0, (1987, 10, 31, 15.388383474200964), 2.5], [1, (1987, 11, 3, 4.348383475095034), 2.5],....
          
    """
#### Mudda (Varsha Vimsottari) jhora.horoscope.dhasa.annual.mudda
##### varsha\_vimsottari\_dhasa\_bhukthi (jd, place, years)
    """
        Calculates Varsha Vimshottari (also called Mudda dhasa) Dasha-bhukthi-antara-sukshma-prana
        @param jd: Julian day for birthdate and birth time
        @param place: pancganga.Place Struct ('place_name',latitude,longitude,timezone)
        @param years: # years of from year of birth
        @return: 2D list of [ (dhasa_lord,Bhukthi_lord,bhukthi_start date, bhukthi_duraation),...
          Example: [(7, 7, '1993-06-03', 8.22), (7, 4, '1993-06-11', 7.31), ...]
    """
#### Patyayini Dhasa jhora.horoscope.dhasa.annual.patyayini
##### patyayini\_dhasa (jd\_years, place, ayanamsa\_mode='Lahiri', divisional\_chart\_factor=1)
    """
        Compute Patyaayini Dhasa
        Should be used for Tajaka Annual charts
        @param jd_years:Julian day number for Tajaka Annual date/time
        @param place: panchanga.Place struct tuple of ('Place',latitude,longitude,time_zone_offset)
        @param ayanamsa_mode: Default = 'Lahiri'
        @param divisional_chart_factor: Default = 1 (Raasi) - See const.division_chart_factors for other possible values
        @return patyayini dhasa values as a list [planet, dhasa_duration in days]
        Example: [[5, (1993, 6, 26), 24.9], [3, (1993, 8, 13), 48.1], [1, (1993, 8, 14), 0.57],...]]
    """
#### Varsha Narayana Dhasa jhora.horoscope.dhasa.raasi.narayana
##### varsha\_narayana\_dhasa\_bhukthi(dob,tob,place,years=1,months=1,sixty\_hours=1,divisional\_chart\_factor=1,include\_antardasa=True):
    """
        calculate Varsha Narayana dhasa for Rasi chart / annual chart
        for just divisional charts - use divisional_chart_factor and set years_from_dob = 0
        for annual charts use years_from_dob the non zero value
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param divisional_chart_factor: 1 for Rasi, 2 for Hora etc 
        @param years: Yearly chart, # of years from date of birth
        @param months: Monthly chart, # of months from date of birth
        @param sixty_hours: 60 hour chart, # 60hrs from date of birth
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """    
