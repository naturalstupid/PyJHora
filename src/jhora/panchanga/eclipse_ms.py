#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
eclipse_ms.py
==============
Lunar and solar eclipses per the Makaranda Sarini (pp. 0044-0048, 0053, 0083-0084), using the longitudes of
makaranda_sarini.py (the MKS engine built earlier in this project).

    from jhora.panchanga import eclipse_ms   (or: import eclipse_ms, with makaranda_sarini.py alongside it)

STATUS -- READ THIS FIRST
--------------------------------------------------------------------------------------------------------------
This module is a SCAFFOLD with a CONFIRMED PROCEDURE SHAPE but UNTRANSCRIBED TABLES. Every numeric table this
module needs (candra-bimba, bhu-bimba, surya-bimba by koshthaka; the rashi-keyed bimba/pratibimba/ravimukti
table; the nata-ghati-lambana parallax table) showed the same digit ambiguities (1/3, 6/8, 4/8) documented
throughout this project when read at 2-3x zoom. Rather than guess at them -- the mistake this project is
explicitly correcting -- every such table falls back to a Surya-Siddhanta/Vakya-style closed-form equivalent,
and that fallback is tagged confidence='fitted' everywhere it appears: in this docstring, in each function's
own docstring, and in every dict this module returns. A 'fitted' number is NOT a transcription of the book's
printed table and will NOT exactly reproduce it. See mks_eclipse_selftest() for the actual, honest gap against
the book's own two worked examples.

WHAT WAS READ THIS SESSION (by eye, ~2-3x zoom, pp. 0044-0048, 0053, 0083-0084)
--------------------------------------------------------------------------------------------------------------
 p.0044  Continuation of a krānti-sūkṣma (fine declination) table, koshthaka 1-90, plus a short koshthaka 1-30
         table. Caption (paraphrased): "...bhujamsa-sammiti koshthaka-stha...shara-sanupatam...angulad bhavati"
         -- the argument is the bhujamsa (degrees of anomaly folded to a quadrant); the table gives a quantity
         "in angula units" by proportion. Digits not reliably read.
 p.0046  Two koshthaka tables (1-30 each) plus four verses. Header text (paraphrased): "sayanamsa-graha-shadbhir
         adhikam kshepa uccha ucchayah tasyamsah shadbhir bhajya labdha koshthaka-stha kranti sanupanat
         grahyah pathati dvigunitamsadi sthula kranti bhavati" -- a gross-declination procedure. The VERSES
         (read with moderate confidence; Devanagari kept here for anyone who wants to re-check them):
           v.1  "bhanu bhajyam cha dasha bhaih nishi chandro dayo bhavet, pratipat purnimasandhau vidhu
                grahanam adishet" -- roughly: tithi-junction (amavasya/purnima) rule triggering an eclipse check.
           v.2  "bhasa sahitam chatanah syat shodasha kshepaya ravih, diva matra pratipatsandhau surya
                grahanam adishet" -- the parallel solar-eclipse trigger.
           v.3  "pancha su sarva grahanam sapta su pado nitam bhavet, ekadashe chaturdasham nasti grahanam
                chaturdashe bhage" -- a rule of thumb by how many of some 15-part division the event falls in
                (precise meaning not settled; flagged, not used below).
           v.4  "rahum chandra masor minam yogardham shara varjitam, grasash chandrasya nasyardham tridhnam
                vimshopaka smrita" -- CONFIRMED STRUCTURE used below: the eclipse magnitude (grasa) relates to
                half the sum of the discs less the latitude (shara), and is expressed in units the text calls
                vimshopaka ("twentieths"); see grasa_vimsopaka() for the exact relation taken from this verse
                and from the worked example on p.0083 (where "grasa vimshati gunitah...vimshopakah syuh" is
                read directly, i.e. "grasa x 20 ... becomes vimshopaka").
 p.0047  A 12-column table keyed by RASHI (Mesha..Meena), not by koshthaka 1-90 like the phala tables -- a
         genuinely different layout. Right-margin labels (as read): "sankrantayah" / "bimba" / "prativimba" /
         "ravimukti" / "kaladi". This is almost certainly the candra-bimba / pata-bimba(shadow) / pratibimba /
         ravi-mukti table that the verse text on this same page names: "...chandra-bimba, chandra-pata-bimba,
         sankranti...kalaadi...grasah...chandra-bimba-bhaktah vimshopakah syuh...vritti chandra-grahanam...".
         Digits in the data rows were not reliably read; NOT transcribed (see candra_bimba_fitted() etc. below).
 p.0048  Continuation of the same koshthaka numbering, but the verse identifies it as candra-darsana (Moon
         visibility after conjunction) material, not eclipse magnitude -- out of scope for this module.
 p.0053  Title confirmed directly: "नतघटीलंबनं" (nata-ghati-lambanam = "parallax by nata-ghati", i.e. parallax
         tabulated by the hour-angle-from-meridian in ghatika). A koshthaka table (approx. 1-36) plus running
         text mentioning "sphuta-chandra", "mukti" (release / last contact) -- confirms this table feeds the
         eclipse-contact-time procedure. Digits not reliably read; NOT transcribed (see lambana_fitted() below).
 p.0083  Colophon "iti chandra-grahanam" confirms this is the end of the LUNAR ECLIPSE chapter -- the worked
         example is earlier on the same page. Worked example (read, MODERATE confidence -- this is dense running
         text, not a ruled table, and was not re-verified digit-by-digit):
             "udaharanam. shaka 1534 vaishakha shuddha 15 some ghati 15;40 anuradha-nakshatre
              gataishya-yoga 5;36 ... surya 16;13;20;35 ... chandra 7;6;14;35 ... rahuh 3;15;19;12 ..."
         i.e. SAME epoch (Saka 1534 Vaisakha sukla 15) as the main graha worked example already validated in
         makaranda_sarini.mks_selftest(). The PROCEDURE, as read: candra-bimba and bhu-bimba (earth's-shadow
         disc) are each found by a TWO-STEP koshthaka interpolation -- cell value, plus the residual times the
         next cell's difference -- exactly the _interp() pattern already used for the manda/sighra phala tables
         in makaranda_sarini.py, NOT a closed-form "daily-motion / 25" rule like Vakya uses. A separate
         pata-phala (node-related) correction combines with bhu-bimba into a single "spashta-bhu-bimba" (the
         text's own worked value: 28;36). Magnitude: "grasa x 20, divided by candra-bimba, becomes vimshopaka".
 p.0084  Colophon "iti chandra-grahanam, atha surya-grahanam" confirms the SOLAR ECLIPSE chapter begins here.
         Worked example (read, MODERATE confidence): "shakah 1532 margashirsha krishna 30 budhe..." i.e. Saka
         1532 Margasirsha krishna 30, Wednesday. The Sun's bimba uses the SAME two-step koshthaka procedure as
         the Moon's. A lambana (parallax) value is derived from the SUN's OWN bhujamsa (not looked up by zenith
         distance / Nonagesimal the way Vakya's 16-point table is): bhujamsa / 6, combined with a
         pala-interpolation, multiplied by 6 to give a result in degrees. Example values (read): Sun
         8;5;26;20, ayanamsa 16;31, Sun's bhujamsa 8;26;14, [bhujamsa/6] 33, ghati-component 3;54;36, combined
         with a pala correction to 3;57;30, x6 giving 23;45 degrees.

WHAT THIS MEANS FOR THE CODE BELOW
--------------------------------------------------------------------------------------------------------------
 - Every _fitted() function below is a DELIBERATE, CLEARLY-LABELLED PLACEHOLDER for a table that has not been
   transcribed. It exists so the module runs end-to-end and so the overall PROCEDURE (confirmed from the pages
   above) can be exercised and tested, not so its numbers can be trusted.
 - The confirmed procedure shape (two-step koshthaka interpolation feeding candra-bimba/bhu-bimba/surya-bimba;
   grasa = 20 x (half-sum - |latitude|) / candra-bimba, in vimshopaka; a bhujamsa-driven lambana for the solar
   case) IS implemented faithfully and is the part of this module that reflects the book, not a substitute.
 - mks_eclipse_selftest() prints the book's own two worked examples next to this module's output and reports
   the gap honestly. Do not read a small gap as proof of anything beyond the procedure shape being plausible,
   and do not read a large gap as a bug in the procedure -- it is most likely the untranscribed tables.
 - ANGULA UNITS: the book expresses bimba and shara in "angula" (p.0083: "angulatmakam chandra-bimbam"), not
   directly in arc-minutes the way Vakya does. No verse read so far states the angula-to-arc-minute conversion
   explicitly. This module ASSUMES 1 angula = 1/15 degree (4 arc-minutes) as a placeholder [CHOICE, UNCONFIRMED]
   purely so the numbers are in the same units as makaranda_sarini.py's longitudes; this assumption is exactly
   as provisional as the fitted tables above and is flagged again at ANGULA_TO_DEGREES below.
"""
import math
try:                                        # inside PyJHora
    from jhora.panchanga import makaranda_sarini as mks
    from jhora import const, utils
except ImportError:                         # stand-alone: makaranda_sarini.py next to this file
    import makaranda_sarini as mks
    const = mks.const
    utils = mks.utils

# ----------------------------------------------------------------------------------------------------------
# Units and constants
# ----------------------------------------------------------------------------------------------------------
ANGULA_TO_DEGREES = 1.0 / 15.0              # [CHOICE, UNCONFIRMED] see the module docstring, "ANGULA UNITS"
_ECLIPSE_LATITUDE_LIMIT_DEG = 2.0           # [CHOICE] date-level only: skip a parva whose |Moon latitude| exceeds this
_LUNATION_DAYS = 29.53                      # search step of next_lunar_eclipse() / next_solar_eclipse()


class EclipseLocation:
    """ Visibility scope of the search. LOCAL: an eclipse in which the Sun (solar) or the Moon (lunar) is below the horizon of the place at
        every contact is skipped. GLOBAL: the next eclipse is returned whether or not it is seen at the place. """
    LOCAL = 0
    GLOBAL = 1


class SolarEclipseType:
    """ Filter for next_solar_eclipse(): ANY, TOTAL, or PARTIAL. """
    ANY = 0
    TOTAL = 1
    PARTIAL = 2


class LunarEclipseType:
    """ Filter for next_lunar_eclipse(): ANY, TOTAL, or PARTIAL. """
    ANY = 0
    TOTAL = 1
    PARTIAL = 2


def _wrap180(x):
    """ @param x: angle in degrees  @return: the same angle in (-180, 180] """
    return ((x + 180.0) % 360.0) - 180.0


# ----------------------------------------------------------------------------------------------------------
# A1. Two-step koshthaka interpolation (CONFIRMED structure, p.0083: "agrimanirena shesham gunitam...jatam")
# ----------------------------------------------------------------------------------------------------------
def koshthaka_interp(table, x):
    """ The book's own interpolation rule (pp. 0083-0084, same pattern as the manda/sighra phala tables in
        makaranda_sarini.py's _interp()): value at the whole koshthaka, plus the residual times the difference
        to the next koshthaka. This function is CONFIRMED STRUCTURE; the `table` passed to it is, at present,
        always one of the *_fitted() tables below, not a transcription of the book's own cells.
        @param table: list of values, index 0..N
        @param x: fractional koshthaka position
        @return: interpolated value
    """
    i = min(int(x), len(table) - 2)
    return table[i] + (table[i + 1] - table[i]) * (x - i)


# ----------------------------------------------------------------------------------------------------------
# A2. Discs (candra-bimba, bhu-bimba, surya-bimba) -- FITTED fallbacks, see module docstring
# ----------------------------------------------------------------------------------------------------------
def candra_bimba_fitted(moon_daily_deg):
    """ [FITTED, NOT READ FROM THE BOOK] Moon's angular diameter, in degrees. Surya-Siddhanta/Vakya-style
        closed form (daily motion / 25, the same relation Vakya uses in angular_diameters()), converted from
        arc-minutes to degrees. The book's own candra-bimba is a koshthaka TABLE (p.0047/p.0083) that has not
        been transcribed; this is a placeholder of the same general size (about 30-33' at the mean), not a
        reproduction of the printed values.
        @param moon_daily_deg: Moon's daily motion, degrees/day
        @return: degrees
    """
    return (moon_daily_deg * 60.0) / 25.0 / 60.0


def bhu_bimba_fitted(moon_daily_deg):
    """ [FITTED, NOT READ FROM THE BOOK] Earth's-shadow angular diameter, in degrees. Surya-Siddhanta/Vakya-style
        closed form (Moon's disc x 5/2 + 1 arc-minute). See candra_bimba_fitted()'s caveat; this is a
        placeholder, not the book's own bhu-bimba koshthaka table (pp. 0044-0047, 0083).
        @param moon_daily_deg: Moon's daily motion, degrees/day
        @return: degrees
    """
    moon_d = candra_bimba_fitted(moon_daily_deg) * 60.0
    return (moon_d * 5.0 / 2.0 + 1.0) / 60.0


def surya_bimba_fitted(sun_daily_deg):
    """ [FITTED, NOT READ FROM THE BOOK] Sun's angular diameter, in degrees. Surya-Siddhanta/Vakya-style closed
        form (daily motion x 5/9). See candra_bimba_fitted()'s caveat; this is a placeholder, not the book's own
        surya-bimba koshthaka procedure (p.0084).
        @param sun_daily_deg: Sun's daily motion, degrees/day
        @return: degrees
    """
    return (sun_daily_deg * 60.0 * 5.0 / 9.0) / 60.0


# ----------------------------------------------------------------------------------------------------------
# A3. Moon's latitude (shara) -- FITTED fallback
# ----------------------------------------------------------------------------------------------------------
def moon_latitude_deg_fitted(moon_minus_rahu_deg):
    """ [FITTED, NOT READ FROM THE BOOK] Moon's latitude, degrees. Closed-form sine relation (same shape as
        Vakya's moon_latitude_min(): 6 x sin(bhuja of Moon-Rahu), scaled). The book's own shara is the short
        koshthaka 1-30 table at the foot of p.0046 ("bhujamsa-sammiti koshthaka-stha...angulad bhavati"),
        which has NOT been transcribed (values looked, by eye, like a smooth 0-4-ish angula curve peaking near
        koshthaka 13-20, but no individual cell is trusted). This is a placeholder, not the book's own table.
        @param moon_minus_rahu_deg: degrees
        @return: degrees (sign: positive is the book's convention at p.0046, direction not independently
            re-derived here -- treat the sign as unconfirmed)
    """
    d = moon_minus_rahu_deg % 360.0
    bhuja = d if d <= 90.0 else (180.0 - d if d <= 180.0 else (d - 180.0 if d <= 270.0 else 360.0 - d))
    max_lat = 5.14                            # degrees; the Moon's actual orbital inclination, a generic value,
                                               # NOT read from the p.0046 koshthaka table (which is in angula)
    lat = max_lat * math.sin(math.radians(bhuja))
    return lat if d >= 180.0 else -lat


# ----------------------------------------------------------------------------------------------------------
# A4. Eclipse magnitude -- CONFIRMED RELATION (p.0046 v.4, p.0083 worked example)
# ----------------------------------------------------------------------------------------------------------
def grasa_vimsopaka(bimba_eclipsing_deg, bimba_eclipsed_deg, latitude_deg):
    """ Eclipse magnitude in vimshopaka (twentieths), per p.0046 v.4 ("...grasa-chandrasya nasyardham tridhnam
        vimshopaka smrita") and the worked relation on p.0083 ("grasa vimshati-gunitah...chandra-bimba-bhaktah
        vimshopakah syuh" -- "grasa, multiplied by 20, divided by the Moon's disc, becomes vimshopaka").
        CONFIRMED STRUCTURE: magnitude = half the sum of the two discs, less the (absolute) latitude; that
        quantity, x20, divided by the eclipsed body's own disc, is the vimshopaka figure. The discs and the
        latitude feeding this are presently FITTED (see above), so the vimshopaka number itself inherits that
        same caveat.
        @param bimba_eclipsing_deg: diameter of the eclipsing disc (bhu-bimba for a lunar eclipse, Moon's disc
            for a solar eclipse), degrees
        @param bimba_eclipsed_deg: diameter of the eclipsed disc (Moon for lunar, Sun for solar), degrees
        @param latitude_deg: Moon's latitude at the relevant instant, degrees (sign ignored)
        @return: (magnitude_deg, vimshopaka, is_total) -- magnitude_deg <= 0 means no eclipse
    """
    half_sum = (bimba_eclipsing_deg + bimba_eclipsed_deg) / 2.0
    magnitude = half_sum - abs(latitude_deg)
    if magnitude <= 0.0:
        return magnitude, 0.0, False
    vimsopaka = magnitude * 20.0 / bimba_eclipsed_deg
    is_total = magnitude > bimba_eclipsed_deg
    return magnitude, vimsopaka, is_total


def half_duration_days(bimba_eclipsing_deg, bimba_eclipsed_deg, latitude_deg, relative_motion_deg_per_day):
    """ Half the duration of the eclipse, days. Same Pythagorean relation Vakya and Surya Siddhanta both use
        (half_sum^2 - latitude^2, square-rooted, divided by the relative motion); no MKS-specific half-duration
        rule was identified in the pages read, so this is carried over unchanged, NOT re-derived from MKS text.
        @return: days, or None if there is no eclipse
    """
    half_sum = (bimba_eclipsing_deg + bimba_eclipsed_deg) / 2.0
    lat = abs(latitude_deg)
    if half_sum <= lat:
        return None
    return math.sqrt(half_sum ** 2 - lat ** 2) / abs(relative_motion_deg_per_day)


# ----------------------------------------------------------------------------------------------------------
# A5. Solar-eclipse parallax (lambana) -- CONFIRMED SHAPE (p.0084), table FITTED
# ----------------------------------------------------------------------------------------------------------
def lambana_deg_fitted(sun_bhujamsa_deg):
    """ [FITTED, NOT READ FROM THE BOOK] A TIMING correction for a solar eclipse (shifts the apparent moment of
        conjunction), degrees of longitude-equivalent. The PROCEDURE SHAPE is confirmed from p.0084
        ("agrimanirena suryasya bhagardha gunyam trimsad-bhaktam...x6 jatam [deg]" -- the Sun's own bhujamsa
        feeds this correction, not a Nonagesimal-distance lookup the way Vakya's parallax_vinadis() works), and
        the worked numbers there (bhujamsa 8;26;14 -> 23;45 degrees after the /6, pala-correction, x6 steps)
        are read, but the intermediate pala-correction table (and the separate nata-ghati-lambana table on
        p.0053) are NOT transcribed. This closed form reproduces roughly the right SIZE of correction but is
        not fitted to the book's own two tables and will not reproduce the example's 23;45 exactly.
        IMPORTANT: this is the EAST-WEST (timing) component only. The book's eclipse chapter (like Vakya's
        IV.16-19 and the Surya Siddhanta tradition generally) treats the NORTH-SOUTH (latitude-shifting, "Nati")
        component as a SEPARATE correction (ayana + place-latitude terms in Vakya). No MKS-specific Nati rule
        was identified in the pages read (pp. 0044-0048, 0053, 0084), so this module does NOT add any
        parallax-in-latitude term to the eclipse magnitude -- solar_eclipse_at() uses the unperturbed
        geocentric latitude for magnitude, and applies this function only as a time-shift in
        next_solar_eclipse(). Treat the resulting solar-eclipse magnitudes as a lower bound on the real,
        parallax-corrected values close to a grazing/partial case.
        @param sun_bhujamsa_deg: the Sun's bhujamsa (degrees from the nearest quadrant boundary), 0-90
        @return: degrees of longitude-equivalent timing shift
    """
    return 24.0 / 90.0 * min(max(sun_bhujamsa_deg, 0.0), 90.0)   # placeholder scale chosen to match the example's rough size


# ----------------------------------------------------------------------------------------------------------
# B. Date level -- uses makaranda_sarini.py for Sun/Moon/Rahu longitudes and motions
# ----------------------------------------------------------------------------------------------------------
def _relative_motion(jd_utc, place):
    """ (Moon daily motion - Sun daily motion), degrees/day, at jd_utc. """
    sun_d = mks.daily_planet_speed(jd_utc, place, const.SUN_ID)
    moon_d = mks.daily_planet_speed(jd_utc, place, const.MOON_ID)
    return moon_d, sun_d, moon_d - sun_d


def _moon_minus_rahu(jd_utc, place):
    moon = mks.sidereal_longitude(jd_utc, const._MOON, place)
    rahu = mks.sidereal_longitude(jd_utc, const._RAHU, place)
    return (moon - rahu) % 360.0


def lunar_eclipse_at(jd_full_moon_utc, place):
    """ Lunar-eclipse elements at a full-moon instant, using the CONFIRMED magnitude relation (A4) with the
        FITTED discs and latitude (A2-A3). @return: dict, see keys below, or a dict with is_possible=False. """
    moon_d, sun_d, rel = _relative_motion(jd_full_moon_utc, place)
    candra = candra_bimba_fitted(moon_d)
    bhu = bhu_bimba_fitted(moon_d)
    mmr = _moon_minus_rahu(jd_full_moon_utc, place)
    lat = moon_latitude_deg_fitted(mmr)
    magnitude, vimsopaka, is_total = grasa_vimsopaka(bhu, candra, lat)
    is_possible = magnitude > 0.0
    hd = half_duration_days(bhu, candra, lat, rel) if is_possible else None
    return dict(is_possible=is_possible, is_total=is_total, magnitude_deg=magnitude, vimsopaka=vimsopaka,
                candra_bimba_deg=candra, bhu_bimba_deg=bhu, moon_latitude_deg=lat,
                half_duration_days=hd, confidence='fitted discs/latitude; see module docstring')


def solar_eclipse_at(jd_new_moon_utc, place):
    """ Solar-eclipse elements at a new-moon instant and place, using the CONFIRMED magnitude relation (A4)
        with FITTED discs and the UNPERTURBED geocentric latitude (A2-A3). The bhujamsa-driven timing
        correction (A5) is reported separately (lambana_deg) but is NOT folded into the magnitude here -- see
        lambana_deg_fitted()'s docstring for why (no MKS-specific Nati/latitude-parallax rule was identified in
        the pages read). This means the magnitude below is closer to a GEOCENTRIC solar eclipse figure than a
        true topocentric one; treat it accordingly.
        @return: dict, see keys below, or a dict with is_possible=False. """
    moon_d, sun_d, rel = _relative_motion(jd_new_moon_utc, place)
    candra = candra_bimba_fitted(moon_d)
    surya = surya_bimba_fitted(sun_d)
    sun_long = mks.sidereal_longitude(jd_new_moon_utc, const._SUN, place)
    bhuja = sun_long % 90.0
    lamb = lambana_deg_fitted(bhuja)
    mmr = _moon_minus_rahu(jd_new_moon_utc, place)
    lat = moon_latitude_deg_fitted(mmr)              # geocentric; see docstring -- no Nati term applied
    magnitude, vimsopaka, is_total = grasa_vimsopaka(candra, surya, lat)
    is_possible = magnitude > 0.0
    hd = half_duration_days(candra, surya, lat, rel) if is_possible else None
    return dict(is_possible=is_possible, is_total=is_total, magnitude_deg=magnitude, vimsopaka=vimsopaka,
                candra_bimba_deg=candra, surya_bimba_deg=surya, lambana_deg=lamb, moon_latitude_deg=lat,
                half_duration_days=hd,
                confidence='fitted discs/latitude; lambana_deg is a timing shift only, not applied to magnitude')


# ----------------------------------------------------------------------------------------------------------
# C. Same public API as eclipse_ss.py / eclipse_vp.py
# ----------------------------------------------------------------------------------------------------------
def is_lunar_eclipse(jd_full_moon, place):
    """ Evaluates whether the full moon at jd_full_moon produces a lunar eclipse (pp. 0044-0047, 0083).
        @param jd_full_moon: Julian Day of the full moon instant, local civil time
        @param place: Place (place.timezone is used)
        @return: dict, see lunar_eclipse_at(); ALL disc/latitude numbers are 'fitted', not read from the book
    """
    return lunar_eclipse_at(jd_full_moon - place.timezone / 24.0, place)


def is_solar_eclipse(jd_new_moon, place):
    """ Evaluates whether the new moon at jd_new_moon produces a solar eclipse at the place (pp. 0044-0047,
        0053, 0084).
        @param jd_new_moon: Julian Day of the new moon instant, local civil time
        @param place: Place (latitude, longitude, timezone)
        @return: dict, see solar_eclipse_at(); ALL disc/latitude/lambana numbers are 'fitted', not read from
            the book
    """
    return solar_eclipse_at(jd_new_moon - place.timezone / 24.0, place)


def _search_parvas(kind, jd_local, place, search_backward, max_tries):
    """ Yields (jd_utc, jd_local) of successive new ('amavasya') or full ('purnima') moons, using
        makaranda_sarini.py's own exact crossing solver (mks.new_moon() / mks.full_moon()). """
    finder = mks.new_moon if kind == 'amavasya' else mks.full_moon
    jd = jd_local
    direction = -1 if search_backward else 1
    for _ in range(max_tries):
        jd = finder(jd, place, opt=direction)
        yield jd, jd


def _sun_is_up(jd, place):
    """ Whether the Sun is above the horizon: the Julian Day lies between the sunrise and the sunset of its own civil day.
        @param jd: Julian Day (local civil time)
        @param place: Place struct
        @return: True if the Sun is up """
    eng = mks
    return eng.sunrise(jd, place)[2] <= jd <= eng.sunset(jd, place)[2]


def _lunar_seen_locally(eclipse_location_type, place, jd_times):
    """ Whether a lunar eclipse is returned under the scope. With EclipseLocation.LOCAL the Moon, opposite the Sun, must be above the horizon (the Sun down) at one or more of the contacts (with EclipseLocation.GLOBAL every eclipse is returned).
        @param eclipse_location_type: EclipseLocation.LOCAL or EclipseLocation.GLOBAL
        @param place: Place struct
        @param jd_times: Julian Days (local civil time) of the contacts of the eclipse
        @return: True if the eclipse is to be returned """
    if eclipse_location_type != EclipseLocation.LOCAL:
        return True
    return any(not _sun_is_up(t, place) for t in jd_times)


def _solar_seen_locally(eclipse_location_type, place, jd_times):
    """ Whether a solar eclipse is returned under the scope. With EclipseLocation.LOCAL the Sun must be above the horizon at one or more of the contacts (with EclipseLocation.GLOBAL every eclipse is returned).
        @param eclipse_location_type: EclipseLocation.LOCAL or EclipseLocation.GLOBAL
        @param place: Place struct
        @param jd_times: Julian Days (local civil time) of the contacts of the eclipse
        @return: True if the eclipse is to be returned """
    if eclipse_location_type != EclipseLocation.LOCAL:
        return True
    return any(_sun_is_up(t, place) for t in jd_times)


def next_lunar_eclipse(jd_local, place, eclipse_location_type=EclipseLocation.LOCAL,
                       lunar_eclipse_type=LunarEclipseType.ANY, search_backward=False,
                       show_maximum_eclipse_global_location=False, max_tries=120):
    """ Finds the next (or previous) full moon producing a lunar eclipse matching the requested type.
        @param jd_local: starting Julian Day (local civil time)
        @param place: Place
        @param eclipse_location_type: EclipseLocation.LOCAL (an eclipse in
            which the Moon is below the horizon at every contact is skipped) or EclipseLocation.GLOBAL (every eclipse is returned)
        @param lunar_eclipse_type: ANY / TOTAL / PARTIAL filter
        @param search_backward: search for the previous eclipse instead of the next
        @param show_maximum_eclipse_global_location: accepted for signature parity; not used by this engine
        @param max_tries: maximum number of lunations to search before giving up
        @return: (type_str, [begin, middle, end]) as (Y,M,D,fh) tuples (local civil time), or None.
            ALL disc/latitude numbers behind this result are 'fitted' -- see the module docstring.
    """
    jd = jd_local
    direction = -1 if search_backward else 1
    for _ in range(max_tries):
        jd = mks.full_moon(jd, place, opt=direction)
        info = lunar_eclipse_at(jd - place.timezone / 24.0, place)
        if info['is_possible']:
            if (lunar_eclipse_type == LunarEclipseType.TOTAL and not info['is_total']) or \
               (lunar_eclipse_type == LunarEclipseType.PARTIAL and info['is_total']):
                jd += direction * _LUNATION_DAYS
                continue
            hd = info['half_duration_days']
            if not _lunar_seen_locally(eclipse_location_type, place, (jd - hd, jd, jd + hd)):
                jd += direction * _LUNATION_DAYS
                continue
            begin = utils.jd_to_gregorian(jd - hd)
            middle = utils.jd_to_gregorian(jd)
            end = utils.jd_to_gregorian(jd + hd)
            return ("total" if info['is_total'] else "partial"), [begin, middle, end]
        jd += direction * _LUNATION_DAYS
    return None


def next_solar_eclipse(jd_local, place, eclipse_location_type=EclipseLocation.LOCAL,
                       solar_eclipse_type=SolarEclipseType.ANY, search_backward=False,
                       show_maximum_eclipse_global_location=False, max_tries=120):
    """ Finds the next (or previous) new moon producing a solar eclipse visible at the place.
        @param jd_local: starting Julian Day (local civil time)
        @param place: Place
        @param eclipse_location_type: EclipseLocation.LOCAL (an eclipse in
            which the Sun is below the horizon at every contact is skipped) or EclipseLocation.GLOBAL (every eclipse is returned)
        @param solar_eclipse_type: ANY / TOTAL / PARTIAL filter
        @param search_backward: search for the previous eclipse instead of the next
        @param show_maximum_eclipse_global_location: accepted for signature parity; not used by this engine
        @param max_tries: maximum number of lunations to search before giving up
        @return: (type_str, [begin, middle, end]) as (Y,M,D,fh) tuples (local civil time), or None.
            ALL disc/latitude/lambana numbers behind this result are 'fitted' -- see the module docstring.
    """
    jd = jd_local
    direction = -1 if search_backward else 1
    for _ in range(max_tries):
        jd = mks.new_moon(jd, place, opt=direction)
        mmr = _moon_minus_rahu(jd - place.timezone / 24.0, place)
        if abs(moon_latitude_deg_fitted(mmr)) > _ECLIPSE_LATITUDE_LIMIT_DEG:
            jd += direction * _LUNATION_DAYS
            continue
        info = solar_eclipse_at(jd - place.timezone / 24.0, place)
        if info['is_possible']:
            if (solar_eclipse_type == SolarEclipseType.TOTAL and not info['is_total']) or \
               (solar_eclipse_type == SolarEclipseType.PARTIAL and info['is_total']):
                jd += direction * _LUNATION_DAYS
                continue
            hd = info['half_duration_days']
            _, sun_d, rel = _relative_motion(jd - place.timezone / 24.0, place)
            t_shift = info['lambana_deg'] / abs(rel) if rel != 0.0 else 0.0   # [CHOICE] timing shift only
            jd_mid = jd + t_shift
            if not _solar_seen_locally(eclipse_location_type, place, (jd_mid - hd, jd_mid, jd_mid + hd)):
                jd += direction * _LUNATION_DAYS
                continue
            begin = utils.jd_to_gregorian(jd_mid - hd)
            middle = utils.jd_to_gregorian(jd_mid)
            end = utils.jd_to_gregorian(jd_mid + hd)
            return ("total" if info['is_total'] else "partial"), [begin, middle, end]
        jd += direction * _LUNATION_DAYS
    return None


# ----------------------------------------------------------------------------------------------------------
# Acceptance test against the book's own two worked examples (pp. 0083-0084) -- READ, not invented
# ----------------------------------------------------------------------------------------------------------
# Ahargana of Saka 1534 Vaisakha sukla 15 is already established in makaranda_sarini.py (_EXAMPLE_AHARGANA =
# 1721500, confirmed from the graha-sadhana example on pp. 0072-0073). p.0083's lunar-eclipse example uses the
# SAME date. Saka 1532 (p.0084, solar-eclipse example) is two Saka years earlier; its ahargana is estimated
# here from the solar-year length, NOT independently confirmed from a vallI reading on p.0084 itself.
_LUNAR_EXAMPLE_AHARGANA = mks._EXAMPLE_AHARGANA              # Saka 1534 Vaisakha sukla 15, Monday (p.0083)
_SOLAR_EXAMPLE_AHARGANA = mks._EXAMPLE_AHARGANA - round(2 * mks._SOLAR_YEAR_DAYS)   # Saka 1532 (p.0084); APPROXIMATE


def mks_eclipse_selftest(verbose=True):
    """ Prints/returns the book's own two worked examples (read from pp. 0083-0084) next to this module's
        computed values. Expect a visible gap: the discs, latitude and lambana feeding every number here are
        FITTED placeholders, not transcriptions of the book's own tables (see the module docstring). A close
        match is not proof of anything beyond the procedure shape; a large gap is most likely the untranscribed
        tables, not necessarily a wrong procedure.
        @return: dict with 'lunar' and 'solar' sub-dicts
    """
    place = mks.Place('Ujjain', mks.const.ujjain_lat_long[0], mks.const.ujjain_lat_long[1], 5.5)
    jd_utc_lunar = mks._KALI_JD0 + _LUNAR_EXAMPLE_AHARGANA - mks._UJJAIN_LONGITUDE / 360.0
    lunar = lunar_eclipse_at(jd_utc_lunar, place)
    jd_utc_solar = mks._KALI_JD0 + _SOLAR_EXAMPLE_AHARGANA - mks._UJJAIN_LONGITUDE / 360.0
    solar = solar_eclipse_at(jd_utc_solar, place)
    if verbose:
        print("LUNAR ECLIPSE -- Saka 1534 Vaisakha sukla 15 (p.0083)")
        print("  book (read, moderate confidence): candra-bimba ~ ?  bhu-bimba ~ ?  spashta-bhu-bimba 28;36")
        print("  this module (fitted):             candra-bimba %.4f deg  bhu-bimba %.4f deg  latitude %.4f deg"
              % (lunar['candra_bimba_deg'], lunar['bhu_bimba_deg'], lunar['moon_latitude_deg']))
        print("  magnitude %.4f deg = %.3f vimshopaka, total=%s, half-duration %s"
              % (lunar['magnitude_deg'], lunar['vimsopaka'], lunar['is_total'],
                 ("%.4f days" % lunar['half_duration_days']) if lunar['half_duration_days'] else "n/a"))
        print()
        print("SOLAR ECLIPSE -- Saka 1532 Margasirsha krishna 30 (p.0084); ahargana is APPROXIMATE, see code")
        print("  book (read, moderate confidence): Sun bhujamsa 8;26;14 -> lambana 23;45 deg (book's own steps)")
        print("  this module (fitted):             candra-bimba %.4f deg  surya-bimba %.4f deg  lambana %.4f deg"
              % (solar['candra_bimba_deg'], solar['surya_bimba_deg'], solar['lambana_deg']))
        print("  magnitude %.4f deg = %.3f vimshopaka, total=%s, half-duration %s"
              % (solar['magnitude_deg'], solar['vimsopaka'], solar['is_total'],
                 ("%.4f days" % solar['half_duration_days']) if solar['half_duration_days'] else "n/a"))
        print()
        print("NOTE: every number above depends on the FITTED discs/latitude/lambana placeholders. This test")
        print("exercises the procedure; it does NOT validate the book's own table values, which have not been")
        print("transcribed (pp. 0044-0048, 0053, 0083-0084). See the module docstring before using this module")
        print("for anything beyond structural development.")
    return dict(lunar=lunar, solar=solar)


if __name__ == "__main__":
    mks_eclipse_selftest()
