/**
 * Julian Day Number utilities ported from utils.py
 * Handles date conversions including BC dates
 */

import type { JhoraDate, JhoraTime } from '../types';

// ============================================================================
// JULIAN DAY CONVERSIONS
// ============================================================================

/**
 * Convert Gregorian date to Julian Day Number
 * Supports BC dates (negative years)
 * @param date - Jora date (year can be negative for BC)
 * @param time - Time of day (optional, defaults to noon)
 * @returns Julian Day Number
 */
export function gregorianToJulianDay(date: JhoraDate, time?: JhoraTime): number {
  let { year, month, day } = date;
  const hour = time?.hour ?? 12;
  const minute = time?.minute ?? 0;
  const second = time?.second ?? 0;

  // Handle BC dates: year 1 BC = year 0, 2 BC = year -1, etc.
  if (year < 0) {
    year += 1;
  }

  // Algorithm from Meeus "Astronomical Algorithms"
  if (month <= 2) {
    year -= 1;
    month += 12;
  }

  const A = Math.floor(year / 100);
  const B = 2 - A + Math.floor(A / 4);

  const jd = Math.floor(365.25 * (year + 4716)) +
             Math.floor(30.6001 * (month + 1)) +
             day + B - 1524.5;

  // Add time component
  const timeComponent = (hour + minute / 60 + second / 3600) / 24;

  return jd + timeComponent;
}

/**
 * Convert Julian Day Number to Gregorian date
 * @param jd - Julian Day Number
 * @returns Gregorian date and time
 */
export function julianDayToGregorian(jd: number): { date: JhoraDate; time: JhoraTime } {
  const Z = Math.floor(jd + 0.5);
  const F = jd + 0.5 - Z;

  let A: number;
  if (Z < 2299161) {
    A = Z;
  } else {
    const alpha = Math.floor((Z - 1867216.25) / 36524.25);
    A = Z + 1 + alpha - Math.floor(alpha / 4);
  }

  const B = A + 1524;
  const C = Math.floor((B - 122.1) / 365.25);
  const D = Math.floor(365.25 * C);
  const E = Math.floor((B - D) / 30.6001);

  const day = B - D - Math.floor(30.6001 * E);
  const month = E < 14 ? E - 1 : E - 13;
  let year = month > 2 ? C - 4716 : C - 4715;

  // Convert astronomical year to BC notation
  if (year <= 0) {
    year -= 1;
  }

  // Extract time with proper rounding
  const totalHours = F * 24;
  const hour = Math.floor(totalHours);
  const remainingMinutes = (totalHours - hour) * 60;
  const minute = Math.floor(remainingMinutes + 0.5 / 60); // Add small amount for rounding
  const remainingSeconds = (remainingMinutes - Math.floor(remainingMinutes)) * 60;
  const second = Math.round(remainingSeconds);

  return {
    date: { year, month, day },
    time: { hour, minute, second }
  };
}

/**
 * Calculate Julian Day Number for standard calculation (noon)
 * @param date - Gregorian date
 * @param time - Time of day
 * @returns Julian Day Number
 */
export function julianDayNumber(date: JhoraDate, time: JhoraTime): number {
  return gregorianToJulianDay(date, time);
}

/**
 * Convert Julian Day to UTC Julian Day (remove timezone offset)
 * @param jd - Local Julian Day Number
 * @param timezoneOffset - Timezone offset in hours
 * @returns UTC Julian Day Number
 */
export function toUtc(jd: number, timezoneOffset: number): number {
  return jd - timezoneOffset / 24;
}

/**
 * Convert UTC Julian Day to local Julian Day
 * @param jdUtc - UTC Julian Day Number
 * @param timezoneOffset - Timezone offset in hours
 * @returns Local Julian Day Number
 */
export function fromUtc(jdUtc: number, timezoneOffset: number): number {
  return jdUtc + timezoneOffset / 24;
}

// ============================================================================
// DATE UTILITIES
// ============================================================================

/**
 * Check if a year is a leap year
 * @param year - Gregorian year (can be negative for BC)
 * @returns True if leap year
 */
export function isLeapYear(year: number): boolean {
  // Adjust for astronomical year numbering
  const adjustedYear = year <= 0 ? year + 1 : year;
  
  if (adjustedYear % 4 !== 0) return false;
  if (adjustedYear % 100 !== 0) return true;
  if (adjustedYear % 400 !== 0) return false;
  return true;
}

/**
 * Get number of days in a month
 * @param year - Year
 * @param month - Month (1-12)
 * @returns Number of days
 */
export function daysInMonth(year: number, month: number): number {
  const daysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  
  if (month === 2 && isLeapYear(year)) {
    return 29;
  }
  
  return daysPerMonth[month - 1] ?? 30;
}

/**
 * Add days to a Julian Day Number and return the new date
 * @param jd - Starting Julian Day
 * @param days - Number of days to add (can be negative)
 * @returns New Julian Day Number
 */
export function addDays(jd: number, days: number): number {
  return jd + days;
}

/**
 * Calculate difference between two Julian Days in days
 * @param jd1 - First Julian Day
 * @param jd2 - Second Julian Day
 * @returns Difference in days (jd2 - jd1)
 */
export function daysDifference(jd1: number, jd2: number): number {
  return jd2 - jd1;
}

/**
 * Get weekday from Julian Day (0=Sunday, 1=Monday, etc.)
 * @param jd - Julian Day Number
 * @returns Weekday index
 */
export function weekday(jd: number): number {
  return Math.floor(jd + 1.5) % 7;
}

// ============================================================================
// YEAR/MONTH/DAY OPERATIONS
// ============================================================================

/**
 * Convert years to days (approximate)
 * @param years - Number of years
 * @returns Approximate number of days
 */
export function yearsToDays(years: number): number {
  return years * 365.2425;
}

/**
 * Convert days to years (approximate)
 * @param days - Number of days
 * @returns Approximate number of years
 */
export function daysToYears(days: number): number {
  return days / 365.2425;
}

/**
 * Break down duration into years, months, days
 * @param totalDays - Total number of days
 * @returns Object with years, months, days
 */
export function daysToYMD(totalDays: number): { years: number; months: number; days: number } {
  const years = Math.floor(totalDays / 365.2425);
  const remainingDays = totalDays - years * 365.2425;
  const months = Math.floor(remainingDays / 30.4375);
  const days = Math.round(remainingDays - months * 30.4375);

  return { years, months, days };
}
