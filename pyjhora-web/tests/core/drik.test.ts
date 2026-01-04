/**
 * Tests for drik.ts panchanga calculations
 */

import {
    calculateKarana,
    calculateNakshatra,
    calculateTithi,
    calculateVara,
    calculateYoga,
    dayLength,
    nakshatraPada
} from '@core/panchanga/drik';
import type { Place } from '@core/types';
import { describe, expect, it } from 'vitest';

// Test place: Bangalore, India
const bangalore: Place = {
  name: 'Bangalore',
  latitude: 12.972,
  longitude: 77.594,
  timezone: 5.5
};

describe('Panchanga Calculations (drik.ts)', () => {
  describe('nakshatraPada', () => {
    it('should calculate nakshatra and pada correctly', () => {
      // Test from PVR book Exercise 1: Jupiter at 94°19'
      const longitude = 94 + 19 / 60;
      const [nakshatra, pada, remainder] = nakshatraPada(longitude);
      
      // 94°19' = 7 * 13.333 + remainder in Punarvasu
      expect(nakshatra).toBe(8); // Pushya (after Punarvasu)
      expect(pada).toBeGreaterThanOrEqual(1);
      expect(pada).toBeLessThanOrEqual(4);
    });

    it('should return nakshatra 1 for 0 degrees', () => {
      const [nakshatra, pada] = nakshatraPada(0);
      expect(nakshatra).toBe(1); // Ashwini
      expect(pada).toBe(1);
    });

    it('should return nakshatra 27 for 359 degrees', () => {
      const [nakshatra] = nakshatraPada(359);
      expect(nakshatra).toBe(27); // Revati
    });
  });

  describe('calculateVara', () => {
    it('should calculate weekday correctly', () => {
      // Test a known date
      // January 1, 2000 was a Saturday (index 6)
      const jd2000 = 2451545.0; // J2000.0
      const vara = calculateVara(jd2000);
      expect(vara.number).toBe(6); // Saturday
      expect(vara.name).toBe('Saturday');
    });

    it('should cycle through all weekdays', () => {
      const jd = 2451545.0;
      const days = [];
      for (let i = 0; i < 7; i++) {
        days.push(calculateVara(jd + i).name);
      }
      expect(days).toContain('Sunday');
      expect(days).toContain('Monday');
      expect(days).toContain('Friday');
    });
  });

  describe('calculateTithi', () => {
    it('should return valid tithi data', () => {
      const jd = 2451545.0; // J2000.0
      const tithi = calculateTithi(jd, bangalore);
      
      expect(tithi.number).toBeGreaterThanOrEqual(1);
      expect(tithi.number).toBeLessThanOrEqual(30);
      expect(['shukla', 'krishna']).toContain(tithi.paksha);
      expect(tithi.name).toBeDefined();
    });
  });

  describe('calculateNakshatra', () => {
    it('should return valid nakshatra data', () => {
      const jd = 2451545.0;
      const nakshatra = calculateNakshatra(jd, bangalore);
      
      expect(nakshatra.number).toBeGreaterThanOrEqual(1);
      expect(nakshatra.number).toBeLessThanOrEqual(27);
      expect(nakshatra.pada).toBeGreaterThanOrEqual(1);
      expect(nakshatra.pada).toBeLessThanOrEqual(4);
      expect(nakshatra.name).toBeDefined();
    });
  });

  describe('calculateYoga', () => {
    it('should return valid yoga data', () => {
      const jd = 2451545.0;
      const yoga = calculateYoga(jd, bangalore);
      
      expect(yoga.number).toBeGreaterThanOrEqual(1);
      expect(yoga.number).toBeLessThanOrEqual(27);
      expect(yoga.name).toBeDefined();
    });
  });

  describe('calculateKarana', () => {
    it('should return valid karana data', () => {
      const jd = 2451545.0;
      const karana = calculateKarana(jd, bangalore);
      
      expect(karana.number).toBeGreaterThanOrEqual(1);
      expect(karana.number).toBeLessThanOrEqual(60);
      expect(karana.name).toBeDefined();
    });
  });

  describe('dayLength', () => {
    it('should return approximately 12 hours for equatorial location', () => {
      const jd = 2451545.0;
      const equator: Place = {
        name: 'Equator',
        latitude: 0,
        longitude: 0,
        timezone: 0
      };
      
      const length = dayLength(jd, equator);
      // Day length at equator is approximately 12 hours
      expect(length).toBeGreaterThan(10);
      expect(length).toBeLessThan(14);
    });
  });
});
