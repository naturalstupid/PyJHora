"""Internal Windows backend for the JHora 8.0 birth-input exporter.

Only export_chart's documented calculations use this profile. It is not a
general replacement for every Swiss/PyJHora API. Birth positions are calculated
through a verified, separately installed Swiss DLL; no reference data is read.
"""
from pathlib import Path
from functools import lru_cache
from contextlib import contextmanager
import atexit
import json
import subprocess
import math
import queue
import sys
import threading
from collections import deque

class LegacySwiss:
    """Bounded JSON transport to the separately installed 32-bit numerical DLL."""

    def __init__(self, swiss_dll=None, ephemeris_path=None, worker_timeout=30.0):
        if sys.platform != 'win32':
            raise RuntimeError('The JHora 8.0 legacy backend requires Windows.')
        if not math.isfinite(worker_timeout) or worker_timeout <= 0:
            raise ValueError('worker_timeout must be a positive finite number')
        self.timeout = worker_timeout
        self.process = None
        self._messages = queue.Queue(maxsize=8)
        self._transport_error = None
        self._errors = deque(maxlen=16)
        self._threads = []
        self.position = lru_cache(maxsize=8192)(self.position)
        self.ascendant = lru_cache(maxsize=2048)(self.ascendant)
        self.rise = lru_cache(maxsize=2048)(self.rise)
        args = [r'C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe',
            '-NoLogo', '-NoProfile', '-NonInteractive', '-File',
            str(Path(__file__).with_name('legacy_swiss_worker.ps1'))]
        if swiss_dll is not None:
            args.extend(['-SwissDll', str(swiss_dll)])
        if ephemeris_path is not None:
            args.extend(['-EphemerisPath', str(ephemeris_path)])
        try:
            self.process = subprocess.Popen(args, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                encoding='utf-8', creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            for reader in (self._read_stdout, self._read_stderr):
                thread = threading.Thread(target=reader, daemon=True)
                self._threads.append(thread)
                thread.start()
            ready = json.loads(self._readline())
            if not isinstance(ready, dict) or ready.get('ready') is not True:
                raise RuntimeError('Invalid worker readiness response')
        except Exception as error:
            self.close(force=True)
            raise RuntimeError('Legacy numerical worker failed to start: ' +
                               str(error) + ' ' + ''.join(self._errors)) from error
        atexit.register(self.close)

    def _read_stdout(self):
        try:
            for line in self.process.stdout:
                self._messages.put_nowait(line)
        except queue.Full:
            self._transport_error = 'Legacy worker exceeded the response queue limit'
        except (OSError, ValueError):
            pass
        finally:
            try:
                self._messages.put_nowait(None)
            except queue.Full:
                pass

    def _read_stderr(self):
        try:
            for line in self.process.stderr:
                self._errors.append(line[-1024:])
        except (OSError, ValueError):
            pass

    def _readline(self):
        if self._transport_error is not None:
            raise RuntimeError(self._transport_error)
        try:
            line = self._messages.get(timeout=self.timeout)
        except queue.Empty as error:
            raise RuntimeError('Legacy numerical worker timed out') from error
        if line is None:
            raise RuntimeError('Legacy worker terminated: ' + ''.join(self._errors))
        return line

    def call(self, op, **values):
        try:
            self.process.stdin.write(json.dumps({'op': op, **values}) + '\n')
            self.process.stdin.flush()
            response = json.loads(self._readline())
            if not isinstance(response, dict):
                raise ValueError('Invalid worker response')
            if 'error' in response:
                raise RuntimeError(response['error'])
            if 'result' not in response:
                raise ValueError('Missing worker result')
        except Exception as error:
            self.close(force=True)
            raise RuntimeError(str(error)) from error
        return response['result']

    def position(self,ut,planet,flags=2+256+16+65536):
        return self.call('position',ut=ut,planet=planet,flags=flags)

    def ascendant(self,ut,lat,lon):
        return self.call('ascendant',ut=ut,latitude=lat,longitude=lon)

    def rise(self,ut,lat,lon,alt,rsmi,flags=2+16):
        return self.call('rise',ut=ut,planet=0,flags=flags,rsmi=rsmi,
                         latitude=lat,longitude=lon,altitude=alt)

    def close(self, force=False):
        process = self.process
        if process is not None:
            if process.stdin is not None and not process.stdin.closed:
                process.stdin.close()
            if process.poll() is None:
                if force:
                    process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    process.wait(timeout=5)
            for thread in self._threads:
                thread.join(timeout=1)
            for stream in (process.stdout, process.stderr):
                if stream is not None and not stream.closed:
                    stream.close()
        atexit.unregister(self.close)
        for cached in (self.position, self.ascendant, self.rise):
            cached.cache_clear()

def _install(drik,swe,swiss_dll=None,ephemeris_path=None):
    from jhora import const,utils
    const.set_node_mode(False)
    backend=LegacySwiss(swiss_dll,ephemeris_path)

    def sidereal_longitude(jd_utc,planet):
        if planet==const._KETU:
            return (backend.position(jd_utc,swe.MEAN_NODE)[0]+180)%360
        return backend.position(jd_utc,planet)[0]

    def ascendant(jd,place,dhasa_progression_correction=0.0):
        value=(backend.ascendant(jd-place.timezone/24,place.latitude,place.longitude)[0]+
               dhasa_progression_correction)%360
        nak,pada,_=drik.nakshatra_pada(value)
        return [int(value//30),value%30,nak,pada]

    @lru_cache(maxsize=1024)
    def native_events(jd,lat,lon,alt,tz):
        # Native event search: next rise from birth, previous rise from that
        # result minus 1.5 days, then sunset from previous rise.
        # Swiss 2.02's root is slightly sensitive to the starting epoch.
        flags=swe.FLG_SWIEPH|swe.FLG_TRUEPOS|swe.FLG_SPEED
        rise_mode=swe.CALC_RISE|swe.BIT_DISC_CENTER|swe.BIT_NO_REFRACTION
        set_mode=swe.CALC_SET|swe.BIT_DISC_CENTER|swe.BIT_NO_REFRACTION
        next_rise=backend.rise(jd-tz/24,lat,lon,alt,rise_mode,flags)
        previous_rise=backend.rise(next_rise-1.5,lat,lon,alt,rise_mode,flags)
        setting=backend.rise(previous_rise,lat,lon,alt,set_mode,flags)
        return previous_rise+tz/24,setting+tz/24,next_rise+tz/24

    def events(jd,place):
        return native_events(jd,place.latitude,place.longitude,place.elevation,place.timezone)

    def rising(jd,place,index):
        # These are internal Vedic-day events, not the public civil-date API.
        y,m,d,_=utils.jd_to_gregorian(jd)
        midnight=swe.julday(y,m,d,0)
        local=events(jd,place)[index]
        hour=(local-midnight)*24
        return [hour,utils.to_dms(hour),local]

    def sunrise(jd,place):
        # The native profile uses 0x300, not BIT_HINDU_RISING (0x380).
        # Keep the Sun's ecliptic latitude when calculating center/no-refraction rise.
        return rising(jd,place,0)
    def sunset(jd,place):
        return rising(jd,place,1)

    def vedic_weekday(jd,place):
        import datetime
        previous_rise=events(jd,place)[0]
        date=utils.jd_to_gregorian(previous_rise)[:3]
        return (datetime.date(*date).weekday()+1)%7

    def upagraha(dob,tob,place,planet_index,upagraha_part='middle',dhasa_progression_correction=0.0):
        jd=utils.julian_day_number(dob,tob)
        rise,setting,next_rise=events(jd,place)
        if jd<rise:
            start=sunset(jd-1,place)[2]
            end=rise
            weekday=drik.vaara(jd-1,place)
            rulers=const.night_rulers[weekday]
        elif jd>=setting:
            start=setting
            end=next_rise
            rulers=const.night_rulers[drik.vaara(jd,place)]
        else:
            start=rise
            end=setting
            rulers=const.day_rulers[drik.vaara(jd,place)]
        offset=.5 if upagraha_part.lower()=='middle' else 0
        time=start+(rulers.index(planet_index)+offset)*(end-start)/8
        value=ascendant(time,place)[0:2]
        return (value[0]*30+value[1]+dhasa_progression_correction)%360

    def special(jd,place,lagna_rate_factor=1.0,dhasa_progression_correction=0.0,special_lagna_continuity=None):
        rise=sunrise(jd,place)[2]
        if jd<rise:
            rise=sunrise(jd-1,place)[2]
        if special_lagna_continuity is None:
            special_lagna_continuity = const.special_lagna_continuity
        anchor = jd if special_lagna_continuity else rise
        sun=sidereal_longitude(anchor-place.timezone/24,swe.SUN)
        value=(sun+(jd-rise)*1440*lagna_rate_factor+dhasa_progression_correction)%360
        return int(value//30),value%30

    def pranapada(jd,place,dhasa_progression_correction=0.0,special_lagna_continuity=None):
        rise=sunrise(jd,place)[2]
        if jd<rise:
            rise=sunrise(jd-1,place)[2]
        sun=sidereal_longitude(jd-place.timezone/24,swe.SUN)
        sign=int(sun//30)
        offset=240 if sign in const.fixed_signs else 120 if sign in const.dual_signs else 0
        value=(sun+(jd-rise)*1440*5+offset+dhasa_progression_correction)%360
        return int(value//30),value%30

    drik.sidereal_longitude=sidereal_longitude
    drik.ascendant=ascendant
    drik.sunrise=sunrise
    drik.sunset=sunset
    drik.vedic_weekday=vedic_weekday
    drik._upagraha_longitude_full=upagraha
    drik.special_ascendant=special
    drik.pranapada_lagna=pranapada
    drik._jhora_backend=backend
    return backend

@contextmanager
def _export_profile(*,swiss_dll=None,ephemeris_path=None):
    """Private calculation scope for export_chart only.

    Use in a dedicated calculation process: Swiss/PyJHora settings are global
    and this context is not designed for concurrent calculation threads.
    No JHora preferences, chart files, or GUI state are read or modified.
    """
    from jhora import const
    from jhora.panchanga import drik
    import swisseph as swe
    if const._DEFAULT_AYANAMSA_MODE.upper() in {'SIDM_USER', 'SENTHIL', 'SUNDAR_SS'}:
        raise ValueError('The legacy exporter cannot restore a custom ayanamsa; '
                         'use a dedicated process with a standard named mode.')
    names=['_RAHU','_KETU','_DEFAULT_AYANAMSA_MODE','_TROPICAL_MODE',
           'special_lagna_continuity','exclude_non_planets_in_varga_chart_calculations',
           '_INCLUDE_URANUS_TO_PLUTO','_use_true_nodes_for_rahu_ketu']
    saved_const={name:getattr(const,name) for name in names}
    names=['sidereal_longitude','ascendant','sunrise','sunset','vedic_weekday','_upagraha_longitude_full',
           'special_ascendant','pranapada_lagna','planet_list','PLANET_FLAGS','RISE_FLAGS','SET_FLAGS']
    saved_drik={name:getattr(drik,name) for name in names}
    saved_backend=getattr(drik,'_jhora_backend',None)
    backend=None
    try:
        drik.set_ayanamsa_mode('TRUE_CITRA')
        const._TROPICAL_MODE=False
        const.special_lagna_continuity=False
        const.exclude_non_planets_in_varga_chart_calculations=True
        drik.set_planet_list(set_rahu_ketu_as_true_nodes=False,include_western_planets=False)
        drik.PLANET_FLAGS=swe.FLG_SWIEPH|swe.FLG_SIDEREAL|swe.FLG_TRUEPOS|swe.FLG_SPEED
        backend=_install(drik,swe,swiss_dll,ephemeris_path)
        yield backend
    finally:
        try:
            if backend is not None:
                backend.close()
        finally:
            for name,value in saved_drik.items():
                setattr(drik,name,value)
            for name,value in saved_const.items():
                setattr(const,name,value)
            if saved_backend is None:
                if hasattr(drik,'_jhora_backend'):
                    delattr(drik,'_jhora_backend')
            else:
                drik._jhora_backend=saved_backend
            drik.set_ayanamsa_mode(saved_const['_DEFAULT_AYANAMSA_MODE'])
