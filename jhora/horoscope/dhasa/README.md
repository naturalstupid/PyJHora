### Graha Dhasas:
#### Vimsottari Dhasa
##### get\_vimsottari\_dhasa\_bhukthi (jd, place,star\_position\_from\_moon=1):
    """
        provides Vimsottari dhasa bhukthi for a given date in julian day (includes birth time)
        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param star_position_from_moon: 
        	1 => Default - moon
        	4 => Kshema Star (4th constellation from moon)
        	5 => Utpanna Star (5th constellation from moon)
        	8 => Adhana Star (8th constellation from moon)
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """

#### Ashtottari Dhasa
##### get\_ashtottari\_dhasa\_bhukthi(jd, place,star\_position\_from\_moon=1):
    """
        provides Ashtottari dhasa bhukthi for a given date in julian day (includes birth time)
        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param star_position_from_moon: 
        	1 => Default - moon
        	4 => Kshema Star (4th constellation from moon)
        	5 => Utpanna Star (5th constellation from moon)
        	8 => Adhana Star (8th constellation from moon)
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
#### Yogini Dhasa
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
#### Shodasottari Dhasa
##### get\_dhasa\_bhukthi(dob,tob,place,include\_antardhasa=True):
    """
        provides Shodasottari dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param include_antardhasa True/False. Default=True 
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """
#### Dwadasottari Dhasa
##### get\_dhasa\_bhukthi(dob,tob,place,include\_antardhasa=True,star\_position\_from\_moon=1):
    """
        provides Dwadasottari dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param include_antardhasa True/False. Default=True 
        @param star_position_from_moon: 
        	1 => Default - moon
        	4 => Kshema Star (4th constellation from moon)
        	5 => Utpanna Star (5th constellation from moon)
        	8 => Adhana Star (8th constellation from moon)
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """
#### Dwisatpathi Dhasa
##### get\_dhasa\_bhukthi(dob,tob,place,include\_antardhasa=True,star\_position\_from\_moon=1):
    """
        provides Dwisatpathi dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param include_antardhasa True/False. Default=True 
        @param star_position_from_moon: 
        	1 => Default - moon
        	4 => Kshema Star (4th constellation from moon)
        	5 => Utpanna Star (5th constellation from moon)
        	8 => Adhana Star (8th constellation from moon)
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """
#### Panchottari Dhasa
##### get\_dhasa\_bhukthi(dob,tob,place,include\_antardhasa=True,star\_position\_from\_moon=1):
    """
        provides Panchottari dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param include_antardhasa True/False. Default=True 
        @param star_position_from_moon: 
        	1 => Default - moon
        	4 => Kshema Star (4th constellation from moon)
        	5 => Utpanna Star (5th constellation from moon)
        	8 => Adhana Star (8th constellation from moon)
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """
#### Sataatbika Dhasa
##### get\_dhasa\_bhukthi(dob,tob,place,include\_antardhasa=True,star\_position\_from\_moon=1):
    """
        provides Sataatbika dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param include_antardhasa True/False. Default=True 
        @param star_position_from_moon: 
        	1 => Default - moon
        	4 => Kshema Star (4th constellation from moon)
        	5 => Utpanna Star (5th constellation from moon)
        	8 => Adhana Star (8th constellation from moon)
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """
#### Chathuraseethi Sama Dhasa
##### get\_dhasa\_bhukthi(dob,tob,place,include\_antardhasa=True,star\_position\_from\_moon=1):
    """
        provides Chathuraseethi Sama dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param include_antardhasa True/False. Default=True 
        @param star_position_from_moon: 
        	1 => Default - moon
        	4 => Kshema Star (4th constellation from moon)
        	5 => Utpanna Star (5th constellation from moon)
        	8 => Adhana Star (8th constellation from moon)
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """
#### Shattrimsa Sama Dhasa
##### get\_dhasa\_bhukthi(dob,tob,place,include\_antardhasa=True,star\_position\_from\_moon=1):
    """
        provides Shattrimsa Sama dhasa bhukthi for a given date in julian day (includes birth time)
        @param dob: date of birth as tuple
        @param tob: time of birth as tuple
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param include_antardhasa True/False. Default=True 
        @param star_position_from_moon: 
        	1 => Default - moon
        	4 => Kshema Star (4th constellation from moon)
        	5 => Utpanna Star (5th constellation from moon)
        	8 => Adhana Star (8th constellation from moon)
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start, duration]
          Example: [ [7, 5, '1915-02-09',0.25], [7, 0, '1917-06-10',0.25], ...]
    """
#### Naisargika Dhasa
##### get\_dhasa\_bhukthi(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True):
    """
        provides Naisargika dhasa bhukthi for a given date in julian day (includes birth time)
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
#### Tara Dhasa
##### get\_dhasa\_bhukthi(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True):
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
#### Karaka Dhasa
##### get\_dhasa\_bhukthi(dob,tob,place,divisional\_chart\_factor=1,years=1,months=1,sixty\_hours=1,include\_antardasa=True):
    """
        provides Karaka dhasa bhukthi for a given date in julian day (includes birth time)
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
### Rasi Dhasa
#### Narayana Dhasa
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
#### Lagna Kendraadhi Raasi Dhasa (Moola)
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
#### Sudasa Dhasa
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
#### Drig Dhasa
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
#### Nirayana Shoola Dhasa
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
#### Shoola Dhasa
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
#### Chara Dhasa
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
#### Lagnamsaka Dhasa
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
#### Padhanadhamsa Dhasa
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
#### Mandooka Dhasa
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
#### Sthira Dhasa
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
#### Tara Lagna Dhasa
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
#### Brahma Dhasa
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
#### Varnada Dhasa
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
#### Yogardha Dhasa
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
#### Navamsa Dhasa
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
#### Paryaaya Dhasa
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
#### Trikona Dhasa
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
#### Kalachakra Dhasa
##### kalachakra\_dhasa(lunar\_longitude, dob)
    """
        Kalachara Dhasa calculation
        @param lunar_longitude: Longitude of moon at the time of date/time of birth as float
        	Note: one can get this from panchanga.lunar_longitude()
        @param dob: date of birth as tuple (year,month,day)
        @return: list of [dhasa_rasi,dhasa_rasi_start_date, dhasa_rasi_end_date,[abtadhasa_rasis],dhasa_rasi_duration]
        Example: [[7, '1946-12-2', '1955-12-2', [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6], 9], [8, '1955-12-2', '1964-12-2', [8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7], 9], ...]
    """
#### Sudharsana Chakra Dhasa
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
#### Mudda (Varsha Vimsottari)
##### varsha\_vimsottari\_dhasa\_bhukthi (jd, place, years)
    """
        Calculates Varsha Vimshottari (also called Mudda dhasa) Dasha-bhukthi-antara-sukshma-prana
        @param jd: Julian day for birthdate and birth time
        @param place: pancganga.Place Struct ('place_name',latitude,longitude,timezone)
        @param years: # years of from year of birth
        @return: 2D list of [ (dhasa_lord,Bhukthi_lord,bhukthi_start date, bhukthi_duraation),...
          Example: [(7, 7, '1993-06-03', 8.22), (7, 4, '1993-06-11', 7.31), ...]
    """
#### Patyayini Dhasa
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
#### Varsha Narayana Dhasa
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
