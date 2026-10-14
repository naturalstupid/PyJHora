# Calculation compatibility

## Portable calculation corrections

The third element returned by `drik.sunrise()` and `drik.sunset()` is a precise
**local** Julian day. The display string rounds to seconds; the numerical epoch
retains the solver's fractional seconds. Consumers should convert that local
epoch to UTC only once.

Special lagnas use the most recent sunrise, including births before the current
civil day's sunrise. Their `special_lagna_continuity` option selects the birth
Sun when true and the sunrise Sun when false. Pranapada uses the **birth Sun**
in both modes, with the movable/fixed/dual sign offset, and applies progression
correction once.

Daytime upagrahas use sunrise through sunset. Nighttime upagrahas use sunset
through the following sunrise, with the corresponding Vedic weekday's rulers.
Absolute local Julian days preserve the date when the interval crosses midnight.

Selecting true or mean nodes updates both `planet_list` and `const._RAHU`, so
special points such as Bhrigu Bindu use the same node convention as the planets.

## Optional Varnada convention

Existing natal-projection behavior remains the default. With
`jhora_compatible=True`, BV Raman Varnada signs are recomputed using the
requested chart's Ascendant and Hora Lagna; their degrees retain the ordinary
transformation of the natal Varnada longitude. Other Varnada methods are rejected
in this mode rather than silently applying an unverified rule.

```python
from jhora import const
from jhora.horoscope.chart import charts

points = charts.varnada_lagna_longitudes(
    date, time, place,
    divisional_chart_factor=9, chart_method=1,
    varnada_method=const.VARNADA_METHOD.BV_RAMAN,
    jhora_compatible=True,
)
```

For a mixed chart, the first chart's Varnada context is recomputed and then
transformed through the second chart. For example, the mixed wrapper with
`varga_factor_1=10`, `chart_method_1=1`, `varga_factor_2=9`, and
`chart_method_2=1` applies traditional D10 followed by traditional D9.
Factor 0 represents the native zero-degree display placeholder, not a physical
divisional chart.

## Optional Windows JHora 8.0 exporter

This exporter is a narrowly scoped compatibility feature. It does not replace
all PyJHora or Swiss Ephemeris APIs, and ordinary imports activate no profile.
Use it in a dedicated calculation process because PyJHora configuration is
global and not designed for concurrent profile calculations.

Requirements:

- Windows with 32-bit Windows PowerShell available.
- A separately installed JHora 8.0 Swiss Ephemeris **2.02.01** DLL with SHA256
  `d56ba3a6158fcec3921774b5c9fcc533374413d7b77cdbc6b83ffa082d260a69`.
- That installation's ephemeris data and `fixstars.cat` catalogue.

No DLL or JHora executable is redistributed. The application does not need to
be running. This feature neither automates a GUI nor sends calculation inputs
to a service. DLL and ephemeris paths may be supplied explicitly; the defaults
use the standard installation under `C:\Program Files (x86)\Jagannatha Hora`.

```python
from jhora.compatibility.export import export_chart

# Synthetic example; time and coordinates are explicitly supplied.
data = export_chart(
    (2000, 1, 1), (12, 0, 0), 0.0, 0.0, 0.0,
    name="Example", place_name="Synthetic",
    elevation=0.0,
    dasha_windows=(("Rahu",), ("Rahu", "Venus")),
)
```

The result contains 56 positions, 25 chart columns, calendar details,
Ashtakavarga, and Vimshottari maha periods. `dasha_windows` requests additional
child periods under the listed parents; an empty value exports only maha
periods. Numerical values and timezone-aware ISO timestamps are retained.

The fixed native profile uses True Chitra, true geocentric positions, mean
nodes, and solar-arc years. Its internal event search finds the next sunrise
after the input time, finds the previous sunrise from that result minus 1.5
days, and finds sunset from the previous sunrise. Matching those starting
epochs matters with the older solver. These are **Vedic-day** events internal
to the exporter, so pre-dawn inputs may return the previous civil day's sunrise
and sunset. The ordinary public `drik.sunrise()` / `sunset()` APIs retain their
civil-date behavior outside the exporter.

The internal scope restores the recorded PyJHora functions and settings on
success or failure. Custom ayanamsa modes (`SIDM_USER`, `SENTHIL`, and
`SUNDAR_SS`) are rejected before mutation because their epoch/value parameters
cannot be recovered from a mode name alone. Configure a standard named mode in
the dedicated process before using the exporter.

Formatted chart cells intentionally reproduce the native display: whole
degrees are floored and the minute part is rounded, including an occasional
minute value of `60`. Use `degrees_in_sign` for numerical calculations.

Historical dasha timestamps can differ from a modern Swiss engine because of
the engine's time models and the chosen solar-year convention. Matching a
legacy application's output is distinct from improving astronomical accuracy.

Validation covers the described positions/charts, calendar, Ashtakavarga, and
Vimshottari windows. Shadbala, yogas, other dasha systems, and other JHora
preferences are outside this exporter's scope.

## Regression tests

Run the portable, synthetic tests from the repository root:

```sh
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*compatibility.py'
```

These tests require the calculation dependencies, but neither Qt nor a JHora
installation. Optional real-worker checks skip on machines without the verified
DLL. Private birth data, native exports, and binary-analysis artifacts are not
part of the test fixtures.
