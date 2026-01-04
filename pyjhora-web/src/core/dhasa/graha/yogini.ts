/**
 * Yogini Dasha System
 * Ported from PyJHora yogini.py
 * 
 * 36-year dasha cycle with 8 lords, typically run for 3 cycles (108 years total)
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

export interface YoginiDashaPeriod {
  lord: number;
  lordName: string;
  yoginiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface YoginiBhuktiPeriod {
  dashaLord: number;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface YoginiResult {
  mahadashas: YoginiDashaPeriod[];
  bhuktis?: YoginiBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

/** Year duration in days */
const YEAR_DURATION = SIDEREAL_YEAR;

/** 
 * Yogini lords and their durations
 * Total: 1+2+3+4+5+6+7+8 = 36 years
 */
const YOGINI_LORDS = [MOON, SUN, JUPITER, MARS, MERCURY, SATURN, VENUS, 7]; // 7 = Rahu

/** Dasha period for each lord in years */
const YOGINI_YEARS: Record<number, number> = {
  [MOON]: 1,
  [SUN]: 2,
  [JUPITER]: 3,
  [MARS]: 4,
  [MERCURY]: 5,
  [SATURN]: 6,
  [VENUS]: 7,
  7: 8  // Rahu
};

/** Yogini names for each lord */
const YOGINI_NAMES: Record<number, string> = {
  [MOON]: 'Mangala',
  [SUN]: 'Pingala',
  [JUPITER]: 'Dhanya',
  [MARS]: 'Bhramari',
  [MERCURY]: 'Bhadrika',
  [SATURN]: 'Ulka',
  [VENUS]: 'Siddha',
  7: 'Sankata'  // Rahu
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get the next Yogini lord in sequence
 * @param lord - Current lord
 * @param direction - 1 for forward, -1 for backward
 * @returns Next lord
 */
export function getNextYoginiLord(lord: number, direction = 1): number {
  const currentIndex = YOGINI_LORDS.indexOf(lord);
  if (currentIndex === -1) {
    return YOGINI_LORDS[0]!;
  }
  const nextIndex = ((currentIndex + direction) % 8 + 8) % 8;
  return YOGINI_LORDS[nextIndex]!;
}

/**
 * Get Yogini mahadasha lord for a nakshatra
 * @param nakshatra - Nakshatra number (1-27)
 * @param seedStar - Starting nakshatra (default 7 = Punarvasu)
 * @returns [lord, durationYears]
 */
export function getYoginiDhasaLord(nakshatra: number, seedStar = 7): [number, number] {
  // Calculate which lord based on nakshatra position from seed
  const offset = ((nakshatra - seedStar) % 27 + 27) % 27;
  const lordIndex = offset % 8;
  const lord = YOGINI_LORDS[lordIndex]!;
  const duration = YOGINI_YEARS[lord] ?? 1;
  
  return [lord, duration];
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
 * Calculate the start date of the Yogini mahadasha at birth
 * @param jd - Julian Day Number (birth time)
 * @param place - Place data
 * @param starPositionFromMoon - Which nakshatra to use
 * @param seedStar - Seed star (default 7)
 * @param startingPlanet - Planet to calculate from
 * @returns [lord, startDate JD, duration]
 */
export function yoginiDashaStart(
  jd: number,
  place: Place,
  starPositionFromMoon = 1,
  seedStar = 7,
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
  const [lord, duration] = getYoginiDhasaLord(nakNumber, seedStar);
  
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
 * Get complete Yogini dasha-bhukti data
 * @param jd - Julian Day Number (birth time)
 * @param place - Place data
 * @param options - Calculation options
 * @returns Yogini result with periods
 */
export function getYoginiDashaBhukti(
  jd: number,
  place: Place,
  options: {
    starPositionFromMoon?: number;
    seedStar?: number;
    startingPlanet?: number;
    includeBhuktis?: boolean;
    antardashaOption?: number;
    cycles?: number;
  } = {}
): YoginiResult {
  const {
    starPositionFromMoon = 1,
    seedStar = 7,
    startingPlanet = MOON,
    includeBhuktis = true,
    antardashaOption = 1,
    cycles = 3  // Default 3 cycles = 108 years
  } = options;
  
  // Get starting dasha
  let [currentLord, startJd] = yoginiDashaStart(
    jd, place, starPositionFromMoon, seedStar, startingPlanet
  );
  
  const mahadashas: YoginiDashaPeriod[] = [];
  const bhuktis: YoginiBhuktiPeriod[] = [];
  
  // Generate dashas for specified number of cycles
  for (let cycle = 0; cycle < cycles; cycle++) {
    for (let i = 0; i < 8; i++) {
      const durationYears = YOGINI_YEARS[currentLord] ?? 1;
      const lordName = currentLord === 7 ? 'Rahu' : (PLANET_NAMES_EN[currentLord] ?? `Planet ${currentLord}`);
      const yoginiName = YOGINI_NAMES[currentLord] ?? 'Unknown';
      
      mahadashas.push({
        lord: currentLord,
        lordName,
        yoginiName,
        startJd,
        startDate: formatJdAsDate(startJd),
        durationYears
      });
      
      // Calculate bhuktis if requested
      if (includeBhuktis) {
        let bhuktiLord = currentLord;
        
        // Adjust starting bhukti lord based on option
        if (antardashaOption === 3 || antardashaOption === 4) {
          bhuktiLord = getNextYoginiLord(bhuktiLord, 1);
        } else if (antardashaOption === 5 || antardashaOption === 6) {
          bhuktiLord = getNextYoginiLord(bhuktiLord, -1);
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
          bhuktiLord = getNextYoginiLord(bhuktiLord, direction);
        }
      }
      
      startJd += durationYears * YEAR_DURATION;
      currentLord = getNextYoginiLord(currentLord);
    }
  }
  
  if (!includeBhuktis) {
    return { mahadashas };
  }
  
  return {
    mahadashas,
    bhuktis
  };
}
