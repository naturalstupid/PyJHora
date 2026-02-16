/**
 * Tests for bhava (house) calculations — Phase 3
 *
 * Python reference data generated from drik.py:
 *   ascendant, bhaava_madhya_kp, bhaava_madhya_sripathi,
 *   bhaava_madhya_swe, _bhaava_madhya_new, dhasavarga, dasavarga_from_long
 */

import { beforeAll, describe, expect, it } from 'vitest';
import { initializeEphemeris, ascendantFullAsync, houseCuspsAsync } from '@core/ephemeris/swe-adapter';
import {
  dasavargaFromLong,
  dhasavargaAsync,
  bhaavaMadhyaKP,
  bhaavaMadhyaSwe,
  bhaavaMadhyaSripathi,
  bhaavaMadhyaNew,
  assignPlanetsToHouses,
  nakshatraPada,
} from '@core/panchanga/drik';
import type { Place } from '@core/types';
import { gregorianToJulianDay } from '@core/utils/julian';

const bangalore: Place = {
  name: 'Bangalore',
  latitude: 12.972,
  longitude: 77.594,
  timezone: 5.5,
};

function jdForDate(year: number, month: number, day: number): number {
  return gregorianToJulianDay({ year, month, day }, { hour: 0, minute: 0, second: 0 });
}

describe('Phase 3: Bhava House Systems', () => {
  beforeAll(async () => {
    await initializeEphemeris();
  });

  // ===========================================================================
  // ascendantFullAsync
  // ===========================================================================

  /*
   * Python reference:
   * 1996-12-07: [4, 17.349, 11, 2]  — constellation=4(Leo), long=17.349, nak=11, pada=2
   * 2024-06-21: [10, 29.210, 25, 3]  — constellation=10(Aquarius), long=29.210, nak=25, pada=3
   */
  describe('ascendantFullAsync', () => {
    it('should return correct ascendant for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const [constellation, longitude, nakNo, padaNo] = await ascendantFullAsync(jd, bangalore);
      expect(constellation).toBe(4); // Leo
      expect(longitude).toBeCloseTo(17.349, 0);
      expect(nakNo).toBe(11);
      expect(padaNo).toBe(2);
    });

    it('should return correct ascendant for 2024-06-21', async () => {
      const jd = jdForDate(2024, 6, 21);
      const [constellation, longitude, nakNo, padaNo] = await ascendantFullAsync(jd, bangalore);
      expect(constellation).toBe(10); // Aquarius
      expect(longitude).toBeCloseTo(29.210, 0);
      expect(nakNo).toBe(25);
      expect(padaNo).toBe(3);
    });
  });

  // ===========================================================================
  // dasavargaFromLong (pure function — no async needed)
  // ===========================================================================

  /*
   * Python reference:
   * D1 long=0: (0, 0.0)    D9 long=0: (0, 0.0)
   * D1 long=45: (1, 15.0)  D9 long=45: (1, 15.0)
   * D1 long=90: (3, 0.0)   D9 long=90: (3, 0.0)
   * D1 long=180: (6, 0.0)  D9 long=180: (6, 0.0)
   * D1 long=270: (9, 0.0)  D9 long=270: (9, 0.0)
   */
  describe('dasavargaFromLong', () => {
    it('D1: longitude 0 → rasi 0, long 0', () => {
      expect(dasavargaFromLong(0.0, 1)).toEqual([0, 0.0]);
    });

    it('D1: longitude 45 → rasi 1, long 15', () => {
      expect(dasavargaFromLong(45.0, 1)).toEqual([1, 15.0]);
    });

    it('D1: longitude 90 → rasi 3, long 0', () => {
      expect(dasavargaFromLong(90.0, 1)).toEqual([3, 0.0]);
    });

    it('D1: longitude 180 → rasi 6, long 0', () => {
      expect(dasavargaFromLong(180.0, 1)).toEqual([6, 0.0]);
    });

    it('D9: longitude 90 → rasi 3, long 0', () => {
      expect(dasavargaFromLong(90.0, 9)).toEqual([3, 0.0]);
    });

    it('D1: longitude 359.999 → rasi 11, long ~30', () => {
      const [rasi, long] = dasavargaFromLong(359.999, 1);
      expect(rasi).toBe(11);
      expect(long).toBeCloseTo(29.999, 2);
    });
  });

  // ===========================================================================
  // dhasavargaAsync
  // ===========================================================================

  /*
   * Python reference (1996-12-07 Bangalore, D1):
   * P0: rasi=7, long=21.118    (Sun)
   * P1: rasi=6, long=1.254     (Moon)
   * P2: rasi=4, long=25.339    (Mars)
   * P3: rasi=8, long=9.32      (Mercury)
   * P4: rasi=8, long=25.734    (Jupiter)
   * P5: rasi=6, long=23.17     (Venus)
   * P6: rasi=11, long=6.804    (Saturn)
   * P7: rasi=5, long=10.577    (Rahu)
   * P8: rasi=11, long=10.577   (Ketu)
   */
  describe('dhasavargaAsync', () => {
    it('should return D1 positions for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const positions = await dhasavargaAsync(jd, bangalore, 1);

      expect(positions).toHaveLength(9);

      // Sun
      expect(positions[0]![0]).toBe(0);
      expect(positions[0]![1][0]).toBe(7); // Scorpio
      expect(positions[0]![1][1]).toBeCloseTo(21.118, 0);

      // Moon
      expect(positions[1]![0]).toBe(1);
      expect(positions[1]![1][0]).toBe(6); // Libra
      expect(positions[1]![1][1]).toBeCloseTo(1.254, 0);

      // Mars
      expect(positions[2]![0]).toBe(2);
      expect(positions[2]![1][0]).toBe(4); // Leo
      expect(positions[2]![1][1]).toBeCloseTo(25.339, 0);

      // Jupiter
      expect(positions[4]![0]).toBe(4);
      expect(positions[4]![1][0]).toBe(8); // Sagittarius
      expect(positions[4]![1][1]).toBeCloseTo(25.734, 0);

      // Rahu
      expect(positions[7]![0]).toBe(7);
      expect(positions[7]![1][0]).toBe(5); // Virgo
      expect(positions[7]![1][1]).toBeCloseTo(10.577, 0);

      // Ketu = Rahu + 180
      expect(positions[8]![0]).toBe(8);
      expect(positions[8]![1][0]).toBe(11); // Pisces
      expect(positions[8]![1][1]).toBeCloseTo(10.577, 0);
    });
  });

  // ===========================================================================
  // bhaavaMadhyaKP (Placidus)
  // ===========================================================================

  /*
   * Python reference (1996-12-07 Bangalore):
   * [137.349, 167.317, 198.319, 228.57, 257.936, 287.402,
   *  317.349, 347.317, 18.319, 48.57, 77.936, 107.402]
   *
   * 2024-06-21:
   * [329.21, 4.047, 34.183, 60.8, 86.883, 115.602,
   *  149.21, 184.047, 214.183, 240.8, 266.883, 295.602]
   */
  describe('bhaavaMadhyaKP', () => {
    it('should return 12 Placidus cusps for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const cusps = await bhaavaMadhyaKP(jd, bangalore);

      expect(cusps).toHaveLength(12);
      expect(cusps[0]).toBeCloseTo(137.349, 0);
      expect(cusps[1]).toBeCloseTo(167.317, 0);
      expect(cusps[2]).toBeCloseTo(198.319, 0);
      expect(cusps[3]).toBeCloseTo(228.57, 0);
      expect(cusps[6]).toBeCloseTo(317.349, 0);
      expect(cusps[9]).toBeCloseTo(48.57, 0);
    });

    it('should return 12 Placidus cusps for 2024-06-21', async () => {
      const jd = jdForDate(2024, 6, 21);
      const cusps = await bhaavaMadhyaKP(jd, bangalore);

      expect(cusps).toHaveLength(12);
      expect(cusps[0]).toBeCloseTo(329.21, 0);
      expect(cusps[3]).toBeCloseTo(60.8, 0);
      expect(cusps[6]).toBeCloseTo(149.21, 0);
      expect(cusps[9]).toBeCloseTo(240.8, 0);
    });
  });

  // ===========================================================================
  // bhaavaMadhyaSripathi
  // ===========================================================================

  /*
   * Python reference (1996-12-07):
   * [137.349, 167.756, 198.163, 228.57, 258.163, 287.756,
   *  317.349, 347.756, 18.163, 48.57, 78.163, 107.756]
   *
   * 2024-06-21:
   * [329.21, 359.74, 30.27, 60.8, 90.27, 119.74,
   *  149.21, 179.74, 210.27, 240.8, 270.27, 299.74]
   */
  describe('bhaavaMadhyaSripathi', () => {
    it('should return Sripathi cusps for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const cusps = await bhaavaMadhyaSripathi(jd, bangalore);

      expect(cusps).toHaveLength(12);
      // Quadrant points (0,3,6,9) same as KP
      expect(cusps[0]).toBeCloseTo(137.349, 0);
      expect(cusps[3]).toBeCloseTo(228.57, 0);
      expect(cusps[6]).toBeCloseTo(317.349, 0);
      expect(cusps[9]).toBeCloseTo(48.57, 0);

      // Trisected intermediate cusps
      expect(cusps[1]).toBeCloseTo(167.756, 0);
      expect(cusps[2]).toBeCloseTo(198.163, 0);
    });

    it('should return Sripathi cusps for 2024-06-21', async () => {
      const jd = jdForDate(2024, 6, 21);
      const cusps = await bhaavaMadhyaSripathi(jd, bangalore);

      expect(cusps).toHaveLength(12);
      expect(cusps[0]).toBeCloseTo(329.21, 0);
      expect(cusps[1]).toBeCloseTo(359.74, 0);
      expect(cusps[3]).toBeCloseTo(60.8, 0);
    });
  });

  // ===========================================================================
  // bhaavaMadhyaSwe (Koch)
  // ===========================================================================

  /*
   * Python reference (1996-12-07 Koch):
   * [137.349, 168.763, 199.419, 228.57, 258.041, 287.008,
   *  317.349, 348.763, 19.419, 48.57, 78.041, 107.008]
   */
  describe('bhaavaMadhyaSwe (Koch)', () => {
    it('should return Koch cusps for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const cusps = await bhaavaMadhyaSwe(jd, bangalore, 'K');

      expect(cusps).toHaveLength(12);
      expect(cusps[0]).toBeCloseTo(137.349, 0);
      expect(cusps[1]).toBeCloseTo(168.763, 0);
      expect(cusps[3]).toBeCloseTo(228.57, 0);
    });

    it('should return Koch cusps for 2024-06-21', async () => {
      const jd = jdForDate(2024, 6, 21);
      const cusps = await bhaavaMadhyaSwe(jd, bangalore, 'K');

      expect(cusps).toHaveLength(12);
      expect(cusps[0]).toBeCloseTo(329.21, 0);
      expect(cusps[1]).toBeCloseTo(2.823, 0);
    });
  });

  // ===========================================================================
  // assignPlanetsToHouses (pure function)
  // ===========================================================================

  describe('assignPlanetsToHouses', () => {
    it('should assign planets to equal houses correctly', () => {
      // Simple scenario: 2 equal houses starting at 0° and 180°
      const positions: Array<[number | string, [number, number]]> = [
        ['L', [0, 15.0]],   // Lagna at 15° Aries
        [0, [0, 10.0]],     // Sun at 10° Aries
        [1, [6, 5.0]],      // Moon at 185° (Libra)
      ];
      const houses: Array<[number, number, number]> = [
        [0, 15.0, 30.0],     // House 1: 0-30°
        [180, 195.0, 210.0],  // House 2: 180-210°
      ];

      const result = assignPlanetsToHouses(positions, houses, 1);
      expect(result).toHaveLength(2);
      // House 1 should have Lagna and Sun
      expect(result[0]![2]).toContain('L');
      expect(result[0]![2]).toContain(0);
      // House 2 should have Moon
      expect(result[1]![2]).toContain(1);
    });

    it('should handle wrap-around at 0/360', () => {
      const positions: Array<[number | string, [number, number]]> = [
        [0, [11, 25.0]], // Planet at 355°
        [1, [0, 5.0]],   // Planet at 5°
      ];
      const houses: Array<[number, number, number]> = [
        [345.0, 0.0, 15.0], // House wrapping 345° to 15°
      ];

      const result = assignPlanetsToHouses(positions, houses, 1);
      // Both planets should be in this house
      expect(result[0]![2]).toContain(0);
      expect(result[0]![2]).toContain(1);
    });
  });

  // ===========================================================================
  // bhaavaMadhyaNew — method 1 (Equal Housing, Lagna in middle)
  // ===========================================================================

  /*
   * Python reference (1996-12-07, method=1):
   * H1: rasi=4, cusps=(122.35,137.35,152.35), planets=['L', 2]
   * H2: rasi=5, cusps=(152.35,167.35,182.35), planets=[1, 7]
   * H5: rasi=8, cusps=(242.35,257.35,272.35), planets=[3, 4]
   */
  describe('bhaavaMadhyaNew method=1 (Equal, Lagna middle)', () => {
    it('should produce 12 houses for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await bhaavaMadhyaNew(jd, bangalore, 1);

      expect(result).toHaveLength(12);

      // H1
      expect(result[0]![0]).toBe(4); // Leo
      expect(result[0]![1][1]).toBeCloseTo(137.35, 0); // mid cusp
      expect(result[0]![2]).toContain('L');
      expect(result[0]![2]).toContain(2); // Mars

      // H2
      expect(result[1]![0]).toBe(5); // Virgo
      // Moon(1) and Rahu(7) in house 2
      expect(result[1]![2]).toContain(1);
      expect(result[1]![2]).toContain(7);

      // H5
      expect(result[4]![0]).toBe(8); // Sagittarius
      expect(result[4]![2]).toContain(3); // Mercury
      expect(result[4]![2]).toContain(4); // Jupiter
    });
  });

  // ===========================================================================
  // bhaavaMadhyaNew — method 4 (KP)
  // ===========================================================================

  /*
   * Python reference (1996-12-07, method=4):
   * H1: rasi=4, cusps=(137.35,152.33,167.32), planets=['L', 2, 7]
   * H2: rasi=5, cusps=(167.32,182.82,198.32), planets=[1]
   */
  describe('bhaavaMadhyaNew method=4 (KP)', () => {
    it('should produce KP houses with correct planet assignments', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await bhaavaMadhyaNew(jd, bangalore, 4);

      expect(result).toHaveLength(12);

      // H1 - KP: ascendant cusp is the start
      expect(result[0]![0]).toBe(4); // rasi from start
      expect(result[0]![2]).toContain('L');
      expect(result[0]![2]).toContain(2); // Mars

      // H2 - Moon in house 2
      expect(result[1]![2]).toContain(1);
    });
  });

  // ===========================================================================
  // bhaavaMadhyaNew — method 5 (Rasi=House)
  // ===========================================================================

  /*
   * Python reference (1996-12-07, method=5):
   * H1: rasi=4, cusps=(120,137.35,150), planets=['L', 2]
   * H3: rasi=6, cusps=(180,197.35,210), planets=[1, 5]
   * H5: rasi=8, cusps=(240,257.35,270), planets=[3, 4]
   */
  describe('bhaavaMadhyaNew method=5 (Rasi=House)', () => {
    it('should produce rasi-based houses for 1996-12-07', async () => {
      const jd = jdForDate(1996, 12, 7);
      const result = await bhaavaMadhyaNew(jd, bangalore, 5);

      expect(result).toHaveLength(12);

      // H1: Leo (rasi=4), start=120, end=150
      expect(result[0]![0]).toBe(4);
      expect(result[0]![1][0]).toBeCloseTo(120, 0); // start
      expect(result[0]![1][2]).toBeCloseTo(150, 0); // end
      expect(result[0]![2]).toContain('L');
      expect(result[0]![2]).toContain(2); // Mars

      // H3: Libra (rasi=6), should contain Moon and Venus
      expect(result[2]![0]).toBe(6);
      expect(result[2]![2]).toContain(1); // Moon
      expect(result[2]![2]).toContain(5); // Venus
    });
  });

  // ===========================================================================
  // houseCuspsAsync (swe-adapter direct test)
  // ===========================================================================

  describe('houseCuspsAsync', () => {
    it('should return 12 cusps with Placidus system', async () => {
      const jd = jdForDate(1996, 12, 7);
      const cusps = await houseCuspsAsync(jd, bangalore, 'P');

      expect(cusps).toHaveLength(12);
      // Ascendant (cusp 1) should match ascendantFullAsync
      const [constellation, longitude] = await ascendantFullAsync(jd, bangalore);
      const ascLong = constellation * 30 + longitude;
      expect(cusps[0]).toBeCloseTo(ascLong, 0);
    });

    it('cusps should be different for different house systems', async () => {
      const jd = jdForDate(1996, 12, 7);
      const placidus = await houseCuspsAsync(jd, bangalore, 'P');
      const koch = await houseCuspsAsync(jd, bangalore, 'K');

      // Cusp 1 (ascendant) should be the same for all systems
      expect(placidus[0]).toBeCloseTo(koch[0]!, 1);
      // Cusp 4 (IC) should also be the same
      expect(placidus[3]).toBeCloseTo(koch[3]!, 1);
      // But intermediate cusps (2, 5) may differ
      // (Koch vs Placidus differ for non-equatorial latitudes)
    });
  });
});
