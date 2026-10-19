"""Birth-input exporter for the opt-in JHora 8.0 profile (no GUI or reference data)."""
import datetime as dt
import math
from jhora import const,utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts,sphuta,ashtakavarga
from .jhora8 import _export_profile

SIGNS=['Ar','Ta','Ge','Cn','Le','Vi','Li','Sc','Sg','Cp','Aq','Pi']
PLANETS=['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']
UPAGRAHAS={'Maandi':'maandi','Gulika':'gulika','Kaala':'kaala','Mrityu':'mrityu',
          'Artha Prahara':'artha_praharaka','Yama Ghantaka':'yama_ghantaka'}
LAGNAS={'Bhava Lagna':'bhava_lagna','Hora Lagna':'hora_lagna','Ghati Lagna':'ghati_lagna',
        'Vighati Lagna':'vighati_lagna','Pranapada Lagna':'pranapada_lagna',
        'Sree Lagna':'sree_lagna','Indu Lagna':'indu_lagna','Bhrigu Bindu':'bhrigu_bindhu_lagna',
        'Kunda':'kunda_lagna'}
SOLAR_POINTS={'Dhooma':'dhuma','Vyatipata':'vyatipaata','Parivesha':'parivesha',
              'Indra Chapa':'indrachaapa','Upaketu':'upaketu'}
SPHUTAS={'Prana Sphuta':'prana','Deha Sphuta':'deha','Mrityu Sphuta':'mrityu',
         'Sookshma TriSphuta':'sookshma_tri','Tithi Sphuta':'tithi',
         'Yoga Sphuta (Sun-Moon)':'yoga','Rahu Tithi Sphuta':'rahu_tithi',
         'Kshetra Sphuta':'kshetra','Beeja Sphuta':'beeja','TriSphuta':'tri',
         'ChatusSphuta':'chatur','PanchaSphuta':'pancha','Yoga Sphuta':'yogi',
         'Avayoga Sphuta':'avayogi'}
COLUMNS=['D-1','D-9','D-10 (Trd)','D-2 (US)','D-3 (Trd)','D-4','D-7 (Trd)',
         'D-12 (Trd)','D-16 (Trd)','D-20 (Trd)','D-24 (Trd)','D-27 (Trd)',
         'D-30','D-40','D-45','D-60 (Trd)','D-10 x D-9','D-0','D-5','D-6',
         'D-8','D-11','D-81','D-108','D-144']
DURATIONS={'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17,'Ketu':7,'Venus':20}
DASHA_ORDER=['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
NAKSHATRAS=['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya',
            'Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati',
            'Vishakha','Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttarashadha','Shravana',
            'Dhanishtha','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati']

def absolute(position):
    return position[0]*30+position[1]

def cell(position):
    sign,degree=position
    whole=math.floor(degree)
    minute=math.floor((degree-whole)*60+.5)
    return {'sign':sign,'degrees_in_sign':degree,'formatted':f'{whole}{SIGNS[sign]}{minute:02}'}

def dashas(backend,jd_utc,offset,moon,windows):
    first=DASHA_ORDER[int(moon/(40/3))%9]
    elapsed=(moon/(40/3)%1)*DURATIONS[first]
    order=DASHA_ORDER[DASHA_ORDER.index(first):]+DASHA_ORDER[:DASHA_ORDER.index(first)]
    nominal={}
    start=-elapsed
    for lord in order:
        nominal[(lord,)]=(start,start+DURATIONS[lord])
        start+=DURATIONS[lord]
    for parent in sorted(set(tuple(w) for w in windows),key=len):
        if parent not in nominal:
            raise ValueError(f'Dasha parent {parent} is outside the exported cycle')
        first=parent[-1]
        order=DASHA_ORDER[DASHA_ORDER.index(first):]+DASHA_ORDER[:DASHA_ORDER.index(first)]
        start,end=nominal[parent]
        duration=end-start
        for lord in order:
            span=duration*DURATIONS[lord]/120
            nominal[parent+(lord,)]=(start,start+span)
            start+=span
    epoch=dt.datetime(2000,1,1,12,tzinfo=dt.timezone.utc)
    tz=dt.timezone(dt.timedelta(hours=offset))
    records=[]
    cache={}
    for lords,(start,end) in nominal.items():
        pair=[]
        for years in (start,end):
            if years not in cache:
                ut=backend.call('solar',birth=jd_utc,years=years,flags=2+256+16+65536)
                cache[years]=(epoch+dt.timedelta(days=ut-2451545)).astimezone(tz).isoformat()
            pair.append(cache[years])
        records.append({'lords':list(lords),'start':pair[0],'end':pair[1]})
    return records

def export_chart(date,time,latitude,longitude,utc_offset,*,name='',place_name='',
                 dasha_windows=(),elevation=0.0,swiss_dll=None,ephemeris_path=None):
    """Export the compared 56 points, 25 columns, calendar, and selected dashas.

    Date/time are local civil tuples; coordinates are decimal north/east degrees.
    D0 is retained solely as the native display placeholder. D10 x D9 is explicitly
    traditional D10 followed by traditional D9, recalculated from current inputs.
    """
    civil=dt.datetime(*date,*time)
    if not all(math.isfinite(value) for value in (latitude, longitude, utc_offset, elevation)) or \
            not -90<=latitude<=90 or not -180<=longitude<=180 or not -24<utc_offset<24:
        raise ValueError('Invalid coordinates or UTC offset')
    dob=drik.Date(*date)
    place=drik.Place(place_name,latitude,longitude,utc_offset,elevation=elevation)
    jd=utils.julian_day_number(dob,time)
    with _export_profile(swiss_dll=swiss_dll,ephemeris_path=ephemeris_path) as backend:
        rasi=charts.rasi_chart(jd,place)
        points={'Lagna':absolute(rasi[0][1])}
        points.update({p:absolute(v[1]) for p,v in zip(PLANETS,rasi[1:])})
        for p,f in UPAGRAHAS.items():
            points[p]=absolute(getattr(drik,f+'_longitude')(dob,time,place))
        for p,f in LAGNAS.items():
            points[p]=absolute(getattr(drik,f)(jd,place))
        for p,f in SOLAR_POINTS.items():
            points[p]=absolute(drik.solar_upagraha_longitudes(points['Sun'],f))
        for p,f in SPHUTAS.items():
            points[p]=absolute(getattr(sphuta,f+'_sphuta')(dob,time,place))
        varna=charts.varnada_lagna_longitudes(dob,time,place,
            varnada_method=const.VARNADA_METHOD.BV_RAMAN,jhora_compatible=True)
        points.update({('Varnada Lagna' if k=='V1' else k):absolute(p) for k,p in varna})
        rows={p:{} for p in points}
        natal=[[p,[int(lon//30),lon%30]] for p,lon in points.items()]
        for col in COLUMNS:
            if col=='D-0':
                pp=[[p,[0,0.0]] for p in points]
            elif col=='D-1':
                pp=natal
            elif col=='D-10 x D-9':
                pp=charts.mixed_chart_from_rasi_positions(natal,10,1,9,1)
            else:
                n=int(col.split()[0][2:])
                pp=getattr(charts,charts.divisional_chart_functions[n])(natal,chart_method=1)
            if col=='D-10 x D-9':
                varna=charts.varnada_lagna_longitudes_mixed_chart(dob,time,place,
                    varga_factor_1=10,chart_method_1=1,varga_factor_2=9,chart_method_2=1,
                    varnada_method=const.VARNADA_METHOD.BV_RAMAN,jhora_compatible=True)
            else:
                varna=charts.varnada_lagna_longitudes(dob,time,place,
                    divisional_chart_factor=int(col.split()[0][2:]),chart_method=1,
                    varnada_method=const.VARNADA_METHOD.BV_RAMAN,jhora_compatible=True)
            positions=dict(pp)
            positions.update({('Varnada Lagna' if k=='V1' else k):p for k,p in varna})
            for p,value in positions.items():
                rows[p][col]=cell(value)
        moon=points['Moon']; sun=points['Sun']
        nak,pada,_=drik.nakshatra_pada(moon)
        # The native previous sunrise establishes the Vedic date, including pre-dawn births.
        rise=drik.sunrise(jd,place)
        rise_date=utils.jd_to_gregorian(rise[2])[:3]
        weekday=(dt.date(*rise_date).weekday()+1)%7
        panchanga={'tithi_index':int((moon-sun)%360//12)+1,'nakshatra_index':nak,
                  'nakshatra':NAKSHATRAS[nak-1],'nakshatra_pada':pada,
                  'vedic_weekday_index':weekday,
                  'vedic_weekday':['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][weekday],
                  'yoga_index':int((moon+sun)%360//(40/3))+1}
        tithi_names=['Pratipada','Dvitiya','Tritiya','Chaturthi','Panchami','Shashthi','Saptami',
                     'Ashtami','Navami','Dashami','Ekadashi','Dvadashi','Trayodashi','Chaturdashi']
        t=panchanga['tithi_index']
        panchanga['tithi']=('Shukla ' if t<=15 else 'Krishna ')+(tithi_names[(t-1)%15]
                             if t not in (15,30) else 'Purnima' if t==15 else 'Amavasya')
        house_chart=utils.get_house_planet_list_from_planet_positions(rasi)
        bav,sav,prastara=ashtakavarga.get_ashtaka_varga(house_chart,
            reverse_ashtakavarga=False,consolidate_houses=False,include_lagna_as_planet=False,
            moon_benefic_9_from_moon=True,moon_malefic_9_from_mars=True,
            moon_benefic_2_from_jupiter=True,moon_malefic_12_from_jupiter=True,
            venus_benefic_4_from_mars=True,venus_malefic_5_from_mars=True)
        result={'birth':{'name':name,'local_datetime':civil.isoformat(),'latitude':latitude,
                        'longitude':longitude,'utc_offset':utc_offset,'place':place_name,'elevation':elevation},
                'positions':points,'divisionals':rows,'columns':COLUMNS,'panchanga':panchanga,
                'sunrise':rise,'sunset':drik.sunset(jd,place),
                'vimshottari':dashas(backend,jd-utc_offset/24,utc_offset,moon,dasha_windows),
                'ashtakavarga':{'bhinna':bav,'sarva':sav},
                'provenance':{'profile':'JHora 8.0 native compatibility','Swiss_Ephemeris':'2.02.01',
                   'ayanamsa':'True Chitra','positions':'true geocentric','nodes':'mean',
                   'rise_set':'solar center, no refraction, native search epochs',
                   'mixed_chart':'D10 traditional then D9 traditional','D0':'native placeholder',
                   'source':'independently calculated from birth input; no reference-position seeds'}}
    return result
