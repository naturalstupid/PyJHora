"""Opt-in JHora 8 Parasara sphuta-drishti; no engine or settings are changed.

This native compatibility curve is not the classical BPHS curve: Jupiter's
240--270 degree taper is 60 - 1.5*r instead of 60 - 2*r. See the calculation
compatibility guide for the source identity, complete curve and limitations.
"""

import math
from numbers import Integral, Real
from typing import Dict, List, Mapping, Optional, Tuple, Union

FORMULA_ID = "JH8-Parasara-sphuta-v1"
FORMULA_VERSION = "1.0.0"
PLANET_IDS = tuple(range(9))  # PyJHora IDs: Sun, Moon, Mars, ..., Rahu, Ketu.
Target = Union[int, str]
Strength = Optional[Union[float, int]]
AspectTable = Dict[int, Dict[Target, Strength]]


def jhora8_parasara_virupas(angle_degrees: float, aspecting_id: int) -> float:
    """Evaluate the directed native Parasara curve in unrounded virupas.

    Args:
        angle_degrees: (Target longitude - source longitude) modulo 360, in
            degrees in [0, 360). No intermediate rounding is performed.
        aspecting_id: Canonical PyJHora ID 0--8 (Sun through Ketu), not a Swiss
            Ephemeris body ID or the input's presentation index.

    Returns:
        A value in [0, 60]; 60 virupas represents full strength. Rahu and Ketu
        use the ordinary curve. This is a pair strength, not drik bala.

    Raises:
        ValueError: The angle or source ID is invalid or unsupported.
        ArithmeticError: The evaluated result is outside the curve's range.
    """
    angle = _degree(angle_degrees, "angle_degrees")
    source = _planet_id(aspecting_id)
    value = _special_virupas(angle, source)
    if not math.isfinite(value) or not 0.0 <= value <= 60.0:
        raise ArithmeticError("JHora 8 Parasara curve returned invalid virupas")
    return value


def jhora8_parasara_aspects(
    planet_longitudes: Mapping[int, float],
    *,
    ascendant_longitude: Optional[float] = None,
    normalize_as_percentage: bool = True,
) -> AspectTable:
    """Calculate a source-to-target matrix from one chart's exact coordinates.

    Args:
        planet_longitudes: All nine canonical IDs 0--8 mapped to unrounded
            longitudes in [0, 360) degrees, already transformed for this chart.
            Input order is immaterial. Missing and unsupported IDs are errors.
        ascendant_longitude: Optional transformed Ascendant in [0, 360).
            Supplying it adds targets H1--H12 at Asc + 30*(house-1) degrees.
            No natal or unequal-house cusps are inferred or recalculated.
        normalize_as_percentage: True returns half-up integer percentages,
            floor(virupas * (100/60) + 0.5); False returns unrounded virupas.

    Returns:
        Rows keyed by aspecting IDs 0--8, each with aspected IDs 0--8 then
        optional H1--H12 in that order. Self entries are None; calculated zero
        is numeric zero, including distinct bodies at the same longitude.

    Raises:
        ValueError: Required coordinates, IDs or the output option are invalid.
    """
    points = _longitudes(planet_longitudes)
    if not isinstance(normalize_as_percentage, bool):
        raise ValueError("normalize_as_percentage must be a bool")
    targets: List[Tuple[Target, float]] = list(points.items())
    if ascendant_longitude is not None:
        ascendant = _degree(ascendant_longitude, "ascendant_longitude")
        targets.extend(("H%d" % (house + 1), (ascendant + 30.0 * house) % 360.0) for house in range(12))
    return {
        source: {
            target: None if target == source else _strength((longitude - points[source]) % 360.0, source, normalize_as_percentage)
            for target, longitude in targets
        }
        for source in PLANET_IDS
    }


def _strength(angle: float, source: int, percentage: bool) -> Union[float, int]:
    value = jhora8_parasara_virupas(angle, source)
    return math.floor(value * (100.0 / 60.0) + 0.5) if percentage else value


def _ordinary_virupas(angle: float) -> float:
    if angle < 30.0 or angle >= 300.0:
        return 0.0
    if angle < 60.0:
        return 0.5 * (angle - 30.0)
    if angle < 90.0:
        return angle - 45.0
    if angle < 120.0:
        return 30.0 + 0.5 * (120.0 - angle)
    if angle < 150.0:
        return 150.0 - angle
    if angle < 180.0:
        return 2.0 * (angle - 150.0)
    return 0.5 * (300.0 - angle)


def _special_virupas(angle: float, source: int) -> float:
    if source == 2:  # Mars
        if 60.0 <= angle < 90.0:
            return 15.0 + 1.5 * (angle - 60.0)
        if 90.0 <= angle < 120.0:
            return 150.0 - angle
        if 180.0 <= angle < 210.0:
            return 60.0
        if 210.0 <= angle < 240.0:
            return 270.0 - angle
    elif source == 4:  # Jupiter
        if 90.0 <= angle < 120.0 or 210.0 <= angle < 240.0:
            return 45.0 + 0.5 * (angle % 30.0)
        if 120.0 <= angle < 150.0:
            return 60.0 - 2.0 * (angle - 120.0)
        if 240.0 <= angle < 270.0:
            return 60.0 - 1.5 * (angle - 240.0)
    elif source == 6:  # Saturn
        if 30.0 <= angle < 60.0:
            return 2.0 * (angle - 30.0)
        if 60.0 <= angle < 90.0:
            return 60.0 - 0.5 * (angle - 60.0)
        if 240.0 <= angle < 270.0:
            return angle - 210.0
        if 270.0 <= angle < 300.0:
            return 2.0 * (300.0 - angle)
    return _ordinary_virupas(angle)


def _planet_id(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value not in PLANET_IDS:
        raise ValueError("Expected a canonical PyJHora planet ID 0--8 (Sun through Ketu)")
    return int(value)


def _degree(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real) or not 0.0 <= value < 360.0 or not math.isfinite(value):
        raise ValueError(name + " must be finite degrees in [0, 360)")
    return float(value)


def _longitudes(values: Mapping[int, float]) -> Dict[int, float]:
    if not isinstance(values, Mapping):
        raise ValueError("planet_longitudes must map all nine planet IDs 0--8 to degrees")
    for source in values:
        _planet_id(source)
    if set(values) != set(PLANET_IDS):
        raise ValueError("planet_longitudes requires all nine planet IDs 0--8")
    return {source: _degree(values[source], "planet longitude") for source in PLANET_IDS}
