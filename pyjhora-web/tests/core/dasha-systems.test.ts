/**
 * Tests for Ashtottari and Yogini dasha systems
 */

import { JUPITER, MOON, SUN } from '@core/constants';
import {
  ashtottariMahadasha,
  getAshtottariAdhipati,
  getAshtottariDashaBhukti,
  getNextAshtottariAdhipati
} from '@core/dhasa/graha/ashtottari';
import { getPanchottariDashaBhukti } from '@core/dhasa/graha/panchottari';
import { getShastihayaniDashaBhukti } from '@core/dhasa/graha/shastihayani';
import { getShodasottariDashaBhukti } from '@core/dhasa/graha/shodasottari';
import {
  getNextYoginiLord,
  getYoginiDashaBhukti,
  getYoginiDhasaLord
} from '@core/dhasa/graha/yogini';
import type { Place } from '@core/types';
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
      const [lord, duration] = getYoginiDhasaLord(7, 7); // Same as seed = first lord
      expect(lord).toBe(MOON); // Moon is first Yogini lord
      expect(duration).toBe(1); // Moon has 1 year
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
