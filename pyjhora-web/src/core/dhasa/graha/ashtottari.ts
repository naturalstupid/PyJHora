/**
 * Ashtottari Dasha System
 * Ported from PyJHora ashtottari.py
 * 
 * 108-year dasha cycle with 8 lords (excludes Rahu and Ketu lords)
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

export interface AshtottariDashaBalance {
  years: number;
  months: number;
  days: number;
}

export interface AshtottariDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface AshtottariBhuktiPeriod {
  dashaLord: number;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
}

export interface AshtottariResult {
  mahadashas: AshtottariDashaPeriod[];
  bhuktis?: AshtottariBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

/** Total lifespan for Ashtottari = 108 years */
const ASHTOTTARI_TOTAL_YEARS = 108;

/** Year duration in days */
const YEAR_DURATION = SIDEREAL_YEAR;

/** 
 * Ashtottari adhipati (lords) list
 * Order: Sun(6), Moon(15), Mars(8), Mercury(17), Saturn(10), Jupiter(19), Rahu(12), Venus(21)
 * Note: This uses only 8 lords unlike Vimsottari's 9
 */
const ASHTOTTARI_LORDS = [SUN, MOON, MARS, MERCURY, SATURN, JUPITER, 7, VENUS]; // 7 = Rahu placeholder

/** Dasha period for each lord in years */
const ASHTOTTARI_YEARS: Record<number, number> = {
  [SUN]: 6,
  [MOON]: 15,
  [MARS]: 8,
  [MERCURY]: 17,
  [SATURN]: 10,
  [JUPITER]: 19,
  7: 12,  // Rahu
  [VENUS]: 21
};

/**
 * Nakshatra ranges for each lord
 * Format: [startNak, endNak] (1-indexed)
 * Each range corresponds to specific nakshatras
 */
interface NakshatraRange {
  start: number;
  end: number;
  duration: number;
}

const ASHTOTTARI_NAK_RANGES: Record<number, NakshatraRange> = {
  [SUN]: { start: 6, end: 9, duration: 6 },
  [MOON]: { start: 10, end: 12, duration: 15 },
  [MARS]: { start: 13, end: 16, duration: 8 },
  [MERCURY]: { start: 17, end: 19, duration: 17 },
  [SATURN]: { start: 20, end: 22, duration: 10 },
  [JUPITER]: { start: 23, end: 25, duration: 19 },
  7: { start: 26, end: 2, duration: 12 },  // Rahu (wraps around)
  [VENUS]: { start: 3, end: 5, duration: 21 }
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get the Ashtottari adhipati (lord) for a nakshatra
 * @param nakshatra - Nakshatra number (1-27)
 * @returns [lord, nakRangeInfo] or undefined
 */
export function getAshtottariAdhipati(nakshatra: number): [number, NakshatraRange] | undefined {
  for (const [lordStr, range] of Object.entries(ASHTOTTARI_NAK_RANGES)) {
    const lord = parseInt(lordStr, 10);
    let { start, end } = range;
    let nak = nakshatra;
    
    // Handle wraparound (e.g., Rahu: 26-2)
    if (end < start) {
      end += 27;
      if (nak < start) {
        nak += 27;
      }
    }
    
    if (nak >= start && nak <= end) {
      return [lord, range];
    }
  }
  return undefined;
}

/**
 * Get the next adhipati in the Ashtottari sequence
 * @param lord - Current lord
 * @param direction - 1 for forward, -1 for backward
 * @returns Next lord
 */
export function getNextAshtottariAdhipati(lord: number, direction = 1): number {
  const currentIndex = ASHTOTTARI_LORDS.indexOf(lord);
  if (currentIndex === -1) {
    // Default to first lord if not found
    return ASHTOTTARI_LORDS[0]!;
  }
  const nextIndex = ((currentIndex + direction) % 8 + 8) % 8;
  return ASHTOTTARI_LORDS[nextIndex]!;
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
 * Calculate the start date of the Ashtottari mahadasha at birth
 * @param jd - Julian Day Number (birth time)
 * @param place - Place data
 * @param starPositionFromMoon - Which nakshatra to use
 * @param startingPlanet - Planet to calculate from
 * @returns [lord, startDate JD]
 */
export function ashtottariDashaStartDate(
  jd: number,
  place: Place,
  starPositionFromMoon = 1,
  startingPlanet = MOON
): [number, number] {
  const oneStar = 360 / 27; // 13°20'
  
  // Get the planet longitude
  let planetLong = getPlanetLongitude(jd, place, startingPlanet);
  
  // Adjust for star position from moon
  if (startingPlanet === MOON) {
    planetLong += (starPositionFromMoon - 1) * oneStar;
    planetLong = normalizeDegrees(planetLong);
  }
  
  // Calculate nakshatra (1-indexed)
  const nakIndex = Math.floor(planetLong / oneStar);
  const nakNumber = nakIndex + 1;
  
  // Get the lord and range info
  const result = getAshtottariAdhipati(nakNumber);
  if (!result) {
    // Fallback to first lord
    return [SUN, jd];
  }
  
  const [lord, range] = result;
  let { start, end, duration } = range;
  
  // Handle wraparound
  if (end < start) {
    end += 27;
  }
  const rangeSpan = end - start + 1;
  
  // Calculate position within the range
  const rangeStartLong = (start - 1) * oneStar;
  const rangeSpanDegrees = rangeSpan * oneStar;
  const positionInRange = (planetLong - rangeStartLong + 360) % 360;
  
  // Calculate elapsed period
  const periodElapsedFraction = positionInRange / rangeSpanDegrees;
  const periodElapsedDays = periodElapsedFraction * duration * YEAR_DURATION;
  
  // Start date is that many days before birth
  const startDate = jd - periodElapsedDays;
  
  return [lord, startDate];
}

// ============================================================================
// MAHADASHA CALCULATION
// ============================================================================

/**
 * Calculate all 8 Ashtottari mahadashas
 * @param jd - Julian Day Number
 * @param place - Place data
 * @param starPositionFromMoon - Which nakshatra to use
 * @param startingPlanet - Starting planet
 * @returns Map of lord to start date
 */
export function ashtottariMahadasha(
  jd: number,
  place: Place,
  starPositionFromMoon = 1,
  startingPlanet = MOON
): Map<number, number> {
  let [lord, startDate] = ashtottariDashaStartDate(
    jd, place, starPositionFromMoon, startingPlanet
  );
  
  const dashas = new Map<number, number>();
  
  for (let i = 0; i < 8; i++) {
    dashas.set(lord, startDate);
    const periodYears = ASHTOTTARI_YEARS[lord] ?? 0;
    startDate += periodYears * YEAR_DURATION;
    lord = getNextAshtottariAdhipati(lord);
  }
  
  return dashas;
}

// ============================================================================
// BHUKTI CALCULATION
// ============================================================================

/**
 * Calculate bhuktis (sub-periods) for an Ashtottari mahadasha
 * @param mahaLord - Mahadasha lord
 * @param startDate - Start date of mahadasha
 * @param antardashaOption - Variation option (1-6)
 * @returns Map of bhukti lord to start date
 */
export function ashtottariBhukti(
  mahaLord: number,
  startDate: number,
  antardashaOption = 1
): Map<number, number> {
  let lord = mahaLord;
  
  // Adjust starting lord based on option
  if (antardashaOption === 3 || antardashaOption === 4) {
    lord = getNextAshtottariAdhipati(lord, 1);
  } else if (antardashaOption === 5 || antardashaOption === 6) {
    lord = getNextAshtottariAdhipati(lord, -1);
  }
  
  // Direction
  const direction = (antardashaOption === 1 || antardashaOption === 3 || antardashaOption === 5) ? 1 : -1;
  
  const bhuktis = new Map<number, number>();
  const mahaYears = ASHTOTTARI_YEARS[mahaLord] ?? 0;
  
  for (let i = 0; i < 8; i++) {
    bhuktis.set(lord, startDate);
    
    // Bhukti duration = (maha period * bhukti period) / total cycle
    const bhuktiYears = ASHTOTTARI_YEARS[lord] ?? 0;
    const factor = (mahaYears * bhuktiYears) / ASHTOTTARI_TOTAL_YEARS;
    
    startDate += factor * YEAR_DURATION;
    lord = getNextAshtottariAdhipati(lord, direction);
  }
  
  return bhuktis;
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get complete Ashtottari dasha-bhukti data
 * @param jd - Julian Day Number (birth time)
 * @param place - Place data
 * @param options - Calculation options
 * @returns Ashtottari result with periods
 */
export function getAshtottariDashaBhukti(
  jd: number,
  place: Place,
  options: {
    starPositionFromMoon?: number;
    startingPlanet?: number;
    includeBhuktis?: boolean;
    antardashaOption?: number;
  } = {}
): AshtottariResult {
  const {
    starPositionFromMoon = 1,
    startingPlanet = MOON,
    includeBhuktis = true,
    antardashaOption = 1
  } = options;
  
  // Get all mahadashas
  const dashaMap = ashtottariMahadasha(jd, place, starPositionFromMoon, startingPlanet);
  
  // Convert to array
  const dashaEntries = Array.from(dashaMap.entries());
  const mahadashas: AshtottariDashaPeriod[] = dashaEntries.map((entry) => {
    const [lord, startJd] = entry;
    const periodYears = ASHTOTTARI_YEARS[lord] ?? 0;
    
    // Get lord name (handle Rahu specially)
    const lordName = lord === 7 ? 'Rahu' : (PLANET_NAMES_EN[lord] ?? `Planet ${lord}`);
    
    return {
      lord,
      lordName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: periodYears
    };
  });
  
  if (!includeBhuktis) {
    return { mahadashas };
  }
  
  // Calculate bhuktis
  const bhuktis: AshtottariBhuktiPeriod[] = [];
  
  for (const dasha of mahadashas) {
    const bhuktiMap = ashtottariBhukti(dasha.lord, dasha.startJd, antardashaOption);
    
    for (const [bhuktiLord, startJd] of bhuktiMap) {
      const bhuktiLordName = bhuktiLord === 7 ? 'Rahu' : (PLANET_NAMES_EN[bhuktiLord] ?? `Planet ${bhuktiLord}`);
      
      bhuktis.push({
        dashaLord: dasha.lord,
        bhuktiLord,
        bhuktiLordName,
        startJd,
        startDate: formatJdAsDate(startJd)
      });
    }
  }
  
  return {
    mahadashas,
    bhuktis
  };
}
