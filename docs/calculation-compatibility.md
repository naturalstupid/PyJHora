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

## Optional JHora 8 Parasara aspect table

`jhora.compatibility.aspects` implements the explicit, versioned curve
`JH8-Parasara-sphuta-v1` (version `1.0.0`). It uses supplied chart coordinates;
it needs neither Windows nor JHora binaries and changes no PyJHora settings.
The existing `strength.planet_aspect_relationship_table`, its `_pvr` variant,
and Shadbala/drik-bala calculations remain unchanged.

```python
from jhora.compatibility.aspects import (
    jhora8_parasara_aspects, jhora8_parasara_virupas,
)

# Purely synthetic coordinates, in degrees; IDs are PyJHora Sun=0 .. Ketu=8.
longitudes = {planet: (40.0 * planet + 0.125) % 360 for planet in range(9)}
percent = jhora8_parasara_aspects(longitudes, ascendant_longitude=17.125)
raw = jhora8_parasara_aspects(
    longitudes, ascendant_longitude=17.125, normalize_as_percentage=False,
)
assert percent[0][0] is None       # Self diagonal is unavailable, not zero.
assert raw[0]["H1"] == 0.0        # A calculated zero remains numeric.
assert jhora8_parasara_virupas(255.0, 4) == 37.5  # Jupiter -> target.
```

For an existing PyJHora chart, retain its unrounded sign/degree values and map
by **body ID**, never by display order:

```python
# positions = charts.divisional_chart(...) or charts.mixed_chart(...)
coordinates = {body: sign * 30.0 + degree for body, (sign, degree) in positions}
table = jhora8_parasara_aspects(
    {body: coordinates[body] for body in range(9)},
    ascendant_longitude=coordinates["L"],
)
```

Recompute the table from each Varga's own transformed planets and Ascendant.
No natal chart, ephemeris, birth time, place or global chart settings are read.
Omit `ascendant_longitude` for a planet-only table. A supplied Ascendant adds
equal-degree targets `H1` through `H12` at `Asc + 30*(house-1)` modulo 360;
these are not unequal-house cusps or the starts of the Ascendant's signs.

Rows are **aspecting/source** planet IDs `0..8`; columns are **aspected/target**
IDs `0..8`, then optional `H1..H12`. Input mapping order is irrelevant. Angles
are `(target longitude - source longitude) % 360` in degrees. Raw strength is
in `0..60` virupas, with full strength `60`; the default integer percentage is
`floor(virupas * (100/60) + 0.5)`, with full strength `100`. Only this last step
is rounded. Self entries are `None`; distinct coincident bodies and valid
zero-strength targets remain numeric zero. Missing, non-finite, out-of-domain
coordinates or unsupported source IDs raise an error rather than returning a
plausible strength. No clamping is used. Rahu and Ketu use the ordinary curve.

### Complete native curve

Let `a` be the directed angle in `[0,360)`. Every interval below includes its
lower bound and excludes its upper bound. Start with the ordinary curve:

| Angle interval | Virupas |
| --- | --- |
| `[0,30)` and `[300,360)` | `0` |
| `[30,60)` | `(a-30)/2` |
| `[60,90)` | `a-45` |
| `[90,120)` | `30+(120-a)/2` |
| `[120,150)` | `150-a` |
| `[150,180)` | `2*(a-150)` |
| `[180,300)` | `(300-a)/2` |

Override only these intervals for the named **aspecting** planet:

| Source | Angle interval | Virupas |
| --- | --- | --- |
| Mars | `[60,90)` | `15+1.5*(a-60)` |
| Mars | `[90,120)` | `150-a` |
| Mars | `[180,210)` | `60` |
| Mars | `[210,240)` | `270-a` |
| Jupiter | `[90,120)` | `45+0.5*(a-90)` |
| Jupiter | `[120,150)` | `60-2*(a-120)` |
| Jupiter | `[210,240)` | `45+0.5*(a-210)` |
| Jupiter | `[240,270)` | `60-1.5*(a-240)` |
| Saturn | `[30,60)` | `2*(a-30)` |
| Saturn | `[60,90)` | `60-0.5*(a-60)` |
| Saturn | `[240,270)` | `a-210` |
| Saturn | `[270,300)` | `2*(300-a)` |

The special Mars, Jupiter and Saturn branches are complete; both planets and
houses use this same function. In particular Jupiter is `60` at `240` degrees,
`37.5` at `255`, and `15` at `270`. The native `[240,270)` taper differs from
the classical BPHS chapter 26 verses 6--12 taper `60-2*(a-240)`, which would be
`30` at `255`. This API intentionally identifies the **native JHora 8 Parasara
variant**, not a correction to the classical text or a Raman implementation.

### Evidence and limits

The method selection and all numerical branches were checked by read-only
static analysis of JHora 8.0, executable SHA256
`3ddbe5fb0458ad1f0ad91b002c7efb8bba9f08891d3f46190aba97d570b17908`.
This is an independent arithmetic implementation; no executable, recovered
code, disassembly, screenshots or private chart fixtures are distributed.
The author's [official release notes, items 3--4](https://vedicastrologer.org/jh/update_7.6.htm)
document the selectable Parasara/Raman special aspects and the color-coded
table. Those notes establish the option's meaning, not the numerical equations.
The classical Sanskrit rules are separately available in
[BPHS chapter 26](https://vedicpupil.in/library/books/brihat-parashara-hora-shastra/chapter-26).

The public tests use synthetic interval endpoints, directed matrices, rotations,
and independently transformed D1/D9/D10/D144/mixed charts. They do not establish
parity for every JHora version, chart setting or house system. Colors/planetary
relationships, sign-based graha/rasi lists, and aggregate drik bala are separate
calculations. Raman and unequal-house modes are not supported by this API;
there is no automatic fallback to another method or to the legacy helpers.

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
