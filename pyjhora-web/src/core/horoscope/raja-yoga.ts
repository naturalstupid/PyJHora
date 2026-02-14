/**
 * Raja Yoga calculations
 * Ported from PyJHora raja_yoga.py
 *
 * Raja Yoga: Association between lords of quadrants (kendras) and trines (trikonas)
 * from Lagna. The association can be:
 *   1. Conjunction (same house)
 *   2. Mutual graha drishti (planetary aspect)
 *   3. Parivartana (exchange of signs)
 */

import {
  ASCENDANT_SYMBOL,
  GRAHA_DRISHTI,
  HOUSE_STRENGTHS_OF_PLANETS,
  SIGN_LORDS,
  STRENGTH_DEBILITATED,
  STRENGTH_EXALTED,
} from '../constants';
import type { HouseChart, PlanetPosition } from '../types';
import {
  getLordOfSign,
  getQuadrantsOfRaasi,
  getTrinesOfRaasi,
} from './house';

// ============================================================================
// HELPER: Chart parsing
// ============================================================================

/**
 * Parse a HouseChart (string[]) into a planet-to-house dictionary.
 * Keys are planet IDs (number) and 'L' for Lagna.
 * Values are house/rasi indices (0-11).
 */
const getPlanetToHouseFromChart = (
  chart: HouseChart
): Record<number | string, number> => {
  const pToH: Record<number | string, number> = {};
  for (let h = 0; h < 12; h++) {
    if (!chart[h] || chart[h] === '') continue;
    const parts = chart[h].split('/');
    for (const part of parts) {
      const trimmed = part.trim();
      if (trimmed === ASCENDANT_SYMBOL) {
        pToH[ASCENDANT_SYMBOL] = h;
      } else if (trimmed !== '') {
        const planet = parseInt(trimmed, 10);
        if (!isNaN(planet)) {
          pToH[planet] = h;
        }
      }
    }
  }
  return pToH;
};

/**
 * Convert a planet-to-house dict back to a HouseChart (string[]).
 */
const getChartFromPlanetToHouse = (
  pToH: Record<number | string, number>
): HouseChart => {
  const chart: string[] = Array(12).fill('');
  for (const [key, house] of Object.entries(pToH)) {
    if (chart[house] === '') {
      chart[house] = key;
    } else {
      chart[house] += '/' + key;
    }
  }
  return chart;
};

// ============================================================================
// HELPER: Graha Drishti check
// ============================================================================

/**
 * Get the list of planets aspected by a given planet via graha drishti,
 * given the chart (HouseChart format).
 *
 * Graha drishti: Each planet aspects certain houses from its position.
 * The GRAHA_DRISHTI constant stores 0-based offsets.
 * For example, Sun aspects [6] meaning the 7th house from Sun.
 */
const getGrahaDrishtiPlanets = (
  chart: HouseChart,
  planet: number
): number[] => {
  const pToH = getPlanetToHouseFromChart(chart);
  const planetHouse = pToH[planet];
  if (planetHouse === undefined) return [];

  const aspects = GRAHA_DRISHTI[planet];
  if (!aspects) return [];

  const aspectedPlanets: number[] = [];
  for (const offset of aspects) {
    const targetHouse = (planetHouse + offset) % 12;
    // Find all planets in the target house
    if (!chart[targetHouse] || chart[targetHouse] === '') continue;
    const parts = chart[targetHouse].split('/');
    for (const part of parts) {
      const trimmed = part.trim();
      if (trimmed !== '' && trimmed !== ASCENDANT_SYMBOL) {
        const p = parseInt(trimmed, 10);
        if (!isNaN(p) && p !== planet) {
          aspectedPlanets.push(p);
        }
      }
    }
  }
  return aspectedPlanets;
};

/**
 * Check if planet1 aspects planet2 via graha drishti (one-way check).
 */
const hasGrahaDrishti = (
  chart: HouseChart,
  fromPlanet: number,
  toPlanet: number
): boolean => {
  const aspected = getGrahaDrishtiPlanets(chart, fromPlanet);
  return aspected.includes(toPlanet);
};

// ============================================================================
// HELPER: Association check (conjunction, mutual aspect, parivartana)
// ============================================================================

/**
 * Check if two lords are associated via conjunction, mutual graha drishti,
 * or parivartana (exchange of signs).
 *
 * This mirrors Python's _check_association.
 *
 * @param chart - HouseChart (string array, 12 elements)
 * @param lord1 - Planet ID of first lord
 * @param lord2 - Planet ID of second lord
 * @returns true if the two lords are associated
 */
const checkAssociation = (
  chart: HouseChart,
  lord1: number,
  lord2: number
): boolean => {
  const pToH = getPlanetToHouseFromChart(chart);
  const house1 = pToH[lord1];
  const house2 = pToH[lord2];

  if (house1 === undefined || house2 === undefined) return false;

  // (1) Conjunction: both planets in the same house
  if (house1 === house2) {
    return true;
  }

  // (2) Mutual graha drishti (Rahu/Ketu excluded from graha drishti check)
  if (lord1 !== 7 && lord1 !== 8 && lord2 !== 7 && lord2 !== 8) {
    const lord1AspectsLord2 = hasGrahaDrishti(chart, lord1, lord2);
    const lord2AspectsLord1 = hasGrahaDrishti(chart, lord2, lord1);
    if (lord1AspectsLord2 && lord2AspectsLord1) {
      return true;
    }
  }

  // (3) Parivartana (exchange): lord1 is in lord2's sign and vice versa
  const ownerOfHouse1 = getLordOfSign(house1);
  const ownerOfHouse2 = getLordOfSign(house2);
  if (lord1 === ownerOfHouse2 && lord2 === ownerOfHouse1) {
    return true;
  }

  return false;
};

// ============================================================================
// PUBLIC: getRajaYogaPairs
// ============================================================================

/**
 * Find pairs of planets that form Raja Yoga in the given chart.
 *
 * Raja Yoga occurs when the lord of a quadrant (kendra) house is associated
 * with the lord of a trine (trikona) house from Lagna.
 *
 * @param chart - HouseChart (string[], 12 elements) where each element
 *   contains planet IDs separated by '/' and 'L' for Lagna.
 *   Example: ['', '', '', '', '2', '7', '1/5', '0', '3/4', 'L', '', '6/8']
 * @returns Array of [planet1, planet2] pairs forming Raja Yoga
 */
export const getRajaYogaPairs = (chart: HouseChart): [number, number][] => {
  const pToH = getPlanetToHouseFromChart(chart);
  const ascHouse = pToH[ASCENDANT_SYMBOL];
  if (ascHouse === undefined) return [];

  // Get quadrant and trine houses from Lagna
  const quadrantHouses = getQuadrantsOfRaasi(ascHouse);
  const trineHouses = getTrinesOfRaasi(ascHouse);

  // Get lords of quadrant and trine houses
  const quadrantLords = new Set(quadrantHouses.map((h) => getLordOfSign(h)));
  const trineLords = new Set(trineHouses.map((h) => getLordOfSign(h)));

  // Generate all possible (quadrant_lord, trine_lord) pairs where they differ
  const possiblePairsSet = new Set<string>();
  const possiblePairs: [number, number][] = [];

  for (const ql of quadrantLords) {
    for (const tl of trineLords) {
      if (ql === tl) continue;
      const sorted: [number, number] =
        ql < tl ? [ql, tl] : [tl, ql];
      const key = `${sorted[0]},${sorted[1]}`;
      if (!possiblePairsSet.has(key)) {
        possiblePairsSet.add(key);
        possiblePairs.push(sorted);
      }
    }
  }

  // Check each pair for association
  const rajaYogaPairs: [number, number][] = [];
  for (const [p1, p2] of possiblePairs) {
    if (checkAssociation(chart, p1, p2)) {
      rajaYogaPairs.push([p1, p2]);
    }
  }

  return rajaYogaPairs;
};

// ============================================================================
// PUBLIC: getRajaYogaPairsFromPositions
// ============================================================================

/**
 * Wrapper that converts PlanetPosition[] to a HouseChart, then calls getRajaYogaPairs.
 *
 * @param positions - Array of PlanetPosition objects (must include one with
 *   planet === -1 or a separate Lagna indicator). If the first position has
 *   planet === -1, it is treated as the Ascendant.
 * @returns Array of [planet1, planet2] pairs forming Raja Yoga
 */
export const getRajaYogaPairsFromPositions = (
  positions: PlanetPosition[]
): [number, number][] => {
  // Build chart from positions
  const chart: string[] = Array(12).fill('');
  for (const pos of positions) {
    const key = pos.planet === -1 ? ASCENDANT_SYMBOL : String(pos.planet);
    if (chart[pos.rasi] === '') {
      chart[pos.rasi] = key;
    } else {
      chart[pos.rasi] += '/' + key;
    }
  }
  return getRajaYogaPairs(chart);
};

// ============================================================================
// PUBLIC: dharmaKarmadhipatiRajaYoga
// ============================================================================

/**
 * Check if the two planets are lords of the 9th (dharma) and 10th (karma) houses.
 *
 * Dharma-Karmadhipati Yoga is a special case of Raja Yoga where the lords
 * of the 9th and 10th houses form an association.
 *
 * @param planetToHouse - Map of planet ID (or 'L'/-1) to house/rasi index
 * @param planet1 - First raja yoga planet
 * @param planet2 - Second raja yoga planet
 * @returns true if {planet1, planet2} are the lords of the 9th and 10th houses
 */
export const dharmaKarmadhipatiRajaYoga = (
  planetToHouse: Record<number | string, number>,
  planet1: number,
  planet2: number
): boolean => {
  const lagnaHouse =
    planetToHouse[ASCENDANT_SYMBOL] ?? planetToHouse[-1];
  if (lagnaHouse === undefined) return false;

  // Build chart from planetToHouse for house_owner lookup
  const chart = getChartFromPlanetToHouse(planetToHouse);

  // 9th house = (lagnaHouse + 8) % 12, 10th house = (lagnaHouse + 9) % 12
  const ninthHouse = (lagnaHouse + 8) % 12;
  const tenthHouse = (lagnaHouse + 9) % 12;

  const lord9 = getLordOfSign(ninthHouse);
  const lord10 = getLordOfSign(tenthHouse);

  // Check if {planet1, planet2} matches {lord9, lord10} in any order
  const houseLords = [lord9, lord10];
  const dkCheck =
    houseLords.includes(planet1) && houseLords.includes(planet2) &&
    planet1 !== planet2;

  return dkCheck;
};

// ============================================================================
// PUBLIC: vipareethaRajaYoga
// ============================================================================

/**
 * Check if the raja yoga planets form Vipareetha Raja Yoga.
 *
 * Vipareetha Raja Yoga occurs when dusthana lords (6th, 8th, 12th) are
 * placed in dusthana houses.
 *
 * @param planetToHouse - Map of planet ID (or 'L'/-1) to house/rasi index
 * @param planet1 - First raja yoga planet
 * @param planet2 - Second raja yoga planet
 * @returns false if not present, or [true, subType] where subType is one of
 *   "Harsh Raja Yoga", "Saral Raja Yoga", "Vimal Raja Yoga"
 */
export const vipareethaRajaYoga = (
  planetToHouse: Record<number | string, number>,
  planet1: number,
  planet2: number
): false | [true, string] => {
  const lagnaHouse =
    planetToHouse[ASCENDANT_SYMBOL] ?? planetToHouse[-1];
  if (lagnaHouse === undefined) return false;

  // Dusthana houses: 6th, 8th, 12th from Lagna
  const dusthanas = [
    (lagnaHouse + 5) % 12,  // 6th house
    (lagnaHouse + 7) % 12,  // 8th house
    (lagnaHouse + 11) % 12, // 12th house
  ];

  // For each raja yoga planet, check if it's in a dusthana
  const planets = [planet1, planet2];
  const inDusthana: boolean[][] = planets.map((rp) => {
    const rpHouse = planetToHouse[rp];
    return dusthanas.map((dh) => rpHouse === dh);
  });

  // Both planets must be in at least one dusthana
  const bothInDusthana =
    inDusthana[0].some((v) => v) && inDusthana[1].some((v) => v);

  if (!bothInDusthana) return false;

  // Determine sub-type based on first planet's position
  let subType = 'Harsh Raja Yoga'; // Default: in 6th house
  if (inDusthana[0][1]) {
    subType = 'Saral Raja Yoga'; // In 8th house
  } else if (inDusthana[0][2]) {
    subType = 'Vimal Raja Yoga'; // In 12th house
  }

  return [true, subType];
};

// ============================================================================
// PUBLIC: neechaBhangaRajaYoga
// ============================================================================

/**
 * Check if the raja yoga planets form Neecha Bhanga Raja Yoga
 * (cancellation of debilitation).
 *
 * Rules checked (first 3 of 5):
 * 1. Lord of the sign of a debilitated planet is exalted, or is in kendra from Moon
 * 2. Debilitated planet is conjunct with an exalted planet
 * 3. Debilitated planet is aspected by the lord of its sign
 *
 * @param planetToHouse - Map of planet ID (or 'L'/-1) to house/rasi index
 * @param planet1 - First raja yoga planet
 * @param planet2 - Second raja yoga planet
 * @returns true if Neecha Bhanga Raja Yoga is present
 */
export const neechaBhangaRajaYoga = (
  planetToHouse: Record<number | string, number>,
  planet1: number,
  planet2: number
): boolean => {
  // Build chart for graha drishti checks
  const chart = getChartFromPlanetToHouse(planetToHouse);

  const rp1Rasi = planetToHouse[planet1];
  const rp2Rasi = planetToHouse[planet2];
  if (rp1Rasi === undefined || rp2Rasi === undefined) return false;

  const rp1Lord = getLordOfSign(rp1Rasi);
  const rp2Lord = getLordOfSign(rp2Rasi);

  // Kendra from Moon
  const moonHouse = planetToHouse[1]; // Moon = 1
  const kendraFromMoon =
    moonHouse !== undefined ? getQuadrantsOfRaasi(moonHouse) : [];

  // Rule 1: Lord of sign of debilitated planet is exalted or in kendra from Moon
  const chk1_1 =
    HOUSE_STRENGTHS_OF_PLANETS[planet1]?.[rp1Rasi] <= STRENGTH_DEBILITATED &&
    ((HOUSE_STRENGTHS_OF_PLANETS[rp1Lord]?.[rp1Rasi] ?? 0) >= STRENGTH_EXALTED ||
      kendraFromMoon.includes(rp1Rasi));

  const chk1_2 =
    HOUSE_STRENGTHS_OF_PLANETS[planet2]?.[rp2Rasi] <= STRENGTH_DEBILITATED &&
    ((HOUSE_STRENGTHS_OF_PLANETS[rp2Lord]?.[rp2Rasi] ?? 0) >= STRENGTH_EXALTED ||
      kendraFromMoon.includes(rp2Rasi));

  if (chk1_1 || chk1_2) return true;

  // Rule 2: Debilitated planet conjunct with exalted planet
  const sameHouse = rp1Rasi === rp2Rasi;
  const chk2_2 =
    (HOUSE_STRENGTHS_OF_PLANETS[planet1]?.[rp1Rasi] ?? 0) >= STRENGTH_EXALTED &&
    HOUSE_STRENGTHS_OF_PLANETS[planet2]?.[rp2Rasi] <= STRENGTH_DEBILITATED;
  const chk2_3 =
    (HOUSE_STRENGTHS_OF_PLANETS[planet2]?.[rp2Rasi] ?? 0) >= STRENGTH_EXALTED &&
    HOUSE_STRENGTHS_OF_PLANETS[planet1]?.[rp1Rasi] <= STRENGTH_DEBILITATED;

  if (sameHouse && (chk2_2 || chk2_3)) return true;

  // Rule 3: Debilitated planet aspected by lord of its sign
  const chk3_1 =
    HOUSE_STRENGTHS_OF_PLANETS[planet1]?.[rp2Rasi] <= STRENGTH_DEBILITATED &&
    hasGrahaDrishti(chart, rp1Lord, planet1);

  const chk3_2 =
    HOUSE_STRENGTHS_OF_PLANETS[planet2]?.[rp2Rasi] <= STRENGTH_DEBILITATED &&
    hasGrahaDrishti(chart, rp2Lord, planet1);

  return chk3_1 || chk3_2;
};
