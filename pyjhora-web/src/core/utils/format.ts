/**
 * Formatting utilities ported from utils.py
 * Handles time strings, degree formatting, and display helpers
 */

import type { JhoraDate, JhoraTime } from '../types';
import { formatDegrees as formatDegreesBase, toDMS } from './angle';

// ============================================================================
// TIME FORMATTING
// ============================================================================

/**
 * Format time as HH:MM:SS string
 * @param time - Time object
 * @returns Formatted time string
 */
export function formatTime(time: JhoraTime): string {
  const pad = (n: number) => n.toString().padStart(2, '0');
  return `${pad(time.hour)}:${pad(time.minute)}:${pad(time.second)}`;
}

/**
 * Format time with AM/PM
 * @param time - Time object
 * @returns Formatted time string with AM/PM
 */
export function formatTime12Hour(time: JhoraTime): string {
  const hour12 = time.hour % 12 || 12;
  const ampm = time.hour < 12 ? 'AM' : 'PM';
  const pad = (n: number) => n.toString().padStart(2, '0');
  return `${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

/**
 * Parse time string to Time object
 * @param timeStr - Time string like "10:30:00" or "10:30:00 AM"
 * @returns Time object or null if invalid
 */
export function parseTime(timeStr: string): JhoraTime | null {
  const match = timeStr.match(/^(\d{1,2}):(\d{2}):(\d{2})\s*(AM|PM)?$/i);
  if (!match) return null;

  let hour = parseInt(match[1]!, 10);
  const minute = parseInt(match[2]!, 10);
  const second = parseInt(match[3]!, 10);
  const period = match[4]?.toUpperCase();

  if (period === 'PM' && hour !== 12) hour += 12;
  if (period === 'AM' && hour === 12) hour = 0;

  if (hour < 0 || hour > 23 || minute < 0 || minute > 59 || second < 0 || second > 59) {
    return null;
  }

  return { hour, minute, second };
}

// ============================================================================
// DATE FORMATTING
// ============================================================================

/**
 * Format date as YYYY-MM-DD
 * @param date - Date object
 * @returns Formatted date string
 */
export function formatDate(date: JhoraDate): string {
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  const year = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
  return `${year}-${pad(date.month)}-${pad(date.day)}`;
}

/**
 * Format date in localized format
 * @param date - Date object
 * @param locale - Locale string (default 'en-US')
 * @returns Formatted date string
 */
export function formatDateLocalized(date: JhoraDate, locale = 'en-US'): string {
  // Handle BC dates specially
  if (date.year <= 0) {
    const bcYear = 1 - date.year; // 0 = 1 BC, -1 = 2 BC
    return `${date.day} ${getMonthName(date.month)}, ${bcYear} BC`;
  }

  // Use native Intl for AD dates
  const jsDate = new Date(date.year, date.month - 1, date.day);
  return jsDate.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

/**
 * Get month name from month number
 * @param month - Month number (1-12)
 * @returns Month name
 */
export function getMonthName(month: number): string {
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  return months[month - 1] ?? 'Unknown';
}

// ============================================================================
// LONGITUDE FORMATTING
// ============================================================================

/**
 * Format longitude as DMS string for planet positions
 * @param longitude - Longitude in degrees (0-30 within sign)
 * @returns Formatted string like "15° 30' 45""
 */
export function formatPlanetLongitude(longitude: number): string {
  const dms = toDMS(longitude);
  return `${dms.degrees}° ${dms.minutes}' ${dms.seconds}"`;
}

/**
 * Convert longitude to formatted string with right single quotes
 * (Matching Python's to_dms output format)
 * @param longitude - Longitude in degrees
 * @param isLatLong - Type: 'lat', 'long', or 'plong' (planet longitude)
 * @returns Formatted string
 */
export function toDmsString(longitude: number, isLatLong: 'lat' | 'long' | 'plong' = 'plong'): string {
  const dms = toDMS(Math.abs(longitude));
  
  let direction = '';
  if (isLatLong === 'lat') {
    direction = longitude >= 0 ? ' N' : ' S';
  } else if (isLatLong === 'long') {
    direction = longitude >= 0 ? ' E' : ' W';
  }

  // Use special Unicode characters matching Python output
  return `${dms.degrees}° ${dms.minutes}' ${dms.seconds}"${direction}`;
}

// ============================================================================
// DURATION FORMATTING
// ============================================================================

/**
 * Format duration in years, months, days
 * @param years - Years
 * @param months - Months
 * @param days - Days
 * @returns Formatted string like "2y 3m 15d"
 */
export function formatDuration(years: number, months: number, days: number): string {
  const parts: string[] = [];
  if (years > 0) parts.push(`${years}y`);
  if (months > 0) parts.push(`${months}m`);
  if (days > 0 || parts.length === 0) parts.push(`${days}d`);
  return parts.join(' ');
}

/**
 * Format duration as full words
 * @param years - Years
 * @param months - Months
 * @param days - Days
 * @returns Formatted string like "2 years, 3 months, 15 days"
 */
export function formatDurationFull(years: number, months: number, days: number): string {
  const parts: string[] = [];
  if (years > 0) parts.push(`${years} ${years === 1 ? 'year' : 'years'}`);
  if (months > 0) parts.push(`${months} ${months === 1 ? 'month' : 'months'}`);
  if (days > 0) parts.push(`${days} ${days === 1 ? 'day' : 'days'}`);
  
  if (parts.length === 0) return '0 days';
  if (parts.length === 1) return parts[0]!;
  
  const last = parts.pop()!;
  return `${parts.join(', ')} and ${last}`;
}

// ============================================================================
// PLANET/RASI FORMATTING
// ============================================================================

/**
 * Format planet name with optional position
 * @param planetIndex - Planet index
 * @param planetNames - Array of planet names
 * @param longitude - Optional longitude to include
 * @returns Formatted string
 */
export function formatPlanet(
  planetIndex: number,
  planetNames: string[],
  longitude?: number
): string {
  const name = planetNames[planetIndex] ?? `Planet${planetIndex}`;
  if (longitude !== undefined) {
    return `${name} (${formatPlanetLongitude(longitude)})`;
  }
  return name;
}

/**
 * Format house chart cell content
 * @param planets - Array of planet indices in the house
 * @param planetSymbols - Array of planet symbols/abbreviations
 * @param hasAscendant - Whether this house has the ascendant
 * @returns Formatted string like "L/Su/Mo"
 */
export function formatHouseContent(
  planets: number[],
  planetSymbols: string[],
  hasAscendant = false
): string {
  const parts: string[] = [];
  
  if (hasAscendant) {
    parts.push('L');
  }
  
  for (const planet of planets) {
    parts.push(planetSymbols[planet] ?? planet.toString());
  }
  
  return parts.join('/');
}

// ============================================================================
// DATETIME FORMATTING
// ============================================================================

/**
 * Format full datetime string
 * @param date - Date object
 * @param time - Time object
 * @returns Formatted string like "2024-01-15 10:30:45"
 */
export function formatDateTime(date: JhoraDate, time: JhoraTime): string {
  return `${formatDate(date)} ${formatTime(time)}`;
}

/**
 * Format datetime for display with AM/PM
 * @param date - Date object
 * @param time - Time object
 * @returns Formatted string like "Jan 15, 2024 10:30:45 AM"
 */
export function formatDateTimeDisplay(date: JhoraDate, time: JhoraTime): string {
  return `${formatDateLocalized(date)} ${formatTime12Hour(time)}`;
}

/** Re-export formatDegrees from angle module */
export { formatDegreesBase as formatDegrees };
