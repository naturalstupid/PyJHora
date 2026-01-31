/**
 * House calculations and Planetary/Sign Aspects (Drishti)
 * Ported from PyJHora house.py
 */

import {
    ARGALA_HOUSES,
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
    PLANETS_EXCEPT_NODES,
    VIRODHARGALA_HOUSES
} from '../constants';

// ... (existing code) ...

// ============================================================================
// ARGALA
// ============================================================================

/**
 * Calculate Argala and Virodhargala (Obstruction) for each house
 * @param planetToHouse - Map of planet ID or 'L' to Rasi index (0-11)
 * @param ascendantRasi - Rasi index of the Ascendant (0-11)
 * @returns Object containing argala and virodhargala lists for each house (0-11)
 *          argala[h] = list of planets causing Argala on House h+1
 */
export const getArgala = (
    planetToHouse: Record<number | string, number>,
    ascendantRasi: number
): {
    argala: Record<number, number[]>;
    virodhargala: Record<number, number[]>;
} => {
    const argala: Record<number, number[]> = {};
    const virodhargala: Record<number, number[]> = {};

    // Invert map for quick lookup: Rasi -> [PlanetIDs]
    const rasiToPlanets: Record<number, number[]> = {};
    for (let r = 0; r < 12; r++) rasiToPlanets[r] = [];

    Object.entries(planetToHouse).forEach(([planetStr, rasi]) => {
        // Skip if 'L' (Ascendant symbol) is strictly used as key and parse fails
        if (planetStr === ASCENDANT_SYMBOL) return;

        const planet = parseInt(planetStr);
        if (!isNaN(planet)) {
            if (rasiToPlanets[rasi]) rasiToPlanets[rasi].push(planet);
        }
    });

    for (let h = 0; h < 12; h++) {
        // Current house's sign
        // h=0 is 1st House. Sign = (ascendantRasi + 0) % 12
        const currentSign = (ascendantRasi + h) % 12;

        argala[h] = [];
        virodhargala[h] = [];

        // Check primary Argala houses (2, 4, 11) from current sign
        // The planets in those signs cause Argala on 'currentSign' (which is House h+1)
        // Formula: Sign causing Argala = (currentSign + a - 1) % 12

        // Note: Ketu exception logic is conditional. Standard rules first.
        // If standard:
        ARGALA_HOUSES.forEach(a => {
            const argalaSign = (currentSign + a - 1) % 12;
            const planetsInSign = rasiToPlanets[argalaSign];
            if (planetsInSign && planetsInSign.length > 0) {
                argala[h].push(...planetsInSign);
            }
        });

        VIRODHARGALA_HOUSES.forEach(va => {
            const obsSign = (currentSign + va - 1) % 12;
            const planetsInSign = rasiToPlanets[obsSign];
            if (planetsInSign && planetsInSign.length > 0) {
                virodhargala[h].push(...planetsInSign);
            }
        });

        // TODO: Implement Ketu exceptions or secondary argala if required for completeness
    }

    return { argala, virodhargala };
};


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

// ============================================================================
// PLANETARY & RASI STRENGTH LOGIC (Used for Dasha Systems)
// ============================================================================

import {
    AQUARIUS,
    HOUSE_STRENGTHS_OF_PLANETS,
    JUPITER,
    KETU,
    MARS,
    MERCURY,
    RAHU,
    SATURN,
    SCORPIO,
    STRENGTH_EXALTED,
    STRENGTH_FRIEND
} from '../constants';

/**
 * Helper to convert planet positions array to a dictionary
 * @param planetPositions
 */
export const getPlanetToHouseDict = (
    planetPositions: Array<{ planet: number; rasi: number; longitude: number }>
): Record<number, number> => {
    const dict: Record<number, number> = {};
    planetPositions.forEach(p => {
        dict[p.planet] = p.rasi;
    });
    return dict;
};

/**
 * Helper to convert planet positions to House -> Planets list
 * @param planetPositions 
 */
export const getHouseToPlanetList = (
    planetPositions: Array<{ planet: number; rasi: number; longitude: number }>
): Record<number, number[]> => {
    const list: Record<number, number[]> = {};
    for (let i = 0; i < 12; i++) list[i] = [];
    planetPositions.forEach(p => {
        if (list[p.rasi]) list[p.rasi].push(p.planet);
    });
    return list;
}

/**
 * Get the owner (lord) of a house, considering exceptions for Scorpio and Aquarius.
 * @param planetPositions 
 * @param sign 
 * @param checkDuringDhasa 
 */
export const getHouseOwnerFromPlanetPositions = (
    planetPositions: Array<{ planet: number; rasi: number; longitude: number }>,
    sign: number,
    checkDuringDhasa: boolean = false
): number => {
    let lord = SIGN_LORDS[sign % 12] ?? 0;

    // Exception for Scorpio (Mars vs Ketu)
    if ((sign % 12) === SCORPIO) {
        lord = getStrongerPlanetFromPositions(planetPositions, MARS, KETU, checkDuringDhasa);
    }
    // Exception for Aquarius (Saturn vs Rahu)
    else if ((sign % 12) === AQUARIUS) {
        lord = getStrongerPlanetFromPositions(planetPositions, SATURN, RAHU, checkDuringDhasa);
    }

    return lord;
};

/**
 * Find the stronger of two planets (usually for Co-lords)
 * @param planetPositions 
 * @param p1 
 * @param p2 
 * @param checkDuringDhasa 
 */
export const getStrongerPlanetFromPositions = (
    planetPositions: Array<{ planet: number; rasi: number; longitude: number }>,
    p1: number,
    p2: number,
    checkDuringDhasa: boolean = false // Keeping parameter for future matching with python signature
): number => {
    if (p1 === p2) return p1;

    // TODO: Handle Ascendant comparisons if needed (usually handled before calling this)

    // Rule 1: Planet joined by more planets is stronger
    const pToH = getPlanetToHouseDict(planetPositions);
    const h1 = pToH[p1];
    const h2 = pToH[p2];

    if (h1 === undefined || h2 === undefined) return p1; // Should not happen with valid data

    // Count planets in same house (excluding self)
    const count1 = planetPositions.filter(p => p.rasi === h1 && p.planet !== p1).length;
    const count2 = planetPositions.filter(p => p.rasi === h2 && p.planet !== p2).length;

    if (count1 > count2) return p1;
    if (count2 > count1) return p2;

    // Rule 2: Conjoin/Aspect by Jupiter, Mercury, or Dispositor
    const { arp } = getRaasiDrishtiFromChart(pToH);

    // Helper to get count of specific associations for a planet/house
    const getAssociationScore = (planet: number, house: number): number => {
        let score = 0;
        const dispositor = SIGN_LORDS[house] ?? 0;
        const benefics = [JUPITER, MERCURY, dispositor];

        // 1. Conjoined (in same house)
        const planetsInHouse = planetPositions.filter(p => p.rasi === house).map(p => p.planet);
        benefics.forEach(b => {
            if (planetsInHouse.includes(b) && b !== planet) score++;
        });

        // 2. Aspecting the Rasi (Raasi Drishti)
        // Find which planets refer to Rasis that aspect 'house'
        const aspectingPlanets: number[] = [];
        Object.entries(arp).forEach(([pStr, aspectedRasis]) => {
            if (aspectedRasis && aspectedRasis.includes(house)) {
                aspectingPlanets.push(parseInt(pStr));
            }
        });

        benefics.forEach(b => {
            if (aspectingPlanets.includes(b)) score++;
        });

        return score;
    };

    const score1 = getAssociationScore(p1, h1);
    const score2 = getAssociationScore(p2, h2);

    if (score1 > score2) return p1;
    if (score2 > score1) return p2;

    // Rule 3: Exalted planet is stronger
    const strength1 = HOUSE_STRENGTHS_OF_PLANETS[p1]?.[h1] ?? 0;
    const strength2 = HOUSE_STRENGTHS_OF_PLANETS[p2]?.[h2] ?? 0;

    if (strength1 === STRENGTH_EXALTED && strength1 > strength2) return p1;
    if (strength2 === STRENGTH_EXALTED && strength2 > strength1) return p2;

    // Rule 4: Natural strength of Rasi
    // Dual > Fixed > Movable
    const getRasiTypeStrength = (r: number): number => {
        if (DUAL_SIGNS.includes(r)) return 3;
        if (FIXED_SIGNS.includes(r)) return 2;
        if (MOVABLE_SIGNS.includes(r)) return 1;
        return 0;
    };

    const rType1 = getRasiTypeStrength(h1);
    const rType2 = getRasiTypeStrength(h2);

    if (rType1 > rType2) return p1;
    if (rType2 > rType1) return p2;

    // Rule 5: Longitude advancement
    const long1 = planetPositions.find(p => p.planet === p1)?.longitude || 0;
    const long2 = planetPositions.find(p => p.planet === p2)?.longitude || 0;

    const deg1 = long1 % 30;
    const deg2 = long2 % 30;

    if (deg1 >= deg2) return p1;
    return p2;
};

/**
 * Find the stronger of two Rasis
 * @param planetPositions 
 * @param r1 
 * @param r2 
 */
export const getStrongerRasi = (
    planetPositions: Array<{ planet: number; rasi: number; longitude: number }>,
    r1: number,
    r2: number
): number => {
    // Logic similar to Stronger Planet but for Rasis directly
    const pToH = getPlanetToHouseDict(planetPositions);

    // Rule 1: Planet count
    const count1All = planetPositions.filter(p => p.rasi === r1).length;
    const count2All = planetPositions.filter(p => p.rasi === r2).length;

    if (count1All > count2All) return r1;
    if (count2All > count1All) return r2;

    // Rule 2: Aspects/Associations (Mercury, Jupiter, Lord)
    // ... Implement simplified version for now reusing structure ...
    // We reuse simplified logic or assume equal if we can't easily calc.
    // Ideally we should replicate Rule 2 fully.

    // Rule 4: Oddity difference

    const lord1 = SIGN_LORDS[r1] ?? 0;
    const lord2 = SIGN_LORDS[r2] ?? 0;
    const lord1Pos = pToH[lord1];
    const lord2Pos = pToH[lord2];

    if (lord1Pos === undefined || lord2Pos === undefined) return r1; // Fallback

    const isDifferentOddity = (rasi: number, lordLoc: number) => {
        return (ODD_SIGNS.includes(rasi) && EVEN_SIGNS.includes(lordLoc)) ||
            (EVEN_SIGNS.includes(rasi) && ODD_SIGNS.includes(lordLoc));
    };

    const diff1 = isDifferentOddity(r1, lord1Pos);
    const diff2 = isDifferentOddity(r2, lord2Pos);

    if (diff1 && !diff2) return r1;
    if (diff2 && !diff1) return r2;

    // Rule 5: Natural Strength (Dual > Fixed > Movable)
    const getRasiTypeStrength = (r: number): number => {
        if (DUAL_SIGNS.includes(r)) return 3;
        if (FIXED_SIGNS.includes(r)) return 2;
        if (MOVABLE_SIGNS.includes(r)) return 1;
        return 0;
    };

    const rt1 = getRasiTypeStrength(r1);
    const rt2 = getRasiTypeStrength(r2);

    if (rt1 > rt2) return r1;
    if (rt2 > rt1) return r2;

    // Fallback: Longitude of Lord
    const lord1Long = planetPositions.find(p => p.planet === lord1)?.longitude || 0;
    const lord2Long = planetPositions.find(p => p.planet === lord2)?.longitude || 0;

    if ((lord1Long % 30) >= (lord2Long % 30)) return r1;
    return r2;
};

// ============================================================================
// BRAHMA CALCULATION
// ============================================================================

/**
 * Calculate Brahma planet for Jaimini dashas
 * Brahma is determined by finding the stronger of Lagna and 7th house,
 * then taking lords of 6th, 8th, and 12th houses from that sign,
 * and finding the strongest among them (excluding Rahu/Ketu).
 *
 * @param planetPositions - Array of planet positions
 * @returns Planet ID of Brahma
 */
export const getBrahma = (
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>
): number => {
  const pToH = getPlanetToHouseDict(planetPositions);

  // Get Lagna house (from first position - assumed to be Ascendant/Lagna)
  const ascHouse = planetPositions[0]?.rasi ?? 0;
  const seventhHouse = (ascHouse + 6) % 12;

  // Find stronger of Lagna and 7th house
  const strongerHouse = getStrongerRasi(planetPositions, ascHouse, seventhHouse);

  // Get lords of 6th, 8th, and 12th houses from stronger house
  // (sp + h - 1) % 12 where h = 6, 8, 12 -> indices are (sp + 5), (sp + 7), (sp + 11) % 12
  const house6th = (strongerHouse + 5) % 12;
  const house8th = (strongerHouse + 7) % 12;
  const house12th = (strongerHouse + 11) % 12;

  let lords = [
    getHouseOwnerFromPlanetPositions(planetPositions, house6th),
    getHouseOwnerFromPlanetPositions(planetPositions, house8th),
    getHouseOwnerFromPlanetPositions(planetPositions, house12th)
  ];

  // Remove Rahu (7) and Ketu (8) from lords
  lords = lords.filter(l => l !== 7 && l !== 8);

  if (lords.length === 0) {
    // Fallback: return Sun if no valid lords
    return 0;
  }

  // Score each lord
  const lordsScores: Map<number, number> = new Map();
  for (const lord of lords) {
    let score = 0;
    const lordHouse = pToH[lord];

    if (lordHouse === undefined) continue;

    // Rule 1: If planet is in friend/own/exalted house
    const strength = HOUSE_STRENGTHS_OF_PLANETS[lord]?.[lordHouse] ?? 0;
    if (strength >= STRENGTH_FRIEND) {
      score += 1;
    }

    // Rule 2: If planet is in odd sign
    if (ODD_SIGNS.includes(lordHouse)) {
      score += 1;
    }

    // Rule 3: If planet is in first 6 houses from stronger house
    const first6Houses = Array.from({ length: 6 }, (_, j) => (strongerHouse + j) % 12);
    if (first6Houses.includes(lordHouse)) {
      score += 1;
    }

    lordsScores.set(lord, score);
  }

  // Sort by score descending and take top 2
  const sortedLords = Array.from(lordsScores.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 2)
    .map(entry => entry[0]);

  if (sortedLords.length === 0) {
    return lords[0] ?? 0;
  } else if (sortedLords.length === 1) {
    return sortedLords[0];
  } else {
    // Find stronger of top 2
    return getStrongerPlanetFromPositions(planetPositions, sortedLords[0], sortedLords[1]);
  }
};
