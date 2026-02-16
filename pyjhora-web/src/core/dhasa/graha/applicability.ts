/**
 * Dhasa Applicability Checks
 * Ported from PyJHora applicability.py
 *
 * Determines which conditional graha dhasas apply to a given chart.
 */

import { SCORPIO, AQUARIUS, CANCER } from '../../constants';
import type { PlanetPosition } from '../../horoscope/charts';
import { getDivisionalChart } from '../../horoscope/charts';
import {
  getHouseOwnerFromPlanetPositions,
  getTrinesOfRaasi,
  getQuadrantsOfRaasi,
  getPlanetToHouseDict,
} from '../../horoscope/house';

// ============================================================================
// INDIVIDUAL CHECKS
// ============================================================================

/**
 * Ashtottari: Rahu in trines or quadrants of Lagna Lord's house,
 * and Rahu not in Ascendant.
 */
export function isAshtottariApplicable(positions: PlanetPosition[]): boolean {
  const ascHouse = positions[0]!.rasi;
  const lagnaLord = getHouseOwnerFromPlanetPositions(positions, ascHouse);
  const houseOfLagnaLord = positions.find(p => p.planet === lagnaLord)?.rasi ?? positions[lagnaLord + 1]?.rasi;
  if (houseOfLagnaLord === undefined) return false;

  const rahuHouse = positions[8]!.rasi;
  if (rahuHouse === ascHouse) return false;

  const trines = getTrinesOfRaasi(houseOfLagnaLord);
  const quadrants = getQuadrantsOfRaasi(houseOfLagnaLord);
  return trines.includes(rahuHouse) || quadrants.includes(rahuHouse);
}

/**
 * Chaturaseethi Sama: 10th Lord in 10th House.
 */
export function isChaturaseethiApplicable(positions: PlanetPosition[]): boolean {
  const ascHouse = positions[0]!.rasi;
  const tenthHouse = (ascHouse + 9) % 12;
  const tenthLord = getHouseOwnerFromPlanetPositions(positions, tenthHouse);
  const p2h = getPlanetToHouseDict(positions);
  return p2h[tenthLord] === tenthHouse;
}

/**
 * Dwadasottari: Lagna in Taurus or Libra Navamsa.
 * Takes navamsa positions as input.
 */
export function isDwadasottariApplicable(navamsaPositions: PlanetPosition[]): boolean {
  const navamsaLagna = navamsaPositions[0]!.rasi;
  return navamsaLagna === 1 || navamsaLagna === 6; // Taurus or Libra
}

/**
 * Dwisatpathi: Lagna Lord in 7th or 7th Lord in Lagna.
 */
export function isDwisatpathiApplicable(positions: PlanetPosition[]): boolean {
  const lagna = positions[0]!.rasi;
  const lagnaLord = getHouseOwnerFromPlanetPositions(positions, lagna);
  const seventhHouse = (lagna + 6) % 12;
  const seventhLord = getHouseOwnerFromPlanetPositions(positions, seventhHouse);

  const lagnaLordHouse = positions.find(p => p.planet === lagnaLord)?.rasi ?? positions[lagnaLord + 1]?.rasi;
  const seventhLordHouse = positions.find(p => p.planet === seventhLord)?.rasi ?? positions[seventhLord + 1]?.rasi;

  return seventhLordHouse === lagna || lagnaLordHouse === seventhHouse;
}

/**
 * Panchottari: Lagna in Cancer Dwadasamsa.
 * Takes dwadasamsa positions as input.
 */
export function isPanchottariApplicable(dwadasamsaPositions: PlanetPosition[]): boolean {
  return dwadasamsaPositions[0]!.rasi === CANCER;
}

/**
 * Sataabdika: Lagna in same sign in Rasi and Navamsa.
 * Takes both rasi and navamsa positions.
 */
export function isSataabdikaApplicable(
  rasiPositions: PlanetPosition[],
  navamsaPositions: PlanetPosition[],
): boolean {
  return rasiPositions[0]!.rasi === navamsaPositions[0]!.rasi;
}

/**
 * Shastihayani: Sun in Lagna (Sun and Ascendant in same house).
 */
export function isShastihayaniApplicable(positions: PlanetPosition[]): boolean {
  return positions[0]!.rasi === positions[1]!.rasi;
}

// ============================================================================
// ORCHESTRATOR
// ============================================================================

export type ApplicableDhasa =
  | 'ashtottari'
  | 'chaturaseethi'
  | 'dwadasottari'
  | 'dwisatpathi'
  | 'panchottari'
  | 'sataabdika'
  | 'shastihayani';

/**
 * Check which conditional graha dhasas are applicable for a given chart.
 * @param d1Positions - D1 (rasi) planet positions
 * @returns Array of applicable dhasa names
 */
export function getApplicableDhasas(d1Positions: PlanetPosition[]): ApplicableDhasa[] {
  const result: ApplicableDhasa[] = [];

  if (isAshtottariApplicable(d1Positions)) result.push('ashtottari');
  if (isChaturaseethiApplicable(d1Positions)) result.push('chaturaseethi');

  // Dwadasottari checks navamsa
  const navamsaPositions = getDivisionalChart(d1Positions, 9);
  if (isDwadasottariApplicable(navamsaPositions)) result.push('dwadasottari');

  if (isDwisatpathiApplicable(d1Positions)) result.push('dwisatpathi');

  // Panchottari checks dwadasamsa
  const dwadasamsaPositions = getDivisionalChart(d1Positions, 12);
  if (isPanchottariApplicable(dwadasamsaPositions)) result.push('panchottari');

  // Sataabdika checks rasi vs navamsa lagna
  if (isSataabdikaApplicable(d1Positions, navamsaPositions)) result.push('sataabdika');

  if (isShastihayaniApplicable(d1Positions)) result.push('shastihayani');

  return result;
}
