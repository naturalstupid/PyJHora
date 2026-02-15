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
    HOUSE_4,
    HOUSE_6,
    HOUSE_7,
    HOUSE_8,
    HOUSE_10,
    HOUSE_11,
    HOUSE_12,
    HOUSE_3,
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
    COMPOUND_ADHIMITRA,
    COMPOUND_ADHISATRU,
    COMPOUND_MITRA,
    COMPOUND_NEUTRAL,
    COMPOUND_SATRU,
    GRAHA_DRISHTI,
    HOUSE_OWNERS,
    HOUSE_STRENGTHS_OF_PLANETS,
    HOUSES_OF_RAHU_KETU,
    JUPITER,
    KETU,
    LONGEVITY,
    LONGEVITY_YEARS,
    MARS,
    MERCURY,
    MOON,
    RAHU,
    RUDRA_EIGHTH_HOUSE,
    SATURN,
    SCORPIO,
    SIGN_LORDS,
    STRENGTH_EXALTED,
    STRENGTH_FRIEND,
    SUN,
    TEMPORARY_ENEMY_RAASI_POSITIONS,
    TEMPORARY_FRIEND_RAASI_POSITIONS,
    VENUS
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

// ============================================================================
// GRAHA DRISHTI FROM CHART (HouseChart format)
// ============================================================================

/**
 * Extended graha drishti map including Rahu and Ketu.
 * The GRAHA_DRISHTI constant only covers Sun-Saturn (0-6).
 * Rahu(7) and Ketu(8) also have 7th house aspect (offset 6 in 0-based).
 * Python: graha_drishti = {0:[7], 1:[7], ..., 7:[7], 8:[7]}
 */
const getFullGrahaDrishti = (planet: number): number[] => {
  if (planet <= 6) {
    return GRAHA_DRISHTI[planet] ?? [];
  }
  // Rahu and Ketu both have 7th-house aspect (0-based offset = 6)
  if (planet === 7 || planet === 8) {
    return [6];
  }
  return [];
};

/**
 * Get graha drishti aspects from a HouseChart (string array format).
 * Mirrors Python's graha_drishti_from_chart.
 *
 * @param chart - HouseChart string array (12 elements), e.g.
 *   ['', '', '', '', '2', '7', '1/5', '0', '3/4', 'L', '', '6/8']
 * @returns { arp, ahp, app } where:
 *   arp[p] = rasis aspected by planet p via graha drishti
 *   ahp[p] = houses aspected (relative to ascendant)
 *   app[p] = planets aspected by planet p via graha drishti
 */
export const getGrahaDrishtiFromChart = (
  chart: string[]
): {
  arp: Record<number, number[]>;
  ahp: Record<number, number[]>;
  app: Record<number, number[]>;
} => {
  // Parse chart to planet-to-house dictionary
  const pToH: Record<number | string, number> = {};
  for (let h = 0; h < 12; h++) {
    if (!chart[h] || chart[h] === '') continue;
    const parts = chart[h].split('/');
    for (const part of parts) {
      const trimmed = part.trim();
      if (trimmed === 'L') {
        pToH['L'] = h;
      } else if (trimmed !== '') {
        const planet = parseInt(trimmed, 10);
        if (!isNaN(planet)) {
          pToH[planet] = h;
        }
      }
    }
  }

  const ascHouse = pToH['L'] ?? 0;
  const arp: Record<number, number[]> = {};
  const ahp: Record<number, number[]> = {};
  const app: Record<number, number[]> = {};

  // For each planet Sun(0) to Ketu(8)
  for (let p = 0; p < 9; p++) {
    const houseOfPlanet = pToH[p];
    if (houseOfPlanet === undefined) {
      arp[p] = [];
      ahp[p] = [];
      app[p] = [];
      continue;
    }

    // Python: arp[p] = [(h + house_of_planet - 1) % 12 for h in const.graha_drishti[p]]
    // Python graha_drishti uses 1-based offsets; TS GRAHA_DRISHTI uses 0-based
    const drishtiOffsets = getFullGrahaDrishti(p);
    arp[p] = drishtiOffsets.map(offset => (offset + houseOfPlanet) % 12);
    ahp[p] = arp[p].map(h => (h - ascHouse + 12) % 12 + 1);

    // Find planets in the aspected rasis
    const planetsAspected: number[] = [];
    for (const ar of arp[p]) {
      if (chart[ar] && chart[ar] !== '') {
        const cleanedEntry = chart[ar].replace('L', '');
        const parts = cleanedEntry.split('/');
        for (const part of parts) {
          const trimmed = part.trim();
          if (trimmed !== '') {
            const pp = parseInt(trimmed, 10);
            if (!isNaN(pp)) {
              planetsAspected.push(pp);
            }
          }
        }
      }
    }
    app[p] = planetsAspected;
  }

  return { arp, ahp, app };
};

// ============================================================================
// COMBINED DRISHTI (Graha + Raasi) OF A PLANET
// ============================================================================

/**
 * Get all planets aspected by a given planet via BOTH graha drishti AND raasi drishti combined.
 * Mirrors Python's graha_drishti_of_the_planet which combines graha + raasi drishti.
 *
 * @param chart - HouseChart string array
 * @param planet - Planet index (0-8)
 * @returns List of planet indices aspected (via either graha or raasi drishti)
 */
const getCombinedDrishtiOfPlanet = (
  chart: string[],
  planet: number
): number[] => {
  // Parse chart
  const pToH: Record<number | string, number> = {};
  for (let h = 0; h < 12; h++) {
    if (!chart[h] || chart[h] === '') continue;
    const parts = chart[h].split('/');
    for (const part of parts) {
      const trimmed = part.trim();
      if (trimmed === 'L') {
        pToH['L'] = h;
      } else if (trimmed !== '') {
        const p = parseInt(trimmed, 10);
        if (!isNaN(p)) pToH[p] = h;
      }
    }
  }

  // Get graha drishti planets
  const { app: grahaDrishtiPlanets } = getGrahaDrishtiFromChart(chart);

  // Get raasi drishti planets
  // Build planetToHouse map for getRaasiDrishtiFromChart
  const planetToHouseMap: Record<number, number> = {};
  for (let p = 0; p < 9; p++) {
    if (pToH[p] !== undefined) planetToHouseMap[p] = pToH[p];
  }
  const { app: raasiDrishtiPlanets, arp: raasiDrishtiRasis } = getRaasiDrishtiFromChart(planetToHouseMap);

  // Combine: graha drishti + raasi drishti planets
  let combined = [
    ...(grahaDrishtiPlanets[planet] ?? []),
    ...(raasiDrishtiPlanets[planet] ?? [])
  ];

  // Additionally, from Python logic: iterate over raasi drishti rasis and find planets there
  const hp = pToH[planet];
  const raasiAspects = raasiDrishtiRasis[planet] ?? [];
  for (const h of raasiAspects) {
    const targetRasi = (h + hp - 1 + 12) % 12;
    if (chart[targetRasi] && chart[targetRasi] !== '') {
      const parts = chart[targetRasi].split('/');
      for (const part of parts) {
        const trimmed = part.trim();
        if (trimmed !== '' && trimmed !== 'L') {
          const p1 = parseInt(trimmed, 10);
          if (!isNaN(p1)) combined.push(p1);
        }
      }
    }
  }

  // Deduplicate
  return [...new Set(combined)];
};

// ============================================================================
// ASSOCIATIONS OF THE PLANET
// ============================================================================

/**
 * Returns list of planets associated with the given planet.
 * Association means:
 *   (1) Conjunction (same rasi)
 *   (2) Mutual graha drishti (both planets aspect each other via combined drishti)
 *   (3) Parivartana (exchange of sign lordship)
 *
 * Mirrors Python's associations_of_the_planet.
 *
 * @param planetPositions - Array of planet positions (first element is Ascendant with planet=-1)
 * @param planet - Planet index (0-8)
 * @returns Array of associated planet indices
 */
export const getAssociationsOfThePlanet = (
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>,
  planet: number
): number[] => {
  // Build house-to-planet chart string (like Python's h_to_p)
  const chart = buildHouseChart(planetPositions);

  // Build planet-to-house dictionary
  const pToH: Record<number, number> = {};
  for (const p of planetPositions) {
    if (p.planet >= 0) pToH[p.planet] = p.rasi;
  }

  const ap: number[] = [];

  // (1) Conjunction: planets in the same rasi
  for (let p = 0; p < 9; p++) {
    if (p !== planet && pToH[p] === pToH[planet]) {
      ap.push(p);
    }
  }

  // (2) Mutual graha drishti: both planets must have combined drishti on each other
  const planetDrishti = getCombinedDrishtiOfPlanet(chart, planet);
  for (const gp of planetDrishti) {
    if (gp === planet) continue;
    const gpDrishti = getCombinedDrishtiOfPlanet(chart, gp);
    if (gpDrishti.includes(planet)) {
      ap.push(gp);
    }
  }
  // Remove self if present
  const selfIdx = ap.indexOf(planet);
  if (selfIdx >= 0) ap.splice(selfIdx, 1);

  // (3) Parivartana (exchange): planet A is in the house owned by planet B and vice versa
  for (let p = 0; p < 9; p++) {
    if (p === planet) continue;
    const ownerOfPlanetHouse = getHouseOwnerFromPlanetPositions(planetPositions, pToH[planet]);
    const ownerOfPHouse = getHouseOwnerFromPlanetPositions(planetPositions, pToH[p]);
    if (ownerOfPHouse === planet && ownerOfPlanetHouse === p) {
      ap.push(p);
    }
  }

  // Deduplicate
  return [...new Set(ap)];
};

/**
 * Build a HouseChart (string[12]) from planet positions.
 * Mirrors Python's get_house_planet_list_from_planet_positions.
 */
export const buildHouseChart = (
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>
): string[] => {
  const chart: string[] = Array(12).fill('');
  for (const p of planetPositions) {
    const label = p.planet === -1 ? 'L' : String(p.planet);
    const h = p.rasi;
    if (chart[h] === '') {
      chart[h] = label;
    } else {
      chart[h] += '/' + label;
    }
  }
  return chart;
};

// ============================================================================
// NATURAL PLANETARY RELATIONSHIPS
// ============================================================================

/**
 * Natural friends of each planet (Sun=0 to Ketu=8).
 * From Python const.friendly_planets derived from planet_relations matrix.
 * Python result: [[1,2,4],[0,3],[0,1,4],[0,5],[0,1,2],[3,6,7],[3,5,7],[5,6],[0,2]]
 */
export const naturalFriendsOfPlanets = (): number[][] => {
  return [
    [1, 2, 4],        // Sun: Moon, Mars, Jupiter
    [0, 3],            // Moon: Sun, Mercury
    [0, 1, 4],         // Mars: Sun, Moon, Jupiter
    [0, 5],            // Mercury: Sun, Venus
    [0, 1, 2],         // Jupiter: Sun, Moon, Mars
    [3, 6, 7],         // Venus: Mercury, Saturn, Rahu
    [3, 5, 7],         // Saturn: Mercury, Venus, Rahu
    [5, 6],            // Rahu: Venus, Saturn
    [0, 2],            // Ketu: Sun, Mars
  ];
};

/**
 * Natural enemies of each planet (Sun=0 to Ketu=8).
 * From Python const.enemy_planets derived from planet_relations matrix.
 * Python result: [[5,6,7],[],[3],[1,8],[3,5,7],[0,1],[0,1,2,8],[0,1,2],[5,6]]
 */
export const naturalEnemiesOfPlanets = (): number[][] => {
  return [
    [5, 6, 7],         // Sun: Venus, Saturn, Rahu
    [],                 // Moon: none
    [3],               // Mars: Mercury
    [1, 8],            // Mercury: Moon, Ketu
    [3, 5, 7],         // Jupiter: Mercury, Venus, Rahu
    [0, 1],            // Venus: Sun, Moon
    [0, 1, 2, 8],      // Saturn: Sun, Moon, Mars, Ketu
    [0, 1, 2],         // Rahu: Sun, Moon, Mars
    [5, 6],            // Ketu: Venus, Saturn
  ];
};

/**
 * Natural neutrals of each planet (Sun=0 to Ketu=8).
 * From Python const.neutral_planets derived from planet_relations matrix.
 * Python result: [[3,8],[2,4,5,6,7,8],[5,6,7,8],[2,4,6,7],[6,8],[2,4,8],[4],[3,4,8],[1,3,4,7]]
 */
export const naturalNeutralOfPlanets = (): number[][] => {
  return [
    [3, 8],            // Sun: Mercury, Ketu
    [2, 4, 5, 6, 7, 8], // Moon: Mars, Jupiter, Venus, Saturn, Rahu, Ketu
    [5, 6, 7, 8],      // Mars: Venus, Saturn, Rahu, Ketu
    [2, 4, 6, 7],      // Mercury: Mars, Jupiter, Saturn, Rahu
    [6, 8],            // Jupiter: Saturn, Ketu
    [2, 4, 8],         // Venus: Mars, Jupiter, Ketu
    [4],               // Saturn: Jupiter
    [3, 4, 8],         // Rahu: Mercury, Jupiter, Ketu
    [1, 3, 4, 7],      // Ketu: Moon, Mercury, Jupiter, Rahu
  ];
};

// ============================================================================
// BAADHAKAS OF RAASI
// ============================================================================

/**
 * Baadhakas constant table.
 * Python: baadhakas = [[10,[6,7]],[9,[6]],[8,[4]],...]
 * Each entry: [baadhaka_sthana_rasi, [baadhaka_planet_ids]]
 */
const BAADHAKAS: [number, number[]][] = [
  [10, [6, 7]],   // Aries -> Aquarius, planets: Saturn, Rahu
  [9, [6]],       // Taurus -> Capricorn, planets: Saturn
  [8, [4]],       // Gemini -> Sagittarius, planets: Jupiter
  [1, [5]],       // Cancer -> Taurus, planets: Venus
  [0, [2]],       // Leo -> Aries, planets: Mars
  [11, [4]],      // Virgo -> Pisces, planets: Jupiter
  [4, [0]],       // Libra -> Leo, planets: Sun
  [3, [1]],       // Scorpio -> Cancer, planets: Moon
  [2, [3]],       // Sagittarius -> Gemini, planets: Mercury
  [7, [2, 8]],    // Capricorn -> Scorpio, planets: Mars, Ketu
  [6, [5]],       // Aquarius -> Libra, planets: Venus
  [5, [3]],       // Pisces -> Virgo, planets: Mercury
];

/**
 * Get baadhaka sthana and baadhaka planets for a given raasi.
 * Mirrors Python's baadhakas_of_raasi.
 *
 * @param raasi - Rasi index (0-11)
 * @returns [baadhaka_house_rasi, baadhaka_planet_ids]
 */
export const getBadhakasOfRaasi = (raasi: number): [number, number[]] => {
  return BAADHAKAS[raasi % 12];
};

// ============================================================================
// MARAKAS FROM PLANET POSITIONS
// ============================================================================

/**
 * Get maraka planets from planet positions.
 * Maraka planets are lords of 2nd and 7th houses from Lagna,
 * plus planets occupying those houses or conjunct with those lords.
 *
 * Mirrors Python's marakas_from_planet_positions.
 *
 * @param planetPositions - Array of planet positions (first element is Ascendant with planet=-1)
 * @returns Array of maraka planet indices
 */
export const getMarakasFromPlanetPositions = (
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>
): number[] => {
  // Build planet-to-house dict
  const pToH: Record<number | string, number> = {};
  for (const p of planetPositions) {
    if (p.planet === -1) {
      pToH['L'] = p.rasi;
    } else {
      pToH[p.planet] = p.rasi;
    }
  }

  const lagnaHouse = pToH['L'] ?? 0;

  // Maraka sthanas: 2nd and 7th houses from Lagna
  // Python: maraka_sthanas = [(h + p_to_h['L'] - 1) % 12 for h in [2, 7]]
  const marakaSthanas = [
    (2 + lagnaHouse - 1 + 12) % 12,  // 2nd house sign
    (7 + lagnaHouse - 1 + 12) % 12,  // 7th house sign
  ];

  // Lords of 2nd and 7th houses
  const marakaPlanets: number[] = marakaSthanas.map(sign =>
    getHouseOwnerFromPlanetPositions(planetPositions, sign)
  );

  // Planets in maraka sthanas or conjunct with maraka lords
  const marakaLordHouses = marakaPlanets.map(mp => pToH[mp]);
  const mpls: number[] = [];
  for (let mp = 0; mp < 9; mp++) {
    const mpHouse = pToH[mp];
    if (mpHouse === undefined) continue;
    if (marakaSthanas.includes(mpHouse) || marakaLordHouses.includes(mpHouse)) {
      mpls.push(mp);
    }
  }

  if (mpls.length > 0) {
    marakaPlanets.push(...mpls);
  }

  // Deduplicate
  return [...new Set(marakaPlanets)];
};

// ============================================================================
// ORDER OF PLANETS BY STRENGTH
// ============================================================================

/**
 * Order planets (Sun=0 to Ketu=8) by strength, strongest first.
 * Uses getStrongerPlanetFromPositions as comparator.
 *
 * Mirrors Python's order_of_planets_by_strength.
 *
 * @param planetPositions - Array of planet positions
 * @returns Array of planet indices ordered strongest to weakest
 */
export const getOrderOfPlanetsByStrength = (
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>
): number[] => {
  const planets = [0, 1, 2, 3, 4, 5, 6, 7, 8];

  // Sort using comparison: if stronger returns planet1, planet1 goes first
  planets.sort((p1, p2) => {
    const stronger = getStrongerPlanetFromPositions(planetPositions, p1, p2);
    return stronger === p1 ? -1 : 1;
  });

  return planets;
};

// ============================================================================
// HOUSE SET GENERATORS
// ============================================================================

/**
 * Get trikona (trine) houses from a given house.
 * Returns 1-based house numbers [1, 5, 9] from the given house.
 * Python: trikonas() returns list of [house, [trikona_houses]] for all houses.
 * This function returns trikonas for a single house.
 *
 * @param house - House index (0-11)
 * @returns Array of 3 trikona house numbers (1-based)
 */
export const trikonasOfHouse = (house: number): number[] => {
  return [
    (house % 12) + 1,
    ((house + 4) % 12) + 1,
    ((house + 8) % 12) + 1,
  ];
};

/**
 * Get all trikonas for all 12 houses.
 * Mirrors Python's trikonas() function.
 *
 * @returns Array of 12 arrays, each containing 3 trikona house numbers (1-based)
 */
export const trikonas = (): number[][] => {
  return Array.from({ length: 12 }, (_, house) => trikonasOfHouse(house));
};

/**
 * Get dushthana (malefic) houses from a given rasi.
 * Returns rasi indices of 6th, 8th, and 12th houses from the given rasi.
 * Python: dushthana_aspects_of_the_raasi = lambda raasi:[int(raasi+HOUSE_6)%12, int(raasi+HOUSE_8)%12, int(raasi+HOUSE_12)%12]
 *
 * @param raasi - Rasi index (0-11)
 * @returns Array of 3 rasi indices
 */
export const getDushthanasOfRaasi = (raasi: number): number[] => {
  return [
    (raasi + HOUSE_6) % 12,
    (raasi + HOUSE_8) % 12,
    (raasi + HOUSE_12) % 12,
  ];
};

/**
 * Get all dushthanas for all 12 houses (1-based house numbers).
 * Mirrors Python's dushthanas() function.
 *
 * @returns Array of 12 arrays, each containing 3 dushthana house numbers (1-based)
 */
export const dushthanas = (): number[][] => {
  return Array.from({ length: 12 }, (_, house) => {
    const dushts = getDushthanasOfRaasi(house);
    return dushts.map(x => x + 1);
  });
};

/**
 * Get chathusra (4th and 7th house) aspects from a given rasi.
 * Python: chathusra_aspects_of_the_raasi = lambda raasi:[(raasi+2)%12, (raasi+4)%12]
 * Note: In Python this returns houses at offsets 3 and 5 (0-based: 2 and 4).
 *
 * @param raasi - Rasi index (0-11)
 * @returns Array of 2 rasi indices
 */
export const getChathusrasOfRaasi = (raasi: number): number[] => {
  return [
    (raasi + 2) % 12,
    (raasi + 4) % 12,
  ];
};

/**
 * Get all chathusras for all 12 houses (1-based house numbers).
 * Mirrors Python's chathusras() function.
 *
 * @returns Array of 12 arrays, each containing 2 chathusra house numbers (1-based)
 */
export const chathusras = (): number[][] => {
  return Array.from({ length: 12 }, (_, house) => {
    const chats = getChathusrasOfRaasi(house);
    return chats.map(x => x + 1);
  });
};

/**
 * Get kendra (quadrant) houses from a given rasi (0-based rasi indices).
 * Python: kendra_aspects_of_the_raasi = lambda raasi:[(raasi)%12, (raasi+3)%12, (raasi+6)%12,(raasi+9)%12]
 * Note: getQuadrantsOfRaasi already exists but this is the explicit kendra function name.
 *
 * @param raasi - Rasi index (0-11)
 * @returns Array of 4 rasi indices
 */
export const getKendrasOfRaasi = (raasi: number): number[] => {
  return [raasi % 12, (raasi + 3) % 12, (raasi + 6) % 12, (raasi + 9) % 12];
};

/**
 * Get all kendras for all 12 houses (1-based house numbers).
 * Mirrors Python's kendras() function.
 *
 * @returns Array of 12 arrays, each containing 4 kendra house numbers (1-based)
 */
export const kendras = (): number[][] => {
  return Array.from({ length: 12 }, (_, house) => {
    const kens = getKendrasOfRaasi(house);
    return kens.map(x => x + 1);
  });
};

/**
 * Alias for kendras().
 * Mirrors Python's quadrants() function.
 */
export const quadrants = (): number[][] => kendras();

/**
 * Get panaphara houses from a given rasi.
 * Python: panaphras_of_the_raasi = lambda raasi:kendra_aspects_of_the_raasi((raasi+1)%12)
 *
 * @param raasi - Rasi index (0-11)
 * @returns Array of 4 rasi indices (2nd, 5th, 8th, 11th from given rasi)
 */
export const getPanaphrasOfRaasi = (raasi: number): number[] => {
  return getKendrasOfRaasi((raasi + 1) % 12);
};

/**
 * Get apoklima houses from a given rasi.
 * Python: apoklimas_of_the_raasi = lambda raasi:kendra_aspects_of_the_raasi((raasi+2)%12)
 *
 * @param raasi - Rasi index (0-11)
 * @returns Array of 4 rasi indices (3rd, 6th, 9th, 12th from given rasi)
 */
export const getApoklimasOfRaasi = (raasi: number): number[] => {
  return getKendrasOfRaasi((raasi + 2) % 12);
};

/**
 * Get all upachayas for all 12 houses (1-based house numbers).
 * Mirrors Python's upachayas() function.
 *
 * @returns Array of 12 arrays, each containing 4 upachaya house numbers (1-based)
 */
export const upachayas = (): number[][] => {
  return Array.from({ length: 12 }, (_, house) => {
    // Python: upa = [house,[(house)%12, (house+3)%12, (house+7)%12,(house+8)%12]]
    // Note: Python upachayas() uses offsets 0,3,7,8 (houses 1,4,8,9 from base)
    // which is different from upachaya_aspects (houses 3,6,10,11)
    return [
      (house % 12) + 1,
      ((house + 3) % 12) + 1,
      ((house + 7) % 12) + 1,
      ((house + 8) % 12) + 1,
    ];
  });
};

/**
 * Get aspected kendras of a rasi via rasi drishti.
 * Returns the rasi drishti targets sorted: those > raasi first, then those < raasi.
 * Mirrors Python's aspected_kendras_of_raasi.
 *
 * @param raasi - Rasi index (0-11)
 * @param reverseDirection - If true, reverse the order (used in drig dhasa)
 * @returns Array of rasi indices aspected via raasi drishti
 */
export const getAspectedKendrasOfRaasi = (raasi: number, reverseDirection: boolean = false): number[] => {
  const rdMap = getRaasiDrishtiMap();
  const rd = rdMap[raasi] ?? [];

  // Sort: rasis > raasi first, then rasis < raasi
  let result = [...rd.filter(r => r > raasi), ...rd.filter(r => r < raasi)];

  if (reverseDirection) {
    result.reverse();
    // Re-sort: rasis < raasi first, then rasis > raasi
    result = [...result.filter(r => r < raasi), ...result.filter(r => r > raasi)];
  }

  return result;
};

/**
 * Get functional benefic lord houses (trine houses from ascendant).
 * Python: functional_benefic_lord_houses = lambda asc_house: trines_of_the_raasi(asc_house)
 *
 * @param ascHouse - Ascendant rasi index (0-11)
 * @returns Array of 3 rasi indices (trines of ascendant)
 */
export const getFunctionalBeneficLordHouses = (ascHouse: number): number[] => {
  return getTrinesOfRaasi(ascHouse);
};

/**
 * Get functional malefic lord houses (3rd, 6th, 11th from ascendant).
 * Python: functional_malefic_lord_houses = lambda asc_house: [(asc_house+2)%12,(asc_house+5)%12,(asc_house+10)%12]
 *
 * @param ascHouse - Ascendant rasi index (0-11)
 * @returns Array of 3 rasi indices
 */
export const getFunctionalMaleficLordHouses = (ascHouse: number): number[] => {
  return [
    (ascHouse + 2) % 12,
    (ascHouse + 5) % 12,
    (ascHouse + 10) % 12,
  ];
};

/**
 * Get functional neutral lord houses (2nd, 8th, 12th from ascendant).
 * Python: functional_neutral_lord_houses = lambda asc_house: [(asc_house+1)%12,(asc_house+7)%12,(asc_house+11)%12]
 *
 * @param ascHouse - Ascendant rasi index (0-11)
 * @returns Array of 3 rasi indices
 */
export const getFunctionalNeutralLordHouses = (ascHouse: number): number[] => {
  return [
    (ascHouse + 1) % 12,
    (ascHouse + 7) % 12,
    (ascHouse + 11) % 12,
  ];
};

/**
 * Check if a planet is a yoga karaka for a given ascendant.
 * A yoga karaka is a planet that owns both a kendra and a trikona house
 * and is in its own sign (strength == 5/Own).
 * Python: is_yoga_kaaraka(asc_house, planet, planet_house)
 *
 * @param ascHouse - Ascendant rasi index (0-11)
 * @param planet - Planet index (0-8)
 * @param planetHouse - Rasi where the planet is placed (0-11)
 * @returns True if the planet is yoga karaka
 */
export const isYogaKaaraka = (ascHouse: number, planet: number, planetHouse: number): boolean => {
  const kends = getKendrasOfRaasi(ascHouse);
  const trines = getTrinesOfRaasi(ascHouse);
  return kends.includes(planetHouse) &&
         trines.includes(planetHouse) &&
         HOUSE_STRENGTHS_OF_PLANETS[planet]?.[planetHouse] === 5; // 5 = Own sign
};

/**
 * Get signs where a planet has a specific strength.
 * Python: strong_signs_of_planet = lambda planet,strength=FRIEND: [h for h in range(12) if house_strengths_of_planets[planet][h]==strength]
 *
 * @param planet - Planet index (0-8)
 * @param strength - Strength code (0=Debilitated, 1=Enemy, 2=Neutral, 3=Friend, 4=Exalted, 5=Own)
 * @returns Array of rasi indices where planet has that strength
 */
export const getStrongSignsOfPlanet = (planet: number, strength: number = STRENGTH_FRIEND): number[] => {
  const strengths = HOUSE_STRENGTHS_OF_PLANETS[planet];
  if (!strengths) return [];
  return Array.from({ length: 12 }, (_, h) => h).filter(h => strengths[h] === strength);
};

/**
 * Get lords of quadrant (kendra) houses from a given rasi.
 * Python: lords_of_quadrants = lambda h_to_p,raasi:[house_owner(h_to_p,h) for h in quadrants_of_the_raasi(raasi)]
 *
 * @param planetPositions - Planet positions
 * @param raasi - Rasi index (0-11)
 * @returns Array of planet IDs that are lords of kendra houses from raasi
 */
export const getLordsOfQuadrants = (
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>,
  raasi: number
): number[] => {
  return getKendrasOfRaasi(raasi).map(h => getHouseOwnerFromPlanetPositions(planetPositions, h));
};

/**
 * Get lords of trine (trikona) houses from a given rasi.
 * Python: lords_of_trines = lambda h_to_p, raasi:[house_owner(h_to_p,h) for h in trines_of_the_raasi(raasi)]
 *
 * @param planetPositions - Planet positions
 * @param raasi - Rasi index (0-11)
 * @returns Array of planet IDs that are lords of trikona houses from raasi
 */
export const getLordsOfTrines = (
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>,
  raasi: number
): number[] => {
  return getTrinesOfRaasi(raasi).map(h => getHouseOwnerFromPlanetPositions(planetPositions, h));
};

// ============================================================================
// TEMPORARY & COMPOUND PLANETARY RELATIONSHIPS
// ============================================================================

/**
 * Parse a HouseChart (string[12]) into planet-to-house dictionary.
 * Utility used by multiple functions.
 */
const parseChartToPlanetHouseDict = (chart: string[]): Record<number | string, number> => {
  const pToH: Record<number | string, number> = {};
  for (let h = 0; h < 12; h++) {
    if (!chart[h] || chart[h] === '') continue;
    const parts = chart[h].split('/');
    for (const part of parts) {
      const trimmed = part.trim();
      if (trimmed === 'L') {
        pToH['L'] = h;
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
 * Get temporary friends of all planets from a chart.
 * Planets within houses 2,3,4,10,11,12 (offsets 1,2,3,9,10,11) from a planet are temporary friends.
 * Mirrors Python's _get_temporary_friends_of_planets.
 *
 * @param chart - HouseChart string array (12 elements)
 * @returns Record mapping each planet (0-8) to array of temporary friend planet IDs
 */
export const getTemporaryFriendsOfPlanets = (chart: string[]): Record<number, number[]> => {
  const pToH = parseChartToPlanetHouseDict(chart);
  const result: Record<number, number[]> = {};

  for (let p = 0; p < 9; p++) {
    const pRaasi = pToH[p];
    if (pRaasi === undefined) {
      result[p] = [];
      continue;
    }

    const tempFriends: number[] = [];
    for (const offset of TEMPORARY_FRIEND_RAASI_POSITIONS) {
      const targetRasi = (pRaasi + offset) % 12;
      if (chart[targetRasi] && chart[targetRasi] !== '') {
        const parts = chart[targetRasi].split('/');
        for (const part of parts) {
          const trimmed = part.trim();
          if (trimmed !== '' && trimmed !== 'L') {
            const planet = parseInt(trimmed, 10);
            if (!isNaN(planet) && planet !== p) {
              tempFriends.push(planet);
            }
          }
        }
      }
    }

    result[p] = [...new Set(tempFriends)];
  }

  return result;
};

/**
 * Get temporary enemies of all planets from a chart.
 * Planets in houses 1,5,6,7,8,9 (offsets 0,4,5,6,7,8) from a planet are temporary enemies.
 * Mirrors Python's _get_temporary_enemies_of_planets.
 *
 * @param chart - HouseChart string array (12 elements)
 * @returns Record mapping each planet (0-8) to array of temporary enemy planet IDs
 */
export const getTemporaryEnemiesOfPlanets = (chart: string[]): Record<number, number[]> => {
  const pToH = parseChartToPlanetHouseDict(chart);
  const result: Record<number, number[]> = {};

  for (let p = 0; p < 9; p++) {
    const pRaasi = pToH[p];
    if (pRaasi === undefined) {
      result[p] = [];
      continue;
    }

    const tempEnemies: number[] = [];
    for (const offset of TEMPORARY_ENEMY_RAASI_POSITIONS) {
      const targetRasi = (pRaasi + offset) % 12;
      if (chart[targetRasi] && chart[targetRasi] !== '') {
        const parts = chart[targetRasi].split('/');
        for (const part of parts) {
          const trimmed = part.trim();
          if (trimmed !== '' && trimmed !== 'L') {
            const planet = parseInt(trimmed, 10);
            if (!isNaN(planet) && planet !== p) {
              tempEnemies.push(planet);
            }
          }
        }
      }
    }

    result[p] = [...new Set(tempEnemies)];
  }

  return result;
};

/**
 * Get compound relationships of all planets from a chart.
 * Combines natural relationships with temporary relationships:
 *   Natural friend + Temporary friend = AdhiMitra (4)
 *   Natural neutral + Temporary friend = Mitra (3)
 *   Natural friend + Temporary enemy OR Natural enemy + Temporary friend = Neutral (2)
 *   Natural neutral + Temporary enemy = Satru (1)
 *   Natural enemy + Temporary enemy = AdhiSatru (0)
 *
 * Mirrors Python's _get_compound_relationships_of_planets.
 *
 * @param chart - HouseChart string array (12 elements)
 * @returns 9x9 matrix where [p][p1] = compound relationship code
 */
export const getCompoundRelationshipsOfPlanets = (chart: string[]): number[][] => {
  const tf = getTemporaryFriendsOfPlanets(chart);
  const te = getTemporaryEnemiesOfPlanets(chart);
  const nf = naturalFriendsOfPlanets();
  const nn = naturalNeutralOfPlanets();
  const ne = naturalEnemiesOfPlanets();

  const result: number[][] = Array.from({ length: 9 }, () => Array(9).fill(0));

  for (let p = 0; p < 9; p++) {
    const tfp = tf[p] ?? [];
    const tep = te[p] ?? [];
    const nfp = nf[p] ?? [];
    const nnp = nn[p] ?? [];
    const nep = ne[p] ?? [];

    for (let p1 = 0; p1 < 9; p1++) {
      if (p === p1) continue;

      if (nfp.includes(p1) && tfp.includes(p1)) {
        // Natural friend + Temporary friend = AdhiMitra
        result[p][p1] = COMPOUND_ADHIMITRA;
      } else if ((nfp.includes(p1) && tep.includes(p1)) || (nep.includes(p1) && tfp.includes(p1))) {
        // Natural friend + Temporary enemy OR Natural enemy + Temporary friend = Neutral
        result[p][p1] = COMPOUND_NEUTRAL;
      } else if (nnp.includes(p1) && tfp.includes(p1)) {
        // Natural neutral + Temporary friend = Mitra
        result[p][p1] = COMPOUND_MITRA;
      } else if (nnp.includes(p1) && tep.includes(p1)) {
        // Natural neutral + Temporary enemy = Satru
        result[p][p1] = COMPOUND_SATRU;
      } else if (nep.includes(p1) && tep.includes(p1)) {
        // Natural enemy + Temporary enemy = AdhiSatru
        result[p][p1] = COMPOUND_ADHISATRU;
      }
    }
  }

  return result;
};

/**
 * Get compound friends of all planets from a chart.
 * Compound friends include AdhiMitra (4) and Mitra (3).
 *
 * @param chart - HouseChart string array (12 elements)
 * @returns Record mapping each planet (0-8) to array of compound friend planet IDs
 */
export const getCompoundFriendsOfPlanets = (chart: string[]): Record<number, number[]> => {
  const cr = getCompoundRelationshipsOfPlanets(chart);
  const result: Record<number, number[]> = {};
  for (let p = 0; p < 9; p++) {
    result[p] = [];
    for (let p1 = 0; p1 < 9; p1++) {
      if (p !== p1 && (cr[p][p1] === COMPOUND_ADHIMITRA || cr[p][p1] === COMPOUND_MITRA)) {
        result[p].push(p1);
      }
    }
  }
  return result;
};

/**
 * Get compound enemies of all planets from a chart.
 * Compound enemies include Satru (1) and AdhiSatru (0).
 *
 * @param chart - HouseChart string array (12 elements)
 * @returns Record mapping each planet (0-8) to array of compound enemy planet IDs
 */
export const getCompoundEnemiesOfPlanets = (chart: string[]): Record<number, number[]> => {
  const cr = getCompoundRelationshipsOfPlanets(chart);
  const result: Record<number, number[]> = {};
  for (let p = 0; p < 9; p++) {
    result[p] = [];
    for (let p1 = 0; p1 < 9; p1++) {
      if (p !== p1 && (cr[p][p1] === COMPOUND_SATRU || cr[p][p1] === COMPOUND_ADHISATRU)) {
        result[p].push(p1);
      }
    }
  }
  return result;
};

/**
 * Get compound neutrals of all planets from a chart.
 * Compound neutrals have relationship code = 2 (COMPOUND_NEUTRAL).
 *
 * @param chart - HouseChart string array (12 elements)
 * @returns Record mapping each planet (0-8) to array of compound neutral planet IDs
 */
export const getCompoundNeutralOfPlanets = (chart: string[]): Record<number, number[]> => {
  const cr = getCompoundRelationshipsOfPlanets(chart);
  const result: Record<number, number[]> = {};
  for (let p = 0; p < 9; p++) {
    result[p] = [];
    for (let p1 = 0; p1 < 9; p1++) {
      if (p !== p1 && cr[p][p1] === COMPOUND_NEUTRAL) {
        result[p].push(p1);
      }
    }
  }
  return result;
};

// ============================================================================
// DRISHTI HELPER FUNCTIONS (from chart data)
// ============================================================================

/**
 * Get graha drishti of a specific planet from the chart.
 * Returns the rasi indices aspected by the planet via graha drishti.
 * Mirrors Python's aspected_rasis_of_the_planet (using graha drishti).
 *
 * @param chart - HouseChart string array (12 elements)
 * @param planet - Planet index (0-8)
 * @returns Array of rasi indices aspected by the planet via graha drishti
 */
export const getGrahaDrishtiRasisOfPlanet = (chart: string[], planet: number): number[] => {
  const { arp } = getGrahaDrishtiFromChart(chart);
  return arp[planet] ?? [];
};

/**
 * Get graha drishti houses aspected by a specific planet from the chart.
 * Mirrors Python's aspected_houses_of_the_planet.
 *
 * @param chart - HouseChart string array (12 elements)
 * @param planet - Planet index (0-8)
 * @returns Array of house numbers (1-12) aspected by the planet via graha drishti
 */
export const getGrahaDrishtiHousesOfPlanet = (chart: string[], planet: number): number[] => {
  const { ahp } = getGrahaDrishtiFromChart(chart);
  return ahp[planet] ?? [];
};

/**
 * Get planets aspected by a specific planet via graha drishti from the chart.
 * Mirrors Python's aspected_planets_of_the_planet.
 *
 * @param chart - HouseChart string array (12 elements)
 * @param planet - Planet index (0-8)
 * @returns Array of planet indices aspected by the given planet via graha drishti
 */
export const getGrahaDrishtiPlanetsOfPlanet = (chart: string[], planet: number): number[] => {
  const { app } = getGrahaDrishtiFromChart(chart);
  return app[planet] ?? [];
};

/**
 * Get planets that aspect a given planet via graha drishti.
 * This is the reverse: which planets have graha drishti ON the given planet.
 * Mirrors Python's graha_drishti_on_planet concept.
 *
 * @param chart - HouseChart string array (12 elements)
 * @param planet - Planet index (0-8) being aspected
 * @returns Array of planet indices that aspect the given planet via graha drishti
 */
export const getGrahaDrishtiOnPlanet = (chart: string[], planet: number): number[] => {
  const { app } = getGrahaDrishtiFromChart(chart);
  const result: number[] = [];
  for (let p = 0; p < 9; p++) {
    if (p !== planet && (app[p] ?? []).includes(planet)) {
      result.push(p);
    }
  }
  return result;
};

/**
 * Get raasi drishti of a specific planet from the chart.
 * Returns the rasi indices aspected by the planet's sign via raasi drishti.
 * Mirrors Python's raasi_drishti_of_the_planet.
 *
 * @param chart - HouseChart string array (12 elements)
 * @param planet - Planet index (0-8)
 * @returns Array of rasi indices aspected via raasi drishti
 */
export const getRaasiDrishtiOfPlanet = (chart: string[], planet: number): number[] => {
  const pToH = parseChartToPlanetHouseDict(chart);
  const planetToHouseMap: Record<number, number> = {};
  for (let p = 0; p < 9; p++) {
    if (pToH[p] !== undefined) planetToHouseMap[p] = pToH[p];
  }
  const { arp } = getRaasiDrishtiFromChart(planetToHouseMap);
  return arp[planet] ?? [];
};

/**
 * Get planets that aspect a given rasi via raasi drishti.
 * Mirrors Python's aspected_planets_of_the_raasi.
 *
 * @param chart - HouseChart string array (12 elements)
 * @param raasi - Rasi index (0-11) being aspected
 * @returns Array of planet indices whose rasi aspects the given rasi
 */
export const getAspectedPlanetsOfRaasi = (chart: string[], raasi: number): number[] => {
  const pToH = parseChartToPlanetHouseDict(chart);
  const planetToHouseMap: Record<number, number> = {};
  for (let p = 0; p < 9; p++) {
    if (pToH[p] !== undefined) planetToHouseMap[p] = pToH[p];
  }
  const { arp } = getRaasiDrishtiFromChart(planetToHouseMap);
  return Object.entries(arp)
    .filter(([, aspectedRasis]) => aspectedRasis.includes(raasi))
    .map(([key]) => parseInt(key, 10));
};

// ============================================================================
// RUDRA CALCULATION
// ============================================================================

/**
 * Calculate Rudra planet from planet positions.
 * Rudra is the stronger of:
 *   - Lord of the 8th house from Lagna (using rudra_eighth_house table)
 *   - Lord of the 8th house from 7th house (using rudra_eighth_house table)
 *
 * Mirrors Python's rudra(planet_positions).
 *
 * @param planetPositions - Array of planet positions (first element is Ascendant with planet=-1)
 * @returns [rudra_planet, rudra_sign, trishoola_rasis]
 */
export const getRudra = (
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>
): [number, number, number[]] => {
  const pToH: Record<number | string, number> = {};
  for (const p of planetPositions) {
    if (p.planet === -1) {
      pToH['L'] = p.rasi;
    } else {
      pToH[p.planet] = p.rasi;
    }
  }

  const chart = buildHouseChart(planetPositions);
  const lagnaHouse = pToH['L'] ?? 0;

  // Lord of 8th house from Lagna (using rudra_eighth_house lookup)
  const eighthHouseLord = getHouseOwnerFromChart(chart, RUDRA_EIGHTH_HOUSE[lagnaHouse]);

  // Lord of 8th house from 7th house
  const seventhHouse = (lagnaHouse + 6) % 12;
  const seventhHouseLord = getHouseOwnerFromChart(chart, RUDRA_EIGHTH_HOUSE[seventhHouse]);

  // Stronger of these two lords
  const rudra = getStrongerPlanetFromPositions(planetPositions, eighthHouseLord, seventhHouseLord);

  const rudraSign = pToH[rudra] ?? 0;
  const trishoolaRasis = getTrinesOfRaasi(rudraSign);

  return [rudra, rudraSign, trishoolaRasis];
};

/**
 * Get trishoola rasis from planet positions.
 * Mirrors Python's trishoola_rasis(planet_positions).
 *
 * @param planetPositions - Array of planet positions
 * @returns Array of 3 rasi indices (trines of Rudra's sign)
 */
export const getTrishoolaRasis = (
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>
): number[] => {
  return getTrinesOfRaasi(getRudra(planetPositions)[1]);
};

/**
 * Helper: get house owner from a chart (string[12]) format.
 * Handles co-lord exceptions for Scorpio and Aquarius.
 */
const getHouseOwnerFromChart = (chart: string[], sign: number): number => {
  let lord = SIGN_LORDS[sign % 12] ?? 0;

  if ((sign % 12) === SCORPIO) {
    // Mars vs Ketu for Scorpio
    lord = getStrongerPlanetFromChart(chart, MARS, KETU);
  } else if ((sign % 12) === AQUARIUS) {
    // Saturn vs Rahu for Aquarius
    lord = getStrongerPlanetFromChart(chart, SATURN, RAHU);
  }

  return lord;
};

/**
 * Helper: find stronger planet from a chart (string[12]).
 * Simplified version using planet count in same house as tiebreaker.
 */
const getStrongerPlanetFromChart = (chart: string[], p1: number, p2: number): number => {
  if (p1 === p2) return p1;

  const pToH = parseChartToPlanetHouseDict(chart);
  const h1 = pToH[p1];
  const h2 = pToH[p2];
  if (h1 === undefined || h2 === undefined) return p1;

  // Count planets in same house (excluding self)
  const countInHouse = (h: number, exclude: number): number => {
    if (!chart[h] || chart[h] === '') return 0;
    const parts = chart[h].split('/').filter(part => {
      const t = part.trim();
      if (t === '' || t === 'L') return false;
      const pid = parseInt(t, 10);
      return !isNaN(pid) && pid !== exclude;
    });
    return parts.length;
  };

  const count1 = countInHouse(h1, p1);
  const count2 = countInHouse(h2, p2);
  if (count1 > count2) return p1;
  if (count2 > count1) return p2;

  // Use house strength as tiebreaker
  const strength1 = HOUSE_STRENGTHS_OF_PLANETS[p1]?.[h1] ?? 0;
  const strength2 = HOUSE_STRENGTHS_OF_PLANETS[p2]?.[h2] ?? 0;
  if (strength1 > strength2) return p1;
  if (strength2 > strength1) return p2;

  // Dual > Fixed > Movable
  const getRasiTypeStrength = (r: number): number => {
    if (DUAL_SIGNS.includes(r)) return 3;
    if (FIXED_SIGNS.includes(r)) return 2;
    if (MOVABLE_SIGNS.includes(r)) return 1;
    return 0;
  };
  const rt1 = getRasiTypeStrength(h1);
  const rt2 = getRasiTypeStrength(h2);
  if (rt1 > rt2) return p1;
  if (rt2 > rt1) return p2;

  return p1;
};

// ============================================================================
// MAHESHWARA CALCULATION
// ============================================================================

/**
 * Calculate Maheshwara planet from planet positions.
 * Maheshwara is determined from the Atma Karaka's 8th lord, with several
 * exception rules for own sign, Rahu/Ketu conjunction, etc.
 *
 * Mirrors Python's maheshwara_from_planet_positions.
 *
 * @param planetPositions - Array of planet positions (first element is Ascendant with planet=-1)
 * @returns Planet ID of Maheshwara
 */
export const getMaheshwara = (
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>
): number => {
  const charaKarakas = getCharaKarakas(planetPositions);
  const atmaKaraka = charaKarakas[0];

  const pToH: Record<number | string, number> = {};
  for (const p of planetPositions) {
    if (p.planet === -1) {
      pToH['L'] = p.rasi;
    } else {
      pToH[p.planet] = p.rasi;
    }
  }

  // Get Atma Karaka's house from planet positions
  const akPos = planetPositions.find(p => p.planet === atmaKaraka);
  const atmaKarakaHouse = akPos?.rasi ?? 0;

  // Lord of 8th from Atma Karaka
  let maheshwara = getHouseOwnerFromPlanetPositions(planetPositions, (atmaKarakaHouse + 7) % 12);

  // If Maheshwara is in its own sign, take stronger of 8th and 12th lords from that sign
  if (pToH[maheshwara] === HOUSE_OWNERS[maheshwara]) {
    const maheshwaraHouse = pToH[maheshwara];
    const atma8thLord = getHouseOwnerFromPlanetPositions(planetPositions, (maheshwaraHouse + 7) % 12);
    const atma12thLord = getHouseOwnerFromPlanetPositions(planetPositions, (maheshwaraHouse + 11) % 12);
    maheshwara = getStrongerPlanetFromPositions(planetPositions, atma8thLord, atma12thLord);
  }

  // If Maheshwara is conjunct Rahu or Ketu, or Rahu/Ketu is in 8th from Maheshwara
  if (pToH[maheshwara] === pToH[RAHU] || pToH[maheshwara] === pToH[KETU]) {
    maheshwara = getHouseOwnerFromPlanetPositions(planetPositions, (atmaKarakaHouse + 5) % 12);
  } else if (pToH[RAHU] === (pToH[maheshwara] + 7) % 12 || pToH[KETU] === (pToH[maheshwara] + 7) % 12) {
    maheshwara = getHouseOwnerFromPlanetPositions(planetPositions, (atmaKarakaHouse + 5) % 12);
  }

  // If Maheshwara is Rahu, replace with Mercury; if Ketu, replace with Jupiter
  if (maheshwara === RAHU) {
    maheshwara = MERCURY;
  } else if (maheshwara === KETU) {
    maheshwara = JUPITER;
  }

  return maheshwara;
};

// ============================================================================
// LONGEVITY CALCULATION (Partial - requires Hora Lagna from ephemeris)
// ============================================================================

/**
 * Get longevity pair category based on two rasi types.
 * Python: longevity_of_pair = lambda rasi1,rasi2: [key for key,value in longevity.items() if (rasi1,rasi2) in value][0]
 *
 * @param rasiType1 - Rasi type (0=Fixed, 1=Movable, 2=Dual)
 * @param rasiType2 - Rasi type (0=Fixed, 1=Movable, 2=Dual)
 * @returns Longevity category (0=Short, 1=Middle, 2=Long)
 */
export const getLongevityOfPair = (rasiType1: number, rasiType2: number): number => {
  for (const [key, pairs] of Object.entries(LONGEVITY)) {
    for (const [r1, r2] of pairs) {
      if (r1 === rasiType1 && r2 === rasiType2) {
        return parseInt(key, 10);
      }
    }
  }
  return 0; // Default to short life
};

/**
 * Get the rasi type for a given sign.
 * @param rasi - Rasi index (0-11)
 * @returns 0=Fixed, 1=Movable, 2=Dual
 */
export const getRasiType = (rasi: number): number => {
  if (FIXED_SIGNS.includes(rasi)) return 0;
  if (MOVABLE_SIGNS.includes(rasi)) return 1;
  if (DUAL_SIGNS.includes(rasi)) return 2;
  return 0;
};

/**
 * Calculate the first two longevity pairs from planet positions.
 * The full longevity calculation requires Hora Lagna (JD/place dependent),
 * but this provides the first two pairs which are chart-data-only.
 *
 * Pair 1: Rasi types of Lagna lord's house and 8th lord's house
 * Pair 2: Rasi types of Moon's house and Saturn's house
 *
 * @param planetPositions - Planet positions
 * @returns Object with pair1, pair2 longevity categories and partial result
 */
export const getLongevityPairs = (
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>
): { pair1: number; pair2: number } => {
  const pToH: Record<number | string, number> = {};
  for (const p of planetPositions) {
    if (p.planet === -1) {
      pToH['L'] = p.rasi;
    } else {
      pToH[p.planet] = p.rasi;
    }
  }

  const chart = buildHouseChart(planetPositions);
  const lagnaHouse = pToH['L'] ?? 0;

  // Pair 1: Lagna lord's house type and 8th lord's house type
  const lagnaLord = getHouseOwnerFromChart(chart, lagnaHouse);
  const lagnaLordHouse = pToH[lagnaLord] ?? 0;
  const eighthLord = getHouseOwnerFromChart(chart, RUDRA_EIGHTH_HOUSE[lagnaHouse]);
  const eighthLordHouse = pToH[eighthLord] ?? 0;
  const pair1 = getLongevityOfPair(getRasiType(lagnaLordHouse), getRasiType(eighthLordHouse));

  // Pair 2: Moon's house type and Saturn's house type
  const moonHouse = pToH[MOON] ?? 0;
  const saturnHouse = pToH[SATURN] ?? 0;
  const pair2 = getLongevityOfPair(getRasiType(moonHouse), getRasiType(saturnHouse));

  return { pair1, pair2 };
};

// ============================================================================
// VARGA VISWA (Compound relationship scores)
// ============================================================================

/**
 * Calculate Varga Viswa scores for each planet.
 * Based on compound relationships with the lord of the occupied sign.
 * Mirrors Python's _get_varga_viswa_of_planets.
 *
 * @param chart - HouseChart string array (12 elements)
 * @returns Array of 9 scores (one per planet, Sun=0 to Ketu=8)
 */
export const getVargaViswaOfPlanets = (chart: string[]): number[] => {
  const pToH = parseChartToPlanetHouseDict(chart);
  const cs = getCompoundRelationshipsOfPlanets(chart);
  const scores = [5, 7, 10, 15, 18]; // AdhiSatru, Satru, Neutral, Mitra, AdhiMitra

  const vv: number[] = Array(9).fill(0);

  for (let p = 0; p < 9; p++) {
    const planetHouse = pToH[p];
    if (planetHouse === undefined) continue;

    if (HOUSE_STRENGTHS_OF_PLANETS[p]?.[planetHouse] === 5) {
      // Planet is owner/ruler of the sign -> score 20
      vv[p] = 20;
    } else {
      const dispositor = HOUSE_OWNERS[planetHouse];
      if (dispositor !== undefined) {
        vv[p] = scores[cs[p][dispositor]] ?? 0;
      }
    }
  }

  return vv;
};
