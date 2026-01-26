/**
 * Tests for Julian Day utilities
 * Ported test cases from PyJHora pvr_tests.py
 */

import {
    daysInMonth,
    daysToYMD,
    gregorianToJulianDay,
    isLeapYear,
    julianDayToGregorian,
    weekday
} from '@core/utils/julian';
import { describe, expect, it } from 'vitest';

describe('Julian Day Conversions', () => {
  describe('gregorianToJulianDay', () => {
    it('should convert standard dates correctly', () => {
      // J2000.0 epoch: January 1, 2000 at noon
      const jd = gregorianToJulianDay({ year: 2000, month: 1, day: 1 }, { hour: 12, minute: 0, second: 0 });
      expect(jd).toBeCloseTo(2451545.0, 5);
    });

    it('should handle dates used in PyJHora tests', () => {
      // Test date from pvr_tests.py: 2009-07-15
      const jd = gregorianToJulianDay({ year: 2009, month: 7, day: 15 }, { hour: 12, minute: 0, second: 0 });
      expect(jd).toBeCloseTo(2455028.0, 1);
    });

    it('should handle BC dates', () => {
      // 1 BC (year 0 in astronomical notation)
      const jd = gregorianToJulianDay({ year: -1, month: 1, day: 1 }, { hour: 12, minute: 0, second: 0 });
      expect(jd).toBeLessThan(2451545.0);
    });

    it('should be reversible', () => {
      const original = { year: 1996, month: 12, day: 7 };
      const time = { hour: 10, minute: 34, second: 0 };
      
      const jd = gregorianToJulianDay(original, time);
      const result = julianDayToGregorian(jd);
      
      expect(result.date.year).toBe(original.year);
      expect(result.date.month).toBe(original.month);
      expect(result.date.day).toBe(original.day);
      expect(result.time.hour).toBe(time.hour);
      expect(result.time.minute).toBe(time.minute);
    });
  });

  describe('Date utilities', () => {
    it('should detect leap years correctly', () => {
      expect(isLeapYear(2000)).toBe(true); // Divisible by 400
      expect(isLeapYear(1900)).toBe(false); // Divisible by 100 but not 400
      expect(isLeapYear(2004)).toBe(true); // Divisible by 4
      expect(isLeapYear(2001)).toBe(false); // Not divisible by 4
    });

    it('should return correct days in month', () => {
      expect(daysInMonth(2000, 2)).toBe(29); // Leap year February
      expect(daysInMonth(2001, 2)).toBe(28); // Non-leap February
      expect(daysInMonth(2000, 1)).toBe(31); // January
      expect(daysInMonth(2000, 4)).toBe(30); // April
    });

    it('should calculate weekday correctly', () => {
      // January 1, 2000 was a Saturday (6)
      const jd = gregorianToJulianDay({ year: 2000, month: 1, day: 1 }, { hour: 12, minute: 0, second: 0 });
      expect(weekday(jd)).toBe(6);
    });
  });

  describe('Duration calculations', () => {
    it('should break down days into YMD', () => {
      const result = daysToYMD(365.2425); // Approximately 1 year
      expect(result.years).toBe(1);
      expect(result.months).toBe(0);
      expect(result.days).toBe(0);
    });

    it('should handle partial years', () => {
      const result = daysToYMD(400);
      expect(result.years).toBe(1);
      expect(result.months).toBeGreaterThan(0);
    });
  });
});
