PyHora 3.1.2
=================
Python package containing almost all the features described in the book

Vedic Astrology - An Integrated Approach - by PVR Narasimha Rao
 
Observational Indian lunisolar calendar, horoscope and matching using the Swiss ephemeris (Hindu
Drig-ganita Panchanga).

Features
--------
See - package_structure.md for package structure

Changes since V3.0.5
=====================
* Data: Added: south indian marriage compatibility csv database file, Marriage_Compatibility-V4.0.1.xlsx
* horoscope/chart/charts.py - benefics_and_malefics function to calculate benefics/malefics based on tithi and planet associations.
* horoscope/chart/dosha.py - functions to calculate various doshas: kala sarpa, manglik/sevvay, pitru, guru chandala, ganda moola, kalathra, ghata and shrapit.
* horoscope/chart/house.py - added *functions associations_of_the_planet* and *baadhakas_of_raasi* 
* horoscope/chart/raja_yoga.py - minor changes: getting benefics from charts.py instead of const.py
* horoscope/chart/strength.py - minor changes: getting benefics from charts.py instead of const.py
* horoscope/match/compatibility.py - Major change: Introduce South Indian (பத்து பொருத்தம்) in addition to existing Ashta Koota. Also automatically checks if dina/gana/yoni/rasi and rajju are matching - depending on the varna of the girl rasi.
* horoscope/prediction.py - provides general predictions based on lagna raasi, planets in houses and lords in houses.
* lang/ - Added language strings for dosha, prediction. ** Please note that translations are based on google translate and hence may not be accurate - for example the word native is translated as "பூர்வீகம்". **
* panchanga/drik.py - Added new function `next_solar_eclipse(jd,place)` to calculate next solar eclipse date.
* ui/ - added changes to support south indian compatibility
* const.py - added constants related to dosha and compatibility
* utils.py - added array lists to support dosha and compatibility.

Major Changes since V2.6.9
==========================
* Divisional chart calculations were incorrect in V2.6.9 or before. They have been fixed now
* Several new dhasa have been added. (14 Graha Dhasa, 19 Rasi Dhasa and 3 Annual Dhasa)
* Graha / Nakshatra Dhasas: 
    * vimsottari, ashtottari, yogini, shodasottari, dwadasottari, dwisatpathi, panchottari, satabdika, chaturaaseeti sama, shashtisama, shattrimsa sama, naisargika, tara, karaka
* Raasi Dhasas:
    * narayana, kendraadhi_rasi, sudasa, drig, nirayana, shoola, kendraadhi karaka, chara, lagnamsaka, padhanadhamsa, mandooka, sthira, tara lagna, brahma, varnada, yogardha, navamsa, paryaaya, trikona, kalachakra
* Annual Dhasas:
    * patyayini, varsha vimsottari, varsha narayana

* Stronger Planet and Rasi are now calculated using planet positions and longitudes (in V2.6.9 or before it was only based on planet houses)

Computation of the five essentials of the panchangam:
* Tithi
* Nakshatra
* Yoga
* Karana
* Vaara

Not just the values, but also the end times of tithis and nakshatras
are computed. The only factor limiting the accuracy of the program
output is the uncertainity in your input values (latitude, longitude).

Also includes computation of sunrise, sunset, moonrise and moonset.

Also Included :
* Instantaneous planetary positions, including Lagna (Ascendant)
* Navamsa positions
* Choghadiya/Gauri panchanga
* Vimsottari Dasha-Bhukti
* Rahu Kala, Yamaganda Kala, Gulika Kala
* Abhijit muhurta and Durmuhurtams
* Marriage compatibility details (0.9.6)
* Special Lagnas and Upagrahas added to charts (1.0.1)
* Ashtaka Varga charts and Shodhya pinda(0.9.8)
* Print the UI as PDF (using img2pdf and pillow to combine two tabs into one page)

Available in English, Tamil and Telugu, Hindi(0.9.7) and Kannada (0.9.8)
-------------------------------------------------------------------------

You can add your own language by creating `list_values_xx.txt` and `msg_strings_xx.txt`	by copying the _en files and replacing with appropriate native language strings.

Do not forget to add the new language into the `available_languages` in `horo_chart.py` and/or `horo_chart_tabs.py`

NOTE:
All timings are end timings. Timings displayed higher than 24:00 denote
hours past midnight because the Hindu day (tithi) starts and ends with
sunrise. If applicable, daylight savings (DST) are accounted for
automatically based on the date and place entered in the textboxes.


Requirements
------------

Python interface to Swiss ephemeris.

```
	pip install pyswisseph	# OR apt-get install pyswisseph
```
The core of the library (`panchanga.py` and `horoscope.py`) can be imported into other code
or used from the command line.

There are three UI files namely: `horo_chart.py`, `horo_chart_tabs.py` and `match_ui.py`.
`horo_chart.py` - provides a one page panchanga, rasi and navamsa charts
`horo_chart_tabs.py`- provides multi-tab/page panchanga, divisional charts and marriage compatibility
`match_ui.py` - provides just marriage compatibility between boy and girl based on their birh stars.

In order to just _run_ the GUI, you also need pyqt6:

```
    pip install pyqt6

```

Using the GUI
-------------

Enter Name, and Place with country name (e.g. Chennai, IN)
If you get an error, enter latitude, longitude and time zone manually.
If you want to be precise, enter the lat/long of the exact place (e.g. hospital)
You can use google to find the latitude, longitude, time zone of the place

Type the Date in YYY,MM,DD format in the 'Date' field. Negative value for YYYY are
interpolated as proleptic Gregorian calendar (Before Christ BC).

Enter Time of birth, choose chart style, ayanamsa mode, language of display

Click Show Chart to display the birth (Raasi and Navamsam) charts

Click Show PDF to save the screen as a PDF file

Using the Code / command line
------------------------------
```
	import horo_chart, panchanga, horoscope
    App = QApplication(sys.argv)
    chart_type = 'North'
    chart = horo_chart.ChartWindow(chart_type=chart_type)
    chart.language('Tamil')
    chart.name('Krishna')
    chart.place('Mathura,IN')
    chart.date_of_birth('-3229,6,17')
    chart.time_of_birth('23:59:00')
    chart.time_zone('5.5')
    chart.chart_type(chart_type)
    chart.compute_horoscope()
    chart.minimum_compatibility_score(20.0)
    chart.mahendra_porutham(False)
    chart.vedha_porutham(False)
    chart.rajju_porutham(False)
    chart.sthree_dheerga_porutham(False)
    chart.show()
    chart.save_as_pdf('delme.pdf')
```
Accuracy
--------

The program is as accurate as the Swiss Ephemeris installed on your system. So generally it is
accurate for years 13000 BCE to 16800 CE. The
computational speed stays the same no matter which date you enter. Required swiss ephimeres files are also /ephe/ folder of this repository.
Overall size of these files is more than 100 MB. To reduce your application size, you can restrict the dates within a range and could remove those ephimeres files from the folder.

Personal Opinion:
------------------
When using BC dates (such as mahabharatha dates) it is advised to use `SURYA_SIDHANTHA` or `SUNDAR_SS` as ayanamsa styles, as ayanamsa values of every other ayanamsa types such as `LAHIRI, KP` etc are inaccurate. 
`SUNDAR_SS` is a sine curve forcing zero ayanamsa every 3200 years from -3101 BCE and 27 degrees as peak ayanamsa.

API Documents
-------------
API are in README.md of respective folders. HTML links are provided here below: 

License
-------
See LICENSE file.

