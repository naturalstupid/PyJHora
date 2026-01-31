/**
 * Ashtakavarga Calculations
 * Ported from PyJHora ashtakavarga.py
 *
 * Includes:
 * - Binna Ashtakavarga (BAV) for 7 planets + Lagna
 * - Sarva Ashtakavarga (SAV) - combined totals
 * - Prastara Ashtakavarga - detailed contribution breakdown
 * - Trikona Sodhana - trine reduction
 * - Ekadhipatya Sodhana - dual lordship reduction
 * - Sodhya Pindas - weighted totals (Rasi, Graha, Sodhya)
 */

import {
  ASCENDANT_SYMBOL,
  ASHTAKA_VARGA_DICT,
  GRAHAMANA_MULTIPLIERS,
  RASIMANA_MULTIPLIERS
} from '../constants';
import type { HouseChart } from '../types';

/**
 * Ashtakavarga result containing all three components
 */
export interface AshtakavargaResult {
  /** Binna Ashtakavarga: 8x12 array [planet][rasi] of benefic points */
  binnaAshtakavarga: number[][];
  /** Sarva Ashtakavarga: 12-element array [rasi] of total points (excluding Lagna) */
  sarvaAshtakavarga: number[];
  /** Prastara Ashtakavarga: 8x9x12 array [planet][contributor][rasi] */
  prastaraAshtakavarga: number[][][];
}

/**
 * Sodhya Pindas result
 */
export interface SodhyaPindasResult {
  /** Rasi Pindas for each planet (Sun to Saturn) */
  raasiPindas: number[];
  /** Graha Pindas for each planet (Sun to Saturn) */
  grahaPindas: number[];
  /** Sodhya Pindas for each planet (Rasi + Graha) */
  sodhyaPindas: number[];
}

/**
 * Convert house chart (string format) to planet-to-house dictionary
 * @param houseChart - Array of 12 strings like ['0', '1/2', 'L', ...] where numbers are planet IDs
 * @returns Map of planet ID or 'L' to house index (0-11)
 */
export const getPlanetToHouseFromChart = (
  houseChart: HouseChart
): Record<number | string, number> => {
  const pToH: Record<number | string, number> = {};

  houseChart.forEach((planets, house) => {
    if (!planets || planets.trim() === '') return;

    // Split by '/' to handle multiple planets in same house
    const planetList = planets.split('/');

    planetList.forEach(p => {
      const trimmed = p.trim();
      if (trimmed === ASCENDANT_SYMBOL || trimmed === 'L') {
        pToH[ASCENDANT_SYMBOL] = house;
      } else {
        const planetId = parseInt(trimmed);
        if (!isNaN(planetId)) {
          pToH[planetId] = house;
        }
      }
    });
  });

  return pToH;
};

/**
 * Calculate Ashtakavarga (Binna, Sarva, and Prastara)
 *
 * @param houseChart - 1D array [0..11] with planets in each rasi
 *                     Example: ['', '', '', '', '2', '7', '1/5', '0', '3/4', 'L', '', '6/8']
 * @returns AshtakavargaResult containing BAV, SAV, and Prastara
 */
export const getAshtakavarga = (houseChart: HouseChart): AshtakavargaResult => {
  const pToH = getPlanetToHouseFromChart(houseChart);

  // Initialize arrays
  // raasi_ashtaka[planet][rasi] - 8 planets x 12 rasis
  const raasiAshtaka: number[][] = Array.from({ length: 8 }, () =>
    Array(12).fill(0)
  );

  // prastara_ashtaka_varga[planet][contributor][rasi] - 8 planets x 10 contributors x 12 rasis
  // Contributors: 0-6 = Sun to Saturn, 7 = Lagna, 8 = unused, 9 = total row
  const prastaraAshtakavarga: number[][][] = Array.from({ length: 8 }, () =>
    Array.from({ length: 10 }, () => Array(12).fill(0))
  );

  // Calculate Binna and Prastara Ashtakavarga
  for (let p = 0; p < 8; p++) {
    const planetRaasiList = ASHTAKA_VARGA_DICT[p];
    if (!planetRaasiList) continue;

    for (let op = 0; op < 8; op++) {
      // Get the rasi of the contributing planet/lagna
      let pr: number | undefined;
      if (op === 7) {
        // Lagna
        pr = pToH[ASCENDANT_SYMBOL];
      } else {
        pr = pToH[op];
      }

      if (pr === undefined) continue;

      const beneficHouses = planetRaasiList[op];
      if (!beneficHouses) continue;

      for (const house of beneficHouses) {
        // house is 1-indexed in the dict, convert to 0-indexed rasi
        const r = (house - 1 + pr) % 12;
        raasiAshtaka[p][r] += 1;
        prastaraAshtakavarga[p][op][r] = 1;
        prastaraAshtakavarga[p][9][r] += 1; // Total row
      }
    }
  }

  // Binna Ashtakavarga (first 8 rows)
  const binnaAshtakavarga = raasiAshtaka.slice(0, 8).map(row => [...row]);

  // Prastara (first 8 planets, first 9 rows per planet)
  const prastara = prastaraAshtakavarga
    .slice(0, 8)
    .map(planetArr => planetArr.slice(0, 9).map(row => [...row]));

  // Sarva Ashtakavarga - sum of BAV for planets 0-6 (excluding Lagna at index 7)
  const sarvaAshtakavarga: number[] = Array(12).fill(0);
  for (let r = 0; r < 12; r++) {
    for (let p = 0; p < 7; p++) {
      sarvaAshtakavarga[r] += binnaAshtakavarga[p][r];
    }
  }

  return {
    binnaAshtakavarga,
    sarvaAshtakavarga,
    prastaraAshtakavarga: prastara
  };
};

/**
 * Trikona Sodhana - Trine reduction on Binna Ashtakavarga
 *
 * Rules:
 * 1. If at least one rasi in the trine group has zero, no reduction
 * 2. If all three rasis have the same value, make them all zero
 * 3. Otherwise, subtract the minimum value from all three
 *
 * @param binnaAshtakavarga - 2D array [planet][rasi] from BAV
 * @returns Reduced BAV after trikona sodhana
 */
export const trikonaSodhana = (binnaAshtakavarga: number[][]): number[][] => {
  // Deep copy
  const bav = binnaAshtakavarga.map(row => [...row]);

  // Process only planets 0-6 (Sun to Saturn), not Lagna
  for (let p = 0; p < 7; p++) {
    // There are 4 trine groups: (0,4,8), (1,5,9), (2,6,10), (3,7,11)
    for (let r = 0; r < 4; r++) {
      const r1 = r;
      const r2 = r + 4;
      const r3 = r + 8;

      const planetRow = bav[p];
      if (!planetRow) continue;

      const v1 = planetRow[r1] ?? 0;
      const v2 = planetRow[r2] ?? 0;
      const v3 = planetRow[r3] ?? 0;

      // Rule 1: If at least one rasi has zero, no reduction
      if (v1 === 0 || v2 === 0 || v3 === 0) {
        continue;
      }

      // Rule 2: If all three have the same value, make them all zero
      if (v1 === v2 && v2 === v3) {
        planetRow[r1] = 0;
        planetRow[r2] = 0;
        planetRow[r3] = 0;
      } else {
        // Rule 3: Subtract the minimum from all three
        const minValue = Math.min(v1, v2, v3);
        planetRow[r1] = (planetRow[r1] ?? 0) - minValue;
        planetRow[r2] = (planetRow[r2] ?? 0) - minValue;
        planetRow[r3] = (planetRow[r3] ?? 0) - minValue;
      }
    }
  }

  return bav;
};

/**
 * Ekadhipatya Sodhana - Dual lordship reduction
 *
 * Applies to Mars, Mercury, Jupiter, Venus, Saturn (planets 2-6)
 * who own two signs each.
 *
 * Rules:
 * 1. If either rasi has zero value, no reduction
 * 2. If both rasis are occupied by planets, no reduction
 * 3. If one is occupied and one empty:
 *    a. If empty rasi has lower value, make it zero
 *    b. If empty rasi has higher value, replace with occupied rasi's value
 * 4. If both rasis are empty:
 *    a. If same value, make both zero
 *    b. If different, replace higher with lower
 *
 * @param bavAfterTrikona - BAV after trikona sodhana
 * @param houseChart - Original house chart to check occupancy
 * @returns Reduced BAV after ekadhipatya sodhana (also called Sodhita Ashtakavarga)
 */
export const ekadhipatyaSodhana = (
  bavAfterTrikona: number[][],
  houseChart: HouseChart
): number[][] => {
  // Deep copy
  const bav = bavAfterTrikona.map(row => [...row]);

  // Rasi pairs owned by each planet (Mars to Saturn, indices 2-6)
  // Format: [rasi1, rasi2] where both are owned by the same planet
  const raasiOwners: [number, number][] = [
    [4, 3], // Mars owns Leo(4) and Cancer(3) - wait, that's wrong
    // Actually: Mars owns Aries(0) and Scorpio(7)
    // Let me check the Python code again...
  ];

  // From Python: rasi_owners=[4,3,(0,7),(2,5),(8,11),(1,6),(9,10)]
  // This means:
  // Index 0: Leo (4) - Sun's only sign
  // Index 1: Cancer (3) - Moon's only sign
  // Index 2: (0, 7) = Aries, Scorpio - Mars
  // Index 3: (2, 5) = Gemini, Virgo - Mercury
  // Index 4: (8, 11) = Sagittarius, Pisces - Jupiter
  // Index 5: (1, 6) = Taurus, Libra - Venus
  // Index 6: (9, 10) = Capricorn, Aquarius - Saturn

  // For ekadhipatya, we only process planets with dual ownership (Mars to Saturn)
  // Python loop: for p in range(2,7): r1,r2 = rasi_owners[p]
  // So p=2 -> rasi_owners[2] = (0,7)
  // p=3 -> rasi_owners[3] = (2,5)
  // etc.

  const dualOwnershipPairs: Record<number, [number, number]> = {
    2: [0, 7], // Mars: Aries, Scorpio
    3: [2, 5], // Mercury: Gemini, Virgo
    4: [8, 11], // Jupiter: Sagittarius, Pisces
    5: [1, 6], // Venus: Taurus, Libra
    6: [9, 10] // Saturn: Capricorn, Aquarius
  };

  // Check if a rasi is occupied (has any planet or Lagna in it)
  const isOccupied = (rasi: number): boolean => {
    const content = houseChart[rasi];
    return content !== undefined && content.trim() !== '';
  };

  for (let p = 2; p <= 6; p++) {
    const pair = dualOwnershipPairs[p];
    if (!pair) continue;
    const [r1, r2] = pair;
    const planetRow = bav[p];
    if (!planetRow) continue;

    const r1Occupied = isOccupied(r1);
    const r2Occupied = isOccupied(r2);

    const val1 = planetRow[r1] ?? 0;
    const val2 = planetRow[r2] ?? 0;

    // Rule 1: If either BAV value is 0, no reduction
    // Rule 2: If both rasis are occupied, no reduction
    if (val1 === 0 || val2 === 0) {
      continue;
    }
    if (r1Occupied && r2Occupied) {
      continue;
    }

    // Rule 4: Both rasis are empty
    if (!r1Occupied && !r2Occupied) {
      if (val1 === val2) {
        // Rule 4(a): Same value, make both zero
        planetRow[r1] = 0;
        planetRow[r2] = 0;
      } else {
        // Rule 4(b): Different values, replace higher with lower
        const minValue = Math.min(val1, val2);
        planetRow[r1] = minValue;
        planetRow[r2] = minValue;
      }
    } else {
      // Rule 3: One rasi is occupied, one is empty
      if (r1Occupied) {
        // r2 is empty
        if (val2 < val1) {
          // Rule 3(a): Empty rasi has lower value, make it zero
          planetRow[r2] = 0;
        } else {
          // Rule 3(b): Empty rasi has higher value, replace with occupied's value
          planetRow[r2] = val1;
        }
      } else {
        // r1 is empty
        if (val1 < val2) {
          // Rule 3(a): Empty rasi has lower value, make it zero
          planetRow[r1] = 0;
        } else {
          // Rule 3(b): Empty rasi has higher value, replace with occupied's value
          planetRow[r1] = val2;
        }
      }
    }
  }

  return bav;
};

/**
 * Calculate Sodhya Pindas from reduced Ashtakavarga
 *
 * @param bavAfterEkadhipatya - BAV after both trikona and ekadhipatya sodhana
 * @param houseChart - Original house chart for planet positions
 * @returns Rasi Pindas, Graha Pindas, and Sodhya Pindas for each planet (0-6)
 */
const calculateSodhyaPindas = (
  bavAfterEkadhipatya: number[][],
  houseChart: HouseChart
): SodhyaPindasResult => {
  const bav = bavAfterEkadhipatya;
  const pToH = getPlanetToHouseFromChart(houseChart);

  const raasiPindas: number[] = Array(7).fill(0);
  const grahaPindas: number[] = Array(7).fill(0);
  const sodhyaPindas: number[] = Array(7).fill(0);

  // Get planet houses for Sun to Saturn (0-6)
  const planetHouses: number[] = [];
  for (let p = 0; p < 7; p++) {
    planetHouses.push(pToH[p] ?? 0);
  }

  // Calculate Rasi Pindas: sum of (BAV[p][r] * rasimana_multiplier[r])
  for (let p = 0; p < 7; p++) {
    let sum = 0;
    for (let r = 0; r < 12; r++) {
      sum += bav[p][r] * RASIMANA_MULTIPLIERS[r];
    }
    raasiPindas[p] = sum;
  }

  // Calculate Graha Pindas: sum of (grahamana_multiplier[i] * BAV[p][house of planet i])
  for (let p = 0; p < 7; p++) {
    let sum = 0;
    for (let i = 0; i < 7; i++) {
      const planetRasi = planetHouses[i];
      sum += GRAHAMANA_MULTIPLIERS[i] * bav[p][planetRasi];
    }
    grahaPindas[p] = sum;
  }

  // Sodhya Pindas = Rasi Pindas + Graha Pindas
  for (let p = 0; p < 7; p++) {
    sodhyaPindas[p] = raasiPindas[p] + grahaPindas[p];
  }

  return { raasiPindas, grahaPindas, sodhyaPindas };
};

/**
 * Calculate Sodhya Pindas from Binna Ashtakavarga
 *
 * Applies Trikona Sodhana, then Ekadhipatya Sodhana, then calculates Pindas.
 *
 * @param binnaAshtakavarga - 2D array [planet][rasi] from getAshtakavarga
 * @param houseChart - Original house chart
 * @returns Rasi Pindas, Graha Pindas, and Sodhya Pindas
 */
export const sodhayaPindas = (
  binnaAshtakavarga: number[][],
  houseChart: HouseChart
): SodhyaPindasResult => {
  // Step 1: Trikona Sodhana
  const bavAfterTrikona = trikonaSodhana(binnaAshtakavarga);

  // Step 2: Ekadhipatya Sodhana (results in Sodhita Ashtakavarga)
  const bavAfterEkadhipatya = ekadhipatyaSodhana(bavAfterTrikona, houseChart);

  // Step 3: Calculate Pindas
  return calculateSodhyaPindas(bavAfterEkadhipatya, houseChart);
};

/**
 * Get complete Ashtakavarga analysis including Sodhya Pindas
 *
 * @param houseChart - House chart with planets
 * @returns Complete Ashtakavarga analysis
 */
export const getCompleteAshtakavarga = (
  houseChart: HouseChart
): AshtakavargaResult & { sodhyaPindas: SodhyaPindasResult } => {
  const avResult = getAshtakavarga(houseChart);
  const pindas = sodhayaPindas(avResult.binnaAshtakavarga, houseChart);

  return {
    ...avResult,
    sodhyaPindas: pindas
  };
};

/**
 * Get Kaksha (sub-division) of a planet for transit predictions
 *
 * Each rasi is divided into 8 kakshas of 3°45' each.
 * Kaksha lords are: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, Lagna
 *
 * @param longitude - Longitude in the sign (0-30)
 * @returns Kaksha index (0-7) and lord
 */
export const getKaksha = (
  longitude: number
): { kakshaIndex: number; kakshaLord: number | string } => {
  // Each kaksha spans 30/8 = 3.75 degrees
  const kakshaSize = 30 / 8;
  const kakshaIndex = Math.floor(longitude / kakshaSize) % 8;

  // Kaksha lords in order: Saturn(6), Jupiter(4), Mars(2), Sun(0),
  // Venus(5), Mercury(3), Moon(1), Lagna('L')
  const kakshaLords: (number | string)[] = [6, 4, 2, 0, 5, 3, 1, ASCENDANT_SYMBOL];

  return {
    kakshaIndex,
    kakshaLord: kakshaLords[kakshaIndex]
  };
};
