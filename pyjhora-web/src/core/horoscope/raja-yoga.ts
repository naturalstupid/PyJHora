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
  NATURAL_BENEFICS,
  SIGN_LORDS,
  STRENGTH_DEBILITATED,
  STRENGTH_EXALTED,
  STRENGTH_FRIEND,
} from '../constants';
import type { HouseChart, PlanetPosition } from '../types';
import {
  getCharaKarakas,
  getHouseOwnerFromPlanetPositions,
  getLordOfSign,
  getQuadrantsOfRaasi,
  getRaasiDrishtiFromChart,
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

// ============================================================================
// HELPER: Build chart and dictionaries from PlanetPosition[]
// ============================================================================

/**
 * Build a HouseChart (string[12]) from PlanetPosition[].
 * Each element contains planet IDs separated by '/' and 'L' for the ascendant.
 */
const buildChartFromPositions = (positions: PlanetPosition[]): HouseChart => {
  const chart: string[] = Array(12).fill('');
  for (const pos of positions) {
    const key = pos.planet === -1 ? ASCENDANT_SYMBOL : String(pos.planet);
    if (chart[pos.rasi] === '') {
      chart[pos.rasi] = key;
    } else {
      chart[pos.rasi] += '/' + key;
    }
  }
  return chart;
};

/**
 * Build a planet-to-house dictionary from PlanetPosition[].
 * Returns a record mapping planet IDs (and 'L' for ascendant) to rasi indices.
 */
const buildPlanetToHouseFromPositions = (
  positions: PlanetPosition[]
): Record<number | string, number> => {
  const pToH: Record<number | string, number> = {};
  for (const pos of positions) {
    if (pos.planet === -1) {
      pToH[ASCENDANT_SYMBOL] = pos.rasi;
    } else {
      pToH[pos.planet] = pos.rasi;
    }
  }
  return pToH;
};

// ============================================================================
// HELPER: Get planets aspecting a raasi via raasi drishti
// ============================================================================

/**
 * Get planets that aspect a given raasi via raasi drishti.
 * Mirrors Python's aspected_planets_of_the_raasi.
 *
 * @param planetToHouse - Planet ID to rasi mapping (numeric keys for planets 0-8)
 * @param raasi - Target rasi index (0-11)
 * @returns Array of planet IDs that aspect the given raasi
 */
const getAspectedPlanetsOfRaasi = (
  planetToHouse: Record<number, number>,
  raasi: number
): number[] => {
  const { arp } = getRaasiDrishtiFromChart(planetToHouse);
  const aspectingPlanets: number[] = [];
  for (const [planetStr, aspectedRasis] of Object.entries(arp)) {
    const planet = parseInt(planetStr, 10);
    if (!isNaN(planet) && aspectedRasis.includes(raasi)) {
      aspectingPlanets.push(planet);
    }
  }
  return aspectingPlanets;
};

// ============================================================================
// PUBLIC: checkOtherRajaYoga1
// ============================================================================

/**
 * Check for Raja Yoga pattern 1.
 *
 * If (a) chara putra karaka (PK) and chara atma karaka (AK) are conjoined and
 * (b) lagna lord and 5th lord conjoin, then Raja Yoga is present and the native
 * enjoys power and prosperity.
 *
 * Ported from Python's check_other_raja_yoga_1.
 * Accepts PlanetPosition[] instead of jd/place (no Swiss Ephemeris needed).
 *
 * @param positions - Array of PlanetPosition objects (must include ascendant with planet === -1)
 * @returns true if this raja yoga pattern is present
 */
export const checkOtherRajaYoga1 = (
  positions: PlanetPosition[]
): boolean => {
  const pToH = buildPlanetToHouseFromPositions(positions);
  const ascHouse = pToH[ASCENDANT_SYMBOL];
  if (ascHouse === undefined) return false;

  // Compute chara karakas
  const charaKarakas = getCharaKarakas(
    positions.filter(p => p.planet >= 0).map(p => ({
      planet: p.planet,
      rasi: p.rasi,
      longitude: p.longitudeInSign,
    }))
  );

  // AK = chara_karakas[0], PK = chara_karakas[5]
  const ak = charaKarakas[0];
  const pk = charaKarakas[5];

  // Lagna lord and 5th lord
  const lagnaLord = getHouseOwnerFromPlanetPositions(
    positions.map(p => ({ planet: p.planet, rasi: p.rasi, longitude: p.longitudeInSign })),
    ascHouse
  );
  const fifthLord = getHouseOwnerFromPlanetPositions(
    positions.map(p => ({ planet: p.planet, rasi: p.rasi, longitude: p.longitudeInSign })),
    (ascHouse + 4) % 12
  );

  // (a) AK and PK are conjoined (same house)
  const chk1 = pToH[ak] === pToH[pk];

  // (b) Lagna lord and 5th lord conjoin (same house)
  const chk2 = pToH[lagnaLord] === pToH[fifthLord];

  return chk1 && chk2;
};

// ============================================================================
// PUBLIC: checkOtherRajaYoga2
// ============================================================================

/**
 * Check for Raja Yoga pattern 2.
 *
 * If (a) lagna lord is in 5th, (b) 5th lord is in lagna, (c) AK and PK are in lagna or
 * the 5th house, and (d) those planets are in own rasi/exaltation or aspected by benefics,
 * then this yoga is present.
 *
 * Ported from Python's check_other_raja_yoga_2.
 * Uses NATURAL_BENEFICS instead of charts.benefics(jd,place) since we lack JD/place.
 *
 * @param positions - Array of PlanetPosition objects (must include ascendant with planet === -1)
 * @returns true if this raja yoga pattern is present
 */
export const checkOtherRajaYoga2 = (
  positions: PlanetPosition[]
): boolean => {
  const pToH = buildPlanetToHouseFromPositions(positions);
  const ascHouse = pToH[ASCENDANT_SYMBOL];
  if (ascHouse === undefined) return false;

  const positionsForHouse = positions.map(p => ({
    planet: p.planet,
    rasi: p.rasi,
    longitude: p.longitudeInSign,
  }));

  // Compute chara karakas
  const charaKarakas = getCharaKarakas(
    positions.filter(p => p.planet >= 0).map(p => ({
      planet: p.planet,
      rasi: p.rasi,
      longitude: p.longitudeInSign,
    }))
  );

  const ak = charaKarakas[0];
  const pk = charaKarakas[5];

  const lagnaLord = getHouseOwnerFromPlanetPositions(positionsForHouse, ascHouse);
  const fifthHouse = (ascHouse + 4) % 12;
  const fifthLord = getHouseOwnerFromPlanetPositions(positionsForHouse, fifthHouse);

  // (a) Lagna lord is in 5th AND (b) 5th lord is in lagna
  const chk1 = pToH[lagnaLord] === fifthHouse && pToH[fifthLord] === ascHouse;

  // (c) AK and PK are both in lagna OR both in 5th house
  const chk2_1 = pToH[ak] === ascHouse && pToH[pk] === ascHouse;
  const chk2_2 = pToH[ak] === fifthHouse && pToH[pk] === fifthHouse;
  const chk2 = chk2_1 || chk2_2;

  // (d) Strength check: those planets in own rasi or exaltation (strength > FRIEND)
  const chk3_1 =
    (HOUSE_STRENGTHS_OF_PLANETS[ak]?.[pToH[ak]] ?? 0) > STRENGTH_FRIEND &&
    (HOUSE_STRENGTHS_OF_PLANETS[pk]?.[pToH[pk]] ?? 0) > STRENGTH_FRIEND;
  const chk3_2 =
    (HOUSE_STRENGTHS_OF_PLANETS[lagnaLord]?.[fifthHouse] ?? 0) > STRENGTH_FRIEND &&
    (HOUSE_STRENGTHS_OF_PLANETS[fifthLord]?.[ascHouse] ?? 0) > STRENGTH_FRIEND;
  const chk3 = chk3_1 && chk3_2;

  // (d) Alternative: aspected by benefics (using NATURAL_BENEFICS as fallback)
  // Build planet-to-house dict for raasi drishti (numeric keys only)
  const numericPToH: Record<number, number> = {};
  for (const pos of positions) {
    if (pos.planet >= 0) {
      numericPToH[pos.planet] = pos.rasi;
    }
  }

  const lagnaLordAspects = getAspectedPlanetsOfRaasi(numericPToH, fifthHouse);
  const chk4_1 = lagnaLordAspects.some(lp => NATURAL_BENEFICS.includes(lp));

  const fifthLordAspects = getAspectedPlanetsOfRaasi(numericPToH, ascHouse);
  const chk4_2 = fifthLordAspects.some(fp => NATURAL_BENEFICS.includes(fp));

  const akAspects = getAspectedPlanetsOfRaasi(numericPToH, pToH[ak]);
  const chk4_3 = akAspects.some(lp => NATURAL_BENEFICS.includes(lp));

  const pkAspects = getAspectedPlanetsOfRaasi(numericPToH, pToH[pk]);
  const chk4_4 = pkAspects.some(fp => NATURAL_BENEFICS.includes(fp));

  const chk4 = chk4_1 && chk4_2 && chk4_3 && chk4_4;

  return chk1 && chk2 && (chk3 || chk4);
};

// ============================================================================
// PUBLIC: checkOtherRajaYoga3
// ============================================================================

/**
 * Check for Raja Yoga pattern 3.
 *
 * If the 9th lord and AK (Atma Karaka) are in lagna, 5th, or 7th, aspected by
 * benefics, then Raja Yoga is present.
 *
 * Ported from Python's check_other_raja_yoga_3.
 * Note: The Python function returns the result of the check but the last line is `pass`
 * indicating it is incomplete. We port what is implemented.
 *
 * @param positions - Array of PlanetPosition objects (must include ascendant with planet === -1)
 * @returns true if this raja yoga pattern is present
 */
export const checkOtherRajaYoga3 = (
  positions: PlanetPosition[]
): boolean => {
  const pToH = buildPlanetToHouseFromPositions(positions);
  const ascHouse = pToH[ASCENDANT_SYMBOL];
  if (ascHouse === undefined) return false;

  const positionsForHouse = positions.map(p => ({
    planet: p.planet,
    rasi: p.rasi,
    longitude: p.longitudeInSign,
  }));

  // Compute chara karakas
  const charaKarakas = getCharaKarakas(
    positions.filter(p => p.planet >= 0).map(p => ({
      planet: p.planet,
      rasi: p.rasi,
      longitude: p.longitudeInSign,
    }))
  );

  const ak = charaKarakas[0];

  const ninthHouse = (ascHouse + 8) % 12;
  const ninthLord = getHouseOwnerFromPlanetPositions(positionsForHouse, ninthHouse);

  // Target houses: lagna (1st), 5th, 7th from ascendant
  const targetHouses = [
    ascHouse,
    (ascHouse + 4) % 12,
    (ascHouse + 6) % 12,
  ];

  // Check if 9th lord or AK is in one of the target houses
  const chk = [pToH[ninthLord], pToH[ak]].some(h1 =>
    targetHouses.some(h2 => h1 === h2)
  );

  return chk;
};

// ============================================================================
// PUBLIC: getRajaYogaDetails
// ============================================================================

/**
 * Result type for a single raja yoga finding.
 */
export interface RajaYogaResult {
  /** Name/key of the raja yoga check */
  name: string;
  /** Planet pairs that triggered this yoga, each as [planet1, planet2] */
  pairs: [number, number][];
  /** Whether dharma-karmadhipati yoga applies for any pair */
  isDharmaKarmadhipati: boolean;
  /** Whether vipareetha raja yoga applies for any pair, with sub-type if present */
  vipareethaResult: false | [true, string];
  /** Whether neecha bhanga raja yoga applies for any pair */
  isNeechaBhanga: boolean;
  /** Whether other raja yoga pattern 1 applies */
  isOtherRajaYoga1: boolean;
  /** Whether other raja yoga pattern 2 applies */
  isOtherRajaYoga2: boolean;
  /** Whether other raja yoga pattern 3 applies */
  isOtherRajaYoga3: boolean;
}

/**
 * Get comprehensive raja yoga details for a given chart.
 *
 * This orchestrator function calls all individual raja yoga checks and returns
 * combined results. It is the main entry point for raja yoga analysis.
 *
 * Ported from Python's get_raja_yoga_details. Since the Python version requires
 * jd/place for chart computation and JSON resource loading, this TS version
 * accepts pre-computed chart data and positions directly.
 *
 * @param chart - HouseChart (string[], 12 elements) with planet placements
 * @param positions - Array of PlanetPosition objects (must include ascendant with planet === -1)
 * @returns RajaYogaResult with all yoga findings
 */
export const getRajaYogaDetails = (
  chart: HouseChart,
  positions: PlanetPosition[]
): RajaYogaResult => {
  // Get raja yoga pairs from chart
  const pairs = getRajaYogaPairs(chart);

  // Build planet-to-house dictionary for vipareetha and other checks
  const pToH = getPlanetToHouseFromChart(chart);

  // Check each pair for specialized yogas
  let isDharmaKarmadhipati = false;
  let vipareethaResult: false | [true, string] = false;
  let isNeechaBhanga = false;

  for (const [p1, p2] of pairs) {
    // Dharma-karmadhipati check
    if (!isDharmaKarmadhipati) {
      isDharmaKarmadhipati = dharmaKarmadhipatiRajaYoga(pToH, p1, p2);
    }

    // Vipareetha check
    if (vipareethaResult === false) {
      vipareethaResult = vipareethaRajaYoga(pToH, p1, p2);
    }

    // Neecha bhanga check
    if (!isNeechaBhanga) {
      isNeechaBhanga = neechaBhangaRajaYoga(pToH, p1, p2);
    }
  }

  // Other raja yoga checks (these operate on planet positions directly)
  const isOtherRajaYoga1 = checkOtherRajaYoga1(positions);
  const isOtherRajaYoga2 = checkOtherRajaYoga2(positions);
  const isOtherRajaYoga3 = checkOtherRajaYoga3(positions);

  return {
    name: 'raja_yoga',
    pairs,
    isDharmaKarmadhipati,
    vipareethaResult,
    isNeechaBhanga,
    isOtherRajaYoga1,
    isOtherRajaYoga2,
    isOtherRajaYoga3,
  };
};
