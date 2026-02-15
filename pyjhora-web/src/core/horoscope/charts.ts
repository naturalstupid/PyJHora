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
    calculateD30_Trimsamsa_Parashara,
    calculateD3_Drekkana_Parashara,
    calculateD40_Khavedamsa_Parashara,
    calculateD45_Akshavedamsa_Parashara,
    calculateD4_Chaturthamsa_Parashara,
    calculateD60_Shashtiamsa_Parashara,
    calculateD7_Saptamsa_Parashara,
  calculateD9_Navamsa_Parashara,
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
} from '../constants';

import { getRelativeHouseOfPlanet } from './house';

export interface PlanetPosition {
  planet: number;
  rasi: number;
  longitude: number; // In degrees (0-30 within sign)
}

export type VargaMethod = 'PARASHARA' | 'CYCLIC' | 'JAGANNATHA' | 'PARIVRITTI_EVEN_REVERSE'; // Add more as needed

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
 * Get planetary positions for a specific divisional chart
 * @param d1Positions - Positions in Rasi chart (D1)
 * @param divisionFactor - Chart to calculate (e.g. 9)
 * @param method - Calculation method (default PARASHARA)
 * @returns Array of transformed positions
 */
export const getDivisionalChart = (
  d1Positions: PlanetPosition[],
  divisionFactor: number,
  method: VargaMethod = 'PARASHARA'
): PlanetPosition[] => {
  return d1Positions.map(pos => {
    // Reconstruct absolute longitude from D1 rasi and longitude
    const totalLongitude = pos.rasi * 30 + pos.longitude;
    
    let vargaSign = 0;
    
    // Dispatch to specific calculator based on factor and method
    // Currently implementing standard PARASHARA methods
    switch (divisionFactor) {
      case 1:
        // Use Python-compliant D1 logic (handles boundary snapping)
        const d1Result = dasavargaFromLong(totalLongitude, 1);
        return {
          planet: pos.planet,
          rasi: d1Result.rasi,
          longitude: d1Result.longitude
        };
      case 2:
        vargaSign = calculateD2_Hora_Parashara(totalLongitude); 
        // Note: Other Hora methods like cyclic/parivritti exist but Parashara is standard
        break;
      case 3:
        vargaSign = calculateD3_Drekkana_Parashara(totalLongitude);
        break;
      case 4:
        vargaSign = calculateD4_Chaturthamsa_Parashara(totalLongitude);
        break;
      case 7:
        vargaSign = calculateD7_Saptamsa_Parashara(totalLongitude);
        break;
      case 9:
        vargaSign = calculateD9_Navamsa_Parashara(totalLongitude);
        break;
      case 10:
        vargaSign = calculateD10_Dasamsa_Parashara(totalLongitude);
        break;
      case 12:
        vargaSign = calculateD12_Dwadasamsa_Parashara(totalLongitude);
        break;
      case 16:
        vargaSign = calculateD16_Shodasamsa_Parashara(totalLongitude);
        break;
      case 20:
        vargaSign = calculateD20_Vimsamsa_Parashara(totalLongitude);
        break;
      case 24:
        vargaSign = calculateD24_Chaturvimsamsa_Parashara(totalLongitude);
        break;
      case 27:
        vargaSign = calculateD27_Bhamsa_Parashara(totalLongitude);
        break;
      case 30:
        vargaSign = calculateD30_Trimsamsa_Parashara(totalLongitude);
        break;
      case 40:
        vargaSign = calculateD40_Khavedamsa_Parashara(totalLongitude);
        break;
      case 45:
        vargaSign = calculateD45_Akshavedamsa_Parashara(totalLongitude);
        break;
      case 60:
        vargaSign = calculateD60_Shashtiamsa_Parashara(totalLongitude);
        break;
      default:
        // Default to Cyclic if no specific logic exists or for custom D-charts
        vargaSign = calculateCyclicVarga(totalLongitude, divisionFactor);
        break;
    }

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
