import { describe, expect, it } from 'vitest';
import {
  SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, RAHU, KETU,
} from '../../../src/core/constants';
import {
  PlanetPosition,
  getKPLordsFromPlanetPositions,
  getPachakadiSambhandha,
  latthaStarsPlanets,
  solarUpagrahaLongitudesFromSunLong,
  solarUpagrahaLongitudes,
  mixedChartFromRasiPositions,
  getDivisionalChart,
} from '../../../src/core/horoscope/charts';
import { nakshatraPada, cyclicCountOfStarsWithAbhijit, cyclicCountOfStars } from '../../../src/core/panchanga/drik';

/**
 * Test data: fictional chart positions.
 * Lagna=Virgo(5) 15.5°, Sun=Pisces(11) 20.5°, Moon=Cancer(3) 12.3°,
 * Mars=Aquarius(10) 5.2°, Mercury=Pisces(11) 8.7°, Jupiter=Libra(6) 22.1°,
 * Venus=Aries(0) 17.8°, Saturn=Aries(0) 28.9°, Rahu=Aquarius(10) 15.3°,
 * Ketu=Leo(4) 15.3°
 */
const TEST_POSITIONS: PlanetPosition[] = [
  { planet: -1, rasi: 5, longitude: 15.5 },
  { planet: SUN, rasi: 11, longitude: 20.5 },
  { planet: MOON, rasi: 3, longitude: 12.3 },
  { planet: MARS, rasi: 10, longitude: 5.2 },
  { planet: MERCURY, rasi: 11, longitude: 8.7 },
  { planet: JUPITER, rasi: 6, longitude: 22.1 },
  { planet: VENUS, rasi: 0, longitude: 17.8 },
  { planet: SATURN, rasi: 0, longitude: 28.9 },
  { planet: RAHU, rasi: 10, longitude: 15.3 },
  { planet: KETU, rasi: 4, longitude: 15.3 },
];

// ============================================================================
// NAKSHATRA PADA TESTS (drik.ts)
// ============================================================================

describe('nakshatraPada', () => {
  it('should return correct nakshatra and pada for 0 degrees', () => {
    const [nak, pada, remainder] = nakshatraPada(0);
    expect(nak).toBe(1);
    expect(pada).toBe(1);
    expect(remainder).toBeCloseTo(0, 5);
  });

  it('should return correct nakshatra for 120.5 degrees', () => {
    const [nak, pada] = nakshatraPada(120.5);
    expect(nak).toBe(10);
    expect(pada).toBe(1);
  });

  it('should return correct nakshatra for 359.9 degrees', () => {
    const [nak, pada] = nakshatraPada(359.9);
    expect(nak).toBe(27);
    expect(pada).toBe(4);
  });
});

// ============================================================================
// CYCLIC STAR COUNTING TESTS (drik.ts)
// ============================================================================

describe('cyclicCountOfStarsWithAbhijit', () => {
  it('should count forward correctly (28 stars)', () => {
    expect(cyclicCountOfStarsWithAbhijit(1, 12, 1, 28)).toBe(12);
  });

  it('should count backward correctly (28 stars)', () => {
    expect(cyclicCountOfStarsWithAbhijit(5, 22, -1, 28)).toBe(12);
  });

  it('should count forward correctly (27 stars)', () => {
    expect(cyclicCountOfStarsWithAbhijit(10, 3, 1, 27)).toBe(12);
  });

  it('should wrap around correctly', () => {
    // From star 27, go forward 3 in 28-star system
    const result = cyclicCountOfStarsWithAbhijit(27, 3, 1, 28);
    expect(result).toBe(1);
  });
});

describe('cyclicCountOfStars (27-star system)', () => {
  it('should count forward in 27-star system', () => {
    expect(cyclicCountOfStars(10, 3, 1)).toBe(12);
  });
});

// ============================================================================
// KP LORDS TESTS (charts.ts)
// ============================================================================

describe('getKPLordsFromPlanetPositions', () => {
  it('should compute KP lords for all planets (Python parity)', () => {
    const kp = getKPLordsFromPlanetPositions(TEST_POSITIONS);

    // Python: planet=-1: [115, 1, 4, 7, 3, 7, 6]
    expect(kp[-1][0]).toBe(115); // KP number
    expect(kp[-1][1]).toBe(1);   // star lord (Moon)
    expect(kp[-1][2]).toBe(4);   // sub lord (Jupiter)

    // Python: planet=0(Sun): [243, 3, 5, 7, 5, 2, 2]
    expect(kp[SUN][0]).toBe(243);
    expect(kp[SUN][1]).toBe(3);
    expect(kp[SUN][2]).toBe(5);

    // Python: planet=1(Moon): [72, 6, 2, 4, 0, 7, 2]
    expect(kp[MOON][0]).toBe(72);
    expect(kp[MOON][1]).toBe(6); // star lord (Saturn)
    expect(kp[MOON][2]).toBe(2); // sub lord (Mars)

    // Python: planet=4(Jupiter): [140, 4, 6, 3, 5, 5, 1]
    expect(kp[JUPITER][0]).toBe(140);
    expect(kp[JUPITER][1]).toBe(4); // star lord (Jupiter)
    expect(kp[JUPITER][2]).toBe(6); // sub lord (Saturn)
  });

  it('should return 7 entries per planet (KP no + star lord + sub lord + 4 sub-sub lords)', () => {
    const kp = getKPLordsFromPlanetPositions(TEST_POSITIONS);
    for (const [, info] of Object.entries(kp)) {
      expect(info.length).toBe(7);
    }
  });

  it('should have entries for all planets including Lagna', () => {
    const kp = getKPLordsFromPlanetPositions(TEST_POSITIONS);
    expect(Object.keys(kp).length).toBe(10); // -1 through 8
  });
});

// ============================================================================
// PACHAKADI SAMBHANDHA TESTS (charts.ts)
// ============================================================================

describe('getPachakadiSambhandha', () => {
  it('should detect correct pachakadi relationships (Python parity)', () => {
    const pachakadi = getPachakadiSambhandha(TEST_POSITIONS);

    // Python: planet=2(Mars): [1, (1, 6, '')]  -> Bodhaka with Moon in 6th from Mars
    expect(pachakadi[MARS]).toBeDefined();
    expect(pachakadi[MARS][0]).toBe(1); // relation index (bodhaka)
    expect(pachakadi[MARS][1][0]).toBe(MOON); // related planet
    expect(pachakadi[MARS][1][1]).toBe(6); // house offset

    // Python: planet=4(Jupiter): [1, (2, 5, '')] -> Bodhaka with Mars in 5th from Jupiter
    expect(pachakadi[JUPITER]).toBeDefined();
    expect(pachakadi[JUPITER][0]).toBe(1);
    expect(pachakadi[JUPITER][1][0]).toBe(MARS);
    expect(pachakadi[JUPITER][1][1]).toBe(5);

    // Python: planet=5(Venus): [2, (0, 12, '')] -> Karaka with Sun in 12th from Venus
    expect(pachakadi[VENUS]).toBeDefined();
    expect(pachakadi[VENUS][0]).toBe(2);
    expect(pachakadi[VENUS][1][0]).toBe(SUN);
    expect(pachakadi[VENUS][1][1]).toBe(12);
  });

  it('should only return planets that have active relationships', () => {
    const pachakadi = getPachakadiSambhandha(TEST_POSITIONS);
    // Only 3 planets had active relationships in this chart
    expect(Object.keys(pachakadi).length).toBe(3);
  });
});

// ============================================================================
// LATTA STARS TESTS (charts.ts)
// ============================================================================

describe('latthaStarsPlanets', () => {
  it('should compute latta stars with Abhijit (28 stars) (Python parity)', () => {
    const latta = latthaStarsPlanets(TEST_POSITIONS, true);

    // Python results for 28-star system:
    const expected28: [number, number][] = [
      [27, 10], // Sun: star=27, latta=10
      [8, 15],  // Moon: star=8, latta=15
      [23, 25], // Mars
      [26, 20], // Mercury
      [16, 21], // Jupiter
      [2, 26],  // Venus
      [3, 10],  // Saturn
      [24, 16], // Rahu
      [11, 3],  // Ketu
    ];

    expect(latta.length).toBe(9);
    for (let i = 0; i < 9; i++) {
      expect(latta[i][0]).toBe(expected28[i][0]); // planet star
      expect(latta[i][1]).toBe(expected28[i][1]); // latta star
    }
  });

  it('should compute latta stars without Abhijit (27 stars)', () => {
    const latta = latthaStarsPlanets(TEST_POSITIONS, false);

    // Python results for 27-star system:
    const expected27: [number, number][] = [
      [27, 11], // Sun
      [8, 14],  // Moon
      [23, 25], // Mars
      [26, 20], // Mercury
      [16, 21], // Jupiter
      [2, 25],  // Venus (different from 28-star)
      [3, 10],  // Saturn
      [24, 16], // Rahu
      [11, 3],  // Ketu
    ];

    expect(latta.length).toBe(9);
    for (let i = 0; i < 9; i++) {
      expect(latta[i][0]).toBe(expected27[i][0]);
      expect(latta[i][1]).toBe(expected27[i][1]);
    }
  });
});

// ============================================================================
// SOLAR UPAGRAHA LONGITUDE TESTS
// ============================================================================

/**
 * Test positions for solar upagraha and divisional chart tests.
 * Sun at Pisces(11) 15.5° → absolute longitude = 345.5
 */
const UPAGRAHA_POSITIONS: PlanetPosition[] = [
  { planet: -1, rasi: 5, longitude: 10.0 },   // Lagna: Virgo
  { planet: SUN, rasi: 11, longitude: 15.5 },  // Sun: Pisces 15.5°
  { planet: MOON, rasi: 3, longitude: 20.0 },  // Moon: Cancer
  { planet: MARS, rasi: 10, longitude: 5.0 },  // Mars: Aquarius
  { planet: MERCURY, rasi: 0, longitude: 25.0 }, // Mercury: Aries
  { planet: JUPITER, rasi: 6, longitude: 12.0 }, // Jupiter: Libra
  { planet: VENUS, rasi: 0, longitude: 8.0 },  // Venus: Aries
  { planet: SATURN, rasi: 0, longitude: 3.0 }, // Saturn: Aries
  { planet: RAHU, rasi: 10, longitude: 22.0 }, // Rahu: Aquarius
  { planet: KETU, rasi: 4, longitude: 22.0 },  // Ketu: Leo
];

describe('Solar Upagraha Longitudes', () => {
  const SUN_LONG = 345.5; // 11*30 + 15.5

  it('should compute dhuma longitude correctly', () => {
    // Python: drik.solar_upagraha_longitudes(345.5, "dhuma") = [3, 28.8333]
    const result = solarUpagrahaLongitudesFromSunLong(SUN_LONG, 'dhuma');
    expect(result).not.toBeNull();
    expect(result!.rasi).toBe(3); // Cancer
    expect(result!.longitude).toBeCloseTo(28.8333, 3);
  });

  it('should compute vyatipaata longitude correctly', () => {
    // Python: [8, 1.1667]
    const result = solarUpagrahaLongitudesFromSunLong(SUN_LONG, 'vyatipaata');
    expect(result).not.toBeNull();
    expect(result!.rasi).toBe(8); // Sagittarius
    expect(result!.longitude).toBeCloseTo(1.1667, 3);
  });

  it('should compute parivesha longitude correctly', () => {
    // Python: [2, 1.1667]
    const result = solarUpagrahaLongitudesFromSunLong(SUN_LONG, 'parivesha');
    expect(result).not.toBeNull();
    expect(result!.rasi).toBe(2); // Gemini
    expect(result!.longitude).toBeCloseTo(1.1667, 3);
  });

  it('should compute indrachaapa longitude correctly', () => {
    // Python: [9, 28.8333]
    const result = solarUpagrahaLongitudesFromSunLong(SUN_LONG, 'indrachaapa');
    expect(result).not.toBeNull();
    expect(result!.rasi).toBe(9); // Capricorn
    expect(result!.longitude).toBeCloseTo(28.8333, 3);
  });

  it('should compute upaketu longitude correctly', () => {
    // Python: [10, 15.5]
    const result = solarUpagrahaLongitudesFromSunLong(SUN_LONG, 'upaketu');
    expect(result).not.toBeNull();
    expect(result!.rasi).toBe(10); // Aquarius
    expect(result!.longitude).toBeCloseTo(15.5, 5);
  });

  it('should return null for invalid upagraha name', () => {
    expect(solarUpagrahaLongitudesFromSunLong(SUN_LONG, 'invalid')).toBeNull();
  });

  it('should compute from planet positions (charts-level)', () => {
    // Python: charts.solar_upagraha_longitudes(pp, "dhuma") = [3, 28.8333]
    const result = solarUpagrahaLongitudes(UPAGRAHA_POSITIONS, 'dhuma');
    expect(result).not.toBeNull();
    expect(result!.rasi).toBe(3);
    expect(result!.longitude).toBeCloseTo(28.8333, 3);
  });

  it('should compute with navamsa divisional factor', () => {
    // Python: charts.solar_upagraha_longitudes(pp, "dhuma", dcf=9) = [11, 28.8333]
    const result = solarUpagrahaLongitudes(UPAGRAHA_POSITIONS, 'dhuma', 9);
    expect(result).not.toBeNull();
    expect(result!.rasi).toBe(11); // Pisces
  });

  it('should compute upaketu with navamsa divisional factor', () => {
    // Python: charts.solar_upagraha_longitudes(pp, "upaketu", dcf=9) = [10, 15.5]
    const result = solarUpagrahaLongitudes(UPAGRAHA_POSITIONS, 'upaketu', 9);
    expect(result).not.toBeNull();
    expect(result!.rasi).toBe(10);
  });
});

// ============================================================================
// MIXED CHART AND DIVISIONAL POSITIONS TESTS
// ============================================================================

describe('Mixed Chart and Divisional Positions', () => {
  it('should compute D9 (Navamsa) correctly', () => {
    // Python: divisional_positions_from_rasi_positions(pp, 9)
    const d9 = getDivisionalChart(UPAGRAHA_POSITIONS, 9);
    expect(d9.length).toBe(UPAGRAHA_POSITIONS.length);
    // Lagna: rasi=11
    expect(d9[0].rasi).toBe(11);
    // Sun: rasi=7, long≈19.5
    expect(d9[1].rasi).toBe(7);
    expect(d9[1].longitude).toBeCloseTo(19.5, 1);
    // Moon: rasi=8, long≈0.0
    expect(d9[2].rasi).toBe(8);
    // Mars: rasi=7, long≈15.0
    expect(d9[3].rasi).toBe(7);
    // Jupiter: rasi=9, long≈18.0
    expect(d9[5].rasi).toBe(9);
    // Saturn: rasi=0, long≈27.0
    expect(d9[7].rasi).toBe(0);
    expect(d9[7].longitude).toBeCloseTo(27.0, 1);
  });

  it('should compute D7 (Saptamsa) correctly', () => {
    // Python: divisional_positions_from_rasi_positions(pp, 7)
    const d7 = getDivisionalChart(UPAGRAHA_POSITIONS, 7);
    // Lagna: rasi=1
    expect(d7[0].rasi).toBe(1);
    // Sun: rasi=8, long≈18.5
    expect(d7[1].rasi).toBe(8);
    expect(d7[1].longitude).toBeCloseTo(18.5, 1);
    // Saturn: rasi=0, long≈21.0
    expect(d7[7].rasi).toBe(0);
    expect(d7[7].longitude).toBeCloseTo(21.0, 1);
  });

  it('should compute mixed D9-D12 chart', () => {
    // Python: mixed_chart_from_rasi_positions(pp, 9, 12)
    const mixed = mixedChartFromRasiPositions(UPAGRAHA_POSITIONS, 9, 12);
    expect(mixed.length).toBe(UPAGRAHA_POSITIONS.length);
    // Lagna: rasi=11
    expect(mixed[0].rasi).toBe(11);
    // Sun: rasi=2, long≈24.0
    expect(mixed[1].rasi).toBe(2);
    expect(mixed[1].longitude).toBeCloseTo(24.0, 1);
    // Moon: rasi=8
    expect(mixed[2].rasi).toBe(8);
    // Mars: rasi=1
    expect(mixed[3].rasi).toBe(1);
    // Jupiter: rasi=4, long≈6.0
    expect(mixed[5].rasi).toBe(4);
    // Saturn: rasi=10, long≈24.0
    expect(mixed[7].rasi).toBe(10);
    expect(mixed[7].longitude).toBeCloseTo(24.0, 1);
    // Rahu: rasi=7, long≈6.0
    expect(mixed[8].rasi).toBe(7);
    // Ketu: rasi=1, long≈6.0
    expect(mixed[9].rasi).toBe(1);
  });

  it('should return D1 positions for factor=1', () => {
    const d1 = getDivisionalChart(UPAGRAHA_POSITIONS, 1);
    expect(d1.length).toBe(UPAGRAHA_POSITIONS.length);
    // Sun should still be in Pisces
    expect(d1[1].rasi).toBe(11);
    expect(d1[1].longitude).toBeCloseTo(15.5, 3);
  });
});
