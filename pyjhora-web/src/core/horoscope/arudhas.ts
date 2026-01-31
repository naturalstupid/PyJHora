/**
 * Arudha Pada Calculations
 * Ported from PyJHora horoscope/chart/arudhas.py
 *
 * Arudhas are special lagnas (ascendants) that represent the image or
 * manifestation of houses and planets. They are extensively used in
 * Jaimini astrology.
 *
 * Types of Arudhas:
 * - Bhava Arudhas (A1-A12): Arudhas of the 12 houses
 *   - A1 is also called Arudha Lagna (AL)
 *   - A12 is also called Upa Lagna (UL)
 * - Surya Arudhas (S1-S12): Bhava Arudhas calculated from Sun's position
 * - Chandra Arudhas (M1-M12): Bhava Arudhas calculated from Moon's position
 * - Graha Arudhas: Arudhas of planets (Pada of each planet)
 */

import {
  PLANET_SIGNS_OWNED,
  PP_COUNT_UPTO_KETU,
  PLANETS_UPTO_KETU,
  SUN,
  MOON,
} from '../constants';

import { countRasis } from '../utils/angle';

import {
  getHouseOwnerFromPlanetPositions,
  getPlanetToHouseDict,
  getHouseToPlanetList,
  getStrongerRasi,
} from './house';

/**
 * Planet position format used for Arudha calculations
 */
export interface ArudhaPlanetPosition {
  planet: number;
  rasi: number;
  longitude: number;
}

/**
 * Calculate Bhava Arudhas for each house from planet positions
 *
 * Bhava Arudhas are calculated as follows:
 * 1. Find the lord of the house
 * 2. Count signs from house to lord's position
 * 3. Count same number from lord's position
 * 4. If result falls in 1st or 7th from original house, add 10 signs
 *
 * @param planetPositions - Array of planet positions (must include at least Lagna to Ketu)
 * @param arudhaBase - Base planet for calculation:
 *   - 0: Lagna (default) - returns A1, A2, ... A12
 *   - 1: Sun - returns Surya Arudhas S1, S2, ... S12
 *   - 2: Moon - returns Chandra Arudhas M1, M2, ... M12
 *   - 3-9: Other planets (Mars to Ketu)
 * @returns Array of 12 rasi indices representing Bhava Arudhas for houses 1-12 from base
 */
export function bhavaArudhasFromPlanetPositions(
  planetPositions: ArudhaPlanetPosition[],
  arudhaBase: number = 0
): number[] {
  // Restrict to planets up to Ketu (exclude Uranus/Neptune/Pluto)
  // This is crucial for correct results as per PyJHora V3.6.4
  const positions = planetPositions.slice(0, PP_COUNT_UPTO_KETU);

  // Build helper dictionaries
  const houseToPlanetList = getHouseToPlanetList(positions);
  const planetToHouse = getPlanetToHouseDict(positions);

  // Get the base house (rasi where base planet is located)
  const baseHouse = positions[arudhaBase]?.rasi ?? 0;

  // Calculate houses from the base
  const houses = Array.from({ length: 12 }, (_, h) => (h + baseHouse) % 12);

  const bhavaArudhasOfHouses: number[] = [];

  for (const h of houses) {
    // Step 1: Find lord of the house
    const lordOfTheHouse = getHouseOwnerFromPlanetPositions(positions, h, false);

    // Step 2: Find house where lord is placed
    const houseOfTheLord = planetToHouse[lordOfTheHouse] ?? 0;

    // Step 3: Count signs from house to lord's position (inclusive)
    const signsBetweenHouseAndLord = countRasis(h, houseOfTheLord);

    // Step 4: Calculate Bhava Arudha position
    // Count same number of signs from lord's position
    let bhavaArudhaOfHouse = (houseOfTheLord + signsBetweenHouseAndLord - 1) % 12;

    // Step 5: Check if Arudha falls in 1st or 7th from original house
    const signsFromTheHouse = countRasis(h, bhavaArudhaOfHouse);

    // Exception: If Arudha is in 1st or 7th house from original, add 10 signs
    if (signsFromTheHouse === 1 || signsFromTheHouse === 7) {
      bhavaArudhaOfHouse = (bhavaArudhaOfHouse + 10 - 1) % 12;
    }

    bhavaArudhasOfHouses.push(bhavaArudhaOfHouse);
  }

  return bhavaArudhasOfHouses;
}

/**
 * Calculate Surya (Sun) Arudhas - Bhava Arudhas calculated from Sun's position
 * @param planetPositions - Array of planet positions
 * @returns Array of 12 rasi indices for Surya Arudhas S1-S12
 */
export function suryaArudhasFromPlanetPositions(
  planetPositions: ArudhaPlanetPosition[]
): number[] {
  return bhavaArudhasFromPlanetPositions(planetPositions, SUN + 1); // +1 because index 0 is Lagna
}

/**
 * Calculate Chandra (Moon) Arudhas - Bhava Arudhas calculated from Moon's position
 * @param planetPositions - Array of planet positions
 * @returns Array of 12 rasi indices for Chandra Arudhas M1-M12
 */
export function chandraArudhasFromPlanetPositions(
  planetPositions: ArudhaPlanetPosition[]
): number[] {
  return bhavaArudhasFromPlanetPositions(planetPositions, MOON + 1); // +1 because index 0 is Lagna
}

/**
 * Calculate Graha Arudhas (Pada) for each planet
 *
 * Graha Arudha (Planetary Pada) calculation:
 * 1. Find the house where planet is placed
 * 2. Find the stronger sign owned by the planet
 * 3. Count from planet's house to the owned sign
 * 4. Count same distance from planet's house
 * 5. If result is 1st or 7th from planet's house, add 10 signs
 *
 * @param planetPositions - Array of planet positions
 * @returns Array of rasi indices for Graha Arudhas
 *          Index 0: Lagna Pada
 *          Index 1-9: Sun Pada, Moon Pada, Mars Pada, etc.
 */
export function grahaArudhasFromPlanetPositions(
  planetPositions: ArudhaPlanetPosition[]
): number[] {
  const positions = planetPositions.slice(0, PP_COUNT_UPTO_KETU);
  const planetToHouse = getPlanetToHouseDict(positions);

  // First element is Lagna's position (Lagna Pada = Lagna's house)
  const grahaArudhasOfPlanets: number[] = [positions[0]?.rasi ?? 0];

  // Calculate for each planet from Sun (0) to Ketu (8)
  for (let p = 0; p < PLANETS_UPTO_KETU; p++) {
    const houseOfThePlanet = planetToHouse[p] ?? 0;

    // Get signs owned by this planet
    let signOwnedByPlanet = PLANET_SIGNS_OWNED[p];

    if (!signOwnedByPlanet || signOwnedByPlanet.length === 0) {
      // Fallback (should not happen with proper data)
      grahaArudhasOfPlanets.push(houseOfThePlanet);
      continue;
    }

    // If planet owns two signs, find the stronger one
    let strongerSign: number;
    if (signOwnedByPlanet.length > 1) {
      strongerSign = getStrongerRasi(
        positions,
        signOwnedByPlanet[0],
        signOwnedByPlanet[1]
      );
    } else {
      strongerSign = signOwnedByPlanet[0];
    }

    // Count from planet's house to its stronger owned sign
    // Formula: (sign + 1 + 12 - house) % 12 in Python
    // This gives 0-based distance, we need 1-based for countRasis
    const countToStrong = ((strongerSign + 1 + 12 - houseOfThePlanet) % 12);

    // Calculate Arudha position: house + 2*(count - 1)
    let countToArudha = (houseOfThePlanet + 2 * (countToStrong - 1)) % 12;

    // Check if Arudha is in 1st or 7th from planet's house
    const countFromHouse = (houseOfThePlanet + 12 - countToArudha) % 12;

    // Exception: If count is 0 or 6 (same house or 7th house), add 9 signs
    if (countFromHouse === 0 || countFromHouse === 6) {
      countToArudha = (countToArudha + 9) % 12;
    }

    const grahaPadhaOfPlanet = countToArudha;
    grahaArudhasOfPlanets.push(grahaPadhaOfPlanet);
  }

  return grahaArudhasOfPlanets;
}

/**
 * Get Arudha Lagna (A1) - the most commonly used Arudha
 * @param planetPositions - Array of planet positions
 * @returns Rasi index of Arudha Lagna
 */
export function getArudhaLagna(planetPositions: ArudhaPlanetPosition[]): number {
  const bhavaArudhas = bhavaArudhasFromPlanetPositions(planetPositions, 0);
  return bhavaArudhas[0]; // A1 is the first element
}

/**
 * Get Upa Lagna (A12) - Arudha of the 12th house
 * @param planetPositions - Array of planet positions
 * @returns Rasi index of Upa Lagna
 */
export function getUpaLagna(planetPositions: ArudhaPlanetPosition[]): number {
  const bhavaArudhas = bhavaArudhasFromPlanetPositions(planetPositions, 0);
  return bhavaArudhas[11]; // A12 is the 12th element (index 11)
}

/**
 * Format Bhava Arudhas as a chart array (for display)
 *
 * @param bhavaArudhas - Array of 12 Bhava Arudha positions
 * @param prefix - Prefix for labels (default 'A' for Bhava Arudhas)
 * @returns Array of 12 strings, one for each rasi, containing Arudha labels
 *          e.g., ['A1/A3', '', 'A2', ...] for Aries, Taurus, etc.
 */
export function formatBhavaArudhasAsChart(
  bhavaArudhas: number[],
  prefix: string = 'A'
): string[] {
  const chart: string[] = Array(12).fill('');

  bhavaArudhas.forEach((rasi, index) => {
    const label = `${prefix}${index + 1}`;
    if (chart[rasi]) {
      chart[rasi] += `/${label}`;
    } else {
      chart[rasi] = label;
    }
  });

  return chart;
}

/**
 * Format Graha Arudhas as a chart array (for display)
 *
 * @param grahaArudhas - Array of Graha Arudha positions (Lagna + 9 planets)
 * @returns Array of 12 strings, one for each rasi, containing planet labels
 *          e.g., ['L/0', '3', '', ...] where L=Lagna, 0=Sun, 3=Mercury
 */
export function formatGrahaArudhasAsChart(grahaArudhas: number[]): string[] {
  const chart: string[] = Array(12).fill('');

  grahaArudhas.forEach((rasi, index) => {
    // Index 0 is Lagna, 1-9 are planets (Sun=0 to Ketu=8 in planet numbering)
    const label = index === 0 ? 'L' : String(index - 1);
    if (chart[rasi]) {
      chart[rasi] += `/${label}`;
    } else {
      chart[rasi] = label;
    }
  });

  return chart;
}
