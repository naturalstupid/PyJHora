
import {
    EVEN_FOOTED_SIGNS,
    HOUSE_STRENGTHS_OF_PLANETS,
    STRENGTH_DEBILITATED,
    STRENGTH_EXALTED
} from '../../constants';
// Adjusted path: src/core/dhasa/raasi/chara.ts -> ../../constants

import {
    getHouseOwnerFromPlanetPositions,
    getPlanetToHouseDict
} from '../../horoscope/house';

// Count Rasis inclusive/exclusive?
// Reusing logic from Narayana if possible or duplicating simple math.
const countRasis = (fromHouse: number, toHouse: number): number => {
  return (toHouse - fromHouse + 12) % 12 + 1;
};

/**
 * Calculate duration of Chara Dasha for a sign (KN Rao Method)
 * @param planetPositions 
 * @param sign 
 */
export const getCharaDhasaDuration = (
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>,
  sign: number
): number => {
    // KN Rao Method Logic (matches standard Parashara exceptions often used)
    const lordOfSign = getHouseOwnerFromPlanetPositions(planetPositions, sign, false); 
    const pToH = getPlanetToHouseDict(planetPositions);
    const houseOfLord = pToH[lordOfSign];
    
    // Check if houseOfLord is valid (e.g. if planet missing). 
    // Assuming valid data.
    
    let dhasaPeriod = 0;
    
    // Check footedness of the Dasha Sign (Pulse)
    if (EVEN_FOOTED_SIGNS.includes(sign)) {
        // Even footed: Count from Lord TO Sign (Backward?)
        // Python: utils.count_rasis(house_of_lord, sign)
        dhasaPeriod = countRasis(houseOfLord, sign);
    } else {
        // Odd footed: Count from Sign TO Lord (Forward?)
        // Python: utils.count_rasis(sign, house_of_lord)
        dhasaPeriod = countRasis(sign, houseOfLord);
    }
    
    dhasaPeriod -= 1; // Subtract 1
    
    // Exception 1: Result 0 -> 12
    if (dhasaPeriod <= 0) {
        dhasaPeriod = 12;
    }
    
    // Exception 2: Exalted Lord -> +1
    const strength = HOUSE_STRENGTHS_OF_PLANETS[lordOfSign]?.[houseOfLord];
    if (strength === STRENGTH_EXALTED) {
        dhasaPeriod += 1;
    }
    // Exception 3: Debilitated Lord -> -1
    else if (strength === STRENGTH_DEBILITATED) {
        dhasaPeriod -= 1;
    }
    
    return dhasaPeriod;
};

/**
 * Get Chara Dasha Progression (KN Rao Method)
 * @param ascendantRasi 
 */
export const getCharaDhasaProgression = (ascendantRasi: number): number[] => {
    const seedHouse = ascendantRasi;
    
    // Check 9th from Seed
    const ninthHouse = (seedHouse + 8) % 12;
    
    let progression: number[] = [];
    
    if (EVEN_FOOTED_SIGNS.includes(ninthHouse)) {
        // Reverse
        // Python: [(seed_house+12-h)%12 for h in range(12)]
        // h=0 -> seed. h=1 -> seed-1...
        progression = Array.from({ length: 12 }, (_, h) => (seedHouse + 12 - h) % 12);
    } else {
        // Forward
        // Python: [(h+seed_house)%12 for h in range(12)]
        progression = Array.from({ length: 12 }, (_, h) => (seedHouse + h) % 12);
    }
    
    return progression;
};

/**
 * Calculate Chara Dasha Periods (KN Rao)
 * @param planetPositions 
 * @param ascendantRasi 
 * @param dob 
 */
export const calculateCharaDasha = (
    planetPositions: Array<{ planet: number; rasi: number; longitude: number }>,
    ascendantRasi: number,
    dob: Date
): Array<{ sign: number; start: Date; end: Date; duration: number }> => {
    const progression = getCharaDhasaProgression(ascendantRasi);
    const periods: Array<{ sign: number; start: Date; end: Date; duration: number }> = [];
    
    let currentStart = new Date(dob);
    
    for (const sign of progression) {
        const duration = getCharaDhasaDuration(planetPositions, sign);
        const end = new Date(currentStart);
        end.setFullYear(end.getFullYear() + duration);
        
        periods.push({
            sign,
            start: new Date(currentStart),
            end: new Date(end),
            duration
        });
        
        currentStart = end;
    }
    
    return periods;
};
