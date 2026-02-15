/**
 * Tests for graha dasha systems
 * Includes structural tests and Python-parity value checks
 */

import { JUPITER, KETU, MARS, MERCURY, MOON, RAHU, SATURN, SUN, VENUS } from '@core/constants';
import {
  ashtottariMahadasha,
  getAshtottariAdhipati,
  getAshtottariDashaBhukti,
  getNextAshtottariAdhipati,
} from '@core/dhasa/graha/ashtottari';
import { getPanchottariDashaBhukti } from '@core/dhasa/graha/panchottari';
import { getShastihayaniDashaBhukti } from '@core/dhasa/graha/shastihayani';
import { getShodasottariDashaBhukti } from '@core/dhasa/graha/shodasottari';
import { getVimsottariDashaBhukti } from '@core/dhasa/graha/vimsottari';
import {
  getNextYoginiLord,
  getYoginiDashaBhukti,
  getYoginiDhasaLord
} from '@core/dhasa/graha/yogini';
import type { Place } from '@core/types';
import { gregorianToJulianDay } from '@core/utils/julian';
import { describe, expect, it } from 'vitest';

// Test place
const bangalore: Place = {
  name: 'Bangalore',
  latitude: 12.972,
  longitude: 77.594,
  timezone: 5.5
};

describe('Ashtottari Dasha System', () => {
  describe('getAshtottariAdhipati', () => {
    it('should return lord for nakshatra in valid range', () => {
      // Nakshatra 7 (Punarvasu) should be in Sun's range
      const result = getAshtottariAdhipati(7);
      expect(result).toBeDefined();
      expect(result![0]).toBe(SUN);
    });
  });

  describe('getNextAshtottariAdhipati', () => {
    it('should return next lord in sequence', () => {
      const next = getNextAshtottariAdhipati(SUN, 1);
      expect(next).toBe(MOON);
    });
  });

  describe('ashtottariMahadasha', () => {
    it('should return 8 mahadashas', () => {
      const jd = 2451545.0;
      const dashas = ashtottariMahadasha(jd, bangalore);
      
      expect(dashas.size).toBe(8);
    });

    it('should have increasing start dates', () => {
      const jd = 2451545.0;
      const dashas = ashtottariMahadasha(jd, bangalore);
      const dates = Array.from(dashas.values());
      
      for (let i = 1; i < dates.length; i++) {
        expect(dates[i]).toBeGreaterThan(dates[i - 1]!);
      }
    });
  });

  describe('getAshtottariDashaBhukti', () => {
    it('should return complete dasha data', () => {
      const jd = 2451545.0;
      const result = getAshtottariDashaBhukti(jd, bangalore);
      
      expect(result.mahadashas.length).toBe(8);
    });

    it('should include bhuktis by default', () => {
      const jd = 2451545.0;
      const result = getAshtottariDashaBhukti(jd, bangalore);
      
      expect(result.bhuktis).toBeDefined();
      expect(result.bhuktis!.length).toBe(64); // 8 * 8
    });
  });
});

describe('Yogini Dasha System', () => {
  describe('getYoginiDhasaLord', () => {
    it('should return lord and duration for nakshatra', () => {
      const [lord, duration] = getYoginiDhasaLord(7, 7); // Same as seed = first lord assigned
      expect(lord).toBe(SUN); // PyJHora assigns Sun (Pingala) to Seed 7 (Punarvasu)
      expect(duration).toBe(2); // Sun has 2 years
    });
  });

  describe('getNextYoginiLord', () => {
    it('should return next lord in sequence', () => {
      expect(getNextYoginiLord(MOON, 1)).toBe(SUN);
      expect(getNextYoginiLord(SUN, 1)).toBe(JUPITER);
    });

    it('should wrap around correctly', () => {
      // Rahu (7) -> Moon going forward
      expect(getNextYoginiLord(7, 1)).toBe(MOON);
    });
  });

  describe('getYoginiDashaBhukti', () => {
    it('should return 24 mahadashas by default (3 cycles)', () => {
      const jd = 2451545.0;
      const result = getYoginiDashaBhukti(jd, bangalore);
      
      expect(result.mahadashas.length).toBe(24); // 8 * 3 cycles
    });

    it('should include yogini names', () => {
      const jd = 2451545.0;
      const result = getYoginiDashaBhukti(jd, bangalore);
      
      const yoginiNames = result.mahadashas.map(d => d.yoginiName);
      expect(yoginiNames).toContain('Mangala');
      expect(yoginiNames).toContain('Pingala');
      expect(yoginiNames).toContain('Siddha');
    });

    it('should include bhuktis by default', () => {
      const jd = 2451545.0;
      const result = getYoginiDashaBhukti(jd, bangalore);
      
      expect(result.bhuktis).toBeDefined();
      expect(result.bhuktis!.length).toBe(192); // 24 * 8
    });

    it('should respect cycles option', () => {
      const jd = 2451545.0;
      const result = getYoginiDashaBhukti(jd, bangalore, { cycles: 1, includeBhuktis: false });
      
      expect(result.mahadashas.length).toBe(8); // 1 cycle
    });
  });
});

describe('Shastihayani Dasha System (60 years)', () => {
  it('should return 8 mahadashas', () => {
    const jd = 2451545.0;
    const result = getShastihayaniDashaBhukti(jd, bangalore, { includeBhuktis: false });

    expect(result.mahadashas.length).toBe(8);
  });

  it('should have total duration of 60 years', () => {
    const jd = 2451545.0;
    const result = getShastihayaniDashaBhukti(jd, bangalore, { includeBhuktis: false });

    const totalYears = result.mahadashas.reduce((sum: number, d: { durationYears: number }) => sum + d.durationYears, 0);
    expect(totalYears).toBe(60);
  });
});

describe('Shodasottari Dasha System (116 years)', () => {
  it('should return 8 mahadashas', () => {
    const jd = 2451545.0;
    const result = getShodasottariDashaBhukti(jd, bangalore, { includeBhuktis: false });

    expect(result.mahadashas.length).toBe(8);
  });

  it('should have total duration of 116 years', () => {
    const jd = 2451545.0;
    const result = getShodasottariDashaBhukti(jd, bangalore, { includeBhuktis: false });

    const totalYears = result.mahadashas.reduce((sum: number, d: { durationYears: number }) => sum + d.durationYears, 0);
    expect(totalYears).toBe(116);
  });
});

describe('Panchottari Dasha System (105 years)', () => {
  it('should return 7 mahadashas', () => {
    const jd = 2451545.0;
    const result = getPanchottariDashaBhukti(jd, bangalore, { includeBhuktis: false });

    expect(result.mahadashas.length).toBe(7);
  });

  it('should have total duration of 105 years', () => {
    const jd = 2451545.0;
    const result = getPanchottariDashaBhukti(jd, bangalore, { includeBhuktis: false });

    const totalYears = result.mahadashas.reduce((sum: number, d: { durationYears: number }) => sum + d.durationYears, 0);
    expect(totalYears).toBe(105);
  });
});

describe('Dwadasottari Dasha System (112 years)', () => {
  it('should return 8 mahadashas', async () => {
    const { getDwadasottariDashaBhukti } = await import('@core/dhasa/graha/dwadasottari');
    const jd = 2451545.0;
    const result = getDwadasottariDashaBhukti(jd, bangalore, { includeBhuktis: false });
    expect(result.mahadashas.length).toBe(8);
  });

  it('should have total duration of 112 years', async () => {
    const { getDwadasottariDashaBhukti } = await import('@core/dhasa/graha/dwadasottari');
    const jd = 2451545.0;
    const result = getDwadasottariDashaBhukti(jd, bangalore, { includeBhuktis: false });
    const totalYears = result.mahadashas.reduce((sum: number, d: { durationYears: number }) => sum + d.durationYears, 0);
    expect(totalYears).toBe(112);
  });
});

describe('Sataabdika Dasha System (100 years)', () => {
  it('should return 7 mahadashas', async () => {
    const { getSataabdikaDashaBhukti } = await import('@core/dhasa/graha/sataabdika');
    const jd = 2451545.0;
    const result = getSataabdikaDashaBhukti(jd, bangalore, { includeBhuktis: false });
    expect(result.mahadashas.length).toBe(7);
  });

  it('should have total duration of 100 years', async () => {
    const { getSataabdikaDashaBhukti } = await import('@core/dhasa/graha/sataabdika');
    const jd = 2451545.0;
    const result = getSataabdikaDashaBhukti(jd, bangalore, { includeBhuktis: false });
    const totalYears = result.mahadashas.reduce((sum: number, d: { durationYears: number }) => sum + d.durationYears, 0);
    expect(totalYears).toBe(100);
  });
});

describe('Dwisatpathi Dasha System (144 years, 2 cycles)', () => {
  it('should return 16 mahadashas by default (2 cycles)', async () => {
    const { getDwisatpathiDashaBhukti } = await import('@core/dhasa/graha/dwisatpathi');
    const jd = 2451545.0;
    const result = getDwisatpathiDashaBhukti(jd, bangalore, { includeBhuktis: false });
    expect(result.mahadashas.length).toBe(16); // 8 lords × 2 cycles
  });

  it('should have total duration of 144 years', async () => {
    const { getDwisatpathiDashaBhukti } = await import('@core/dhasa/graha/dwisatpathi');
    const jd = 2451545.0;
    const result = getDwisatpathiDashaBhukti(jd, bangalore, { includeBhuktis: false });
    const totalYears = result.mahadashas.reduce((sum: number, d: { durationYears: number }) => sum + d.durationYears, 0);
    expect(totalYears).toBe(144);
  });
});

describe('Chaturaseethi Sama Dasha System (84 years)', () => {
  it('should return 7 mahadashas', async () => {
    const { getChaturaseethiDashaBhukti } = await import('@core/dhasa/graha/chaturaseethi');
    const jd = 2451545.0;
    const result = getChaturaseethiDashaBhukti(jd, bangalore, { includeBhuktis: false });
    expect(result.mahadashas.length).toBe(7);
  });

  it('should have total duration of 84 years', async () => {
    const { getChaturaseethiDashaBhukti } = await import('@core/dhasa/graha/chaturaseethi');
    const jd = 2451545.0;
    const result = getChaturaseethiDashaBhukti(jd, bangalore, { includeBhuktis: false });
    const totalYears = result.mahadashas.reduce((sum: number, d: { durationYears: number }) => sum + d.durationYears, 0);
    expect(totalYears).toBe(84);
  });
});

describe('Naisargika Dasha System (132 years)', () => {
  it('should return 8 mahadashas (7 planets + Lagna)', async () => {
    const { getNaisargikaDashaBhukti } = await import('@core/dhasa/graha/naisargika');
    const jd = 2451545.0;
    const result = getNaisargikaDashaBhukti(jd, bangalore, { includeBhuktis: false });
    expect(result.mahadashas.length).toBe(8);
  });

  it('should have total duration of 132 years', async () => {
    const { getNaisargikaDashaBhukti } = await import('@core/dhasa/graha/naisargika');
    const jd = 2451545.0;
    const result = getNaisargikaDashaBhukti(jd, bangalore, { includeBhuktis: false });
    const totalYears = result.mahadashas.reduce((sum: number, d: { durationYears: number }) => sum + d.durationYears, 0);
    expect(totalYears).toBe(132);
  });
});

describe('Tara Dasha System (120 years)', () => {
  it('should return 9 mahadashas', async () => {
    const { getTaraDashaBhukti } = await import('@core/dhasa/graha/tara');
    const jd = 2451545.0;
    const result = getTaraDashaBhukti(jd, bangalore, { includeBhuktis: false });
    expect(result.mahadashas.length).toBe(9);
  });

  it('should have total duration of 120 years', async () => {
    const { getTaraDashaBhukti } = await import('@core/dhasa/graha/tara');
    const jd = 2451545.0;
    const result = getTaraDashaBhukti(jd, bangalore, { includeBhuktis: false });
    const totalYears = result.mahadashas.reduce((sum: number, d: { durationYears: number }) => sum + d.durationYears, 0);
    expect(totalYears).toBe(120);
  });
});

describe('Shattrimsa Sama Dasha System (108 years, 3 cycles)', () => {
  it('should return 24 mahadashas (8 × 3 cycles)', async () => {
    const { getShattrimsaDashaBhukti } = await import('@core/dhasa/graha/shattrimsa');
    const jd = 2451545.0;
    const result = getShattrimsaDashaBhukti(jd, bangalore, { includeBhuktis: false });
    expect(result.mahadashas.length).toBe(24);
  });

  it('should have total duration of 108 years', async () => {
    const { getShattrimsaDashaBhukti } = await import('@core/dhasa/graha/shattrimsa');
    const jd = 2451545.0;
    const result = getShattrimsaDashaBhukti(jd, bangalore, { includeBhuktis: false });
    const totalYears = result.mahadashas.reduce((sum: number, d: { durationYears: number }) => sum + d.durationYears, 0);
    expect(totalYears).toBe(108);
  });
});

describe('Saptharishi Nakshatra Dasha System (100 years)', () => {
  it('should return 10 mahadashas', async () => {
    const { getSaptharishiDashaBhukti } = await import('@core/dhasa/graha/saptharishi');
    const jd = 2451545.0;
    const result = getSaptharishiDashaBhukti(jd, bangalore, { includeBhuktis: false });
    expect(result.mahadashas.length).toBe(10);
  });

  it('should have total duration of 100 years', async () => {
    const { getSaptharishiDashaBhukti } = await import('@core/dhasa/graha/saptharishi');
    const jd = 2451545.0;
    const result = getSaptharishiDashaBhukti(jd, bangalore, { includeBhuktis: false });
    const totalYears = result.mahadashas.reduce((sum: number, d: { durationYears: number }) => sum + d.durationYears, 0);
    expect(totalYears).toBe(100);
  });

  it('should use nakshatra names as lords', async () => {
    const { getSaptharishiDashaBhukti } = await import('@core/dhasa/graha/saptharishi');
    const jd = 2451545.0;
    const result = getSaptharishiDashaBhukti(jd, bangalore, { includeBhuktis: false });
    // Lords should be nakshatra names
    expect(result.mahadashas[0]?.lordName.length).toBeGreaterThan(0);
  });
});

// ============================================================================
// DETAILED GRAHA DHASA VALIDATION TESTS
// ============================================================================

describe('Graha Dhasa - Increasing Start Dates', () => {
  const jd = 2451545.0;

  it('Dwadasottari should have increasing start JDs', async () => {
    const { getDwadasottariDashaBhukti } = await import('@core/dhasa/graha/dwadasottari');
    const result = getDwadasottariDashaBhukti(jd, bangalore, { includeBhuktis: false });
    for (let i = 1; i < result.mahadashas.length; i++) {
      expect(result.mahadashas[i]!.startJd).toBeGreaterThan(result.mahadashas[i - 1]!.startJd);
    }
  });

  it('Sataabdika should have increasing start JDs', async () => {
    const { getSataabdikaDashaBhukti } = await import('@core/dhasa/graha/sataabdika');
    const result = getSataabdikaDashaBhukti(jd, bangalore, { includeBhuktis: false });
    for (let i = 1; i < result.mahadashas.length; i++) {
      expect(result.mahadashas[i]!.startJd).toBeGreaterThan(result.mahadashas[i - 1]!.startJd);
    }
  });

  it('Dwisatpathi should have increasing start JDs', async () => {
    const { getDwisatpathiDashaBhukti } = await import('@core/dhasa/graha/dwisatpathi');
    const result = getDwisatpathiDashaBhukti(jd, bangalore, { includeBhuktis: false });
    for (let i = 1; i < result.mahadashas.length; i++) {
      expect(result.mahadashas[i]!.startJd).toBeGreaterThan(result.mahadashas[i - 1]!.startJd);
    }
  });

  it('Chaturaseethi should have increasing start JDs', async () => {
    const { getChaturaseethiDashaBhukti } = await import('@core/dhasa/graha/chaturaseethi');
    const result = getChaturaseethiDashaBhukti(jd, bangalore, { includeBhuktis: false });
    for (let i = 1; i < result.mahadashas.length; i++) {
      expect(result.mahadashas[i]!.startJd).toBeGreaterThan(result.mahadashas[i - 1]!.startJd);
    }
  });

  it('Naisargika should have increasing start JDs', async () => {
    const { getNaisargikaDashaBhukti } = await import('@core/dhasa/graha/naisargika');
    const result = getNaisargikaDashaBhukti(jd, bangalore, { includeBhuktis: false });
    for (let i = 1; i < result.mahadashas.length; i++) {
      expect(result.mahadashas[i]!.startJd).toBeGreaterThan(result.mahadashas[i - 1]!.startJd);
    }
  });

  it('Tara should have increasing start JDs', async () => {
    const { getTaraDashaBhukti } = await import('@core/dhasa/graha/tara');
    const result = getTaraDashaBhukti(jd, bangalore, { includeBhuktis: false });
    for (let i = 1; i < result.mahadashas.length; i++) {
      expect(result.mahadashas[i]!.startJd).toBeGreaterThan(result.mahadashas[i - 1]!.startJd);
    }
  });

  it('Shattrimsa should have increasing start JDs', async () => {
    const { getShattrimsaDashaBhukti } = await import('@core/dhasa/graha/shattrimsa');
    const result = getShattrimsaDashaBhukti(jd, bangalore, { includeBhuktis: false });
    for (let i = 1; i < result.mahadashas.length; i++) {
      expect(result.mahadashas[i]!.startJd).toBeGreaterThan(result.mahadashas[i - 1]!.startJd);
    }
  });
});

describe('Graha Dhasa - Bhukti Validation', () => {
  const jd = 2451545.0;

  it('Dwadasottari should produce 64 bhuktis (8x8)', async () => {
    const { getDwadasottariDashaBhukti } = await import('@core/dhasa/graha/dwadasottari');
    const result = getDwadasottariDashaBhukti(jd, bangalore, { includeBhuktis: true });
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBe(64);
  });

  it('Chaturaseethi should produce 49 bhuktis (7x7)', async () => {
    const { getChaturaseethiDashaBhukti } = await import('@core/dhasa/graha/chaturaseethi');
    const result = getChaturaseethiDashaBhukti(jd, bangalore, { includeBhuktis: true });
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBe(49);
  });

  it('Tara should produce 81 bhuktis (9x9)', async () => {
    const { getTaraDashaBhukti } = await import('@core/dhasa/graha/tara');
    const result = getTaraDashaBhukti(jd, bangalore, { includeBhuktis: true });
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBe(81);
  });

  it('Naisargika should produce bhuktis with valid structure', async () => {
    const { getNaisargikaDashaBhukti } = await import('@core/dhasa/graha/naisargika');
    const result = getNaisargikaDashaBhukti(jd, bangalore, { includeBhuktis: true });
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBeGreaterThan(0);
    const first = result.bhuktis![0]!;
    expect(first.dashaLord).toBeDefined();
    expect(first.bhuktiLord).toBeDefined();
    expect(first.startJd).toBeDefined();
    expect(first.durationYears).toBeGreaterThan(0);
  });

  it('Sataabdika should produce 49 bhuktis (7x7)', async () => {
    const { getSataabdikaDashaBhukti } = await import('@core/dhasa/graha/sataabdika');
    const result = getSataabdikaDashaBhukti(jd, bangalore, { includeBhuktis: true });
    expect(result.bhuktis).toBeDefined();
    expect(result.bhuktis!.length).toBe(49);
  });
});

describe('Graha Dhasa - Lord Sequence Validation', () => {
  const jd = 2451545.0;

  it('Chaturaseethi should use only lords 0-6 (Sun to Saturn)', async () => {
    const { getChaturaseethiDashaBhukti } = await import('@core/dhasa/graha/chaturaseethi');
    const result = getChaturaseethiDashaBhukti(jd, bangalore, { includeBhuktis: false });
    for (const d of result.mahadashas) {
      expect(d.lord).toBeGreaterThanOrEqual(0);
      expect(d.lord).toBeLessThanOrEqual(6);
    }
  });

  it('Sataabdika should use only lords 0-6 (Sun to Saturn)', async () => {
    const { getSataabdikaDashaBhukti } = await import('@core/dhasa/graha/sataabdika');
    const result = getSataabdikaDashaBhukti(jd, bangalore, { includeBhuktis: false });
    for (const d of result.mahadashas) {
      expect(d.lord).toBeGreaterThanOrEqual(0);
      expect(d.lord).toBeLessThanOrEqual(6);
    }
  });

  it('Panchottari should use only lords 0-6 (Sun to Saturn)', async () => {
    const result = getPanchottariDashaBhukti(jd, bangalore, { includeBhuktis: false });
    for (const d of result.mahadashas) {
      expect(d.lord).toBeGreaterThanOrEqual(0);
      expect(d.lord).toBeLessThanOrEqual(6);
    }
  });

  it('Tara should use lords 0-8 (Sun to Ketu)', async () => {
    const { getTaraDashaBhukti } = await import('@core/dhasa/graha/tara');
    const result = getTaraDashaBhukti(jd, bangalore, { includeBhuktis: false });
    for (const d of result.mahadashas) {
      expect(d.lord).toBeGreaterThanOrEqual(0);
      expect(d.lord).toBeLessThanOrEqual(8);
    }
  });

  it('Naisargika should have fixed lord order', async () => {
    const { getNaisargikaDashaBhukti } = await import('@core/dhasa/graha/naisargika');
    const result = getNaisargikaDashaBhukti(jd, bangalore, { includeBhuktis: false });
    // Naisargika dasha has a fixed lord order: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Lagna
    const lords = result.mahadashas.map((d: { lord: number }) => d.lord);
    expect(new Set(lords).size).toBe(8); // 8 unique lords (7 planets + lagna)
  });
});

// ============================================================================
// PYTHON-PARITY VALUE TESTS
// Tests using the standard Chennai 1996-12-07 10:34 chart
// Expected values computed from Python PyJHora
// ============================================================================

describe('Python Parity - Chennai 1996-12-07 10:34', () => {
  const chennai: Place = {
    name: 'Chennai',
    latitude: 13.0878,
    longitude: 80.2785,
    timezone: 5.5
  };
  const testJd = gregorianToJulianDay(
    { year: 1996, month: 12, day: 7 },
    { hour: 10, minute: 34, second: 0 }
  );

  describe('Naisargika Dasha - Fixed Lord Sequence', () => {
    it('should always have fixed lord order: Moon, Mars, Mercury, Venus, Jupiter, Sun, Saturn, Lagna', async () => {
      const { getNaisargikaDashaBhukti } = await import('@core/dhasa/graha/naisargika');
      const result = getNaisargikaDashaBhukti(testJd, chennai, { includeBhuktis: false });

      // Python: Moon(1y), Mars(2y), Mercury(9y), Venus(20y), Jupiter(18y), Sun(20y), Saturn(50y), Lagna(12y)
      expect(result.mahadashas.length).toBe(8);
      expect(result.mahadashas[0]!.lord).toBe(MOON);
      expect(result.mahadashas[0]!.durationYears).toBe(1);
      expect(result.mahadashas[1]!.lord).toBe(MARS);
      expect(result.mahadashas[1]!.durationYears).toBe(2);
      expect(result.mahadashas[2]!.lord).toBe(MERCURY);
      expect(result.mahadashas[2]!.durationYears).toBe(9);
      expect(result.mahadashas[3]!.lord).toBe(VENUS);
      expect(result.mahadashas[3]!.durationYears).toBe(20);
      expect(result.mahadashas[4]!.lord).toBe(JUPITER);
      expect(result.mahadashas[4]!.durationYears).toBe(18);
      expect(result.mahadashas[5]!.lord).toBe(SUN);
      expect(result.mahadashas[5]!.durationYears).toBe(20);
      expect(result.mahadashas[6]!.lord).toBe(SATURN);
      expect(result.mahadashas[6]!.durationYears).toBe(50);
      expect(result.mahadashas[7]!.lord).toBe('L');
      expect(result.mahadashas[7]!.durationYears).toBe(12);
    });

    it('should start from birth time (JD)', async () => {
      const { getNaisargikaDashaBhukti } = await import('@core/dhasa/graha/naisargika');
      const result = getNaisargikaDashaBhukti(testJd, chennai, { includeBhuktis: false });

      // Naisargika starts from birth itself
      expect(result.mahadashas[0]!.startJd).toBeCloseTo(testJd, 1);
    });
  });

  describe('Saptharishi Nakshatra Dasha - Nakshatra-based Lords', () => {
    it('should start from Moon nakshatra going backwards', async () => {
      const { getSaptharishiDashaBhukti } = await import('@core/dhasa/graha/saptharishi');
      const result = getSaptharishiDashaBhukti(testJd, chennai, { includeBhuktis: false });

      // Python: first lord is nakshatra 14 (Chitra), going backwards
      expect(result.mahadashas.length).toBe(10);
      expect(result.mahadashas[0]!.lord).toBe(14);
      expect(result.mahadashas[1]!.lord).toBe(13);
      expect(result.mahadashas[2]!.lord).toBe(12);

      // All durations should be 10 years
      for (const d of result.mahadashas) {
        expect(d.durationYears).toBe(10);
      }
    });
  });

  describe('Dwadasottari Dasha - First Lord and Sequence', () => {
    it('should start with Rahu and follow correct sequence', async () => {
      const { getDwadasottariDashaBhukti } = await import('@core/dhasa/graha/dwadasottari');
      const result = getDwadasottariDashaBhukti(testJd, chennai, { includeBhuktis: false });

      // Python: Rahu(15), Mars(17), Saturn(19), Moon(21), Sun(7), Jupiter(9), Ketu(11), Mercury(13)
      expect(result.mahadashas.length).toBe(8);
      expect(result.mahadashas[0]!.lord).toBe(RAHU);
      expect(result.mahadashas[0]!.durationYears).toBe(15);
      expect(result.mahadashas[1]!.lord).toBe(MARS);
      expect(result.mahadashas[1]!.durationYears).toBe(17);
      expect(result.mahadashas[2]!.lord).toBe(SATURN);
      expect(result.mahadashas[2]!.durationYears).toBe(19);
      expect(result.mahadashas[3]!.lord).toBe(MOON);
      expect(result.mahadashas[3]!.durationYears).toBe(21);
      expect(result.mahadashas[4]!.lord).toBe(SUN);
      expect(result.mahadashas[4]!.durationYears).toBe(7);
      expect(result.mahadashas[5]!.lord).toBe(JUPITER);
      expect(result.mahadashas[5]!.durationYears).toBe(9);
      expect(result.mahadashas[6]!.lord).toBe(KETU);
      expect(result.mahadashas[6]!.durationYears).toBe(11);
      expect(result.mahadashas[7]!.lord).toBe(MERCURY);
      expect(result.mahadashas[7]!.durationYears).toBe(13);

      // Total should be 112 years
      const total = result.mahadashas.reduce((s, d) => s + d.durationYears, 0);
      expect(total).toBe(112);
    });
  });

  describe('Dwisatpathi Dasha - First Lord and Total Duration', () => {
    it('should start with Rahu with all periods 9 years each', async () => {
      const { getDwisatpathiDashaBhukti } = await import('@core/dhasa/graha/dwisatpathi');
      const result = getDwisatpathiDashaBhukti(testJd, chennai, { includeBhuktis: false });

      // Python: Rahu(9), Sun(9), Moon(9), Mars(9), Mercury(9), Jupiter(9), Venus(9), Saturn(9) x2
      expect(result.mahadashas.length).toBe(16); // 2 cycles
      expect(result.mahadashas[0]!.lord).toBe(RAHU);
      expect(result.mahadashas[1]!.lord).toBe(SUN);
      expect(result.mahadashas[2]!.lord).toBe(MOON);
      expect(result.mahadashas[3]!.lord).toBe(MARS);

      // All periods should be 9 years
      for (const d of result.mahadashas) {
        expect(d.durationYears).toBe(9);
      }

      // Total = 144 years (2 cycles of 72)
      const total = result.mahadashas.reduce((s, d) => s + d.durationYears, 0);
      expect(total).toBe(144);
    });
  });

  describe('Shattrimsa Sama Dasha - First Lord and Cycle Pattern', () => {
    it('should start with Mercury and follow correct sequence across 3 cycles', async () => {
      const { getShattrimsaDashaBhukti } = await import('@core/dhasa/graha/shattrimsa');
      const result = getShattrimsaDashaBhukti(testJd, chennai, { includeBhuktis: false });

      // Python: Mercury(5), Saturn(6), Venus(7), Rahu(8), Moon(1), Sun(2), Jupiter(3), Mars(4) x3
      expect(result.mahadashas.length).toBe(24); // 3 cycles of 8
      expect(result.mahadashas[0]!.lord).toBe(MERCURY);
      expect(result.mahadashas[0]!.durationYears).toBe(5);
      expect(result.mahadashas[1]!.lord).toBe(SATURN);
      expect(result.mahadashas[1]!.durationYears).toBe(6);
      expect(result.mahadashas[2]!.lord).toBe(VENUS);
      expect(result.mahadashas[2]!.durationYears).toBe(7);
      expect(result.mahadashas[3]!.lord).toBe(RAHU);
      expect(result.mahadashas[3]!.durationYears).toBe(8);

      // Second cycle should repeat
      expect(result.mahadashas[8]!.lord).toBe(MERCURY);
      expect(result.mahadashas[8]!.durationYears).toBe(5);

      // Total = 108 years (3 cycles of 36)
      const total = result.mahadashas.reduce((s, d) => s + d.durationYears, 0);
      expect(total).toBe(108);
    });
  });

  describe('Vimsottari Dasha - First Lord Check', () => {
    it('should start with Rahu as first mahadasha lord', () => {
      const result = getVimsottariDashaBhukti(testJd, chennai, { includeBhuktis: false });

      // Python: first lord is Rahu(7) = 18y, Jupiter(16), Saturn(19), ...
      expect(result.mahadashas.length).toBe(9);
      expect(result.mahadashas[0]!.lord).toBe(RAHU);
      expect(result.mahadashas[0]!.durationYears).toBe(18);
      expect(result.mahadashas[1]!.lord).toBe(JUPITER);
      expect(result.mahadashas[1]!.durationYears).toBe(16);
      expect(result.mahadashas[2]!.lord).toBe(SATURN);
      expect(result.mahadashas[2]!.durationYears).toBe(19);

      // Total = 120 years
      const total = result.mahadashas.reduce((s, d) => s + d.durationYears, 0);
      expect(total).toBe(120);
    });
  });

  describe('Ashtottari Dasha - First Lord Check', () => {
    it('should start with Mars as first mahadasha lord', () => {
      const result = getAshtottariDashaBhukti(testJd, chennai, { includeBhuktis: false });

      // Python: Mars(8), Mercury(17), Saturn(10), Jupiter(19), Rahu(12), Venus(21), Sun(6), Moon(15)
      expect(result.mahadashas.length).toBe(8);
      expect(result.mahadashas[0]!.lord).toBe(MARS);
      expect(result.mahadashas[0]!.durationYears).toBe(8);
      expect(result.mahadashas[1]!.lord).toBe(MERCURY);
      expect(result.mahadashas[1]!.durationYears).toBe(17);

      // Total = 108 years
      const total = result.mahadashas.reduce((s, d) => s + d.durationYears, 0);
      expect(total).toBe(108);
    });
  });

  describe('Yogini Dasha - First Lord Check', () => {
    it('should start with Sun as first mahadasha lord', () => {
      const result = getYoginiDashaBhukti(testJd, chennai, { cycles: 1, includeBhuktis: false });

      // Python: Sun(2), Jupiter(3), Mars(4), Mercury(5), Saturn(6), Venus(7), Rahu(8), Moon(1)
      expect(result.mahadashas.length).toBe(8);
      expect(result.mahadashas[0]!.lord).toBe(SUN);
      expect(result.mahadashas[0]!.durationYears).toBe(2);
      expect(result.mahadashas[1]!.lord).toBe(JUPITER);
      expect(result.mahadashas[1]!.durationYears).toBe(3);
      expect(result.mahadashas[2]!.lord).toBe(MARS);
      expect(result.mahadashas[2]!.durationYears).toBe(4);

      // Total per cycle = 36 years
      const total = result.mahadashas.reduce((s, d) => s + d.durationYears, 0);
      expect(total).toBe(36);
    });
  });

  describe('Shodasottari Dasha - First Lord Check', () => {
    it('should start with Venus as first mahadasha lord', () => {
      const result = getShodasottariDashaBhukti(testJd, chennai, { includeBhuktis: false });

      // Python: Venus(18), Sun(11), Mars(12), Jupiter(13), Saturn(14), Ketu(15), Moon(16), Mercury(17)
      expect(result.mahadashas.length).toBe(8);
      expect(result.mahadashas[0]!.lord).toBe(VENUS);
      expect(result.mahadashas[0]!.durationYears).toBe(18);
      expect(result.mahadashas[1]!.lord).toBe(SUN);
      expect(result.mahadashas[1]!.durationYears).toBe(11);
      expect(result.mahadashas[2]!.lord).toBe(MARS);
      expect(result.mahadashas[2]!.durationYears).toBe(12);

      const total = result.mahadashas.reduce((s, d) => s + d.durationYears, 0);
      expect(total).toBe(116);
    });
  });

  describe('Panchottari Dasha - First Lord Check', () => {
    it('should start with Venus as first mahadasha lord', () => {
      const result = getPanchottariDashaBhukti(testJd, chennai, { includeBhuktis: false });

      // Python: Venus(16), Moon(17), Jupiter(18), Sun(12), Mercury(13), Saturn(14), Mars(15)
      expect(result.mahadashas.length).toBe(7);
      expect(result.mahadashas[0]!.lord).toBe(VENUS);
      expect(result.mahadashas[0]!.durationYears).toBe(16);
      expect(result.mahadashas[1]!.lord).toBe(MOON);
      expect(result.mahadashas[1]!.durationYears).toBe(17);
      expect(result.mahadashas[2]!.lord).toBe(JUPITER);
      expect(result.mahadashas[2]!.durationYears).toBe(18);

      const total = result.mahadashas.reduce((s, d) => s + d.durationYears, 0);
      expect(total).toBe(105);
    });
  });

  describe('Chaturaseethi Sama Dasha - First Lord Check', () => {
    it('should start with Sun as first mahadasha lord', async () => {
      const { getChaturaseethiDashaBhukti } = await import('@core/dhasa/graha/chaturaseethi');
      const result = getChaturaseethiDashaBhukti(testJd, chennai, { includeBhuktis: false });

      // Python: Sun(12), Moon(12), Mars(12), Mercury(12), Jupiter(12), Venus(12), Saturn(12)
      expect(result.mahadashas.length).toBe(7);
      expect(result.mahadashas[0]!.lord).toBe(SUN);
      expect(result.mahadashas[0]!.durationYears).toBe(12);
      expect(result.mahadashas[1]!.lord).toBe(MOON);
      expect(result.mahadashas[2]!.lord).toBe(MARS);
      expect(result.mahadashas[3]!.lord).toBe(MERCURY);
      expect(result.mahadashas[4]!.lord).toBe(JUPITER);
      expect(result.mahadashas[5]!.lord).toBe(VENUS);
      expect(result.mahadashas[6]!.lord).toBe(SATURN);

      const total = result.mahadashas.reduce((s, d) => s + d.durationYears, 0);
      expect(total).toBe(84);
    });
  });

  describe('Sataabdika Dasha - First Lord Check', () => {
    it('should start with Moon as first mahadasha lord', async () => {
      const { getSataabdikaDashaBhukti } = await import('@core/dhasa/graha/sataabdika');
      const result = getSataabdikaDashaBhukti(testJd, chennai, { includeBhuktis: false });

      // Python: Moon(5), Venus(10), Mercury(10), Jupiter(20), Mars(20), Saturn(30), Sun(5)
      expect(result.mahadashas.length).toBe(7);
      expect(result.mahadashas[0]!.lord).toBe(MOON);
      expect(result.mahadashas[0]!.durationYears).toBe(5);
      expect(result.mahadashas[1]!.lord).toBe(VENUS);
      expect(result.mahadashas[1]!.durationYears).toBe(10);
      expect(result.mahadashas[2]!.lord).toBe(MERCURY);
      expect(result.mahadashas[2]!.durationYears).toBe(10);
      expect(result.mahadashas[3]!.lord).toBe(JUPITER);
      expect(result.mahadashas[3]!.durationYears).toBe(20);

      const total = result.mahadashas.reduce((s, d) => s + d.durationYears, 0);
      expect(total).toBe(100);
    });
  });

  describe('Tara Dasha - First Lord Check', () => {
    it('should start with Venus as first mahadasha lord (Sanjay Rath method)', async () => {
      const { getTaraDashaBhukti } = await import('@core/dhasa/graha/tara');
      const result = getTaraDashaBhukti(testJd, chennai, { includeBhuktis: false });

      // Python: Venus(20), Moon(10), Ketu(7), Saturn(19), Jupiter(16), Mercury(17), Rahu(18), Mars(7), Sun(6)
      expect(result.mahadashas.length).toBe(9);
      expect(result.mahadashas[0]!.lord).toBe(VENUS);
      expect(result.mahadashas[0]!.durationYears).toBe(20);
      expect(result.mahadashas[1]!.lord).toBe(MOON);
      expect(result.mahadashas[1]!.durationYears).toBe(10);
      expect(result.mahadashas[2]!.lord).toBe(KETU);
      expect(result.mahadashas[2]!.durationYears).toBe(7);
      expect(result.mahadashas[3]!.lord).toBe(SATURN);
      expect(result.mahadashas[3]!.durationYears).toBe(19);

      const total = result.mahadashas.reduce((s, d) => s + d.durationYears, 0);
      expect(total).toBe(120);
    });
  });

  describe('Shastihayani Dasha - First Lord and Durations', () => {
    it('should start with Mercury and have correct durations', () => {
      const result = getShastihayaniDashaBhukti(testJd, chennai, { includeBhuktis: false });

      // Python: Mercury(6), Venus(6), Saturn(6), Rahu(6), Jupiter(10), Sun(10), Mars(10), Moon(6)
      expect(result.mahadashas.length).toBe(8);
      expect(result.mahadashas[0]!.lord).toBe(MERCURY);
      expect(result.mahadashas[0]!.durationYears).toBe(6);
      expect(result.mahadashas[1]!.lord).toBe(VENUS);
      expect(result.mahadashas[1]!.durationYears).toBe(6);
      expect(result.mahadashas[2]!.lord).toBe(SATURN);
      expect(result.mahadashas[2]!.durationYears).toBe(6);
      expect(result.mahadashas[3]!.lord).toBe(RAHU);
      expect(result.mahadashas[3]!.durationYears).toBe(6);
      expect(result.mahadashas[4]!.lord).toBe(JUPITER);
      expect(result.mahadashas[4]!.durationYears).toBe(10);

      const total = result.mahadashas.reduce((s, d) => s + d.durationYears, 0);
      expect(total).toBe(60);
    });
  });
});

// ============================================================================
// CHART-SPECIFIC ASHTOTTARI TESTS
// Ported from Python pvr_tests.py _ashtothari_test_1() through _ashtothari_test_4()
// ============================================================================

describe('Ashtottari Chart Tests (Python parity)', () => {
  describe('Test 1 - Example 60 / Chart 23 (DOB 1912-08-08, IST)', () => {
    // Python: _ashtothari_test_1()
    // dob = (1912,8,8), tob = (19,38,0), lat = 13.0, long = 77+35/60, tz = 5.5
    // Expected first lord = Venus(5)
    const place: Place = {
      name: 'unknown',
      latitude: 13.0,
      longitude: 77 + 35 / 60,
      timezone: 5.5,
    };
    const jd = gregorianToJulianDay(
      { year: 1912, month: 8, day: 8 },
      { hour: 19, minute: 38, second: 0 }
    );

    it('should have Venus as first dasha lord', () => {
      const result = getAshtottariDashaBhukti(jd, place, { includeBhuktis: false });
      expect(result.mahadashas[0]!.lord).toBe(VENUS);
    });
  });

  describe('Test 2 - Example 61 / Indira Gandhi (DOB 1917-11-19, IST)', () => {
    // Python: _ashtothari_test_2()
    // dob = (1917,11,19), tob = (23,3,0), lat = 25+28/60, long = 81+52/60, tz = 5.5
    // Expected first lord = Saturn(6)
    const place: Place = {
      name: 'unknown',
      latitude: 25 + 28 / 60,
      longitude: 81 + 52 / 60,
      timezone: 5.5,
    };
    const jd = gregorianToJulianDay(
      { year: 1917, month: 11, day: 19 },
      { hour: 23, minute: 3, second: 0 }
    );

    it('should have Saturn as first dasha lord', () => {
      const result = getAshtottariDashaBhukti(jd, place, { includeBhuktis: false });
      expect(result.mahadashas[0]!.lord).toBe(SATURN);
    });
  });

  describe('Test 3 - Example 62 / Chart 6 (DOB 1921-06-28, IST)', () => {
    // Python: _ashtothari_test_3()
    // dob = (1921,6,28), tob = (12,49,0), lat = 18+26/60, long = 79+9/60, tz = 5.5
    // Expected first lord = Rahu(7)
    const place: Place = {
      name: 'unknown',
      latitude: 18 + 26 / 60,
      longitude: 79 + 9 / 60,
      timezone: 5.5,
    };
    const jd = gregorianToJulianDay(
      { year: 1921, month: 6, day: 28 },
      { hour: 12, minute: 49, second: 0 }
    );

    it('should have Rahu as first dasha lord', () => {
      const result = getAshtottariDashaBhukti(jd, place, { includeBhuktis: false });
      expect(result.mahadashas[0]!.lord).toBe(RAHU);
    });
  });

  describe('Test 4 - Own Chart (DOB 1996-12-07, Chennai)', () => {
    // Python: _ashtothari_test_4()
    // dob = (1996,12,7), tob = (10,34,0), Chennai
    // Expected lord sequence: Mars(2), Mercury(3), Saturn(6), Jupiter(4), Rahu(7), Venus(5), Sun(0), Moon(1)
    const place: Place = {
      name: 'Chennai',
      latitude: 13.0878,
      longitude: 80.2785,
      timezone: 5.5,
    };
    const jd = gregorianToJulianDay(
      { year: 1996, month: 12, day: 7 },
      { hour: 10, minute: 34, second: 0 }
    );

    it('should have Mars as first dasha lord with correct full sequence', () => {
      const result = getAshtottariDashaBhukti(jd, place, { includeBhuktis: false });
      const lordSequence = result.mahadashas.map(d => d.lord);
      expect(lordSequence).toEqual([MARS, MERCURY, SATURN, JUPITER, RAHU, VENUS, SUN, MOON]);
    });

    it('should have correct durations: 8, 17, 10, 19, 12, 21, 6, 15', () => {
      const result = getAshtottariDashaBhukti(jd, place, { includeBhuktis: false });
      const durations = result.mahadashas.map(d => d.durationYears);
      expect(durations).toEqual([8, 17, 10, 19, 12, 21, 6, 15]);
    });

    it('should have total duration of 108 years', () => {
      const result = getAshtottariDashaBhukti(jd, place, { includeBhuktis: false });
      const total = result.mahadashas.reduce((s, d) => s + d.durationYears, 0);
      expect(total).toBe(108);
    });
  });
});
