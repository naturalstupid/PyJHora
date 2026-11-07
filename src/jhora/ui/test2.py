#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
audit_mercury.py -- indirect audit of the 528 Mercury rows of vakya_planets_arcmin.csv (no printed page needed).

Idea.  A misread digit in one table row would give the SAME error every time that row is used (about 38 times in 250 years,
each time with a different Dhruva).  The book's own model error is a smooth function of the Mercury phase.  Two cycles three
apart (3 x 116 d = 3.96 anomalistic periods) have the same phase to 0.04 of an orbit, so the same row in cycle c-3 and c+3
must show nearly the same error as in cycle c.  The difference "row minus mean of the same row in c-3, c+3" is therefore ~0
for a correct row and equals the misread for a wrong one.

Reference: JPL approximate Keplerian elements (Standish) + the usual linear Lahiri ayanamsa; any error of this reference is the
same for the three cycles and cancels in the difference.

Detection limit: a misread below ~0.5 deg (e.g. a wrong arc-minute digit) cannot be seen this way; cycles 1, 2, 3 and 20-22 cannot
be tested cleanly (the 22-cycle table is 2.6 days longer than 22 synodic periods, so the phase does not repeat across the wrap).
Run:  python audit_mercury.py        (needs jhora.const and the module; about 40 s)
"""
import collections
import math
import statistics
from jhora import const
from jhora.panchanga import vakya_panchanga as V

EL = {"Mercury": (0.38709927, 0.00000037, 0.20563593, 0.00001906, 7.00497902, -0.00594749, 252.25032350, 149472.67411175, 77.45779628, 0.16047689, 48.33076593, -0.12534081),
      "Earth": (1.00000261, 0.00000562, 0.01671123, -0.00004392, -0.00001531, -0.01294668, 100.46457166, 35999.37244981, 102.93768193, 0.32327364, 0.0, 0.0)}


def helio(name, T):
    a0, da, e0, de, I0, dI, L0, dL, w0, dw, O0, dO = EL[name]
    a, e = a0 + da * T, e0 + de * T
    I, O = math.radians(I0 + dI * T), math.radians(O0 + dO * T)
    L, w = L0 + dL * T, w0 + dw * T
    M = math.radians((L - w) % 360)
    E = M
    for _ in range(25):
        E -= (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
    x, y = a * (math.cos(E) - e), a * math.sqrt(1 - e * e) * math.sin(E)
    om = math.radians(w) - O
    co, so, cO, sO, cI = math.cos(om), math.sin(om), math.cos(O), math.sin(O), math.cos(I)
    return (co * cO - so * sO * cI) * x + (-so * cO - co * sO * cI) * y, (co * sO + so * cO * cI) * x + (-so * sO + co * cO * cI) * y


def geocentric_mercury(jd):
    T = (jd - 2451545.0) / 36525.0
    p, e = helio("Mercury", T), helio("Earth", T)
    return math.degrees(math.atan2(p[1] - e[1], p[0] - e[0])) % 360


def signed(x):
    return ((x + 180.0) % 360.0) - 180.0


def main():
    planet = const._MERCURY
    rows = V._load_planets()[planet]
    ncycle = V._PLANET_CONST[planet]["ncycle"]
    k0, k1 = V.kali_days_for_date(1800, 1, 1), V.kali_days_for_date(2050, 1, 1)
    err, pos = {}, {}
    for K in range(k0, k1):
        jd = K + V.KALI_EPOCH_JDN - 0.5 + 0.25 - const.ujjain_lat_long[1] / 360.0
        ayan = 23.853 + 1.3969 * (jd - 2451545.0) / 36525.0
        err[K] = signed(V.longitude_end_of_day(planet, K)[0] - ((geocentric_mercury(jd) - ayan) % 360))
        cyc, day = V.planet_dhruva_and_cycle(planet, K)[1:3]
        pos[K] = (cyc % ncycle + 1, day)
    print("Mercury, vakya minus independent theory, %d days 1800-2050: mean %+.2f  std %.2f  min %.1f  max %.1f deg"
          % (len(err), statistics.mean(err.values()), statistics.pstdev(err.values()), min(err.values()), max(err.values())))
    row_days = {c: [r[0] for r in rows[c]] for c in rows}
    at = collections.defaultdict(list)
    for K in range(k0 + 130, k1 - 130):
        c, day = pos[K]
        for rd in row_days[c]:
            if abs(day - rd) <= 0.5:
                at[(c, rd)].append(err[K])
    mean_err = {k: statistics.mean(v) for k, v in at.items() if len(v) >= 8}
    dev = []
    for (c, d), e in mean_err.items():
        nb = [mean_err[(c + s, d)] for s in (-3, 3) if (c + s, d) in mean_err]
        if len(nb) == 2:
            dev.append((e - statistics.mean(nb), c, d))
    a = sorted(abs(x[0]) for x in dev)
    total = sum(len(v) for v in rows.values())
    print("rows with data %d of %d; rows testable with two same-phase neighbours: %d" % (len(mean_err), total, len(dev)))
    print("row minus same row 3 cycles earlier/later: median %.3f  90th %.3f  99th %.3f  max %.3f deg" % (
        statistics.median(a), a[int(.9 * len(a))], a[int(.99 * len(a))], a[-1]))
    flagged = [(round(d, 2), c, dd) for d, c, dd in sorted(dev, key=lambda x: -abs(x[0])) if abs(d) > 0.7]
    print("rows deviating by more than 0.7 deg (a wrong degree digit would give about 1.0):", flagged if flagged else "none")
    if flagged:
        for d, c, dd in flagged:
            tv = [r for r in rows[c] if r[0] == dd][0][1]
            print("   cycle %2d day %3d  table %s  -> check against the printed page" % (c, dd, V.dms(tv / 60.0)))


if __name__ == "__main__":
    main()
