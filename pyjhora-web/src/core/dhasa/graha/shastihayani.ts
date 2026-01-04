/**
 * Shastihayani (Shashti Sama) Dasha System
 * Ported from PyJHora shastihayani.py
 * 
 * 60-year dasha cycle with 8 lords
 * Also called Shashti Sama Dasa
 * Applicability: Sun in lagna
 */

import {
    JUPITER,
    MARS, MERCURY,
    MOON,
    PLANET_NAMES_EN,
    SATURN,
    SIDEREAL_YEAR,
    SUN,
    VENUS
} from '../../constants';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { normalizeDegrees } from '../../utils/angle';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface ShastihayaniDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface ShastihayaniBhuktiPeriod {
  dashaLord: number;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface ShastihayaniResult {
  mahadashas: ShastihayaniDashaPeriod[];
  bhuktis?: ShastihayaniBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

/** Year duration in days */
const YEAR_DURATION = SIDEREAL_YEAR;

/** 
 * Shastihayani lords and their durations
 * Order: Jupiter(10), Sun(10), Mars(10), Moon(6), Mercury(6), Venus(6), Saturn(6), Rahu(6)
 * Total: 60 years
 */
const SHASTIHAYANI_LORDS = [JUPITER, SUN, MARS, MOON, MERCURY, VENUS, SATURN, 7]; // 7 = Rahu

/** Nakshatra count for each lord (alternating 3 and 4) */
const SHASTIHAYANI_NAK_COUNT: Record<number, number> = {
  [JUPITER]: 3,
  [SUN]: 4,
  [MARS]: 3,
  [MOON]: 4,
  [MERCURY]: 3,
  [VENUS]: 4,
  [SATURN]: 3,
  7: 4  // Rahu
};

/** Dasha period for each lord in years */
const SHASTIHAYANI_YEARS: Record<number, number> = {
  [JUPITER]: 10,
  [SUN]: 10,
  [MARS]: 10,
  [MOON]: 6,
  [MERCURY]: 6,
  [VENUS]: 6,
  [SATURN]: 6,
  7: 6  // Rahu
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Build nakshatra to lord mapping based on seed star
 */
function buildNakshatraDict(seedStar = 1): Map<number, number> {
  const nakToLord = new Map<number, number>();
  let nak = seedStar;
  
  for (const lord of SHASTIHAYANI_LORDS) {
    const count = SHASTIHAYANI_NAK_COUNT[lord] ?? 3;
    for (let i = 0; i < count; i++) {
      nakToLord.set(nak, lord);
      nak = ((nak) % 27) + 1; // Move to next nakshatra (1-27)
    }
  }
  
  return nakToLord;
}

/**
 * Get the Shastihayani lord for a nakshatra
 * @param nakshatra - Nakshatra number (1-27)
 * @param seedStar - Starting nakshatra (default 1 = Ashwini)
 * @returns [lord, durationYears]
 */
export function getShastihayaniDhasaLord(nakshatra: number, seedStar = 1): [number, number] {
  const nakToLord = buildNakshatraDict(seedStar);
  const lord = nakToLord.get(nakshatra) ?? JUPITER;
  const duration = SHASTIHAYANI_YEARS[lord] ?? 10;
  
  return [lord, duration];
}

/**
 * Get the next lord in the Shastihayani sequence
 */
export function getNextShastihayaniLord(lord: number, direction = 1): number {
  const currentIndex = SHASTIHAYANI_LORDS.indexOf(lord);
  if (currentIndex === -1) {
    return SHASTIHAYANI_LORDS[0]!;
  }
  const nextIndex = ((currentIndex + direction) % 8 + 8) % 8;
  return SHASTIHAYANI_LORDS[nextIndex]!;
}

/**
 * Format Julian Day as date string
 */
function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  const hour12 = time.hour % 12 || 12;
  const ampm = time.hour < 12 ? 'AM' : 'PM';
  const yearStr = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
  return `${yearStr}-${pad(date.month)}-${pad(date.day)} ${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

// ============================================================================
// DASHA START DATE CALCULATION
// ============================================================================

/**
 * Calculate the start date of the Shastihayani mahadasha at birth
 */
export function shastihayaniDashaStart(
  jd: number,
  place: Place,
  starPositionFromMoon = 1,
  seedStar = 1,
  startingPlanet = MOON
): [number, number, number] {
  const oneStar = 360 / 27;
  
  // Get the planet longitude
  let planetLong = getPlanetLongitude(jd, place, startingPlanet);
  
  // Adjust for star position from moon
  if (startingPlanet === MOON) {
    planetLong += (starPositionFromMoon - 1) * oneStar;
    planetLong = normalizeDegrees(planetLong);
  }
  
  // Calculate nakshatra
  const nakIndex = Math.floor(planetLong / oneStar);
  const nakNumber = nakIndex + 1;
  const remainder = planetLong % oneStar;
  
  // Get the lord for this nakshatra
  const [lord, duration] = getShastihayaniDhasaLord(nakNumber, seedStar);
  
  // Calculate elapsed period
  const periodElapsedFraction = remainder / oneStar;
  const periodElapsedDays = periodElapsedFraction * duration * YEAR_DURATION;
  
  // Start date is that many days before birth
  const startDate = jd - periodElapsedDays;
  
  return [lord, startDate, duration];
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get complete Shastihayani dasha-bhukti data
 */
export function getShastihayaniDashaBhukti(
  jd: number,
  place: Place,
  options: {
    starPositionFromMoon?: number;
    seedStar?: number;
    startingPlanet?: number;
    includeBhuktis?: boolean;
    antardashaOption?: number;
  } = {}
): ShastihayaniResult {
  const {
    starPositionFromMoon = 1,
    seedStar = 1,
    startingPlanet = MOON,
    includeBhuktis = true,
    antardashaOption = 1
  } = options;
  
  // Get starting dasha
  let [currentLord, startJd] = shastihayaniDashaStart(
    jd, place, starPositionFromMoon, seedStar, startingPlanet
  );
  
  const mahadashas: ShastihayaniDashaPeriod[] = [];
  const bhuktis: ShastihayaniBhuktiPeriod[] = [];
  
  // Generate 8 mahadashas
  for (let i = 0; i < 8; i++) {
    const durationYears = SHASTIHAYANI_YEARS[currentLord] ?? 10;
    const lordName = currentLord === 7 ? 'Rahu' : (PLANET_NAMES_EN[currentLord] ?? `Planet ${currentLord}`);
    
    mahadashas.push({
      lord: currentLord,
      lordName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears
    });
    
    // Calculate bhuktis if requested
    if (includeBhuktis) {
      let bhuktiLord = currentLord;
      
      // Adjust starting bhukti lord based on option
      if (antardashaOption === 3 || antardashaOption === 4) {
        bhuktiLord = getNextShastihayaniLord(bhuktiLord, 1);
      } else if (antardashaOption === 5 || antardashaOption === 6) {
        bhuktiLord = getNextShastihayaniLord(bhuktiLord, -1);
      }
      
      const direction = (antardashaOption === 1 || antardashaOption === 3 || antardashaOption === 5) ? 1 : -1;
      const bhuktiDuration = durationYears / 8; // Divide equally among 8 bhuktis
      let bhuktiStartJd = startJd;
      
      for (let j = 0; j < 8; j++) {
        const bhuktiLordName = bhuktiLord === 7 ? 'Rahu' : (PLANET_NAMES_EN[bhuktiLord] ?? `Planet ${bhuktiLord}`);
        
        bhuktis.push({
          dashaLord: currentLord,
          bhuktiLord,
          bhuktiLordName,
          startJd: bhuktiStartJd,
          startDate: formatJdAsDate(bhuktiStartJd),
          durationYears: bhuktiDuration
        });
        
        bhuktiStartJd += bhuktiDuration * YEAR_DURATION;
        bhuktiLord = getNextShastihayaniLord(bhuktiLord, direction);
      }
    }
    
    startJd += durationYears * YEAR_DURATION;
    currentLord = getNextShastihayaniLord(currentLord);
  }
  
  if (!includeBhuktis) {
    return { mahadashas };
  }
  
  return {
    mahadashas,
    bhuktis
  };
}
