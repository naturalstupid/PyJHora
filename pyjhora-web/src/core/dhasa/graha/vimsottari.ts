/**
 * Vimsottari Dasha System
 * Ported from PyJHora vimsottari.py
 * 
 * The most widely used dasha system spanning 120 years
 */

import {
  MOON,
  PLANET_NAMES_EN,
  SIDEREAL_YEAR,
  VIMSOTTARI_LORDS,
  VIMSOTTARI_TOTAL_YEARS,
  VIMSOTTARI_YEARS
} from '../../constants';
import { getDivisionalChart, PlanetPosition } from '../../horoscope/charts';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { normalizeDegrees } from '../../utils/angle';
import { daysToYMD, julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface DashaBalance {
  years: number;
  months: number;
  days: number;
}

export interface DashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  endJd: number;
  endDate: string;
  durationYears: number;
}

export interface BhuktiPeriod {
  dashaLord: number;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
}

export interface VimsottariResult {
  balance: DashaBalance;
  mahadashas: DashaPeriod[];
  bhuktis?: BhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

/** Year duration in days (sidereal year) */
const YEAR_DURATION = SIDEREAL_YEAR;

/** Nakshatra lords in Vimsottari order */
const ADHIPATI_LIST = VIMSOTTARI_LORDS;

/** Dasha periods for each planet */
const DASHA_YEARS = VIMSOTTARI_YEARS;

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get the Vimsottari adhipati (lord) for a nakshatra
 * @param nakshatra - Nakshatra number (0-26)
 * @param seedStar - Seed star index (default 3 = Krittika)
 * @returns Planet index of the lord
 */
export function getVimsottariAdhipati(nakshatra: number, seedStar = 3): number {
  const index = ((nakshatra - seedStar + 3) % 9 + 9) % 9;
  return ADHIPATI_LIST[index]!;
}

/**
 * Get the next adhipati in the sequence
 * @param lord - Current lord
 * @param direction - 1 for forward, -1 for backward
 * @returns Next lord
 */
export function getNextAdhipati(lord: number, direction = 1): number {
  const currentIndex = ADHIPATI_LIST.indexOf(lord);
  if (currentIndex === -1) {
    throw new Error(`Invalid Vimsottari lord: ${lord}`);
  }
  const nextIndex = ((currentIndex + direction) % 9 + 9) % 9;
  return ADHIPATI_LIST[nextIndex]!;
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
 * Calculate the start date of the mahadasha at birth
 * @param jd - Julian Day Number (birth time)
 * @param place - Place data
 * @param starPositionFromMoon - Which nakshatra to use (1=moon, 4=kshema, 5=utpanna, 8=adhana)
 * @param seedStar - Seed star for calculation (default 3)
 * @param startingPlanet - Planet to calculate from (default Moon)
 * @returns [lord, startDate JD]
 */
export function vimsottariDashaStartDate(
  jd: number,
  place: Place,
  starPositionFromMoon = 1,
  seedStar = 3,
  startingPlanet = MOON,
  divisionalChartFactor = 1
): [number, number] {
  const oneStar = 360 / 27; // 13°20'
  
  // Get the planet longitude
  let planetLong = getPlanetLongitude(jd, place, startingPlanet);
  
  // Apply Varga correction if divisional chart specified
  if (divisionalChartFactor > 1) {
    const d1Pos: PlanetPosition = { planet: startingPlanet, rasi: Math.floor(planetLong / 30), longitude: planetLong % 30 };
    const vargaPos = getDivisionalChart([d1Pos], divisionalChartFactor)[0];
    if (vargaPos) {
      planetLong = vargaPos.rasi * 30 + vargaPos.longitude;
    }
  }

  // Adjust for star position from moon
  if (startingPlanet === MOON) {
    planetLong += (starPositionFromMoon - 1) * oneStar;
    planetLong = normalizeDegrees(planetLong);
  }
  
  // Calculate nakshatra and position within it
  const nakIndex = Math.floor(planetLong / oneStar);
  const remainder = planetLong % oneStar;
  
  // Get the lord of this nakshatra
  const lord = getVimsottariAdhipati(nakIndex, seedStar);
  
  // Get the total period for this lord
  const period = DASHA_YEARS[lord] ?? 0;
  
  // Calculate how much of the period has elapsed
  const periodElapsedYears = (remainder / oneStar) * period;
  const periodElapsedDays = periodElapsedYears * YEAR_DURATION;
  
  // Start date is that many days before birth
  const startDate = jd - periodElapsedDays;
  
  return [lord, startDate];
}

// ============================================================================
// MAHADASHA CALCULATION
// ============================================================================

/**
 * Calculate all 9 mahadashas
 * @param jd - Julian Day Number
 * @param place - Place data
 * @param starPositionFromMoon - Which nakshatra to use
 * @param seedStar - Seed star
 * @param startingPlanet - Starting planet
 * @returns Map of lord to start date
 */
export function vimsottariMahadasha(
  jd: number,
  place: Place,
  starPositionFromMoon = 1,
  seedStar = 3,
  startingPlanet = MOON,
  divisionalChartFactor = 1
): Map<number, number> {
  let [lord, startDate] = vimsottariDashaStartDate(
    jd, place, starPositionFromMoon, seedStar, startingPlanet, divisionalChartFactor
  );
  
  const dashas = new Map<number, number>();
  
  for (let i = 0; i < 9; i++) {
    dashas.set(lord, startDate);
    const periodYears = DASHA_YEARS[lord] ?? 0;
    startDate += periodYears * YEAR_DURATION;
    lord = getNextAdhipati(lord);
  }
  
  return dashas;
}

// ============================================================================
// BHUKTI CALCULATION
// ============================================================================

/**
 * Calculate bhuktis (sub-periods) for a mahadasha
 * @param mahaLord - Mahadasha lord
 * @param startDate - Start date of mahadasha
 * @param antardashaOption - Variation option (1-6)
 * @returns Map of bhukti lord to start date
 */
export function vimsottariBhukti(
  mahaLord: number,
  startDate: number,
  antardashaOption = 1
): Map<number, number> {
  let lord = mahaLord;
  
  // Adjust starting lord based on option
  if (antardashaOption === 3 || antardashaOption === 4) {
    lord = getNextAdhipati(lord, 1);
  } else if (antardashaOption === 5 || antardashaOption === 6) {
    lord = getNextAdhipati(lord, -1);
  }
  
  // Direction
  const direction = (antardashaOption === 1 || antardashaOption === 3 || antardashaOption === 5) ? 1 : -1;
  
  const bhuktis = new Map<number, number>();
  
  for (let i = 0; i < 9; i++) {
    bhuktis.set(lord, startDate);
    
    // Bhukti duration = (maha period * bhukti period) / total cycle
    const mahaYears = DASHA_YEARS[mahaLord] ?? 0;
    const bhuktiYears = DASHA_YEARS[lord] ?? 0;
    const factor = (mahaYears * bhuktiYears) / VIMSOTTARI_TOTAL_YEARS;
    
    startDate += factor * YEAR_DURATION;
    lord = getNextAdhipati(lord, direction);
  }
  
  return bhuktis;
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get complete Vimsottari dasha-bhukti data
 * @param jd - Julian Day Number (birth time)
 * @param place - Place data
 * @param options - Calculation options
 * @returns Vimsottari result with balance and periods
 */
export function getVimsottariDashaBhukti(
  jd: number,
  place: Place,
  options: {
    starPositionFromMoon?: number;
    seedStar?: number;
    startingPlanet?: number;
    includeBhuktis?: boolean;
    antardashaOption?: number;
    divisionalChartFactor?: number;
  } = {}
): VimsottariResult {
  const {
    starPositionFromMoon = 1,
    seedStar = 3,
    startingPlanet = MOON,
    includeBhuktis = true,
    antardashaOption = 1,
    divisionalChartFactor = 1
  } = options;
  
  // Get all mahadashas
  const dashaMap = vimsottariMahadasha(jd, place, starPositionFromMoon, seedStar, startingPlanet, divisionalChartFactor);
  
  // Convert to array and add end dates
  const dashaEntries = Array.from(dashaMap.entries());
  const mahadashas: DashaPeriod[] = dashaEntries.map((entry) => {
    const [lord, startJd] = entry;
    const periodYears = DASHA_YEARS[lord] ?? 0;
    const endJd = startJd + periodYears * YEAR_DURATION;
    
    return {
      lord,
      lordName: PLANET_NAMES_EN[lord] ?? `Planet ${lord}`,
      startJd,
      startDate: formatJdAsDate(startJd),
      endJd,
      endDate: formatJdAsDate(endJd),
      durationYears: periodYears
    };
  });
  
  // Calculate balance at birth
  // Find the dasha running at birth
  const firstDasha = mahadashas[0]!;
  const secondDashaStart = mahadashas[1]?.startJd ?? (firstDasha.startJd + firstDasha.durationYears * YEAR_DURATION);
  const daysToSecondDasha = secondDashaStart - jd;
  const balance = daysToYMD(daysToSecondDasha);
  
  if (!includeBhuktis) {
    return {
      balance,
      mahadashas
    };
  }

  // Calculate bhuktis
  const bhuktis: BhuktiPeriod[] = [];
  
  for (const dasha of mahadashas) {
    const bhuktiMap = vimsottariBhukti(dasha.lord, dasha.startJd, antardashaOption);
    
    for (const [bhuktiLord, startJd] of bhuktiMap) {
      bhuktis.push({
        dashaLord: dasha.lord,
        bhuktiLord,
        bhuktiLordName: PLANET_NAMES_EN[bhuktiLord] ?? `Planet ${bhuktiLord}`,
        startJd,
        startDate: formatJdAsDate(startJd)
      });
    }
  }
  
  return {
    balance,
    mahadashas,
    bhuktis
  };
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Find which dasha period a given date falls into
 * @param jd - Julian Day to check
 * @param mahadashas - List of mahadasha periods
 * @returns The mahadasha period or undefined
 */
export function findDashaPeriodForDate(jd: number, mahadashas: DashaPeriod[]): DashaPeriod | undefined {
  for (let i = mahadashas.length - 1; i >= 0; i--) {
    if (mahadashas[i]!.startJd <= jd) {
      return mahadashas[i];
    }
  }
  return undefined;
}
