
import { describe, expect, it } from 'vitest';
import {
    ARIES,
    CANCER,
    CAPRICORN,
    GEMINI,
    LEO,
    MARS,
    MOON
} from '../../../../src/core/constants';
import {
    getNarayanaDashaBhukti,
    getNarayanaDashaDuration
} from '../../../../src/core/dhasa/raasi/narayana';
import type { Place } from '../../../../src/core/types';

describe('Narayana Dasha', () => {
    
  // Helper to create planet positions
  const createPlanets = (map: Record<number, number>) => {
      // map: Planet ID -> Rasi
      return Object.entries(map).map(([p, r]) => ({
          planet: parseInt(p),
          rasi: r,
          longitude: 15 // midpoint default
      }));
  };

    const testPlace: Place = {
        name: 'Delhi',
        latitude: 28.6139,
        longitude: 77.2090,
        timezone: 5.5
    };
    const testJd = 2447912.0;

  describe('getNarayanaDashaDuration', () => {
      it('should calculate duration for Odd Footed Sign (Forward count)', () => {
        const planets = createPlanets({ [MARS]: GEMINI });
        const duration = getNarayanaDashaDuration(planets, ARIES);
        expect(duration).toBe(2);
    });

      it('should calculate duration for Even Footed Sign (Reverse count)', () => {
        const planets = createPlanets({ [MOON]: LEO });
        const duration = getNarayanaDashaDuration(planets, CANCER);
        expect(duration).toBe(11);
    });
    
      it('should handle Exception 1: Count is 1 -> Duration 12', () => {
        const planets = createPlanets({ [MARS]: ARIES });
        const duration = getNarayanaDashaDuration(planets, ARIES);
        expect(duration).toBe(12);
    });
    
      it('should handle Exception 2: Exalted Lord -> +1 year', () => {
        const planets = createPlanets({ [MARS]: CAPRICORN });
        const duration = getNarayanaDashaDuration(planets, ARIES);
        expect(duration).toBe(10);
    });
    
      it('should handle Exception 3: Debilitated Lord -> -1 year', () => {
        const planets = createPlanets({ [MARS]: CANCER });
        const duration = getNarayanaDashaDuration(planets, ARIES);
        expect(duration).toBe(2);
    });
  });
  
    describe('getNarayanaDashaBhukti (Integration)', () => {
        it('should return valid dasha structure', () => {
            const result = getNarayanaDashaBhukti(testJd, testPlace);
            expect(result.mahadashas.length).toBeGreaterThan(0);
            expect(result.mahadashas[0].durationYears).toBeGreaterThan(0);
        });

      it('should include bhuktis when requested', () => {
          const result = getNarayanaDashaBhukti(testJd, testPlace, { includeBhuktis: true });
          expect(result.bhuktis).toBeDefined();
          expect(result.bhuktis!.length).toBeGreaterThan(0);
      });

      it('should respect seedSignOverride', () => {
          const result = getNarayanaDashaBhukti(testJd, testPlace, { seedSignOverride: GEMINI });
          expect(result.mahadashas[0].rasi).toBe(GEMINI);
      });
  });

});
