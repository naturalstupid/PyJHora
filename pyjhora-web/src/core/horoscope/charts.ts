/**
 * Divisional Chart (Varga) Calculations
 * Dispatcher for calculating various divisional charts.
 * Also includes pure-calculation utility functions for chart analysis.
 */

import {
    calculateCyclicVarga,
    calculateD10_Dasamsa_Parashara,
    calculateD12_Dwadasamsa_Parashara,
    calculateD16_Shodasamsa_Parashara,
    calculateD20_Vimsamsa_Parashara,
    calculateD24_Chaturvimsamsa_Parashara,
    calculateD27_Bhamsa_Parashara,
    calculateD2_Hora_Parashara,
    calculateD2_Hora_ParivrittiEvenReverse,
    calculateD2_Hora_Raman,
    calculateD2_Hora_ParivrittiCyclic,
    calculateD2_Hora_Somanatha,
    calculateD30_Trimsamsa_Parashara,
    calculateD3_Drekkana_Parashara,
    calculateD3_Drekkana_ParivrittiCyclic,
    calculateD3_Drekkana_Somanatha,
    calculateD3_Drekkana_Jagannatha,
    calculateD3_Drekkana_ParivrittiEvenReverse,
    calculateD40_Khavedamsa_Parashara,
    calculateD45_Akshavedamsa_Parashara,
    calculateD4_Chaturthamsa_Parashara,
    calculateD4_ParivrittiCyclic,
    calculateD4_ParivrittiEvenReverse,
    calculateD4_Somanatha,
    calculateD60_Shashtiamsa_Parashara,
    calculateD7_Saptamsa_Parashara,
    calculateD7_ParivrittiCyclic,
    calculateD7_ParivrittiEvenReverse,
    calculateD7_Somanatha,
    calculateD9_Navamsa_Parashara,
    calculateD9_Navamsa_ParivrittiCyclic,
    calculateD9_Navamsa_Kalachakra,
    calculateD9_Navamsa_ParivrittiEvenReverse,
    calculateD9_Navamsa_Somanatha,
    calculateD10_ParivrittiCyclic,
    calculateD10_ParivrittiEvenReverse,
    calculateD10_Somanatha,
    calculateD12_ParivrittiEvenReverse,
    calculateD12_Somanatha,
    calculateD7_Saptamsa_ParasharaEvenBackward,
    calculateD7_Saptamsa_ParasharaReverseEnd7th,
    calculateD10_Dasamsa_ParasharaEvenBackward,
    calculateD10_Dasamsa_ParasharaEvenReverse,
    calculateD12_Dwadasamsa_ParasharaEvenReverse,
    calculateD5_Panchamsa_Parashara,
    calculateD6_Shashthamsa_Parashara,
    calculateD8_Ashtamsa_Parashara,
    calculateD11_Rudramsa_Parashara,
    calculateD11_Rudramsa_BVRaman,
    calculateParivrittiEvenReverse,
    calculateParivrittiAlternate,
    dasavargaFromLong
} from './varga-utils';

import {
  SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, RAHU, KETU,
  NATURAL_BENEFICS, NATURAL_MALEFICS,
  PP_COUNT_UPTO_KETU,
  COMBUSTION_RANGE_OF_PLANETS_FROM_SUN,
  COMBUSTION_RANGE_OF_PLANETS_FROM_SUN_WHILE_RETROGRADE,
  PLANETS_RETROGRADE_LIMITS_FROM_SUN,
  PLANET_RETROGRESSION_CALCULATION_METHOD,
  MARANA_KARAKA_STHANA_OF_PLANETS,
  PUSHKARA_NAVAMSA,
  PUSHKARA_BHAGAS,
  HOUSE_OWNERS,
  ASCENDANT_SYMBOL,
  VIMSOTTARI_ADHIPATI_LIST,
  PAACHAKAADI_SAMBHANDHA,
  LATTA_STARS_OF_PLANETS,
} from '../constants';

import { PRASNA_KP_249_DICT } from '../kp-data';

import { nakshatraPada, cyclicCountOfStarsWithAbhijit } from '../panchanga/drik';

import { kendras } from './house';

import { getRelativeHouseOfPlanet } from './house';

export interface PlanetPosition {
  planet: number;
  rasi: number;
  longitude: number; // In degrees (0-30 within sign)
}

/**
 * Calculate the longitude within the varga sign
 * Formula: (Total Longitude * D) % 30
 * @param totalLongitude - Absolute longitude (0-360)
 * @param divisionFactor - D-Chart factor (e.g. 9 for Navamsa)
 * @returns Longitude in degrees (0-30)
 */
export const getLongitudeInVarga = (totalLongitude: number, divisionFactor: number): number => {
  return (totalLongitude * divisionFactor) % 30;
};

/**
 * Calculate the varga sign for a given longitude, factor, and chart method.
 * Python: Each chart has chart_method parameter (1=Parashara default, 2-6 vary by chart).
 */
const getVargaSignForMethod = (totalLongitude: number, divisionFactor: number, chartMethod: number): number => {
  switch (divisionFactor) {
    case 2: // Hora (Python default is chart_method=2 = Traditional Parasara)
      switch (chartMethod) {
        case 1: return calculateD2_Hora_ParivrittiEvenReverse(totalLongitude);
        case 2: return calculateD2_Hora_Parashara(totalLongitude); // Traditional (Leo/Cancer only)
        case 3: return calculateD2_Hora_Raman(totalLongitude);
        case 4: return calculateD2_Hora_ParivrittiCyclic(totalLongitude);
        case 6: return calculateD2_Hora_Somanatha(totalLongitude);
        default: return calculateD2_Hora_Parashara(totalLongitude); // Default = Traditional
      }
    case 3: // Drekkana
      switch (chartMethod) {
        case 1: return calculateD3_Drekkana_Parashara(totalLongitude);
        case 2: return calculateD3_Drekkana_ParivrittiCyclic(totalLongitude);
        case 3: return calculateD3_Drekkana_Somanatha(totalLongitude);
        case 4: return calculateD3_Drekkana_Jagannatha(totalLongitude);
        case 5: return calculateD3_Drekkana_ParivrittiEvenReverse(totalLongitude);
        default: return calculateD3_Drekkana_Parashara(totalLongitude);
      }
    case 4: // Chaturthamsa
      switch (chartMethod) {
        case 1: return calculateD4_Chaturthamsa_Parashara(totalLongitude);
        case 2: return calculateD4_ParivrittiCyclic(totalLongitude);
        case 3: return calculateD4_ParivrittiEvenReverse(totalLongitude);
        case 4: return calculateD4_Somanatha(totalLongitude);
        default: return calculateD4_Chaturthamsa_Parashara(totalLongitude);
      }
    case 7: // Saptamsa
      switch (chartMethod) {
        case 1: return calculateD7_Saptamsa_Parashara(totalLongitude);
        case 2: return calculateD7_Saptamsa_ParasharaEvenBackward(totalLongitude);
        case 3: return calculateD7_Saptamsa_ParasharaReverseEnd7th(totalLongitude);
        case 4: return calculateD7_ParivrittiCyclic(totalLongitude);
        case 5: return calculateD7_ParivrittiEvenReverse(totalLongitude);
        case 6: return calculateD7_Somanatha(totalLongitude);
        default: return calculateD7_Saptamsa_Parashara(totalLongitude);
      }
    case 9: // Navamsa
      switch (chartMethod) {
        case 1: return calculateD9_Navamsa_Parashara(totalLongitude);
        case 2: return calculateD9_Navamsa_ParivrittiEvenReverse(totalLongitude); // UKM
        case 3: return calculateD9_Navamsa_Kalachakra(totalLongitude);
        case 5: return calculateD9_Navamsa_ParivrittiCyclic(totalLongitude);
        case 6: return calculateD9_Navamsa_Somanatha(totalLongitude);
        default: return calculateD9_Navamsa_Parashara(totalLongitude);
      }
    case 10: // Dasamsa
      switch (chartMethod) {
        case 1: return calculateD10_Dasamsa_Parashara(totalLongitude);
        case 2: return calculateD10_Dasamsa_ParasharaEvenBackward(totalLongitude);
        case 3: return calculateD10_Dasamsa_ParasharaEvenReverse(totalLongitude);
        case 4: return calculateD10_ParivrittiCyclic(totalLongitude);
        case 5: return calculateD10_ParivrittiEvenReverse(totalLongitude);
        case 6: return calculateD10_Somanatha(totalLongitude);
        default: return calculateD10_Dasamsa_Parashara(totalLongitude);
      }
    case 12: // Dwadasamsa
      switch (chartMethod) {
        case 1: return calculateD12_Dwadasamsa_Parashara(totalLongitude);
        case 2: return calculateD12_Dwadasamsa_ParasharaEvenReverse(totalLongitude);
        case 3: return calculateCyclicVarga(totalLongitude, 12);
        case 4: return calculateD12_ParivrittiEvenReverse(totalLongitude);
        case 5: return calculateD12_Somanatha(totalLongitude);
        default: return calculateD12_Dwadasamsa_Parashara(totalLongitude);
      }
    case 5: // Panchamsa
      switch (chartMethod) {
        case 1: return calculateD5_Panchamsa_Parashara(totalLongitude);
        case 2: return calculateCyclicVarga(totalLongitude, 5);
        case 3: return calculateParivrittiEvenReverse(totalLongitude, 5);
        case 4: return calculateParivrittiAlternate(totalLongitude, 5);
        default: return calculateD5_Panchamsa_Parashara(totalLongitude);
      }
    case 6: // Shashthamsa
      switch (chartMethod) {
        case 1: return calculateD6_Shashthamsa_Parashara(totalLongitude);
        case 2: return calculateCyclicVarga(totalLongitude, 6);
        case 3: return calculateParivrittiEvenReverse(totalLongitude, 6);
        case 4: return calculateParivrittiAlternate(totalLongitude, 6);
        default: return calculateD6_Shashthamsa_Parashara(totalLongitude);
      }
    case 8: // Ashtamsa
      switch (chartMethod) {
        case 1: return calculateD8_Ashtamsa_Parashara(totalLongitude);
        case 2: return calculateCyclicVarga(totalLongitude, 8);
        case 3: return calculateParivrittiEvenReverse(totalLongitude, 8);
        case 4: return calculateParivrittiAlternate(totalLongitude, 8);
        default: return calculateD8_Ashtamsa_Parashara(totalLongitude);
      }
    case 11: // Rudramsa
      switch (chartMethod) {
        case 1: return calculateD11_Rudramsa_Parashara(totalLongitude);
        case 2: return calculateD11_Rudramsa_BVRaman(totalLongitude);
        case 3: return calculateCyclicVarga(totalLongitude, 11);
        case 4: return calculateParivrittiEvenReverse(totalLongitude, 11);
        case 5: return calculateParivrittiAlternate(totalLongitude, 11);
        default: return calculateD11_Rudramsa_Parashara(totalLongitude);
      }
    case 16: return calculateD16_Shodasamsa_Parashara(totalLongitude);
    case 20: return calculateD20_Vimsamsa_Parashara(totalLongitude);
    case 24: return calculateD24_Chaturvimsamsa_Parashara(totalLongitude);
    case 27: return calculateD27_Bhamsa_Parashara(totalLongitude);
    case 30: return calculateD30_Trimsamsa_Parashara(totalLongitude);
    case 40: return calculateD40_Khavedamsa_Parashara(totalLongitude);
    case 45: return calculateD45_Akshavedamsa_Parashara(totalLongitude);
    case 60: return calculateD60_Shashtiamsa_Parashara(totalLongitude);
    case 81: // Nava Navamsa (m=1=Cyclic default, m=4=Kalachakra handled in getDivisionalChart)
      switch (chartMethod) {
        case 1: return calculateCyclicVarga(totalLongitude, 81);
        case 2: return calculateParivrittiEvenReverse(totalLongitude, 81);
        case 3: return calculateParivrittiAlternate(totalLongitude, 81);
        default: return calculateCyclicVarga(totalLongitude, 81);
      }
    case 108: // Ashtotharamsa (m=1=composite handled in getDivisionalChart)
      switch (chartMethod) {
        case 2: return calculateCyclicVarga(totalLongitude, 108);
        case 3: return calculateParivrittiEvenReverse(totalLongitude, 108);
        case 4: return calculateParivrittiAlternate(totalLongitude, 108);
        default: return calculateCyclicVarga(totalLongitude, 108);
      }
    case 144: // Dwadas Dwadasamsa (m=1=composite handled in getDivisionalChart)
      switch (chartMethod) {
        case 2: return calculateCyclicVarga(totalLongitude, 144);
        case 3: return calculateParivrittiEvenReverse(totalLongitude, 144);
        case 4: return calculateParivrittiAlternate(totalLongitude, 144);
        default: return calculateCyclicVarga(totalLongitude, 144);
      }
    default:
      // For charts without specific Parashara methods, try generic parivritti
      if (chartMethod > 1) {
        switch (chartMethod) {
          case 2: return calculateCyclicVarga(totalLongitude, divisionFactor);
          case 3: return calculateParivrittiEvenReverse(totalLongitude, divisionFactor);
          case 4: return calculateParivrittiAlternate(totalLongitude, divisionFactor);
        }
      }
      return calculateCyclicVarga(totalLongitude, divisionFactor);
  }
};

/**
 * Get planetary positions for a specific divisional chart
 * @param d1Positions - Positions in Rasi chart (D1)
 * @param divisionFactor - Chart to calculate (e.g. 9)
 * @param chartMethod - Chart calculation method (1=Parashara default, higher=variants)
 * @returns Array of transformed positions
 */
export const getDivisionalChart = (
  d1Positions: PlanetPosition[],
  divisionFactor: number,
  chartMethod: number = 0
): PlanetPosition[] => {
  // Composite charts (apply two vargas sequentially)
  if (divisionFactor === 81 && chartMethod === 4) {
    // D-81 m=4: Kalachakra Nava Navamsa (D-9 Kalachakra applied twice)
    return getMixedDivisionalChart(d1Positions, 9, 3, 9, 3);
  }
  if (divisionFactor === 108 && (chartMethod <= 1)) {
    // D-108 Parashara: D-9 (Parashara) then D-12 (Parashara)
    return getMixedDivisionalChart(d1Positions, 9, 1, 12, 1);
  }
  if (divisionFactor === 144 && (chartMethod <= 1)) {
    // D-144 Parashara: D-12 (Parashara) then D-12 (Parashara)
    return getMixedDivisionalChart(d1Positions, 12, 1, 12, 1);
  }

  return d1Positions.map(pos => {
    const totalLongitude = pos.rasi * 30 + pos.longitude;

    if (divisionFactor === 1) {
      const d1Result = dasavargaFromLong(totalLongitude, 1);
      return { planet: pos.planet, rasi: d1Result.rasi, longitude: d1Result.longitude };
    }

    const vargaSign = getVargaSignForMethod(totalLongitude, divisionFactor, chartMethod);

    // Calculate new longitude in the varga
    const vargaLong = getLongitudeInVarga(totalLongitude, divisionFactor);

    return {
      planet: pos.planet,
      rasi: vargaSign,
      longitude: vargaLong
    };
  });
};

/**
 * Get composite (mixed) divisional chart by applying two varga transformations sequentially.
 * Used for D-108 (D9 then D12) and D-144 (D12 then D12).
 */
export const getMixedDivisionalChart = (
  d1Positions: PlanetPosition[],
  vargaFactor1: number,
  chartMethod1: number,
  vargaFactor2: number,
  chartMethod2: number
): PlanetPosition[] => {
  const pp1 = getDivisionalChart(d1Positions, vargaFactor1, chartMethod1);
  return getDivisionalChart(pp1, vargaFactor2, chartMethod2);
};

/**
 * Get positions for Ascendant and Planets for a specific chart
 * Assumes d1Positions includes Ascendant (usually as special ID or separate)
 * Standardizing input to include everything.
 */
export const calculateDivisionalChart = (
  jd: number, // Not used directly if we have D1 positions, but kept for signature compatibility with future
  d1Positions: PlanetPosition[],
  divisionFactor: number
): PlanetPosition[] => {
  return getDivisionalChart(d1Positions, divisionFactor);
};

// ============================================================================
// HOUSE-PLANET LIST CONVERSION
// ============================================================================

/**
 * Convert planet positions to a house-planet list.
 * Returns an array of 12 strings, one per house (rasi 0-11).
 * Each string contains planet identifiers separated by '/'.
 * Lagna (planet=-1) is represented as 'L'.
 *
 * Python: utils.get_house_planet_list_from_planet_positions(planet_positions)
 *
 * @param positions - Array of PlanetPosition
 * @returns Array of 12 strings, e.g. ['0', '1/5', '', 'L/3', ...]
 */
export const getHousePlanetListFromPositions = (positions: PlanetPosition[]): string[] => {
  const hToP: string[] = Array(12).fill('');
  for (const pos of positions) {
    const label = pos.planet === -1 ? ASCENDANT_SYMBOL : String(pos.planet);
    hToP[pos.rasi] += label + '/';
  }
  return hToP.map(x => x.endsWith('/') ? x.slice(0, -1) : x);
};

/**
 * Convert a house-planet list to a planet-house dict.
 * Given a chart as 12 strings (house-planet list), returns a map
 * from planet identifier to rasi index.
 *
 * @param chart - Array of 12 strings from getHousePlanetListFromPositions
 * @returns Map from planet string to rasi index
 */
export const getPlanetHouseDict = (chart: string[]): Record<string, number> => {
  const result: Record<string, number> = {};
  for (let h = 0; h < 12; h++) {
    if (chart[h] === '') continue;
    const planets = chart[h].split('/');
    for (const p of planets) {
      result[p.trim()] = h;
    }
  }
  return result;
};

// ============================================================================
// RETROGRADE DETECTION
// ============================================================================

/**
 * Determine planets in retrograde using the old (house-based) method.
 * This is used when PLANET_RETROGRESSION_CALCULATION_METHOD === 1.
 *
 * Python: _planets_in_retrograde_old(planet_positions)
 *
 * @param positions - Planet positions array (index 0=Lagna, 1=Sun, 2=Moon, 3-7=Mars..Saturn, 8=Rahu, 9=Ketu)
 * @returns Array of planet indices that are retrograde
 */
const _planetsInRetrogradeOld = (positions: PlanetPosition[]): number[] => {
  const retrogradePlanets: number[] = [];
  const sunPos = positions.find(p => p.planet === SUN);
  if (!sunPos) return retrogradePlanets;

  const sunHouse = sunPos.rasi;
  const sunLong = sunPos.rasi * 30 + sunPos.longitude;

  // Only check Mars(2) through Saturn(6), excluding Lagna, Sun, Moon, Rahu, Ketu
  for (const pos of positions) {
    const p = pos.planet;
    if (p < MARS || p > SATURN) continue;

    const planetHouse = pos.rasi;
    const planetLong = pos.rasi * 30 + pos.longitude;

    if (p === MARS) {
      // Mars retrograde if in 6th-8th house from Sun
      const relHouse = getRelativeHouseOfPlanet(sunHouse, planetHouse);
      if (relHouse >= 6 && relHouse <= 8) {
        retrogradePlanets.push(p);
      }
    } else if (p === MERCURY) {
      // Mercury retrograde if within 20 degrees of Sun
      if (planetLong > sunLong - 20 && planetLong < sunLong + 20) {
        retrogradePlanets.push(p);
      }
    } else if (p === JUPITER) {
      // Jupiter retrograde if in 5th-9th house from Sun
      const relHouse = getRelativeHouseOfPlanet(sunHouse, planetHouse);
      if (relHouse >= 5 && relHouse <= 9) {
        retrogradePlanets.push(p);
      }
    } else if (p === VENUS) {
      // Venus retrograde if within 30 degrees of Sun
      if (planetLong > sunLong - 30 && planetLong < sunLong + 30) {
        retrogradePlanets.push(p);
      }
    } else if (p === SATURN) {
      // Saturn retrograde if in 4th-10th house from Sun
      const relHouse = getRelativeHouseOfPlanet(sunHouse, planetHouse);
      if (relHouse >= 4 && relHouse <= 10) {
        retrogradePlanets.push(p);
      }
    }
  }
  return retrogradePlanets;
};

/**
 * Determine planets in retrograde using the degree-based (wiki) method.
 * This is used when PLANET_RETROGRESSION_CALCULATION_METHOD === 2.
 *
 * Python: planets_in_retrograde (method 2 branch)
 *
 * @param positions - Planet positions array
 * @returns Array of planet indices that are retrograde
 */
const _planetsInRetrogradeNew = (positions: PlanetPosition[]): number[] => {
  const retrogradePlanets: number[] = [];
  const sunPos = positions.find(p => p.planet === SUN);
  if (!sunPos) return retrogradePlanets;

  const sunLong = sunPos.rasi * 30 + sunPos.longitude;

  for (const pos of positions) {
    const p = pos.planet;
    if (p < MARS || p > SATURN) continue;

    const planetLong = pos.rasi * 30 + pos.longitude;
    const limits = PLANETS_RETROGRADE_LIMITS_FROM_SUN[p];
    if (!limits) continue;

    let pLongFromSun1 = (sunLong + 360 + limits[0]) % 360;
    let pLongFromSun2 = (sunLong + 360 + limits[1]) % 360;
    if (pLongFromSun2 < pLongFromSun1) {
      pLongFromSun2 += 360;
    }
    if (planetLong > pLongFromSun1 && planetLong < pLongFromSun2) {
      retrogradePlanets.push(p);
    }
  }
  return retrogradePlanets;
};

/**
 * Get the list of planets that are in retrograde based on planet positions.
 * Uses the calculation method set in PLANET_RETROGRESSION_CALCULATION_METHOD.
 *
 * NOTE: For accurate results, use drik.planetsInRetrograde(jd, place) if available.
 * This function uses position-based estimation only.
 *
 * Python: planets_in_retrograde(planet_positions)
 *
 * @param positions - Planet positions from divisional chart (must include Sun)
 * @param method - Override calculation method (1=old house-based, 2=degree-based). Defaults to constant.
 * @returns Array of planet indices (2-6) that are estimated to be retrograde
 */
export const planetsInRetrograde = (
  positions: PlanetPosition[],
  method: number = PLANET_RETROGRESSION_CALCULATION_METHOD
): number[] => {
  if (method === 1) {
    return _planetsInRetrogradeOld(positions);
  }
  return _planetsInRetrogradeNew(positions);
};

// ============================================================================
// COMBUSTION DETECTION
// ============================================================================

/**
 * Get the list of planets that are in combustion based on planet positions.
 * A planet is combust when it is within certain degrees of the Sun.
 * The combustion range differs for direct and retrograde planets.
 *
 * Python: planets_in_combustion(planet_positions, use_absolute_longitude=True)
 *
 * @param positions - Planet positions from divisional chart
 * @param useAbsoluteLongitude - If true, use absolute longitude (rasi*30+long). If false, use rasi longitude only.
 * @returns Array of planet indices that are combust
 */
export const planetsInCombustion = (
  positions: PlanetPosition[],
  useAbsoluteLongitude: boolean = true
): number[] => {
  const retrogradePlanets = planetsInRetrograde(positions);
  const sunPos = positions.find(p => p.planet === SUN);
  if (!sunPos) return [];

  const sunLong = useAbsoluteLongitude
    ? sunPos.rasi * 30 + sunPos.longitude
    : sunPos.longitude;

  const combustionPlanets: number[] = [];

  // Check Moon(1) through Saturn(6), skipping Sun(0), Rahu(7), Ketu(8)
  for (const pos of positions) {
    const p = pos.planet;
    if (p < MOON || p > SATURN) continue;

    const pLong = useAbsoluteLongitude
      ? pos.rasi * 30 + pos.longitude
      : pos.longitude;

    // Index into combustion arrays: Moon=0, Mars=1, Mercury=2, Jupiter=3, Venus=4, Saturn=5
    // Python uses p-2 index (where p is planet 2-7 for Mars-Saturn, but starts from Moon at p=1)
    // Actually Python iterates planet_positions[2:8] which is Moon(1)..Saturn(6) with index p-2
    // So Moon(1) -> index 1-1=0 (wait, Python does p-2 for combustion_range index)
    // Let me re-read: for p,(h,h_long) in planet_positions[2:8] means positions index 2..7
    // In Python positions: index 0=L, 1=Sun, 2=Moon, 3=Mars, 4=Mercury, 5=Jupiter, 6=Venus, 7=Saturn
    // So the planets are Moon(1),Mars(2),Mercury(3),Jupiter(4),Venus(5),Saturn(6)
    // combustion_range[p-2] where p=1 => index -1?  No...
    // Wait: Python planet id p for Moon=1, p-2=-1? That can't be right.
    // Let me re-check: the slice [2:8] gives indices 2,3,4,5,6,7
    // At index 2: p=1(Moon), index 3: p=2(Mars), ..., index 7: p=6(Saturn)
    // combustion_range[p-2] => Moon: 1-2=-1 (would be last element = Saturn's 15??) No...
    // Actually looking more carefully at the Python: planet_positions[2:8] gives 6 entries
    // These are [1,(h,l)], [2,(h,l)], [3,(h,l)], [4,(h,l)], [5,(h,l)], [6,(h,l)]
    // So p goes 1,2,3,4,5,6
    // combustion_range_of_planets_from_sun = [12,17,14,10,11,15] #moon,mars,mercury,jupiter,venus,saturn
    // p-2: for Moon(1) => -1 which in Python wraps to last index (15=Saturn). That seems like a bug.
    // But actually the comment says order is moon,mars,merc,jup,venus,saturn
    // So index 0=Moon, 1=Mars, 2=Mercury, 3=Jupiter, 4=Venus, 5=Saturn
    // For Moon p=1, p-2=-1 wraps to 5=15(Saturn range). But the Moon range should be 12.
    // Wait, let me re-check... Hmm, this is a potential bug in Python but the function note says
    // "Exclude Lagna, Sun, Rahu and Ketu" - so it checks Moon through Saturn.
    // With Python negative indexing, combustion_range[-1] = 15 (Saturn's range for Moon).
    // But looking at the constant comment: [12,17,14,10,11,15] = Moon,Mars,Merc,Jup,Venus,Saturn
    // So p-1 would be the correct index for Moon=1: p-1=0=12. Let me recheck.
    // Actually wait, Python code says: for p,(h,h_long) in planet_positions[2:8]
    // And combustion_range[p-2] where:
    //   Moon: p=1, p-2=-1 => 15 (this is wrong if intent was 12)
    // Hmm, but maybe the intent was planet_positions[3:8] for Mars..Saturn?
    // Actually re-reading: "planet_positions[2:8]: # Exclude Lagna, Sun, Rahu and Ketu"
    // But index 2 is Moon... So Moon IS included. The indexing p-2 for Moon gives -1.
    // In Python, list[-1] gives the last element = 15 (Saturn). Moon's combustion should be 12 (index 0).
    // This looks like a genuine off-by-one that uses Saturn's range (15) for Moon combustion.
    // We'll match Python's behavior exactly.
    const combustionIndex = p - 2;
    const combustionRange = retrogradePlanets.includes(p)
      ? COMBUSTION_RANGE_OF_PLANETS_FROM_SUN_WHILE_RETROGRADE
      : COMBUSTION_RANGE_OF_PLANETS_FROM_SUN;

    // Match Python negative indexing: combustion_range[p-2]
    const idx = combustionIndex < 0
      ? combustionRange.length + combustionIndex
      : combustionIndex;

    if (idx >= 0 && idx < combustionRange.length) {
      const range = combustionRange[idx];
      if (pLong >= sunLong - range && pLong <= sunLong + range) {
        combustionPlanets.push(p);
      }
    }
  }
  return combustionPlanets;
};

// ============================================================================
// BENEFICS AND MALEFICS CLASSIFICATION
// ============================================================================

/**
 * Classify planets as benefics and malefics based on chart positions and tithi.
 *
 * Rules (PVR Narasimha Rao method, method=2):
 * - Jupiter and Venus are always natural benefics.
 * - Sun, Mars, Rahu, Ketu are always natural malefics.
 * - Waxing Moon (tithi <= 15, Sukla paksha) is benefic; waning Moon is malefic.
 * - Mercury is benefic if alone or with more benefics; malefic if with more malefics.
 *   If equal count, the planet closest to Mercury in longitude decides.
 *
 * Rules (BV Raman method, method=1):
 * - Moon benefic if tithi 8-15 (bright half), malefic if tithi 23-30 (dark half)
 *
 * Python: benefics_and_malefics(jd, place, ...)
 * NOTE: This version takes tithi and positions as parameters instead of jd/place
 * to avoid Swiss Ephemeris dependency.
 *
 * @param positions - Planet positions from divisional chart
 * @param tithi - Tithi number (1-30). Sukla paksha: 1-15, Krishna paksha: 16-30.
 * @param method - 1=BV Raman, 2=PVR Narasimha Rao (default)
 * @param excludeRahuKetu - If true, exclude Rahu/Ketu from malefics list
 * @returns Tuple [benefics, malefics] where each is a sorted array of planet indices
 */
export const beneficsAndMalefics = (
  positions: PlanetPosition[],
  tithi: number,
  method: number = 2,
  excludeRahuKetu: boolean = false
): [number[], number[]] => {
  const beneficsList = [...NATURAL_BENEFICS];
  const maleficsList = excludeRahuKetu
    ? NATURAL_MALEFICS.filter(p => p !== RAHU && p !== KETU)
    : [...NATURAL_MALEFICS];

  // Classify Moon
  if (method === 2) {
    if (tithi > 15) {
      maleficsList.push(MOON);
    } else {
      beneficsList.push(MOON);
    }
  } else {
    if (tithi >= 8 && tithi <= 15) beneficsList.push(MOON);
    if (tithi >= 23 && tithi <= 30) maleficsList.push(MOON);
  }

  // Classify Mercury based on association
  const mercuryPos = positions.find(p => p.planet === MERCURY);
  if (mercuryPos) {
    const mercuryHouse = mercuryPos.rasi;

    // Count benefics and malefics in Mercury's house (Mars = Mercury's house in Python,
    // the variable name is misleading - it checks planets in Mercury's house)
    const marsMalefics = maleficsList.filter(p => {
      const pPos = positions.find(pos => pos.planet === p);
      return pPos && pPos.rasi === mercuryHouse;
    });
    const marsBenefics = beneficsList.filter(p => {
      const pPos = positions.find(pos => pos.planet === p);
      return pPos && pPos.rasi === mercuryHouse;
    });

    if (marsBenefics.length === 0 && marsMalefics.length === 0) {
      // Mercury alone -> benefic
      beneficsList.push(MERCURY);
    } else if (marsBenefics.length > marsMalefics.length) {
      beneficsList.push(MERCURY);
    } else if (marsMalefics.length > marsBenefics.length) {
      maleficsList.push(MERCURY);
    } else {
      // Equal count: closest planet to Mercury in longitude decides
      const planetsInMercuryHouse = positions.filter(
        pos => pos.rasi === mercuryHouse && pos.planet !== MERCURY && pos.planet !== -1
      );
      if (planetsInMercuryHouse.length > 0) {
        const closest = planetsInMercuryHouse.reduce((prev, curr) =>
          Math.abs(curr.longitude - mercuryPos.longitude) < Math.abs(prev.longitude - mercuryPos.longitude)
            ? curr
            : prev
        );
        if (beneficsList.includes(closest.planet)) {
          beneficsList.push(MERCURY);
        } else {
          maleficsList.push(MERCURY);
        }
      } else {
        // No other planets => benefic
        beneficsList.push(MERCURY);
      }
    }
  }

  // Deduplicate and sort
  const uniqueBenefics = [...new Set(beneficsList)].sort((a, b) => a - b);
  const uniqueMalefics = [...new Set(maleficsList)].sort((a, b) => a - b);
  return [uniqueBenefics, uniqueMalefics];
};

/**
 * Get list of benefic planets.
 * Convenience wrapper around beneficsAndMalefics.
 *
 * @param positions - Planet positions
 * @param tithi - Tithi number (1-30)
 * @param method - Classification method (1 or 2)
 * @param excludeRahuKetu - Whether to exclude Rahu/Ketu
 * @returns Sorted array of benefic planet indices
 */
export const getBenefics = (
  positions: PlanetPosition[],
  tithi: number,
  method: number = 2,
  excludeRahuKetu: boolean = false
): number[] => {
  return beneficsAndMalefics(positions, tithi, method, excludeRahuKetu)[0];
};

/**
 * Get list of malefic planets.
 * Convenience wrapper around beneficsAndMalefics.
 *
 * @param positions - Planet positions
 * @param tithi - Tithi number (1-30)
 * @param method - Classification method (1 or 2)
 * @param excludeRahuKetu - Whether to exclude Rahu/Ketu
 * @returns Sorted array of malefic planet indices
 */
export const getMalefics = (
  positions: PlanetPosition[],
  tithi: number,
  method: number = 2,
  excludeRahuKetu: boolean = false
): number[] => {
  return beneficsAndMalefics(positions, tithi, method, excludeRahuKetu)[1];
};

// ============================================================================
// MARANA KARAKA STHANA
// ============================================================================

/**
 * Get planets that are in their Marana Karaka Sthana (death-inflicting positions).
 * A planet is in MKS when it occupies a specific house relative to the ascendant:
 * Sun/12th, Moon/8th, Mars/7th, Mercury/7th, Jupiter/3rd, Venus/6th,
 * Saturn/1st, Rahu/9th, Ketu/4th.
 *
 * Python: get_planets_in_marana_karaka_sthana(planet_positions, consider_ketu_4th_house=True)
 *
 * @param positions - Planet positions (must include Lagna as planet=-1)
 * @param considerKetu4thHouse - If true, include Ketu; if false, check up to Rahu only.
 * @returns Array of [planet, house_number] pairs for planets in MKS
 */
export const getPlanetsInMaranaKarakaSthana = (
  positions: PlanetPosition[],
  considerKetu4thHouse: boolean = true
): [number, number][] => {
  const mksResults: [number, number][] = [];
  const lagnaPos = positions.find(p => p.planet === -1);
  if (!lagnaPos) return mksResults;

  const ascHouse = lagnaPos.rasi;
  const maxPlanet = considerKetu4thHouse ? KETU : RAHU - 1;

  for (const pos of positions) {
    const p = pos.planet;
    if (p < SUN || p > maxPlanet) continue;

    const planetHouse = getRelativeHouseOfPlanet(ascHouse, pos.rasi);
    if (planetHouse === MARANA_KARAKA_STHANA_OF_PLANETS[p]) {
      mksResults.push([p, planetHouse]);
    }
  }
  return mksResults;
};

// ============================================================================
// PUSHKARA NAVAMSA AND BHAGA
// ============================================================================

/**
 * Find planets in Pushkara Navamsa and Pushkara Bhaga positions.
 * Pushkara Navamsa: specific navamsa ranges within each sign considered auspicious.
 * Pushkara Bhaga: specific degree points within each sign considered auspicious.
 *
 * Python: planets_in_pushkara_navamsa_bhaga(planet_positions)
 *
 * @param positions - Planet positions (should include Sun through Ketu, Lagna excluded from results)
 * @returns Tuple [pushkaraNavamsaPlanets, pushkaraBhagaPlanets]
 */
export const planetsInPushkaraNavamsaBhaga = (
  positions: PlanetPosition[]
): [number[], number[]] => {
  const pna: number[] = [];
  const pb: number[] = [];

  // Process planets only (skip Lagna at planet=-1)
  // Python slices [1:PP_COUNT_UPTO_KETU] which is Sun(index 1) through Ketu(index 9)
  const planetPositions = positions.filter(p => p.planet >= SUN && p.planet <= KETU);

  for (const pos of planetPositions) {
    const sign = pos.rasi;
    const long = pos.longitude;
    const pushNavStart = PUSHKARA_NAVAMSA[sign];
    const navamsaSpan = 30 / 9; // 3.333... degrees

    // Check two pushkara navamsa ranges per sign
    if ((long >= pushNavStart && long < pushNavStart + navamsaSpan) ||
        (long >= pushNavStart + 60 / 9 && long < pushNavStart + 10)) {
      pna.push(pos.planet);
    }

    // Check pushkara bhaga (1-degree range ending at the pushkara bhaga degree)
    const pushBhaga = PUSHKARA_BHAGAS[sign];
    if (long >= pushBhaga - 1 && long < pushBhaga) {
      pb.push(pos.planet);
    }
  }

  return [pna, pb];
};

// ============================================================================
// 64TH NAVAMSA AND 22ND DREKKANA
// ============================================================================

/**
 * Calculate the 64th navamsa for each planet/lagna from navamsa positions.
 * The 64th navamsa is the 4th sign from the navamsa position (i.e., (rasi+3) % 12),
 * along with its lord.
 *
 * Python: get_64th_navamsa(navamsa_planet_positions)
 *
 * @param navamsaPositions - Planet positions in the D-9 (Navamsa) chart
 * @returns Map from planet id to [64th_navamsa_rasi, lord_of_that_rasi]
 */
export const get64thNavamsa = (
  navamsaPositions: PlanetPosition[]
): Record<number, [number, number]> => {
  const result: Record<number, [number, number]> = {};
  for (const pos of navamsaPositions) {
    const navamsa64 = (pos.rasi + 3) % 12;
    const lord = HOUSE_OWNERS[navamsa64];
    result[pos.planet] = [navamsa64, lord];
  }
  return result;
};

/**
 * Calculate the 22nd drekkana for each planet/lagna from drekkana positions.
 * The 22nd drekkana is the 8th sign from the drekkana position (i.e., (rasi+7) % 12),
 * along with its lord.
 *
 * Python: get_22nd_drekkana(drekkana_planet_positions)
 *
 * @param drekkanaPositions - Planet positions in the D-3 (Drekkana) chart
 * @returns Map from planet id to [22nd_drekkana_rasi, lord_of_that_rasi]
 */
export const get22ndDrekkana = (
  drekkanaPositions: PlanetPosition[]
): Record<number, [number, number]> => {
  const result: Record<number, [number, number]> = {};
  for (const pos of drekkanaPositions) {
    const drekkana22 = (pos.rasi + 7) % 12;
    const lord = HOUSE_OWNERS[drekkana22];
    result[pos.planet] = [drekkana22, lord];
  }
  return result;
};

// ============================================================================
// PLANET ORDERING & HOUSE ASSIGNMENT
// ============================================================================

/**
 * Order planets starting from the kendra houses of a given rasi.
 * Planets within the same house are sorted by longitude (descending, most advanced first).
 *
 * Python: order_planets_from_kendras_of_raasi(planet_positions, raasi, include_lagna)
 *
 * @param positions - Planet positions array
 * @param raasi - Base rasi to calculate kendras from (defaults to Lagna rasi)
 * @param includeLagna - Whether to include Lagna in the result
 * @returns Array of planet indices ordered from kendras
 */
export const orderPlanetsFromKendrasOfRaasi = (
  positions: PlanetPosition[],
  raasi?: number,
  includeLagna: boolean = false
): number[] => {
  const baseHouse = raasi ?? (positions.find(p => p.planet === -1)?.rasi ?? 0);

  // Get kendra offsets (1st, 4th, 7th, 10th) plus 2nd, 5th, 8th, 11th, 3rd, 6th, 9th, 12th
  // kendras() returns arrays for each house; use first 3 groups (kendra, panapara, apoklima)
  const ks = kendras().slice(0, 3).flat();

  // Build house->planets map
  const hToP: Record<number, PlanetPosition[]> = {};
  for (const pos of positions) {
    if (!includeLagna && pos.planet === -1) continue;
    const h = pos.rasi;
    if (!hToP[h]) hToP[h] = [];
    hToP[h].push(pos);
  }

  const result: number[] = [];
  for (const offset of ks) {
    const house = (baseHouse + offset - 1) % 12;
    const planetsInHouse = hToP[house];
    if (!planetsInHouse || planetsInHouse.length === 0) continue;

    // Sort by longitude descending (most advanced first)
    const sorted = [...planetsInHouse].sort((a, b) => b.longitude - a.longitude);
    for (const p of sorted) {
      result.push(p.planet);
    }
  }
  return result;
};

/**
 * Assign planets to bhava (house) divisions based on their longitudes within house cusps.
 *
 * Python: _assign_planets_to_houses(planet_positions, bhava_houses, bhava_madhya_method)
 *
 * @param positions - Planet positions
 * @param bhavaHouses - Array of 12 bhava cusp triples [start, mid, end] in degrees (0-360)
 * @param bhavaMadhyaMethod - Bhava rasi assignment method:
 *   1 or 5: Rasi based on bhava cusp mid-point (or equal rasi)
 *   2: Rasi based on bhava start
 *   3 or 4+: Sripati/KP/Western (rasi based on bhava start, degrees modded)
 * @returns Array of 12 bhava objects: { rasi, cusps: [start, mid, end], planets: number[] }
 */
export const assignPlanetsToHouses = (
  positions: PlanetPosition[],
  bhavaHouses: [number, number, number][],
  bhavaMadhyaMethod: number = 1
): Array<{ rasi: number; cusps: [number, number, number]; planets: number[] }> => {
  const result: Array<{ rasi: number; cusps: [number, number, number]; planets: number[] }> = [];

  for (const [bhavaStart, bhavaMid, bhavaEnd] of bhavaHouses) {
    const planetsInHouse: number[] = [];
    let effectiveEnd = bhavaEnd;
    if (effectiveEnd < bhavaStart) effectiveEnd += 360;

    for (const pos of positions) {
      const pLong = pos.rasi * 30 + pos.longitude;
      if ((pLong >= bhavaStart && pLong < effectiveEnd) ||
          (pLong + 360 >= bhavaStart && pLong + 360 < effectiveEnd)) {
        planetsInHouse.push(pos.planet);
      }
    }

    let rasi: number;
    if (bhavaMadhyaMethod === 1 || bhavaMadhyaMethod === 5) {
      rasi = Math.floor(bhavaMid / 30);
    } else if (bhavaMadhyaMethod === 2) {
      rasi = Math.floor(bhavaStart / 30);
    } else {
      // Sripati / KP / Western
      rasi = Math.floor(bhavaStart / 30);
    }

    const cusps: [number, number, number] =
      bhavaMadhyaMethod >= 3
        ? [bhavaStart % 360, bhavaMid % 360, bhavaEnd % 360]
        : [bhavaStart, bhavaMid, bhavaEnd];

    result.push({ rasi, cusps, planets: planetsInHouse });
  }

  return result;
};

// ============================================================================
// KP (KRISHNAMURTI PADDHATI) LORDS
// ============================================================================

/**
 * Get KP details for a planet longitude from the 249 sub-lord table.
 * Python: utils.get_KP_details_from_planet_longitude
 *
 * @param planetLongitude - Absolute longitude (0-360)
 * @returns Map of { kpNo: [rasi, nakshatra, startDeg, endDeg, signLord, starLord, subLord] }
 */
const getKPDetailsFromPlanetLongitude = (
  planetLongitude: number
): Record<number, [number, number, number, number, number, number, number]> => {
  const result: Record<number, [number, number, number, number, number, number, number]> = {};
  for (const [kpNoStr, details] of Object.entries(PRASNA_KP_249_DICT)) {
    const [r, n, sd, ed, rl, sl, ssl] = details;
    if (planetLongitude >= r * 30 + sd && planetLongitude <= r * 30 + ed) {
      result[Number(kpNoStr)] = [r, n, sd, ed, rl, sl, ssl];
    }
  }
  return result;
};

/**
 * Get KP lords for a single planet from its rasi and longitude.
 * Returns [kpNo, starLord, subLord, subSubLord1..4].
 * Python: charts._get_KP_lords_from_planet_longitude
 */
const getKPLordsFromPlanetLongitude = (
  planet: number,
  rasi: number,
  rasiLongitude: number
): Record<number, number[]> => {
  const lords = VIMSOTTARI_ADHIPATI_LIST;
  const lordFractions = [7 / 120, 20 / 120, 6 / 120, 10 / 120, 7 / 120, 18 / 120, 16 / 120, 19 / 120, 17 / 120];
  const nextLord = (lord: number, dirn: number = 1): number =>
    lords[(lords.indexOf(lord) + dirn + lords.length) % lords.length];

  const pLong = rasi * 30 + rasiLongitude;
  const kpDetails = getKPDetailsFromPlanetLongitude(pLong);
  const entries = Object.entries(kpDetails);
  if (entries.length === 0) return {};

  const [kpNoStr, details] = entries[0];
  const kpNo = Number(kpNoStr);
  let [, , sd, ed, , starLord, starSubLord] = details;

  const kpInfo: Record<number, number[]> = {};
  kpInfo[planet] = [kpNo, starLord, starSubLord];

  let subLord = starSubLord;
  for (let i = 0; i < 4; i++) {
    let subSubLord = subLord;
    let count = 1;
    const durn = ed - sd;
    while (true) {
      ed = sd + lordFractions[subSubLord] * durn;
      if ((rasiLongitude > sd && rasiLongitude < ed) || count > 9) break;
      subSubLord = nextLord(subSubLord);
      count++;
      sd = ed;
    }
    kpInfo[planet].push(subSubLord);
    subLord = subSubLord;
  }

  return kpInfo;
};

/**
 * Get KP lords for all planets from their positions.
 * Python: charts.get_KP_lords_from_planet_positions
 *
 * @param positions - Planet positions array
 * @returns Map of planet -> [kpNo, starLord, subLord, subSub1, subSub2, subSub3, subSub4]
 */
export const getKPLordsFromPlanetPositions = (
  positions: PlanetPosition[]
): Record<number, number[]> => {
  let kpInfo: Record<number, number[]> = {};
  for (const pos of positions) {
    const planetKP = getKPLordsFromPlanetLongitude(pos.planet, pos.rasi, pos.longitude);
    kpInfo = { ...kpInfo, ...planetKP };
  }
  return kpInfo;
};

// ============================================================================
// PACHAKADI SAMBHANDHA
// ============================================================================

/**
 * Get pachakadi sambhandha (pachaka/bodhaka/karaka/vedhaka) relationships.
 * Python: charts.get_pachakadi_sambhandha
 *
 * @param positions - Planet positions array (must include Lagna at planet=-1)
 * @returns Map of planet -> [relationIndex, [relatedPlanet, houseOffset, relationType]]
 */
export const getPachakadiSambhandha = (
  positions: PlanetPosition[]
): Record<number, [number, [number, number, string]]> => {
  const posMap = new Map<number, number>();
  for (const pos of positions) {
    posMap.set(pos.planet, pos.rasi);
  }

  const result: Record<number, [number, [number, number, string]]> = {};

  for (const [planetStr, relations] of Object.entries(PAACHAKAADI_SAMBHANDHA)) {
    const planet = Number(planetStr);
    const planetRasi = posMap.get(planet);
    if (planetRasi === undefined) continue;

    for (let idx = 0; idx < relations.length; idx++) {
      const [relPlanet, houseOffset, relType] = relations[idx];
      const relPlanetRasi = posMap.get(relPlanet);
      if (relPlanetRasi === undefined) continue;

      if (relPlanetRasi === (planetRasi + houseOffset - 1) % 12) {
        result[planet] = [idx, [relPlanet, houseOffset, relType]];
      }
    }
  }

  return result;
};

// ============================================================================
// LATTA STARS
// ============================================================================

/**
 * Get latta (malefic) star for each planet based on its position.
 * Python: charts.lattha_stars_planets
 *
 * @param positions - Planet positions array (including Lagna at index 0)
 * @param includeAbhijit - Whether to use 28-star system (with Abhijit) or 27
 * @returns Array of [planetStar, lattaStar] tuples for each planet (Sun through Ketu)
 */
export const latthaStarsPlanets = (
  positions: PlanetPosition[],
  includeAbhijit: boolean = true
): [number, number][] => {
  const starCount = includeAbhijit ? 28 : 27;
  const result: [number, number][] = [];

  // Process planets Sun(0) through Ketu(8), skipping Lagna(-1)
  for (let p = 0; p <= 8; p++) {
    const pos = positions.find(pp => pp.planet === p);
    if (!pos) continue;

    const pLong = pos.rasi * 30 + pos.longitude;
    const pStar = nakshatraPada(pLong)[0];
    const [count, direction] = LATTA_STARS_OF_PLANETS[p];
    const lattaStar = cyclicCountOfStarsWithAbhijit(pStar, count, direction, starCount);
    result.push([pStar, lattaStar]);
  }

  return result;
};

// ============================================================================
// SOLAR UPAGRAHA LONGITUDES
// ============================================================================

/**
 * Solar upagraha longitude calculation lambdas.
 * Python: drik.py lines 1595-1599
 */
const dhumaLongitude = (sunLong: number): number => (sunLong + 133 + 20.0 / 60) % 360;
const vyatipaataLongitude = (sunLong: number): number => (360.0 - dhumaLongitude(sunLong)) % 360;
const pariveshaLongitude = (sunLong: number): number => (vyatipaataLongitude(sunLong) + 180.0) % 360;
const indrachaapaLongitude = (sunLong: number): number => (360.0 - pariveshaLongitude(sunLong)) % 360;
const upaketuLongitude = (sunLong: number): number => (sunLong - 30.0 + 360) % 360;

const SOLAR_UPAGRAHA_LIST = ['dhuma', 'vyatipaata', 'parivesha', 'indrachaapa', 'upaketu'] as const;
type SolarUpagraha = typeof SOLAR_UPAGRAHA_LIST[number];

const SOLAR_UPAGRAHA_FUNCTIONS: Record<SolarUpagraha, (sunLong: number) => number> = {
  dhuma: dhumaLongitude,
  vyatipaata: vyatipaataLongitude,
  parivesha: pariveshaLongitude,
  indrachaapa: indrachaapaLongitude,
  upaketu: upaketuLongitude,
};

/**
 * Get longitudes of solar-based upagrahas from a solar longitude.
 * Python: drik.solar_upagraha_longitudes
 *
 * @param solarLongitude - Absolute longitude of the Sun (0-360)
 * @param upagraha - One of 'dhuma', 'vyatipaata', 'parivesha', 'indrachaapa', 'upaketu'
 * @param divisionalChartFactor - Division factor (1=D1, 9=Navamsa, etc.)
 * @returns { rasi, longitude } or null if invalid upagraha
 */
export const solarUpagrahaLongitudesFromSunLong = (
  solarLongitude: number,
  upagraha: string,
  divisionalChartFactor: number = 1
): { rasi: number; longitude: number } | null => {
  const name = upagraha.toLowerCase() as SolarUpagraha;
  const fn = SOLAR_UPAGRAHA_FUNCTIONS[name];
  if (!fn) return null;
  const long = fn(solarLongitude);
  return dasavargaFromLong(long, divisionalChartFactor);
};

/**
 * Get longitudes of solar-based upagrahas from planet positions.
 * Python: charts.solar_upagraha_longitudes
 *
 * @param positions - Planet positions (first element is Lagna, second is Sun)
 * @param upagraha - One of 'dhuma', 'vyatipaata', 'parivesha', 'indrachaapa', 'upaketu'
 * @param divisionalChartFactor - Division factor (1=D1, 9=Navamsa, etc.)
 * @returns { rasi, longitude } or null if invalid
 */
export const solarUpagrahaLongitudes = (
  positions: PlanetPosition[],
  upagraha: string,
  divisionalChartFactor: number = 1
): { rasi: number; longitude: number } | null => {
  const sunPos = positions.find(p => p.planet === SUN);
  if (!sunPos) return null;
  const solarLongitude = sunPos.rasi * 30 + sunPos.longitude;
  return solarUpagrahaLongitudesFromSunLong(solarLongitude, upagraha, divisionalChartFactor);
};

// ============================================================================
// MIXED CHART FROM RASI POSITIONS
// ============================================================================

/**
 * Calculate a mixed (composite) divisional chart by chaining two varga calculations.
 * Python: charts.mixed_chart_from_rasi_positions
 *
 * @param d1Positions - Planet positions in D1 (Rasi chart)
 * @param vargaFactor1 - First divisional factor (e.g. 9 for Navamsa)
 * @param vargaFactor2 - Second divisional factor (e.g. 12 for Dwadasamsa)
 * @returns Planet positions in the mixed chart
 */
export const mixedChartFromRasiPositions = (
  d1Positions: PlanetPosition[],
  vargaFactor1: number,
  vargaFactor2: number
): PlanetPosition[] => {
  const pp1 = getDivisionalChart(d1Positions, vargaFactor1);
  return getDivisionalChart(pp1, vargaFactor2);
};
