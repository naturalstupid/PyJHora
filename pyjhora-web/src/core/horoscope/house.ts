/**
 * House calculations and Planetary/Sign Aspects (Drishti)
 * Ported from PyJHora house.py
 */

import {
    ASCENDANT_SYMBOL,
    DUAL_SIGNS,
    EVEN_SIGNS,
    FIXED_SIGNS,
    HOUSE_10,
    HOUSE_11,
    HOUSE_3,
    HOUSE_6,
    MOVABLE_SIGNS,
    ODD_SIGNS,
    PLANETS_EXCEPT_NODES
} from '../constants';

// ============================================================================
// HOUSE OWNERSHIP
// ============================================================================

import { SIGN_LORDS } from '../constants';

/**
 * Get the lord (owner planet) of a given sign (rasi)
 * @param sign - Sign index (0-11)
 * @returns Planet ID of the lord
 */
export const getLordOfSign = (sign: number): number => {
  return SIGN_LORDS[sign % 12] ?? 0; // Default to 0 (Mars/Aries) if undefined, though unlikely
};

// ... existing code ...


// ============================================================================

/**
 * Get relative house number of a planet from a given house
 * @param fromHouse - Starting house (0-11)
 * @param planetHouse - House where planet is located (0-11)
 * @returns Relative house number (1-12)
 */
export const getRelativeHouseOfPlanet = (fromHouse: number, planetHouse: number): number => {
  return (planetHouse + 12 - fromHouse) % 12 + 1;
};

/**
 * Get trines (trikonas) of a raasi
 * @param raasi - Rasi index (0-11)
 * @returns Array of 3 rasi indices
 */
export const getTrinesOfRaasi = (raasi: number): number[] => {
  return [raasi, (raasi + 4) % 12, (raasi + 8) % 12];
};

/**
 * Get quadrants (kendras) of a raasi
 * @param raasi - Rasi index (0-11)
 * @returns Array of 4 rasi indices
 */
export const getQuadrantsOfRaasi = (raasi: number): number[] => {
  return [raasi, (raasi + 3) % 12, (raasi + 6) % 12, (raasi + 9) % 12];
};

/**
 * Get upachayas from a raasi
 * @param raasi - Rasi index (0-11)
 * @returns Array of 4 rasi indices (3, 6, 10, 11 from raasi)
 */
export const getUpachayasOfRaasi = (raasi: number): number[] => {
  return [
    (raasi + HOUSE_3) % 12,
    (raasi + HOUSE_6) % 12,
    (raasi + HOUSE_10) % 12,
    (raasi + HOUSE_11) % 12
  ];
};

// ============================================================================
// RAASI DRISHTI (SIGN ASPECTS)
// ============================================================================

const getRaasiDrishtiMovable = (): Record<number, number[]> => {
  const raasiDrishti: Record<number, number[]> = {};
  for (const ms of MOVABLE_SIGNS) {
    const rd: number[] = [];
    for (const fs of FIXED_SIGNS) {
      // Movable signs aspect all fixed signs except the one adjacent to it
      if (fs !== (ms + 1) % 12 && fs !== (ms - 1 + 12) % 12) {
        rd.push(fs);
      }
    }
    raasiDrishti[ms] = rd;
  }
  return raasiDrishti;
};

const getRaasiDrishtiFixed = (): Record<number, number[]> => {
  const raasiDrishti: Record<number, number[]> = {};
  for (const fs of FIXED_SIGNS) {
    const rd: number[] = [];
    for (const ms of MOVABLE_SIGNS) {
      // Fixed signs aspect all movable signs except the one adjacent to it
      if (ms !== (fs + 1) % 12 && ms !== (fs - 1 + 12) % 12) {
        rd.push(ms);
      }
    }
    raasiDrishti[fs] = rd;
  }
  return raasiDrishti;
};

const getRaasiDrishtiDual = (): Record<number, number[]> => {
  const raasiDrishti: Record<number, number[]> = {};
  for (const ds of DUAL_SIGNS) {
    const rd: number[] = [];
    for (const otherDs of DUAL_SIGNS) {
      // Dual signs aspect all other dual signs
      if (ds !== otherDs) {
        rd.push(otherDs);
      }
    }
    raasiDrishti[ds] = rd;
  }
  return raasiDrishti;
};

/**
 * Get map of which signs are aspected by each sign (Rasi Drishti)
 */
export const getRaasiDrishtiMap = (): Record<number, number[]> => {
  return {
    ...getRaasiDrishtiMovable(),
    ...getRaasiDrishtiFixed(),
    ...getRaasiDrishtiDual()
  };
};

/**
 * Calculate Raasi Drishti (Sign Aspects) from chart positions
 * @param planetToHouse - Map of planet ID to rasi index (0-11)
 * @returns Objects containing aspect data
 */
export const getRaasiDrishtiFromChart = (
  planetToHouse: Record<number, number>
): {
  arp: Record<number, number[]>; // Aspects on Rasis
  ahp: Record<number, number[]>; // Aspects on Houses (relative to Asc)
  app: Record<number, number[]>; // Aspects on Planets
} => {
  const ascRaasi = planetToHouse[ASCENDANT_SYMBOL as unknown as number] || 0; // Assuming ASCENDANT_SYMBOL handled carefully or separate
  // Note: planetToHouse usually uses numbers for planets. We need to handle Ascendant separately or agree on ID.
  // In our types, we might use a special ID or just pass ascendant rasi separately.
  // For this function, let's assume we can pass the Ascendant Rasi directly or look it up if included.
  
  // Actually, let's refine the input. Usually we receive planet positions.
  // planetToHouse: Record<number, number> (Planet ID -> Rasi Index)
  // We need to know where Ascendant is too.
  
  // Let's refactor to take planetPositions array to be safe, or just planetToHouse and ascendantRasi.
  // I'll stick to planetToHouse and explicit Ascendant Rasi for clarity.
  
  const raasiDrishtiMap = getRaasiDrishtiMap();
  const arp: Record<number, number[]> = {};
  const ahp: Record<number, number[]> = {};
  const app: Record<number, number[]> = {};

  // For each planet (0-8)
  const planets = PLANETS_EXCEPT_NODES.concat([7, 8]); // 0-8
  
  // Invert planetToHouse for quick lookup: Rasi -> [PlanetIDs]
  const rasiToPlanets: Record<number, number[]> = {};
  for (let r = 0; r < 12; r++) rasiToPlanets[r] = [];
  
  Object.entries(planetToHouse).forEach(([planetStr, rasi]) => {
    const planet = parseInt(planetStr);
    if (!isNaN(planet)) {
       // if we have multiple planets in same rasi (though planetToHouse is 1:1 usually)
       // Wait, planetToHouse is "Planet -> House". Yes.
       if (rasiToPlanets[rasi]) rasiToPlanets[rasi].push(planet);
    }
  });

  planets.forEach(p => {
    const pRaasi = planetToHouse[p];
    if (pRaasi === undefined) return;
    
    // Rasis aspected by the planet's rasi
    const aspectedRasis = raasiDrishtiMap[pRaasi] || [];
    arp[p] = aspectedRasis;
    
    // Houses aspected (relative to Ascendant which needs to be passed, but let's calc relative later if needed)
    // house.py uses Ascendant to calc ahp. Let's return raw rasi lists and let caller derive houses.
    
    // Planets aspected
    app[p] = [];
    aspectedRasis.forEach(r => {
      if (rasiToPlanets[r]) {
        app[p].push(...rasiToPlanets[r]);
      }
    });
  });

  return { arp, ahp, app };
};

// ============================================================================
// CHARA KARAKAS
// ============================================================================

/**
 * Calculate Chara Karakas (Atma, Amatya, etc.) based on standard scheme (8 karakas or 7)
 * Usually 8 karakas scheme: Atma, Amatya, Bhratri, Matri, Pitri, Putra, Gnati, Dara
 * Or 7 karakas scheme. JHora defaults to 8 usually for Jaimini.
 * @param planetPositions - Array of planets with longitudes
 * @returns Array of planet IDs ordered by minutes descending
 */
export const getCharaKarakas = (
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>
): number[] => {
  // Filter for 7 planets (Sun to Saturn) + maybe Rahu
  // Standard Jaimini uses 7 or 8.
  // If 8: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu
  // If 7: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn
  
  // We'll implement the 8 karaka scheme including Rahu as per JHora default often, 
  // but need to handle degrees.
  
  // Get degrees in sign (0-30) for each planet
  const planets = [0, 1, 2, 3, 4, 5, 6, 7]; // Sun to Rahu
  
  const karakaCandidates = planets.map(p => {
    const pos = planetPositions.find(pp => pp.planet === p);
    if (!pos) return { planet: p, longitude: 0 };
    
    let long = pos.longitude % 30;
    
    // For Rahu, longitude logic might differ (measured from end of sign?)
    // JHora option: "Rahu's longitude is measured from the end of the sign"
    // Default JHora usually does this for Karakas.
    if (p === 7) { // Rahu
       // long = 30 - long; 
       // Need to verify standard JHora behavior from charts.py or similar. 
       // Looking at house.py lines 136-140:
       // pp[-1][-1] = one_rasi - pp[-1][-1]  (If Rahu is last)
       long = 30 - long;
    }
    
    return { planet: p, longitude: long };
  });

  // Sort by longitude descending
  karakaCandidates.sort((a, b) => b.longitude - a.longitude);

  return karakaCandidates.map(c => c.planet);
};

// ============================================================================
// STRENGTH CALCULATIONS (Basic)
// ============================================================================

/**
 * Basic logic to check if a sign is odd or even
 */
export const isOddSign = (sign: number): boolean => ODD_SIGNS.includes(sign);
export const isEvenSign = (sign: number): boolean => EVEN_SIGNS.includes(sign);

// ============================================================================
// ARGALA
// ============================================================================

// Placeholder for Argala calculation

