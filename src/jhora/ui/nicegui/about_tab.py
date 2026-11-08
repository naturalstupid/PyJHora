#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""About page (/about).

A static information page, always shown in English (unlike every other page, which follows the
visitor's language setting): what SarvaJyotish is, the astrology models and languages it supports,
how birth details and cookies are handled, accuracy/warranty, and attribution. Shows no birth-detail
fields and runs no calculation, so it does not use calc_lock() or render_control_bar().

"""
from nicegui import ui
from jhora import const
from components import navigation_header, render_footer, _get_app_name_version

# Astrology models offered by PyJHora, in the order they appear in Options -> Astrology Engine.
_MODELS = [
    ("Drik", "Swiss-Ephemeris based; the only model supporting Topocentric, True/Apparent positions, "
     "nutation, gravitational deflection etc)."),
    ("Surya Siddhantha", "Traditional geometric model from the Surya Siddhantha text (~1534 BCE)."),
    ("Khanda Khaadyaka", "Traditional model by Brahmagupta (665 CE)."),
    ("Graha Laaghavam", "Traditional model by Ganesha Daivajna (1520 CE)."),
    ("Tantra Sangraha", "Traditional model by Nilakantha Somayaji (~1500 CE)."),
    ("Vakya Panchangam", "Traditional South Indian vakya (memorised-verse) method (~1300CE)."),
    ("Makaranda Sarini", "Traditional model based on the Makaranda tables (~1478 CE)."),
    ("Vateshvara Sidhantha", "Traditional model based on Vateshwvara Sidhandtha (904CE)")
]

_LANGUAGES = const.available_languages.keys()

_MODULES = [
    ("Panchangam", "Tithi, nakshatra, yoga, karana, sunrise/sunset and more, for any date and place."),
    ("Vedic Calendar", "A month grid of a chosen calendar system, with festivals and daily panchangam."),
    ("Kundali", "The birth chart in any of the 24 divisional charts (D1-D150) and 5 chart styles."),
    ("Bhava", "The bhava (house) chart and house cusps, with a choice of house systems (Drik only)."),
    ("Chakra", "Kota, Kaala, Sarvatobadra and six other traditional chakras."),
    ("Transit", "A chart cast for a date found by a pravesha type: Annual, Tithi Pravesha, Prenatal, "
     "Lunar Month/Year, planetary conjunctions and transits, retrograde changes, eclipses, and "
     "Nakshathra Dhasa Progression."),
    ("Dhasa/Bhukthi", "Graha, Raasi and Annual dhasas, drilled down to six levels."),
    ("Compatibility", "Marriage compatibility (Porutham) by birth star, paadham and gender."),
    ("Pancha Pakshi", "The five-bird schedule of activities for a date, time and place."),
    ("Vrathas", "Observance and festival dates between two dates, including festival-name search."),
    ("Calculations", "Amsa Ruler, Sphuta, Saham, Drishti, Arudha, Ashtakavarga, Argala, Shodhaya "
     "Pinda, KP-Lord."),
    ("Strength", "Vimsopaka, Vaiseshikamsa, Shad Bala, Bhava Bala and other strength scores."),
    ("Yoga / Dosha / Prediction", "Yogas and doshas present in the chart, and general predictions."),
]


@ui.page('/about')
def about_page():
    """About page: what SarvaJyotish is, supported models and languages, accuracy/warranty notice,
    privacy and attribution. Always shown in English.
    """
    navigation_header()
    with ui.column().classes('w-full max-w-4xl mx-auto p-2 gap-4'):
        # IMPORTANT: Only this title is translation-aware (_get_app_name_version() -> res_str()), so it
        # is the only piece of this page whose script can actually be Urdu. navigation_header() (in
        # components.py) puts the ENTIRE page in dir="rtl" whenever the visitor's language is RTL
        # (RTL_LANGUAGES) - that flip is on an ancestor element (#app), so by default it mirrors EVERY
        # descendant, including the plain hardcoded-English labels below. components.py's own global
        # print/theme CSS already defines the opt-out for exactly this situation:
        #     .chart-surface, .keep-ltr { direction: ltr !important; }
        # So the title is left WITHOUT that class (it should keep following the page direction), and
        # everything else on this page is wrapped in a '.keep-ltr' container so it stays left-to-right
        # and left-aligned regardless of the visitor's language - matching this page's own docstring
        # ("always shown in English").
        ui.label(f"{_get_app_name_version()}").classes('text-2xl font-bold text-green-700')
        #ui.label(f"SarvaJyotish \u2014 V{const._APP_VERSION}").classes('text-2xl font-bold text-green-700')

        with ui.column().classes('w-full gap-4 keep-ltr'):
          ui.label("A free, browser-based Vedic astrology application.").classes('text-base text-gray-700')
          ui.label("Built on, and currently distributed as part of, the PyJHora engine.") \
              .classes('text-sm text-gray-500')

          with ui.card().classes('w-full p-4'):
              ui.label("What it offers").classes('text-lg font-bold text-green-700')
              with ui.column().classes('gap-1 mt-2'):
                  for name, desc in _MODULES:
                      ui.html(f"<b>{name}</b> \u2014 {desc}").classes('text-sm')
              ui.label(
                  "Many of these, where applicable, offer a choice of calculation methods or variations "
                  "by different traditional authors (for example dhasa and divisional-chart methods, or "
                  "the astrology engine itself) \u2014 select these under each page's Options / Chart "
                  "Options / Dhasa Options. Also, there are various configuration options such as planet "
                  "flags, calendar types, choice of language, astrology engine etc that can be selected "
                  "from Options. Please note: many of them were used by astrologers for research "
                  "purposes and results may be different from your expectations."
              ).classes('text-sm text-gray-600 mt-2 italic')
              ui.label(
                  "Some Settings are technical in nature \u2014 for example, Geocentric vs. Topocentric "
                  "planet positions, whether or not to apply nutation, True vs. Apparent positions, or "
                  "which edge of the solar/lunar disc to use. Changing these affects every calculation on "
                  "every page. If you are not sure what a setting does, it is best to leave it at its "
                  "default; you can always restore every setting to its factory default from Settings "
                  "\u2192 Restore Defaults."
              ).classes('text-sm text-gray-600 mt-2 italic')

          with ui.card().classes('w-full p-4'):
              ui.label("Astrology models").classes('text-lg font-bold text-green-700')
              ui.label("Choose the engine in Settings. Each model computes its own panchangam, charts "
                       "and dhasas; results can differ between models for the same birth details.") \
                  .classes('text-sm text-gray-600 mb-2')
              with ui.column().classes('gap-1'):
                  for name, desc in _MODELS:
                      ui.html(f"<b>{name}</b> \u2014 {desc}").classes('text-sm')

          with ui.card().classes('w-full p-4'):
              ui.label("Languages").classes('text-lg font-bold text-green-700')
              ui.label(', '.join(_LANGUAGES)).classes('text-sm mt-1')
              ui.label("Choose the display language in Settings; it is remembered for this browser. "
                       "This About page is always shown in English.").classes('text-sm text-gray-600 mt-1')

          with ui.card().classes('w-full p-4'):
              ui.label("Privacy").classes('text-lg font-bold text-green-700')
              ui.label(
                  "The birth details you enter (date, time and place) are held only in the server's "
                  "memory while you use this site. They are never written to disk or stored in a "
                  "cookie, are discarded after a period of inactivity, and are lost whenever the "
                  "server restarts."
              ).classes('text-sm mt-1')
              ui.label(
                  "SarvaJyotish itself sets only one cookie: a random ID that remembers your settings "
                  "(such as language). We do not control, and cannot see, any other cookies that your "
                  "browser, its extensions, or the network path to this site may set independently of "
                  "this application."
              ).classes('text-sm mt-1')

          with ui.card().classes('w-full p-4 border-2 border-amber-400 bg-amber-50'):
              ui.label("Accuracy and warranty").classes('text-lg font-bold text-amber-800')
              ui.label(
                  "The calculations in this application have been tested and verified against the "
                  "worked examples in the source texts and against Jagannatha Hora V8.0. No claims are "
                  "made, however, as to the accuracy or fitness of these calculations for any particular "
                  "purpose. This software is provided \u201cas is\u201d, without warranty of any kind, "
                  "express or implied, including but not limited to the warranties of merchantability, "
                  "fitness for a particular purpose, and non-infringement."
              ).classes('text-sm mt-1')
              ui.label(
                  "IMPORTANT NOTE: Please note the astrological calculations such as tithi, "
                  "lunar/solar month/day etc depend on planet longitudes which in turn depend on ayanamsa,"
                  "sidereal/topo planet true/mean nodes etc. If you want to compare your results with "
                  "regular/daily calendars - try using settings those calendars use (e.g. LAHIRI ayanamsa) "
                  "and in case you want to compare results with jagannatha hora V8.0 - try using "
                  "True Pushya ayanamsa and other settings in that software. From V5.0.2 onwards, "
                  "PyJHora uses the default ayanamsa to LAHIRI to align with regular calendars."
              ).classes('font-bold')

          with ui.card().classes('w-full p-4'):
              ui.label("Acknowledgements").classes('text-lg font-bold text-green-700')
              ui.html(
                  "SarvaJyotish/VedicAstrology is a web service built on top of the <b>PyJHora</b> "
                  "Vedic astrology library by Dr. Sundar Sundaresan, Open Astro Technologies, USA. It is "
                  "currently distributed as part of the PyJHora/SarvaJyotish project, under the same version "
                  "number, for ease of distribution; it is expected to become a separate project once it "
                  "has enough users of its own to need that.<br>"
                  "Library source: "
                  "<a href='https://github.com/naturalstupid/PyJHora' target='_blank' "
                  "class='text-blue-700 underline'>github.com/naturalstupid/PyJHora</a><br>"
                  "PyJHora is free software distributed under the GNU Affero General Public License."
              ).classes('text-sm mt-1')
    render_footer()
