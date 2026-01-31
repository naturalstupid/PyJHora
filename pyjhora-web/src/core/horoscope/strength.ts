/**
 * Shadbala (Six-fold Strength) Calculations
 * Ported from PyJHora strength.py
 *
 * Calculates various planetary strengths including:
 * - Harsha Bala
 * - Pancha Vargeeya Bala
 * - Dwadhasa Vargeeya Bala
 * - Shadbala (Sthana, Kaala, Dig, Cheshta, Naisargika, Drik)
 * - Bhava Bala
 *
 * References:
 * - https://www.scribd.com/document/426763000/Shadbala-and-Bhavabala-Calculation-pdf
 * - https://medium.com/thoughts-on-jyotish/shadbala-the-6-sources-of-strength-4c5befc0c59a
 */

import type { Place } from '../types';
import type { PlanetPosition } from './charts';
import {
  EVEN_SIGNS,
  HOUSE_STRENGTHS_OF_PLANETS,
  JUPITER,
  MARS,
  MERCURY,
  MOON,
  ODD_SIGNS,
  SATURN,
  SIGN_LORDS,
  STRENGTH_ENEMY,
  STRENGTH_EXALTED,
  STRENGTH_FRIEND,
  STRENGTH_OWN_SIGN,
  SUN,
  SUN_TO_SATURN,
  VENUS
} from '../constants';
import { getDivisionalChart } from './charts';
import { normalizeDegrees, roundTo } from '../utils/angle';
import {
  gregorianToJulianDay,
  isLeapYear,
  julianDayToGregorian
} from '../utils/julian';
import {
  sunrise,
  sunset,
  siderealLongitude,
  getAllPlanetPositionsAsync
} from '../ephemeris/swe-adapter';
import { calculateTithi, calculateVara, dayLength, nightLength } from '../panchanga/drik';
import { getHouseOwnerFromPlanetPositions, getHouseToPlanetList, getPlanetToHouseDict } from './house';

// ============================================================================
// STRENGTH CONSTANTS
// ============================================================================

/** Moola Trikona signs for each planet (Sun to Saturn) */
const MOOLA_TRIKONA_OF_PLANETS = [4, 1, 0, 5, 8, 6, 10];

/** Deep exaltation longitudes for planets */
const PLANET_DEEP_EXALTATION_LONGITUDES = [10.0, 33.0, 298.0, 165.0, 95.0, 357.0, 200.0];

/** Deep debilitation longitudes (opposite of exaltation) */
const PLANET_DEEP_DEBILITATION_LONGITUDES = PLANET_DEEP_EXALTATION_LONGITUDES.map(e => (e + 180) % 360);

/** Hadda lords for each sign - (planet, max_degree) pairs */
const HADDA_LORDS: Array<Array<[number, number]>> = [
  [[4, 6], [5, 12], [3, 20], [2, 25], [6, 30]], // Aries
  [[5, 8], [3, 14], [5, 22], [6, 27], [2, 30]], // Taurus
  [[3, 6], [5, 12], [4, 17], [2, 24], [6, 30]], // Gemini
  [[2, 7], [5, 13], [3, 19], [4, 26], [6, 30]], // Cancer
  [[4, 6], [5, 11], [6, 18], [3, 24], [2, 30]], // Leo
  [[3, 7], [5, 17], [4, 21], [2, 28], [6, 30]], // Virgo
  [[6, 6], [3, 14], [4, 21], [5, 28], [2, 30]], // Libra
  [[2, 7], [5, 11], [3, 19], [4, 24], [6, 30]], // Scorpio
  [[4, 12], [5, 17], [3, 21], [2, 26], [6, 30]], // Sagittarius
  [[3, 7], [4, 14], [5, 22], [6, 26], [2, 30]], // Capricorn
  [[3, 7], [5, 13], [4, 20], [2, 25], [6, 30]], // Aquarius (note: original has 50, likely typo, using 30)
  [[5, 12], [4, 16], [3, 19], [2, 28], [6, 30]]  // Pisces
];

/** Hadda bala points: Own, Friend, Enemy */
const HADDA_POINTS = [15, 7.5, 3.75];

/** Harsha bala houses for each planet */
const HARSHA_BALA_HOUSES = [8, 2, 5, 0, 10, 11, 11];

/** Feminine houses for harsha bala */
const HARSHA_BALA_FEMININE_HOUSES = [0, 1, 2, 6, 7, 8];

/** Masculine houses for harsha bala */
const HARSHA_BALA_MASCULINE_HOUSES = [3, 4, 5, 9, 10, 11];

/** Feminine planets */
const FEMININE_PLANETS = [1, 3, 5, 6]; // Moon, Mercury, Venus, Saturn

/** Masculine planets */
const MASCULINE_PLANETS = [0, 2, 4]; // Sun, Mars, Jupiter

/** Naisargika bala values (natural strength) */
const NAISARGIKA_BALA = [60.0, 51.43, 17.14, 25.71, 34.29, 42.86, 8.57];

/** Minimum bhava bala in rupas */
const MINIMUM_BHAVA_BALA_RUPA = 7.0;

/** Planet disc diameters (for yuddha bala) */
const PLANETS_DISC_DIAMETERS = [-1, -1, 9.4, 6.6, 190.4, 16.6, 158.0, -1, -1];

/** Friendly planets for each planet (0-6) */
const FRIENDLY_PLANETS: number[][] = [
  [1, 2, 4],    // Sun: Moon, Mars, Jupiter
  [0, 3],       // Moon: Sun, Mercury
  [0, 1, 4],    // Mars: Sun, Moon, Jupiter
  [0, 5],       // Mercury: Sun, Venus
  [0, 1, 2],    // Jupiter: Sun, Moon, Mars
  [3, 6],       // Venus: Mercury, Saturn
  [3, 5]        // Saturn: Mercury, Venus
];

/** Enemy planets for each planet (0-6) */
const ENEMY_PLANETS: number[][] = [
  [5, 6],       // Sun: Venus, Saturn
  [],           // Moon: none
  [3],          // Mars: Mercury
  [1],          // Mercury: Moon
  [3, 5],       // Jupiter: Mercury, Venus
  [0, 1],       // Venus: Sun, Moon
  [0, 1, 2]     // Saturn: Sun, Moon, Mars
];

/** Compound planet relations matrix */
const COMPOUND_PLANET_RELATIONS = [
  [-1, 5, 5, 4, 3, 3, 3, 3, 3], // Sun
  [5, -1, 2, 5, 2, 2, 4, 1, 1], // Moon
  [5, 3, -1, 3, 3, 2, 4, 1, 5], // Mars
  [5, 3, 4, -1, 2, 5, 2, 4, 2], // Mercury
  [3, 3, 3, 1, -1, 1, 2, 3, 4], // Jupiter
  [3, 1, 2, 5, 2, -1, 5, 3, 5], // Venus
  [3, 3, 3, 3, 2, 5, -1, 5, 1], // Saturn
  [3, 1, 1, 4, 2, 3, 5, -1, 1], // Rahu
  [3, 1, 5, 2, 4, 5, 1, 1, -1]  // Ketu
];

/** Compound relation constants */
const ADHIMITRA_GREATFRIEND = 5;
const MITHRA_FRIEND = 4;
const SAMAM_NEUTRAL = 3;
const SATHRU_ENEMY = 2;
const ADHISATHRU_GREATENEMY = 1;

/** House owners list */
const HOUSE_OWNERS_LIST = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4];

/** Use Saravali formula for uccha bala */
const USE_SARAVALI_FORMULA_FOR_UCCHA_BALA = true;

// ============================================================================
// CHESTA BALA CONSTANTS
// ============================================================================

const EPOCH_YEAR = 1900;
const EPOCH_JD = 2415020.5; // JD for 1900-01-01

/** Planet mean positions at epoch (Ujjain 1900) */
const PLANET_MEAN_POSITIONS_AT_EPOCH = [257.4568, -1, 270.22, 164, 220.04, 328.51, 236.74];

/** Planet speeds at epoch */
const PLANET_SPEED_AT_EPOCH = [0.9856, -1, 0.524, 4.0923, 0.0831, 1.60215, 0.033439];

/** Correction factors per year since epoch: (sign, factor1, factor2) */
const PLANET_CORRECTION_FACTORS: Array<[number, number, number]> = [
  [1, 0, 0],       // Sun
  [1, 0, 0],       // Moon
  [1, 0, 0],       // Mars
  [1, 6.67, -0.00133],  // Mercury
  [-1, 3.3, 0.0067],    // Jupiter
  [-1, 5, 0.0001],      // Venus
  [1, 5, 0.001]         // Saturn
];

/** Ujjain epoch table for planets */
const UJJAIN_EPOCH_TABLE: Record<number, Record<number, number[]>> = {
  0: { // Sun
    1: [0.9856, 98.5602, 265.6026, 136.0265],
    2: [1.9712, 197.1205, 171.2053, 272.0531],
    3: [2.9568, 295.6808, 76.8080, 48.0796],
    4: [3.9424, 34.2411, 342.4106, 184.1062],
    5: [4.9280, 132.8013, 248.0133, 320.1327],
    6: [5.9136, 231.3616, 153.6159, 96.1593],
    7: [6.8992, 329.9218, 59.2186, 232.1868],
    8: [7.8848, 68.4821, 324.8212, 8.2124],
    9: [8.8704, 167.0424, 230.4239, 144.2389]
  },
  2: { // Mars
    1: [0.524, 52.40, 164.02, 200.19],
    2: [1.048, 104.80, 328.04, 40.39],
    3: [1.572, 157.21, 132.06, 240.58],
    4: [2.096, 209.61, 296.08, 80.78],
    5: [2.620, 262.01, 100.10, 280.97],
    6: [3.144, 314.41, 264.12, 121.16],
    7: [3.668, 6.81, 68.14, 321.36],
    8: [4.192, 59.22, 232.15, 161.55],
    9: [4.716, 111.62, 36.17, 1.74]
  },
  3: { // Mercury
    1: [4.09, 40.92, 49.23, 132.32, 243.18],
    2: [8.18, 81.84, 98.46, 264.64, 126.36],
    3: [12.28, 122.77, 147.70, 36.95, 9.54],
    4: [16.37, 163.69, 196.93, 169.27, 252.72],
    5: [20.46, 204.62, 246.16, 301.59, 135.90],
    6: [24.55, 245.54, 295.39, 73.91, 19.08],
    7: [28.65, 286.46, 344.62, 206.23, 262.26],
    8: [32.74, 327.38, 33.85, 338.54, 145.44],
    9: [36.83, 8.31, 83.09, 110.86, 28.63]
  },
  4: { // Jupiter
    1: [0.08, 0.83, 8.31, 83.1, 110.96],
    2: [0.17, 1.66, 16.62, 166.19, 221.93],
    3: [0.25, 2.49, 24.93, 249.29, 332.89],
    4: [0.33, 3.32, 33.24, 332.39, 83.85],
    5: [0.41, 4.15, 41.55, 55.48, 194.82],
    6: [0.50, 4.99, 49.86, 138.58, 305.78],
    7: [0.58, 5.82, 58.17, 221.67, 56.74],
    8: [0.66, 6.65, 66.48, 304.77, 167.71],
    9: [0.75, 7.48, 74.79, 27.87, 278.67]
  },
  5: { // Venus
    1: [1.60, 16.02, 160.21, 162.15, 181.46],
    2: [3.20, 32.04, 320.43, 324.29, 2.93],
    3: [4.81, 48.06, 120.64, 126.44, 184.39],
    4: [6.41, 64.09, 280.86, 288.59, 5.86],
    5: [8.01, 80.11, 81.07, 90.73, 187.32],
    6: [9.61, 96.13, 241.29, 252.88, 8.78],
    7: [11.21, 112.15, 41.50, 55.02, 190.25],
    8: [12.82, 128.17, 201.72, 217.17, 11.71],
    9: [14.42, 144.19, 1.93, 19.32, 193.18]
  },
  6: { // Saturn
    1: [0.03, 0.33, 3.34, 33.44, 334.39],
    2: [0.07, 0.67, 6.69, 66.88, 308.79],
    3: [0.10, 1.00, 10.03, 100.32, 283.18],
    4: [0.13, 1.34, 13.38, 133.76, 257.57],
    5: [0.17, 1.67, 16.72, 167.20, 231.97],
    6: [0.20, 2.01, 20.06, 200.64, 206.36],
    7: [0.23, 2.34, 23.41, 234.08, 180.75],
    8: [0.27, 2.68, 26.75, 267.51, 155.14],
    9: [0.30, 3.01, 30.10, 300.95, 129.54]
  }
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get kendras (angular houses) from ascendant
 */
const getKendras = (ascHouse: number): number[] =>
  [1, 4, 7, 10].map(h => (ascHouse + h - 1) % 12);

/**
 * Get panapharas (succedent houses) from ascendant
 */
const getPanapharas = (ascHouse: number): number[] =>
  [2, 5, 8, 11].map(h => (ascHouse + h - 1) % 12);

/**
 * Get apoklimas (cadent houses) from ascendant
 */
const getApoklimas = (ascHouse: number): number[] =>
  [3, 6, 9, 12].map(h => (ascHouse + h - 1) % 12);

/**
 * Calculate days from epoch for a given JD and place
 */
const daysFromEpoch = (jd: number, placeLongitude: number): number => {
  const ujjainLongitude = 76; // Ujjain longitude
  return jd - EPOCH_JD + (ujjainLongitude - placeLongitude) / 15 / 24;
};

/**
 * Calculate planet longitude correction
 */
const planetLongitudeCorrection = (planetIndex: number, yearsSinceEpoch: number): number => {
  const [sign, factor1, factor2] = PLANET_CORRECTION_FACTORS[planetIndex];
  return sign * (factor1 + factor2 * yearsSinceEpoch);
};

/**
 * Get planet mean longitude using epoch table
 */
const getPlanetMeanLongitudeUsingEpochTable = (
  jd: number,
  place: Place,
  planetIndex: number
): number => {
  if (planetIndex === 1) return 0; // Moon not supported

  const epochTable = UJJAIN_EPOCH_TABLE[planetIndex];
  if (!epochTable) return 0;

  const dfe = daysFromEpoch(jd, place.longitude);
  const { date } = julianDayToGregorian(jd);
  const yearJd = date.year;

  const hasTens = (epochTable[1]?.length ?? 0) > 4;

  const digits = dfe.toString().split('.');
  const wholeDays = parseInt(digits[0]);
  const decimalPart = digits.length > 1 ? parseFloat(`0.${digits[1]}`) : 0;

  const tenThousands = Math.floor(wholeDays / 10000) % 10;
  const thousands = Math.floor(wholeDays / 1000) % 10;
  const hundreds = Math.floor(wholeDays / 100) % 10;
  const tens = Math.floor(wholeDays / 10) % 10;
  const units = wholeDays % 10;
  const tensAndUnits = wholeDays % 100;

  const getValue = (digit: number, colIndex: number): number => {
    const row = epochTable[digit];
    if (!row || colIndex >= row.length) return 0;
    return row[colIndex];
  };

  const valueTenThousands = getValue(tenThousands, (epochTable[1]?.length ?? 4) - 1);
  const valueThousands = getValue(thousands, (epochTable[1]?.length ?? 4) - 2);
  const valueHundreds = getValue(hundreds, (epochTable[1]?.length ?? 4) - 3);

  let combinedUnitsValue: number;
  if (hasTens) {
    const valueTens = getValue(tens, 1);
    const valueUnits = getValue(units, 0);
    combinedUnitsValue = valueTens + valueUnits;
  } else {
    const unitsRow = Math.floor(tensAndUnits / 10);
    const unitsRowValue = getValue(unitsRow, 0);
    combinedUnitsValue = 10 * unitsRowValue;
  }

  const valueDecimal = decimalPart * getValue(1, 0);

  let totalSum = valueTenThousands + valueThousands + valueHundreds +
    combinedUnitsValue + valueDecimal +
    PLANET_MEAN_POSITIONS_AT_EPOCH[planetIndex];

  const yearsSinceEpoch = yearJd - EPOCH_YEAR;
  totalSum += planetLongitudeCorrection(planetIndex, yearsSinceEpoch);

  return totalSum % 360;
};

/**
 * Get planet mean longitude (simple formula)
 */
const getPlanetMeanLongitude = (jd: number, place: Place, planetIndex: number): number => {
  if (planetIndex === 1) return 0;

  const dfe = daysFromEpoch(jd, place.longitude);
  const speed = PLANET_SPEED_AT_EPOCH[planetIndex];
  const { date } = julianDayToGregorian(jd);
  const yearsSinceEpoch = date.year - EPOCH_YEAR;
  const correction = planetLongitudeCorrection(planetIndex, yearsSinceEpoch);

  return (PLANET_MEAN_POSITIONS_AT_EPOCH[planetIndex] + dfe * speed + correction) % 360;
};

/**
 * Find closest elements in an array
 */
const findClosestElements = (arr: number[]): [number, number] => {
  let minDiff = Infinity;
  let closest: [number, number] = [0, 0];

  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      const diff = Math.abs(arr[i] - arr[j]);
      const normalizedDiff = diff > 180 ? 360 - diff : diff;
      if (normalizedDiff < minDiff) {
        minDiff = normalizedDiff;
        closest = [arr[i], arr[j]];
      }
    }
  }

  return closest;
};

/**
 * Days elapsed since base year
 */
const daysElapsedSinceBase = (year: number, baseYear = 1951, baseDays = 174): number => {
  const totalYears = year - baseYear;

  let leapYears = 0;
  for (let y = baseYear + 1; y <= year; y++) {
    if (isLeapYear(y)) leapYears++;
  }

  const nonLeapYears = totalYears - leapYears;
  return baseDays + (leapYears * 366) + (nonLeapYears * 365);
};

// ============================================================================
// UCHCHA BALA (Exaltation Strength)
// ============================================================================

/**
 * Calculate Uchcha Bala (exaltation strength) for all planets
 */
export const calculateUchchaBala = (planetPositions: PlanetPosition[]): number[] => {
  const ub: number[] = [];

  for (let p = 0; p < 7; p++) {
    const pos = planetPositions.find(pp => pp.planet === p);
    if (!pos) {
      ub.push(0);
      continue;
    }

    const pLong = pos.rasi * 30 + pos.longitude;
    let pd = (pLong + 360 - PLANET_DEEP_DEBILITATION_LONGITUDES[p]) % 360;

    if (pd > 180) pd = 360 - pd;

    if (USE_SARAVALI_FORMULA_FOR_UCCHA_BALA) {
      ub.push(roundTo(pd / 3, 2));
    } else {
      ub.push(roundTo((pd / 180) * 20, 2));
    }
  }

  return ub;
};

// ============================================================================
// SAPTAVARGAJA BALA
// ============================================================================

/**
 * Calculate Saptavargaja Bala
 */
export const calculateSaptavargajaBala = (
  d1Positions: PlanetPosition[],
  jd: number,
  place: Place
): number[] => {
  const sv = [1, 2, 3, 7, 9, 12, 30];
  const charts: Record<number, PlanetPosition[]> = {};

  for (const dcf of sv) {
    charts[dcf] = getDivisionalChart(d1Positions, dcf);
  }

  // Get compound relationships
  const hToP = getHouseToPlanetList(d1Positions);

  const svb: number[][] = [];
  for (const dcf of sv) {
    const svbc = calculateSaptavargajaBalaForChart(charts[dcf], dcf);
    svb.push(svbc);
  }

  // Sum up all the balas
  const result: number[] = new Array(7).fill(0);
  for (const row of svb) {
    for (let i = 0; i < 7; i++) {
      result[i] += row[i];
    }
  }

  return result.map(v => roundTo(v, 2));
};

/**
 * Calculate Saptavargaja Bala for a single chart
 */
const calculateSaptavargajaBalaForChart = (
  planetPositions: PlanetPosition[],
  dcf: number
): number[] => {
  const sb: number[] = new Array(8).fill(0);

  const sbFac: Record<number, number> = {
    [ADHISATHRU_GREATENEMY - 1]: 1.875,
    [SATHRU_ENEMY - 1]: 3.75,
    [SAMAM_NEUTRAL - 1]: 7.5,
    [MITHRA_FRIEND - 1]: 15,
    [ADHIMITRA_GREATFRIEND - 1]: 22.5
  };

  for (let p = 0; p < 7; p++) {
    const pos = planetPositions.find(pp => pp.planet === p);
    if (!pos) continue;

    const h = pos.rasi;
    const owner = HOUSE_OWNERS_LIST[h];

    if (h === MOOLA_TRIKONA_OF_PLANETS[p] && dcf === 1) {
      sb[p] = 45;
    } else if (HOUSE_STRENGTHS_OF_PLANETS[p]?.[h] === STRENGTH_OWN_SIGN) {
      sb[p] = 30;
    } else {
      const relation = COMPOUND_PLANET_RELATIONS[p]?.[owner] ?? SAMAM_NEUTRAL;
      sb[p] = sbFac[relation - 1] ?? 7.5;
    }
  }

  return sb.slice(0, 7);
};

// ============================================================================
// OJAYUGAMA BALA
// ============================================================================

/**
 * Calculate Ojayugama Bala (odd-even strength)
 */
export const calculateOjayugamaBala = (
  rasiPositions: PlanetPosition[],
  navamsaPositions: PlanetPosition[]
): number[] => {
  const sb: number[] = new Array(7).fill(0);

  for (let p = 0; p < 7; p++) {
    const rasiPos = rasiPositions.find(pp => pp.planet === p);
    const navPos = navamsaPositions.find(pp => pp.planet === p);

    if (!rasiPos || !navPos) continue;

    const rh = rasiPos.rasi;
    const nh = navPos.rasi;

    // Moon and Venus prefer even signs, others prefer odd
    if (p === MOON || p === VENUS) {
      if (EVEN_SIGNS.includes(rh)) sb[p] = 15;
      if (EVEN_SIGNS.includes(nh)) sb[p] += 15;
    } else {
      if (ODD_SIGNS.includes(rh)) sb[p] = 15;
      if (ODD_SIGNS.includes(nh)) sb[p] += 15;
    }
  }

  return sb;
};

// ============================================================================
// KENDRA BALA
// ============================================================================

/**
 * Calculate Kendra Bala (angular house strength)
 */
export const calculateKendraBala = (rasiPositions: PlanetPosition[]): number[] => {
  const kb: number[] = new Array(7).fill(0);

  const ascPos = rasiPositions.find(pp => pp.planet === -1);
  const ascHouse = ascPos?.rasi ?? 0;

  const kendras = getKendras(ascHouse);
  const panapharas = getPanapharas(ascHouse);
  const apoklimas = getApoklimas(ascHouse);

  for (let p = 0; p < 7; p++) {
    const pos = rasiPositions.find(pp => pp.planet === p);
    if (!pos) continue;

    const h = pos.rasi;

    if (kendras.includes(h)) {
      kb[p] = 60;
    } else if (panapharas.includes(h)) {
      kb[p] = 30;
    } else if (apoklimas.includes(h)) {
      kb[p] = 15;
    }
  }

  return kb;
};

// ============================================================================
// DREKKANA BALA
// ============================================================================

/**
 * Calculate Dreshkon Bala
 */
export const calculateDreshkonBala = (planetPositions: PlanetPosition[]): number[] => {
  const kb: number[] = new Array(7).fill(0);

  // Planets benefiting from each drekkana (1st, 2nd, 3rd part of sign)
  const kbf: number[][] = [[0, 2, 4], [3, 6], [1, 5]];

  for (let p = 0; p < 7; p++) {
    const pos = planetPositions.find(pp => pp.planet === p);
    if (!pos) continue;

    const pd = Math.floor(pos.longitude / 10);
    if (kbf[pd]?.includes(p)) {
      kb[p] = 15;
    }
  }

  return kb;
};

// ============================================================================
// STHANA BALA (Positional Strength)
// ============================================================================

/**
 * Calculate Sthana Bala (positional strength)
 */
export const calculateSthanaBala = (
  d1Positions: PlanetPosition[],
  jd: number,
  place: Place
): number[] => {
  const d9Positions = getDivisionalChart(d1Positions, 9);

  const ub = calculateUchchaBala(d1Positions);
  const svb = calculateSaptavargajaBala(d1Positions, jd, place);
  const ob = calculateOjayugamaBala(d1Positions, d9Positions);
  const kb = calculateKendraBala(d1Positions);
  const db = calculateDreshkonBala(d1Positions);

  const sb: number[] = [];
  for (let i = 0; i < 7; i++) {
    sb.push(roundTo(ub[i] + svb[i] + ob[i] + kb[i] + db[i], 2));
  }

  return sb;
};

// ============================================================================
// KAALA BALA COMPONENTS
// ============================================================================

/**
 * Calculate Nathonnath Bala (day/night strength)
 */
export const calculateNathonnathBala = (jd: number, place: Place): number[] => {
  const nbp: number[] = new Array(7).fill(0);

  const { date, time } = julianDayToGregorian(jd);
  const tobh = time.hour + time.minute / 60 + time.second / 3600;

  // Approximate midnight
  const mnhl = 0;
  const tDiff = tobh < 12 ? (tobh - mnhl) * 60 / 12 : (24 + mnhl - tobh) * 60 / 12;

  // Diurnal planets (Sun, Jupiter, Venus) get strength during day
  for (const p of [0, 4, 5]) {
    nbp[p] = roundTo(tDiff, 2);
  }

  // Nocturnal planets (Moon, Mars, Saturn) get strength during night
  for (const p of [1, 2, 6]) {
    nbp[p] = roundTo(60 - tDiff, 2);
  }

  // Mercury always gets 60
  nbp[3] = 60;

  return nbp;
};

/**
 * Calculate Paksha Bala (lunar fortnight strength)
 */
export const calculatePakshaBala = (
  jd: number,
  place: Place,
  d1Positions: PlanetPosition[]
): number[] => {
  const sunPos = d1Positions.find(p => p.planet === SUN);
  const moonPos = d1Positions.find(p => p.planet === MOON);

  if (!sunPos || !moonPos) return new Array(7).fill(0);

  const sunLong = sunPos.rasi * 30 + sunPos.longitude;
  const moonLong = moonPos.rasi * 30 + moonPos.longitude;

  const pb = roundTo(Math.abs(sunLong - moonLong) / 3, 2);
  const pbp: number[] = new Array(7).fill(pb);

  // Get benefics and malefics
  const tithi = calculateTithi(jd, place);
  const waxingMoon = tithi.number <= 15;

  // Natural benefics (Jupiter, Venus, waxing Moon, Mercury with benefics)
  const benefics = waxingMoon ? [1, 3, 4, 5] : [3, 4, 5];
  const malefics = waxingMoon ? [0, 2, 6] : [0, 1, 2, 6];

  for (const p of benefics) {
    pbp[p] = pb;
  }

  for (const p of malefics) {
    pbp[p] = roundTo(60 - pb, 2);
  }

  // Moon gets double
  pbp[1] *= 2;

  return pbp;
};

/**
 * Calculate Tribhaga Bala
 */
export const calculateTribhagaBala = (jd: number, place: Place): number[] => {
  const tbp: number[] = new Array(7).fill(0);

  const { time } = julianDayToGregorian(jd);
  const tobh = time.hour + time.minute / 60 + time.second / 3600;

  const sunriseData = sunrise(jd, place);
  const sunsetData = sunset(jd, place);
  const srh = sunriseData.localTime;
  const ssh = sunsetData.localTime;

  const dl = dayLength(jd, place);
  const nl = nightLength(jd, place);
  const dlinc = dl / 3;
  const nlinc = nl / 3;

  // Jupiter always gets 60
  tbp[4] = 60;

  if (tobh >= srh && tobh < srh + dlinc) {
    tbp[3] = 60; // Mercury - 1st part of day
  } else if (tobh >= srh + dlinc && tobh < srh + 2 * dlinc) {
    tbp[0] = 60; // Sun - 2nd part of day
  } else if (tobh >= srh + 2 * dlinc && tobh < ssh) {
    tbp[6] = 60; // Saturn - 3rd part of day
  } else if (tobh > ssh && tobh < ssh + nlinc) {
    tbp[1] = 60; // Moon - 1st part of night
  } else if ((tobh >= ssh + nlinc && tobh < 24) || (tobh >= 0 && tobh < srh - nlinc)) {
    tbp[5] = 60; // Venus - 2nd part of night
  } else if (tobh >= srh - nlinc && tobh < srh) {
    tbp[2] = 60; // Mars - 3rd part of night
  }

  return tbp;
};

/**
 * Calculate Abda Bala (year lord strength)
 */
export const calculateAbdadhipathiBala = (jd: number, place: Place): number[] => {
  const abp: number[] = new Array(7).fill(0);
  const abdaWeekdays = [2, 3, 4, 5, 6, 0, 1]; // Starts from Tuesday

  const { date } = julianDayToGregorian(jd);
  const year = date.year;

  const jan1Jd = gregorianToJulianDay({ year, month: 1, day: 1 });
  const elapsedDays = Math.floor(jd - jan1Jd + 1);
  const ahargana = daysElapsedSinceBase(year - 1) + elapsedDays;

  const day = (Math.floor(ahargana / 360) * 3 + 1) % 7;
  abp[abdaWeekdays[day]] = 15;

  return abp;
};

/**
 * Calculate Masa Bala (month lord strength)
 */
export const calculateMasadhipathiBala = (jd: number, place: Place): number[] => {
  const abp: number[] = new Array(7).fill(0);
  const abdaWeekdays = [2, 3, 4, 5, 6, 0, 1];

  const { date } = julianDayToGregorian(jd);
  const year = date.year;

  const jan1Jd = gregorianToJulianDay({ year, month: 1, day: 1 });
  const elapsedDays = Math.floor(jd - jan1Jd + 1);
  const ahargana = daysElapsedSinceBase(year - 1) + elapsedDays;

  const day = (Math.floor(ahargana / 30) * 2 + 1) % 7;
  abp[abdaWeekdays[day]] = 30;

  return abp;
};

/**
 * Calculate Vaara Bala (weekday lord strength)
 */
export const calculateVaaradhipathiBala = (jd: number, place: Place): number[] => {
  const abp: number[] = new Array(7).fill(0);
  const abdaWeekdays = [2, 3, 4, 5, 6, 0, 1];

  const { date, time } = julianDayToGregorian(jd);
  const bth = time.hour + time.minute / 60;
  const year = date.year;

  const jan1Jd = gregorianToJulianDay({ year, month: 1, day: 1 });
  const elapsedDays = Math.floor(jd - jan1Jd + 1);
  let ahargana = daysElapsedSinceBase(year - 1, 1827, 244) + elapsedDays;

  const sunriseData = sunrise(jd, place);
  if (bth < sunriseData.localTime) ahargana -= 1;

  const day = Math.floor(ahargana) % 7;
  abp[abdaWeekdays[day]] = 45;

  return abp;
};

/**
 * Calculate Hora Bala (hour lord strength)
 */
export const calculateHoraBala = (jd: number, place: Place): number[] => {
  const abp: number[] = new Array(7).fill(0);

  const vara = calculateVara(jd);
  let day = vara.number;

  const { time } = julianDayToGregorian(jd);
  let tobh = time.hour + time.minute / 60;

  const sunriseData = sunrise(jd, place);
  const srise = sunriseData.localTime;

  if (tobh < srise) {
    day = (day - 1 + 7) % 7;
    tobh += 24;
  }

  const horaOrder = [6, 4, 2, 0, 5, 3, 1];
  const hora = (Math.floor(tobh - srise) + day + 1) % 7;
  abp[horaOrder[hora]] = 60;

  return abp;
};

/**
 * Calculate Ayana Bala
 */
export const calculateAyanaBala = (jd: number, place: Place): number[] => {
  const ab: number[] = new Array(7).fill(0);

  // Simplified declination calculation
  // Full implementation would use drik.declination_of_planets
  for (let p = 0; p < 7; p++) {
    // Approximate declination (simplified)
    ab[p] = roundTo((24 + 0) * 1.25, 2); // Placeholder
    if (p === 0) ab[p] *= 2;
  }

  return ab;
};

/**
 * Calculate Yuddha Bala (planetary war strength)
 */
export const calculateYuddhaBala = (
  jd: number,
  place: Place,
  d1Positions: PlanetPosition[]
): number[] => {
  const yb: number[] = new Array(7).fill(0);

  const pLongs = d1Positions.slice(0, 7).map(p => p.rasi * 30 + p.longitude);

  const [ce1, ce2] = findClosestElements(pLongs);
  const indices = [pLongs.indexOf(ce1), pLongs.indexOf(ce2)].filter(i => i >= 0);

  // If Sun or Moon involved, no yuddha
  if (indices.includes(0) || indices.includes(1)) {
    return yb;
  }

  if (indices.length < 2) return yb;

  // Calculate sum of balas for involved planets
  const sb = calculateSthanaBala(d1Positions, jd, place);
  const dgb = calculateDigBala(jd, place, d1Positions);
  const nb = calculateNathonnathBala(jd, place);
  const pb = calculatePakshaBala(jd, place, d1Positions);
  const tb = calculateTribhagaBala(jd, place);
  const hb = calculateHoraBala(jd, place);

  const balaTotals: number[] = new Array(7).fill(0);
  for (const i of indices) {
    balaTotals[i] = sb[i] + dgb[i] + nb[i] + pb[i] + tb[i] + hb[i];
  }

  const bDiff = Math.abs(balaTotals[indices[0]] - balaTotals[indices[1]]);
  const diaDiff = Math.abs(
    PLANETS_DISC_DIAMETERS[indices[0]] - PLANETS_DISC_DIAMETERS[indices[1]]
  );

  const yBala = diaDiff > 0 ? roundTo(bDiff / diaDiff, 2) : 0;

  yb[indices[0]] = yBala;
  yb[indices[1]] = -yBala;

  return yb;
};

/**
 * Calculate Kaala Bala (temporal strength)
 */
export const calculateKaalaBala = (
  jd: number,
  place: Place,
  d1Positions: PlanetPosition[]
): number[] => {
  const nb = calculateNathonnathBala(jd, place);
  const pb = calculatePakshaBala(jd, place, d1Positions);
  const tb = calculateTribhagaBala(jd, place);
  const ab = calculateAbdadhipathiBala(jd, place);
  const mb = calculateMasadhipathiBala(jd, place);
  const vb = calculateVaaradhipathiBala(jd, place);
  const hb = calculateHoraBala(jd, place);
  const ayb = calculateAyanaBala(jd, place);
  const yb = calculateYuddhaBala(jd, place, d1Positions);

  const kb: number[] = [];
  for (let p = 0; p < 7; p++) {
    const total = nb[p] + pb[p] + tb[p] + ab[p] + mb[p] + vb[p] + hb[p] + ayb[p] + yb[p];
    kb.push(roundTo(total, 2));
  }

  return kb;
};

// ============================================================================
// DIG BALA (Directional Strength)
// ============================================================================

/**
 * Calculate Dig Bala (directional strength)
 */
export const calculateDigBala = (
  jd: number,
  place: Place,
  d1Positions: PlanetPosition[]
): number[] => {
  // Powerless houses for each planet (0-indexed)
  const powerlessHouses = [3, 9, 3, 6, 6, 9, 0];

  // Simplified bhava madhya (house cusp midpoints)
  const ascPos = d1Positions.find(p => p.planet === -1);
  const ascLong = ascPos ? ascPos.rasi * 30 + ascPos.longitude : 0;

  const bm: number[] = [];
  for (let h = 0; h < 12; h++) {
    bm.push((ascLong + h * 30) % 360);
  }

  const dbf = powerlessHouses.map(h => bm[h]);
  const dbp: number[] = new Array(7).fill(0);

  for (let p = 0; p < 7; p++) {
    const pos = d1Positions.find(pp => pp.planet === p);
    if (!pos) continue;

    const pLong = pos.rasi * 30 + pos.longitude;
    dbp[p] = roundTo(Math.abs(dbf[p] - pLong) / 3, 2);
  }

  return dbp;
};

// ============================================================================
// CHESHTA BALA (Motional Strength)
// ============================================================================

/**
 * Calculate Cheshta Bala (motional strength)
 */
export const calculateCheshtaBala = (
  jd: number,
  place: Place,
  d1Positions: PlanetPosition[],
  useEpochTable = true
): number[] => {
  const cb: number[] = new Array(7).fill(0);

  const sunMeanLong = getPlanetMeanLongitude(jd, place, SUN);

  for (const p of [MARS, MERCURY, JUPITER, VENUS, SATURN]) {
    const meanLong = useEpochTable
      ? getPlanetMeanLongitudeUsingEpochTable(jd, place, p)
      : getPlanetMeanLongitude(jd, place, p);

    let seegrocha = sunMeanLong;
    let adjustedMeanLong = meanLong;

    if (p === MERCURY || p === VENUS) {
      seegrocha = meanLong;
      adjustedMeanLong = sunMeanLong;
    }

    const pos = d1Positions.find(pp => pp.planet === p);
    if (!pos) continue;

    const trueLong = pos.rasi * 30 + pos.longitude;
    const aveLong = 0.5 * (trueLong + adjustedMeanLong);
    const reducedCheshtaKendra = Math.abs(seegrocha - aveLong);

    cb[p] = roundTo(reducedCheshtaKendra / 3, 2);
  }

  return cb;
};

// ============================================================================
// NAISARGIKA BALA (Natural Strength)
// ============================================================================

/**
 * Calculate Naisargika Bala (natural strength)
 */
export const calculateNaisargikaBala = (): number[] => {
  return [...NAISARGIKA_BALA];
};

// ============================================================================
// DRIK BALA (Aspectual Strength)
// ============================================================================

/**
 * Calculate aspect strength between two longitudes
 */
const calculateDrikBalaValue = (dkAngle: number, aspectingPlanet: number): number => {
  let value = 0;

  if (dkAngle >= 0 && dkAngle <= 30) {
    value = 0;
  } else if (dkAngle > 30 && dkAngle <= 60) {
    value = 0.5 * (dkAngle - 30);
  } else if (dkAngle > 60 && dkAngle <= 90) {
    value = (dkAngle - 60) + 15;
    if (aspectingPlanet === 6) value += 45; // Saturn special aspect
  } else if (dkAngle > 90 && dkAngle <= 120) {
    value = 0.5 * (120 - dkAngle) + 30;
    if (aspectingPlanet === 2) value += 15; // Mars special aspect
  } else if (dkAngle > 120 && dkAngle <= 150) {
    value = 150 - dkAngle;
    if (aspectingPlanet === 4) value += 30; // Jupiter special aspect
  } else if (dkAngle > 150 && dkAngle <= 180) {
    value = 2 * (dkAngle - 150);
  } else if (dkAngle > 180 && dkAngle <= 300) {
    value = 0.5 * (300 - dkAngle);
    if (aspectingPlanet === 2 && dkAngle >= 210 && dkAngle <= 240) value += 15;
    if (aspectingPlanet === 4 && dkAngle >= 240 && dkAngle <= 270) value += 30;
    if (aspectingPlanet === 6 && dkAngle >= 270 && dkAngle <= 300) value += 45;
  }

  return value;
};

/**
 * Calculate Drik Bala (aspectual strength)
 */
export const calculateDrikBala = (
  jd: number,
  place: Place,
  d1Positions: PlanetPosition[]
): number[] => {
  const dk: number[][] = Array.from({ length: 7 }, () => new Array(7).fill(0));

  const tithi = calculateTithi(jd, place);
  const waxingMoon = tithi.number <= 15;

  // Natural benefics (adjusted for lunar phase)
  const subhaGrahas = waxingMoon ? [1, 3, 4, 5] : [3, 4, 5];
  const asubhaGrahas = waxingMoon ? [0, 2, 6] : [0, 1, 2, 6];

  // Calculate aspect matrix
  for (let p1 = 0; p1 < 7; p1++) {
    const pos1 = d1Positions.find(p => p.planet === p1);
    if (!pos1) continue;
    const p1Long = pos1.rasi * 30 + pos1.longitude;

    for (let p2 = 0; p2 < 7; p2++) {
      const pos2 = d1Positions.find(p => p.planet === p2);
      if (!pos2) continue;
      const p2Long = pos2.rasi * 30 + pos2.longitude;

      const dkAngle = normalizeDegrees(p1Long - p2Long);
      dk[p1][p2] = roundTo(calculateDrikBalaValue(dkAngle, p2), 2);
    }
  }

  // Transpose the matrix
  const dkT: number[][] = Array.from({ length: 7 }, (_, i) =>
    Array.from({ length: 7 }, (_, j) => dk[j][i])
  );

  // Calculate final drik bala
  const dkp: number[] = new Array(7).fill(0);
  const dkm: number[] = new Array(7).fill(0);
  const dkFinal: number[] = new Array(7).fill(0);

  for (let row = 0; row < 7; row++) {
    for (let col = 0; col < 7; col++) {
      if (subhaGrahas.includes(row)) {
        dkp[col] += dkT[row][col];
      }
      if (asubhaGrahas.includes(row)) {
        dkm[col] += dkT[row][col];
      }
    }
  }

  for (let col = 0; col < 7; col++) {
    dkFinal[col] = roundTo((dkp[col] - dkm[col]) / 4, 2);
  }

  return dkFinal;
};

// ============================================================================
// SHADBALA (Six-fold Strength)
// ============================================================================

/**
 * Shadbala result interface
 */
export interface ShadBalaResult {
  sthanaBala: number[];
  kaalaBala: number[];
  digBala: number[];
  cheshtaBala: number[];
  naisargikaBala: number[];
  drikBala: number[];
  total: number[];
  rupas: number[];
  strength: number[];
}

/**
 * Calculate Shadbala (six-fold strength)
 */
export const calculateShadBala = (
  jd: number,
  place: Place,
  d1Positions: PlanetPosition[]
): ShadBalaResult => {
  const stb = calculateSthanaBala(d1Positions, jd, place);
  const kb = calculateKaalaBala(jd, place, d1Positions);
  const dgb = calculateDigBala(jd, place, d1Positions);
  const cb = calculateCheshtaBala(jd, place, d1Positions, true);
  const nb = calculateNaisargikaBala();
  const dkb = calculateDrikBala(jd, place, d1Positions);

  // Sum all balas
  const total: number[] = [];
  for (let i = 0; i < 7; i++) {
    total.push(roundTo(stb[i] + kb[i] + dgb[i] + cb[i] + nb[i] + dkb[i], 2));
  }

  // Convert to rupas (divide by 60)
  const rupas = total.map(t => roundTo(t / 60, 2));

  // Required strength for each planet
  const sbReq = [5, 6, 5, 7, 6.5, 5.5, 5];
  const strength = rupas.map((r, i) => roundTo(r / sbReq[i], 2));

  return {
    sthanaBala: stb,
    kaalaBala: kb,
    digBala: dgb,
    cheshtaBala: cb,
    naisargikaBala: nb,
    drikBala: dkb,
    total,
    rupas,
    strength
  };
};

// ============================================================================
// BHAVA BALA (House Strength)
// ============================================================================

/**
 * Calculate Bhava Adhipathi Bala (house lord strength)
 */
export const calculateBhavaAdhipathiBala = (
  jd: number,
  place: Place,
  d1Positions: PlanetPosition[]
): number[] => {
  const ascPos = d1Positions.find(p => p.planet === -1);
  const ascRasi = ascPos?.rasi ?? 0;

  const shadBala = calculateShadBala(jd, place, d1Positions);
  const sbSum = shadBala.total;

  const bb: number[] = [];
  for (let h = 0; h < 12; h++) {
    const r = (h + ascRasi) % 12;
    const owner = SIGN_LORDS[r];
    bb.push(sbSum[owner] ?? 0);
  }

  return bb;
};

/**
 * Calculate Bhava Dig Bala (house directional strength)
 */
export const calculateBhavaDigBala = (
  jd: number,
  place: Place,
  d1Positions: PlanetPosition[]
): number[] => {
  const bdb: number[] = new Array(12).fill(0);

  const ascPos = d1Positions.find(p => p.planet === -1);
  const ascLong = ascPos ? ascPos.rasi * 30 + ascPos.longitude : 0;

  // Simplified bhava madhya
  const bm: number[] = [];
  for (let h = 0; h < 12; h++) {
    bm.push((ascLong + h * 30) % 360);
  }

  // Nara (human), Jalachara (aquatic), Chatushpada (quadruped), Keeta (insect) rasis
  const naraRanges = [[60, 90], [150, 180], [180, 210], [240, 255], [300, 330]];
  const jalacharaRanges = [[90, 120], [285, 300], [330, 360]];
  const chatushpadaRanges = [[0, 30], [30, 60], [120, 150], [255, 270], [270, 285]];
  const keetaRanges = [[210, 240]];

  // Base directions for each type
  const typeBaseHouses: Record<number, number[][]> = {
    0: naraRanges,       // 1st house
    3: jalacharaRanges,  // 4th house
    9: chatushpadaRanges, // 10th house
    6: keetaRanges       // 7th house
  };

  for (let h = 0; h < 12; h++) {
    const bmh = bm[h];

    for (const [baseHouse, ranges] of Object.entries(typeBaseHouses)) {
      for (const [r1, r2] of ranges) {
        if (bmh >= r1 && bmh <= r2) {
          const distance = Math.abs(h - parseInt(baseHouse));
          bdb[h] = Math.max(bdb[h], 60 - Math.min(distance, 12 - distance) * 10);
        }
      }
    }
  }

  return bdb;
};

/**
 * Bhava Bala result interface
 */
export interface BhavaBalaResult {
  total: number[];
  rupas: number[];
  strength: number[];
}

/**
 * Calculate Bhava Bala (house strength)
 */
export const calculateBhavaBala = (
  jd: number,
  place: Place,
  d1Positions: PlanetPosition[]
): BhavaBalaResult => {
  const bab = calculateBhavaAdhipathiBala(jd, place, d1Positions);
  const bdb = calculateBhavaDigBala(jd, place, d1Positions);

  // Simplified bhava drik bala (aspectual strength on houses)
  const bdrb: number[] = new Array(12).fill(0);

  // Sum all components
  const bb = bab.map((v, i) => roundTo(v + bdb[i] + bdrb[i], 2));
  const rupas = bb.map(b => roundTo(b / 60, 2));
  const strength = rupas.map(b => roundTo(b / MINIMUM_BHAVA_BALA_RUPA, 2));

  return { total: bb, rupas, strength };
};

// ============================================================================
// HARSHA BALA
// ============================================================================

/**
 * Harsha Bala result
 */
export type HarshaBalaResult = Record<number, number>;

/**
 * Calculate Harsha Bala
 */
export const calculateHarshaBala = (
  jd: number,
  place: Place,
  d1Positions: PlanetPosition[],
  divisionalFactor = 1
): HarshaBalaResult => {
  const sunriseData = sunrise(jd, place);
  const sunsetData = sunset(jd, place);

  const { time } = julianDayToGregorian(jd);
  const fh = time.hour + time.minute / 60 + time.second / 3600;

  const newYearDaytimeStart = fh >= sunriseData.localTime && fh <= sunsetData.localTime;

  const positions = divisionalFactor === 1
    ? d1Positions
    : getDivisionalChart(d1Positions, divisionalFactor);

  const pToH = getPlanetToHouseDict(positions);
  const ascPos = d1Positions.find(p => p.planet === -1);
  const ascHouse = ascPos?.rasi ?? 0;

  const harshaBala: HarshaBalaResult = {};
  for (let p = 0; p < 7; p++) {
    harshaBala[p] = 0;
  }

  for (let p = 0; p < 7; p++) {
    const hP = pToH[p] ?? 0;
    const hFA = (hP - ascHouse + 12) % 12;

    // Rule 1: Planet in harsha bala house
    if (HARSHA_BALA_HOUSES[p] === hFA) {
      harshaBala[p] += 5;
    }

    // Rule 2: Exalted or own house
    const strength = HOUSE_STRENGTHS_OF_PLANETS[p]?.[hP] ?? 0;
    if (strength > STRENGTH_FRIEND || SIGN_LORDS[hP] === p) {
      harshaBala[p] += 5;
    }

    // Rule 3: Feminine/masculine placement
    if (FEMININE_PLANETS.includes(p) && HARSHA_BALA_FEMININE_HOUSES.includes(hFA)) {
      harshaBala[p] += 5;
    } else if (MASCULINE_PLANETS.includes(p) && HARSHA_BALA_MASCULINE_HOUSES.includes(hFA)) {
      harshaBala[p] += 5;
    }

    // Rule 4: Day/night birth
    if (newYearDaytimeStart && MASCULINE_PLANETS.includes(p)) {
      harshaBala[p] += 5;
    } else if (!newYearDaytimeStart && FEMININE_PLANETS.includes(p)) {
      harshaBala[p] += 5;
    }
  }

  return harshaBala;
};

// ============================================================================
// PANCHA VARGEEYA BALA
// ============================================================================

/**
 * Calculate Kshetra Bala
 */
const calculateKshetraBala = (d1Positions: PlanetPosition[]): number[] => {
  const kb: number[] = new Array(7).fill(0);
  const pToH = getPlanetToHouseDict(d1Positions);

  for (let p = 0; p < 7; p++) {
    const hP = pToH[p] ?? 0;
    const strength = HOUSE_STRENGTHS_OF_PLANETS[p]?.[hP] ?? 0;

    if (strength > STRENGTH_FRIEND) {
      kb[p] = 30;
    } else if (strength === STRENGTH_FRIEND) {
      kb[p] = 15;
    } else if (strength === STRENGTH_ENEMY) {
      kb[p] = 7.5;
    }
  }

  return kb;
};

/**
 * Calculate Hadda points for a planet
 */
const getHaddaPoints = (rasi: number, pLong: number, planet: number): number => {
  const lRange = HADDA_LORDS[rasi];
  if (!lRange) return 0;

  const hp = lRange.find(([_, maxLong]) => pLong <= maxLong)?.[0];
  if (hp === undefined) return 0;

  if (planet === hp) {
    return HADDA_POINTS[0];
  } else if (FRIENDLY_PLANETS[planet]?.includes(hp)) {
    return HADDA_POINTS[1];
  } else if (ENEMY_PLANETS[planet]?.includes(hp)) {
    return HADDA_POINTS[2];
  }

  return 0;
};

/**
 * Calculate Hadda Bala
 */
const calculateHaddaBala = (d1Positions: PlanetPosition[]): number[] => {
  const hb: number[] = [];

  for (let p = 0; p < 7; p++) {
    const pos = d1Positions.find(pp => pp.planet === p);
    if (!pos) {
      hb.push(0);
      continue;
    }
    hb.push(getHaddaPoints(pos.rasi, pos.longitude, p));
  }

  return hb;
};

/**
 * Calculate Drekkana Bala (for pancha vargeeya)
 */
const calculateDrekkanaBala = (d3Positions: PlanetPosition[]): Record<number, number> => {
  const kb: Record<number, number> = {};
  const pToH = getPlanetToHouseDict(d3Positions);

  for (let p = 0; p < 7; p++) {
    kb[p] = 0;
    const hP = pToH[p] ?? 0;
    const strength = HOUSE_STRENGTHS_OF_PLANETS[p]?.[hP] ?? 0;

    if (strength > STRENGTH_FRIEND) {
      kb[p] = 10;
    } else if (strength === STRENGTH_FRIEND) {
      kb[p] = 5;
    } else if (strength === STRENGTH_ENEMY) {
      kb[p] = 2.5;
    }
  }

  return kb;
};

/**
 * Calculate Navamsa Bala (for pancha vargeeya)
 */
const calculateNavamsaBala = (d9Positions: PlanetPosition[]): Record<number, number> => {
  const kb: Record<number, number> = {};
  const pToH = getPlanetToHouseDict(d9Positions);

  for (let p = 0; p < 7; p++) {
    kb[p] = 0;
    const hP = pToH[p] ?? 0;
    const strength = HOUSE_STRENGTHS_OF_PLANETS[p]?.[hP] ?? 0;

    if (strength > STRENGTH_FRIEND) {
      kb[p] = 5;
    } else if (strength === STRENGTH_FRIEND) {
      kb[p] = 2.5;
    } else if (strength === STRENGTH_ENEMY) {
      kb[p] = 1.25;
    }
  }

  return kb;
};

/**
 * Pancha Vargeeya Bala result
 */
export type PanchaVargeeyaBalaResult = Record<number, number>;

/**
 * Calculate Pancha Vargeeya Bala (five-fold varga strength)
 */
export const calculatePanchaVargeeyaBala = (
  jd: number,
  place: Place,
  d1Positions: PlanetPosition[]
): PanchaVargeeyaBalaResult => {
  const kb = calculateKshetraBala(d1Positions);
  const ub = calculateUchchaBala(d1Positions);
  const hb = calculateHaddaBala(d1Positions);

  const d3Positions = getDivisionalChart(d1Positions, 3);
  const db = calculateDrekkanaBala(d3Positions);

  const d9Positions = getDivisionalChart(d1Positions, 9);
  const nb = calculateNavamsaBala(d9Positions);

  const pvb: PanchaVargeeyaBalaResult = {};
  for (let k = 0; k < 7; k++) {
    const sum = kb[k] + ub[k] + hb[k] + (db[k] ?? 0) + (nb[k] ?? 0);
    pvb[k] = roundTo(sum / 4, 2);
  }

  return pvb;
};

// ============================================================================
// DWADHASA VARGEEYA BALA
// ============================================================================

/**
 * Dwadhasa Vargeeya Bala result
 */
export type DwadhasaVargeeyaBalaResult = Record<number, number>;

/**
 * Calculate Dwadhasa Vargeeya Bala (twelve-fold strength)
 */
export const calculateDwadhasaVargeeyaBala = (
  jd: number,
  place: Place,
  d1Positions: PlanetPosition[]
): DwadhasaVargeeyaBalaResult => {
  const dvp: DwadhasaVargeeyaBalaResult = {};
  for (let p = 0; p < 7; p++) {
    dvp[p] = 0;
  }

  for (let dvf = 1; dvf <= 12; dvf++) {
    const positions = getDivisionalChart(d1Positions, dvf);
    const pToH = getPlanetToHouseDict(positions);

    for (let p = 0; p < 7; p++) {
      const hP = pToH[p] ?? 0;
      const strength = HOUSE_STRENGTHS_OF_PLANETS[p]?.[hP] ?? 0;
      if (strength >= STRENGTH_FRIEND) {
        dvp[p] += 1;
      }
    }
  }

  return dvp;
};

// ============================================================================
// PLANET ASPECT RELATIONSHIP TABLE
// ============================================================================

/**
 * Calculate planet aspect relationship table
 */
export const calculatePlanetAspectRelationshipTable = (
  d1Positions: PlanetPosition[],
  includeHouses = false
): number[][] => {
  const rows = includeHouses ? 21 : 9;
  const dk: number[][] = Array.from({ length: rows }, () => new Array(9).fill(0));

  for (let p1 = 0; p1 < 9; p1++) {
    const pos1 = d1Positions.find(p => p.planet === p1);
    if (!pos1) continue;
    const p1Long = pos1.rasi * 30 + pos1.longitude;

    for (let p2 = 0; p2 < 9; p2++) {
      const pos2 = d1Positions.find(p => p.planet === p2);
      if (!pos2) continue;
      const p2Long = pos2.rasi * 30 + pos2.longitude;

      const dkAngle = normalizeDegrees(p1Long - p2Long);
      dk[p1][p2] = roundTo(calculateDrikBalaValue(dkAngle, p2), 2);
    }
  }

  if (includeHouses) {
    const ascPos = d1Positions.find(p => p.planet === -1);
    const ascHouse = ascPos?.rasi ?? 0;
    const ascLong = ascPos?.longitude ?? 0;

    for (let h = 0; h < 12; h++) {
      const h1 = (ascHouse + h) % 12;
      const p1Long = h1 * 30 + ascLong;

      for (let p2 = 0; p2 < 9; p2++) {
        const pos2 = d1Positions.find(p => p.planet === p2);
        if (!pos2) continue;
        const p2Long = pos2.rasi * 30 + pos2.longitude;

        const dkAngle = normalizeDegrees(p1Long - p2Long);
        dk[9 + h][p2] = roundTo(calculateDrikBalaValue(dkAngle, p2), 2);
      }
    }
  }

  // Transpose
  return dk[0].map((_, colIndex) => dk.map(row => row[colIndex]));
};
