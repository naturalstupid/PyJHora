/**
 * Yogini Dasha System
 * Ported from PyJHora yogini.py
 * 
 * 36-year cycle with 8 Yoginis (Lords).
 */

import {
  JUPITER,
  MARS,
  MERCURY,
  MOON,
  SATURN,
  SIDEREAL_YEAR,
  SUN,
  VENUS
} from '../../constants';
import { getDivisionalChart, PlanetPosition } from '../../horoscope/charts';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { normalizeDegrees } from '../../utils/angle';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface YoginiDashaPeriod {
  lord: number;
  yoginiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface YoginiBhuktiPeriod {
  dashaLord: number;
  bhuktiLord: number;
  bhuktiYoginiName: string;
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

// const YOGINI_TOTAL_YEARS = 36; // Unused
const YEAR_DURATION = SIDEREAL_YEAR;

/**
 * Yogini Lords and their Durations (Years)
 * Sequence: Mangala(Moon-1), Pingala(Sun-2), Dhanya(Jup-3), Bhramari(Mar-4), 
 *           Bhadrika(Mer-5), Ulka(Sat-6), Siddha(Ven-7), Sankata(Rahu-8)
 */
export const YOGINI_LORDS_ORDER = [MOON, SUN, JUPITER, MARS, MERCURY, SATURN, VENUS, 7]; // 7 is Rahu

export const YOGINI_DURATIONS: Record<number, number> = {
  [MOON]: 1,
  [SUN]: 2,
  [JUPITER]: 3,
  [MARS]: 4,
  [MERCURY]: 5,
  [SATURN]: 6,
  [VENUS]: 7,
  7: 8 // Rahu
};

export const YOGINI_NAMES: Record<number, string> = {
  [MOON]: 'Mangala',
  [SUN]: 'Pingala',
  [JUPITER]: 'Dhanya',
  [MARS]: 'Bhramari',
  [MERCURY]: 'Bhadrika',
  [SATURN]: 'Ulka',
  [VENUS]: 'Siddha',
  7: 'Sankata'
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Generate Nakshatra to Lord mapping
 * @param seedStar - Starting Nakshatra (1-27). Default 7 (Punarvasu) per PyJHora
 * @param seedLord - Starting Lord. Default 0 (Sun/Pingala) per PyJHora
 */
function getYoginiDashaDict(seedStar: number = 7, seedLord: number = SUN): Map<number, number[]> {
  const dict = new Map<number, number[]>();
  YOGINI_LORDS_ORDER.forEach(lord => dict.set(lord, []));

  let nak = seedStar - 1; // 0-indexed

  // Find start index of seedLord in SEQUENCE
  let lordIndex = YOGINI_LORDS_ORDER.indexOf(seedLord);
  if (lordIndex === -1) lordIndex = 0;

  for (let i = 0; i < 27; i++) {
    const lord = YOGINI_LORDS_ORDER[lordIndex]!;
    const nakList = dict.get(lord);
    if (nakList) {
      nakList.push(nak + 1); // 1-indexed
    }

    // Increment
    nak = (nak + 1) % 27;
    lordIndex = (lordIndex + 1) % YOGINI_LORDS_ORDER.length;
  }

  return dict;
}

export function getNextYoginiLord(lord: number, direction: number = 1): number {
  const idx = YOGINI_LORDS_ORDER.indexOf(lord);
  const len = YOGINI_LORDS_ORDER.length;
  const nextIdx = (idx + direction + len) % len;
  return YOGINI_LORDS_ORDER[nextIdx]!;
}

export function getYoginiDhasaLord(nakshatra: number, seedStar: number = 7): [number, number] {
  const dict = getYoginiDashaDict(seedStar, SUN);
  let lord = SUN;
  for (const [l, naks] of dict.entries()) {
    if (naks.includes(nakshatra)) {
      lord = l;
      break;
    }
  }
  return [lord, YOGINI_DURATIONS[lord] ?? 0];
}

function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  const hour12 = time.hour % 12 || 12;
  const ampm = time.hour < 12 ? 'AM' : 'PM';
  const yearStr = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
  return `${yearStr}-${pad(date.month)}-${pad(date.day)} ${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

// ============================================================================
// MAIN CALCULATIONS
// ============================================================================

export function getYoginiDashaBhukti(
  jd: number,
  place: Place,
  options: {
    starPositionFromMoon?: number;
    startingPlanet?: number;
    includeBhuktis?: boolean;
    seedStar?: number;
    divisionalChartFactor?: number;
    cycles?: number;
  } = {}
): YoginiResult {
  const {
    starPositionFromMoon = 1,
    startingPlanet = MOON,
    includeBhuktis = true,
    seedStar = 7,
    divisionalChartFactor = 1,
    cycles = 3
  } = options;

  const oneStar = 360 / 27;
  
  // 1. Calculate Planet Position
  let planetLong = getPlanetLongitude(jd, place, startingPlanet);

  if (divisionalChartFactor > 1) {
    const d1Pos: PlanetPosition = { planet: startingPlanet, rasi: Math.floor(planetLong / 30), longitude: planetLong % 30 };
    const vargaPos = getDivisionalChart([d1Pos], divisionalChartFactor)[0];
    if (vargaPos) planetLong = vargaPos.rasi * 30 + vargaPos.longitude;
  }

  if (startingPlanet === MOON) {
    planetLong += (starPositionFromMoon - 1) * oneStar;
    planetLong = normalizeDegrees(planetLong);
  }

  const nakIndex = Math.floor(planetLong / oneStar);
  const nakNumber = nakIndex + 1;
  const remDegrees = planetLong - (nakIndex * oneStar);
  
  // 2. Identify Dasha Lord for current Nakshatra
  const dashaDict = getYoginiDashaDict(seedStar, SUN); // PyJHora defaults: seedStar=7, seedLord=SUN(0)
  
  let currentDashaLord = SUN; // default
  for (const [lord, naks] of dashaDict.entries()) {
    if (naks.includes(nakNumber)) {
      currentDashaLord = lord;
      break;
    }
  }

  // 3. Calculate Balance
  const duration = YOGINI_DURATIONS[currentDashaLord]!;
  const elapsedYears = (remDegrees / oneStar) * duration;
  const elapsedDays = elapsedYears * YEAR_DURATION;
  
  let startJd = jd - elapsedDays;
  let dhasaLord = currentDashaLord;
  
  const mahadashas: YoginiDashaPeriod[] = [];
  const bhuktis: YoginiBhuktiPeriod[] = [];
  
  for (let c = 0; c < cycles; c++) {
    for (let i = 0; i < YOGINI_LORDS_ORDER.length; i++) {
      const dDuration = YOGINI_DURATIONS[dhasaLord]!;
      const yoginiName = YOGINI_NAMES[dhasaLord]!;

      mahadashas.push({
          lord: dhasaLord,
          yoginiName,
          startJd,
          startDate: formatJdAsDate(startJd),
          durationYears: dDuration
        });

      if (includeBhuktis) {
          let bhuktiLord = dhasaLord; // Default option 1
          const bhuktiCount = YOGINI_LORDS_ORDER.length;
          const bhuktiDuration = dDuration / bhuktiCount; // Equal division logic

          let bStartJd = startJd;

          for (let b = 0; b < bhuktiCount; b++) {
            const bName = YOGINI_NAMES[bhuktiLord]!;
              bhuktis.push({
                   dashaLord: dhasaLord,
                   bhuktiLord,
                   bhuktiYoginiName: bName,
                   startJd: bStartJd,
                   startDate: formatJdAsDate(bStartJd),
                   durationYears: bhuktiDuration
                 });
          bStartJd += bhuktiDuration * YEAR_DURATION;
          bhuktiLord = getNextYoginiLord(bhuktiLord);
        }
      }

      startJd += dDuration * YEAR_DURATION;
      dhasaLord = getNextYoginiLord(dhasaLord);
    }
  }
  
  const result: YoginiResult = { mahadashas };
  if (includeBhuktis) {
    result.bhuktis = bhuktis;
  }
  
  return result;
}
