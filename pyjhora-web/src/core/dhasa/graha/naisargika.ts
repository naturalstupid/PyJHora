/**
 * Naisargika Dasha System
 * Ported from PyJHora naisargika.py
 *
 * Fixed age-based dasha system (132 years total)
 * Periods: Moon(1), Mars(2), Mercury(9), Venus(20), Jupiter(18), Sun(20), Saturn(50), Lagna(12)
 */

import {
    ASCENDANT_SYMBOL,
    JUPITER,
    MARS, MERCURY,
    MOON,
    PLANET_NAMES_EN,
    SATURN,
    SIDEREAL_YEAR,
    SUN,
    VENUS
} from '../../constants';
import { getDivisionalChart, PlanetPosition } from '../../horoscope/charts';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface NaisargikaDashaPeriod {
  lord: number | 'L';  // 'L' for Lagna
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface NaisargikaBhuktiPeriod {
  dashaLord: number | 'L';
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface NaisargikaResult {
  mahadashas: NaisargikaDashaPeriod[];
  bhuktis?: NaisargikaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

/**
 * Bhukti house order: kendras first (1,4,7,10), then (2,5,8,11), then (3,6,9,12)
 * 0-indexed offsets from the dasha lord's house
 */
const BHUKTI_HOUSE_LIST = [0, 3, 6, 9, 1, 4, 7, 10, 2, 5, 8, 11];

/** Houses to exclude with antardhasa_option1: 3rd and 10th (0-indexed: 2, 9) */
const BHUKTI_EXEMPT_LIST_1 = [2, 9];

/** Houses to exclude with antardhasa_option2: 2nd, 6th, 11th, 12th (0-indexed: 1, 5, 10, 11) */
const BHUKTI_EXEMPT_LIST_2 = [1, 5, 10, 11];

/**
 * Naisargika lords and their durations (age-based sequence)
 * Moon(1), Mars(2), Mercury(9), Venus(20), Jupiter(18), Sun(20), Saturn(50), Lagna(12)
 * Total: 132 years
 */
const NAISARGIKA_SEQUENCE: Array<{ lord: number | 'L'; years: number }> = [
  { lord: MOON, years: 1 },
  { lord: MARS, years: 2 },
  { lord: MERCURY, years: 9 },
  { lord: VENUS, years: 20 },
  { lord: JUPITER, years: 18 },
  { lord: SUN, years: 20 },
  { lord: SATURN, years: 50 },
  { lord: 'L', years: 12 }  // Lagna
];

function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  const hour12 = time.hour % 12 || 12;
  const ampm = time.hour < 12 ? 'AM' : 'PM';
  const yearStr = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
  return `${yearStr}-${pad(date.month)}-${pad(date.day)} ${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

/**
 * Build house-to-planet mapping from planet positions.
 * Returns an array of 12 strings, each containing planet indices separated by '/'.
 * Mirrors Python's utils.get_house_planet_list_from_planet_positions.
 *
 * @param planetPositions - Array of PlanetPosition (planets 0-6 = Sun through Saturn,
 *                          index 0 in Python is Lagna but we handle separately)
 * @param ascendantRasi - Rasi of the ascendant
 */
function getHousePlanetList(planetPositions: PlanetPosition[], ascendantRasi: number): string[] {
  const hToP: string[] = Array(12).fill('');

  // Add ascendant (Lagna) to its house
  if (hToP[ascendantRasi] !== '') {
    hToP[ascendantRasi] += '/' + ASCENDANT_SYMBOL;
  } else {
    hToP[ascendantRasi] = ASCENDANT_SYMBOL;
  }

  // Add planets to their houses
  for (const pos of planetPositions) {
    const rasi = pos.rasi;
    const pStr = String(pos.planet);
    if (hToP[rasi] !== '') {
      hToP[rasi] += '/' + pStr;
    } else {
      hToP[rasi] = pStr;
    }
  }

  return hToP;
}

/**
 * Get complete Naisargika dasha data
 * This is age-based: starts from birth and runs through fixed periods.
 * Bhuktis are determined by planets' house positions relative to the dasha lord.
 */
export function getNaisargikaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    includeBhuktis?: boolean;
    mahadhasaLordHasNoAntardhasa?: boolean;
    antardhasaOption1?: boolean;
    antardhasaOption2?: boolean;
    divisionalChartFactor?: number;
  } = {}
): NaisargikaResult {
  const {
    includeBhuktis = false,
    mahadhasaLordHasNoAntardhasa = true,
    antardhasaOption1 = false,
    antardhasaOption2 = false,
    divisionalChartFactor = 1,
  } = options;

  // Build bhukti house list with exemptions applied
  let bhuktiHouseList = [...BHUKTI_HOUSE_LIST];
  if (antardhasaOption1) {
    bhuktiHouseList = bhuktiHouseList.filter(h => !BHUKTI_EXEMPT_LIST_1.includes(h));
  }
  if (antardhasaOption2) {
    bhuktiHouseList = bhuktiHouseList.filter(h => !BHUKTI_EXEMPT_LIST_2.includes(h));
  }

  // Get planet positions (Sun=0 through Saturn=6, Rahu=7 excluded per Python [:8] which is Lagna+7 planets)
  // Python uses planet_positions[:8] which includes Lagna(index 0) + Sun(1) through Rahu(7), ignoring Rahu onwards
  // We compute positions for planets 0-6 (Sun through Saturn) to match Python's exclusion of Rahu/Ketu
  let planetPositions: PlanetPosition[] = [];
  const d1Positions: PlanetPosition[] = [];
  for (let planet = 0; planet <= 6; planet++) {
    const longitude = getPlanetLongitude(jd, place, planet);
    d1Positions.push({
      planet,
      rasi: Math.floor(longitude / 30),
      longitude: longitude % 30
    });
  }

  if (divisionalChartFactor > 1) {
    planetPositions = getDivisionalChart(d1Positions, divisionalChartFactor);
  } else {
    planetPositions = d1Positions;
  }

  // Get ascendant position (use Sun as proxy since sync ascendant is not available)
  // TODO: Replace with actual ascendant when sync ascendant calculation is implemented
  const ascendantRasi = planetPositions[0]?.rasi ?? 0;

  // Build house-to-planet mapping
  const hToP = getHousePlanetList(planetPositions, ascendantRasi);

  let startJd = jd; // Starts from birth

  const mahadashas: NaisargikaDashaPeriod[] = [];
  const bhuktis: NaisargikaBhuktiPeriod[] = [];

  for (const entry of NAISARGIKA_SEQUENCE) {
    const lordName = entry.lord === 'L' ? 'Lagna' : (PLANET_NAMES_EN[entry.lord] ?? `Planet ${entry.lord}`);

    mahadashas.push({
      lord: entry.lord,
      lordName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: entry.years
    });

    if (includeBhuktis) {
      // Determine the dasha lord's house
      let lordHouse: number;
      if (entry.lord === 'L') {
        lordHouse = ascendantRasi;
      } else {
        const lordPos = planetPositions.find(p => p.planet === entry.lord);
        lordHouse = lordPos ? lordPos.rasi : 0;
      }

      // Collect bhukti lords from house positions relative to dasha lord
      const bhuktiLords: number[] = [];
      for (const h of bhuktiHouseList) {
        const houseStr = hToP[(h + lordHouse) % 12] ?? '';
        if (houseStr !== '') {
          const parts = houseStr.split('/');
          for (const p of parts) {
            // Skip Lagna ('L'), Rahu (7), Ketu (8)
            if (p === ASCENDANT_SYMBOL || p === '7' || p === '8') continue;
            const planetNum = parseInt(p, 10);
            if (!isNaN(planetNum)) {
              bhuktiLords.push(planetNum);
            }
          }
        }
      }

      // Remove dasha lord from its own bhuktis if option set
      if (mahadhasaLordHasNoAntardhasa && entry.lord !== 'L') {
        const idx = bhuktiLords.indexOf(entry.lord as number);
        if (idx !== -1) {
          bhuktiLords.splice(idx, 1);
        }
      }

      // Divide duration equally among bhukti lords
      if (bhuktiLords.length > 0) {
        const bhuktiDuration = entry.years / bhuktiLords.length;
        let bhuktiStartJd = startJd;

        for (const bhuktiLord of bhuktiLords) {
          const bhuktiLordName = PLANET_NAMES_EN[bhuktiLord] ?? `Planet ${bhuktiLord}`;

          bhuktis.push({
            dashaLord: entry.lord,
            bhuktiLord,
            bhuktiLordName,
            startJd: bhuktiStartJd,
            startDate: formatJdAsDate(bhuktiStartJd),
            durationYears: Math.round(bhuktiDuration * 100) / 100
          });
          bhuktiStartJd += bhuktiDuration * YEAR_DURATION;
        }
      }
    }

    startJd += entry.years * YEAR_DURATION;
  }

  return includeBhuktis ? { mahadashas, bhuktis } : { mahadashas };
}
