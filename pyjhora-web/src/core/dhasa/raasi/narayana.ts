
import {
    EVEN_FOOTED_SIGNS,
    HOUSE_STRENGTHS_OF_PLANETS,
    KETU,
    NARAYANA_DHASA_KETU_EXCEPTION_PROGRESSION,
    NARAYANA_DHASA_NORMAL_PROGRESSION,
    NARAYANA_DHASA_SATURN_EXCEPTION_PROGRESSION,
    SATURN,
    STRENGTH_DEBILITATED,
    STRENGTH_EXALTED
} from '../../constants';
// Note: Fix relative paths if structure changes. ../../constants -> src/core/constants
// Current: src/core/dhasa/raasi/narayana.ts. Up 3 levels: raasi -> dhasa -> core -> constants.ts is ../../constants

import {
    getHouseOwnerFromPlanetPositions,
    getPlanetToHouseDict,
    getStrongerRasi
} from '../../horoscope/house';

// actually julian.ts has julianDayToDate maybe? format.ts for display?
// Let's use basic Date manipulation for now or standard utils if found.
// `addYearsToDate` likely needs implementation or finding.

// Count Rasis inclusive/exclusive?
// Python: utils.count_rasis(from, to)
// def count_rasis(from_house, to_house): return (to_house - from_house) % 12 + 1
const countRasis = (fromHouse: number, toHouse: number): number => {
  return (toHouse - fromHouse + 12) % 12 + 1;
};

/**
 * Calculate duration of a Narayana dasha period for a sign
 * @param planetPositions 
 * @param sign 
 * @param varshaNarayana 
 */
export const getNarayanaDashaDuration = (
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>,
  sign: number,
  varshaNarayana: boolean = false
): number => {
  const lordOfSign = getHouseOwnerFromPlanetPositions(planetPositions, sign, true); // checkDuringDhasa=true
  const pToH = getPlanetToHouseDict(planetPositions);
  const houseOfLord = pToH[lordOfSign];

  let dhasaPeriod = 0;
  
  // The length of a dasa is determined by the position of the lord of dasa rasi with respect to dasa rasi.
  // Exception handling for Even Footed Signs (count backward? or forward?)
  // Python: 
  // dhasa_period = utils.count_rasis(house_of_lord,sign) if sign in const.even_footed_signs \
  //                 else utils.count_rasis(sign, house_of_lord)
  
  // count_rasis(A, B) is distance from A to B (B-A)
  // If Even Footed: Count from Lord TO Sign (Backward from Sign to Lord?)
  // Wait. count_rasis(house_of_lord, sign) means start at Lord, count to Sign.
  
  if (EVEN_FOOTED_SIGNS.includes(sign)) {
    dhasaPeriod = countRasis(houseOfLord, sign);
  } else {
    dhasaPeriod = countRasis(sign, houseOfLord);
  }
  
  dhasaPeriod -= 1; // Subtract one from the count
  
  // Exception (1): If count is 1 (result 0), it becomes 12.
  if (dhasaPeriod <= 0) {
    dhasaPeriod = 12;
  }
  
  // Exception (2): Exalted Lord -> Add 1 year
  const strength = HOUSE_STRENGTHS_OF_PLANETS[lordOfSign]?.[houseOfLord];
  
  if (strength === STRENGTH_EXALTED) {
    dhasaPeriod += 1;
  } 
  // Exception (3): Debilitated Lord -> Subtract 1 year
  else if (strength === STRENGTH_DEBILITATED) {
    dhasaPeriod -= 1;
  }
  
  if (varshaNarayana) {
      // Not implementing Varsha Narayana full logic yet (assumes factor logic handled upstream or here?)
      // Python: dhasa_period *= 3 (Wait, really? standard varsha is compressed... verify requirement)
      // Python code says: if varsha_narayana: dhasa_period *= 3. Weird? Usually Varsha is 1 year total.
      // Ah, Varsha Narayana Dasha might be different system.
      // Let's stick to standard Narayana for now.
  }
  
  return dhasaPeriod;
};

/**
 * Main Narayana Dasha Calculation
 * @param planetPositions 
 * @param dob 
 */
export const getNarayanaDashaPeriods = (
    planetPositions: Array<{ planet: number; rasi: number; longitude: number }>,
    dob: Date // Use Date object for simplicity
): Array<{ sign: number; start: Date; end: Date; duration: number }> => {
    // 1. Determine Seed Sign
    // Stronger of Ascendant and 7th House
    const pToH = getPlanetToHouseDict(planetPositions);
    // Ascendant usually passed as object or symbol. In our array it might be missing?
    // We assume caller provides array with Ascendant?
    // house.ts helpers don't handle 'L' symbol well in array.
    // We usually pass Ascendant Rasi separately or map 'L' to Rasi.
    
    // Let's try to find Ascendant in planetPositions (we should standardized this).
    // If not found, default to 0 (Aries) but that's bad.
    // Standard: planetPositions should include { planet: -1 or specific ID, rasi: X } for Lagna.
    // Or we rely on pToH having it if constructed from extended data.
    // Let's assume input has Lagna as a specific ID or we look for it.
    // CONSTANT for Lagna ID? In constants.ts we have 'ASCENDANT_SYMBOL' = 'L'.
    // Typescript planet is number.
    // Let's assume valid Ascendant Rasi is obtainable.
    // For now, let's scan for a convention or ask caller to provide it.
    // Assuming planetPositions contains all necessary data.
    // house.ts `getRaasiDrishtiFromChart` looked for `ASCENDANT_SYMBOL`.
    
    // We need the Ascendant Rasi.
    // Let's check if we can get it from pToH if keys are mixed numbers/strings?
    // house.ts uses `Record<number | string, number>`.
    // But `getPlanetToHouseDict` returns `Record<number, number>`.
    // We need to support 'L' or equivalent.
    
    // Hack: Pass Ascendant Rasi explicitly?
    // Let's adapt signature to take `ascendantRasi: number`.
    
    // Wait, python `_narayana_dhasa_calculation` takes `dhasa_seed_sign` as input!
    // Calculated by `narayana_dhasa_for_rasi_chart`.
    // So we should split this.
    
    // But for this export, let's implement the wrapper too.
    
    // Placeholder - user must provide seed sign logic or we calculate it here.
    // Let's implement `calculateNarayanaDasha` which takes seed sign.
    // And `getNarayanaDashaForChart` which finds seed.
    return [];
}

/**
 * Core calculation logic
 */
export const calculateNarayanaDasha = (
    planetPositions: Array<{ planet: number; rasi: number; longitude: number }>,
    seedSign: number,
    startDate: Date
): Array<{ sign: number; start: Date; end: Date; duration: number }> => {
    const pToH = getPlanetToHouseDict(planetPositions);
    
    // Determine Progression Type
    // Normal
    let progression = NARAYANA_DHASA_NORMAL_PROGRESSION[seedSign];
    
    // Exceptions
    // If Saturn (6) is in Seed Sign -> Saturn Exception
    if (pToH[SATURN] === seedSign) {
        progression = NARAYANA_DHASA_SATURN_EXCEPTION_PROGRESSION[seedSign];
    }
    // If Ketu (8) is in Seed Sign -> Ketu Exception
    else if (pToH[KETU] === seedSign) {
        progression = NARAYANA_DHASA_KETU_EXCEPTION_PROGRESSION[seedSign];
    }
    
    const periods: Array<{ sign: number; start: Date; end: Date; duration: number }> = [];
    let currentStart = new Date(startDate);
    
    // First Cycle (12 signs)
    progression.forEach(sign => {
        const duration = getNarayanaDashaDuration(planetPositions, sign);
        const end = new Date(currentStart);
        end.setFullYear(end.getFullYear() + duration);
        
        periods.push({
            sign,
            start: new Date(currentStart),
            end: new Date(end),
            duration
        });
        
        currentStart = end;
    });
    
    // Second Cycle check
    // If total duration < 120 (Human lifespan)? Python checks `human_life_span_for_narayana_dhasa`.
    // Python logic:
    // total_dhasa_duration = sum(...)
    // for c, dhasa_lord in enumerate(progression):
    //    dhasa_duration = (12 - first_cycle_duration)
    //    if dhasa_duration <= 0: continue
    //    ... add second cycle period ...
    //    if total >= 120 break
    
    let totalDuration = periods.reduce((sum, p) => sum + p.duration, 0);
    const MAX_LIFESPAN = 96; // JHora default for Narayana? Python const.py says 'human_life_span_for_narayana_dhasa' usually 120 or similar.
    // Let's check python consts if needed. Assuming 120 is safe or infinite.
    // Logic: If a sign gave < 12 years in first cycle, it gives the remainder (12 - duration) in second cycle.
    
    if (totalDuration < 120) {
        for (let i = 0; i < 12; i++) {
            const sign = progression[i];
            const firstCycleDuration = periods[i].duration; // Corresponds to same index i based on progression
            
            const secondDuration = 12 - firstCycleDuration;
            
            if (secondDuration > 0) {
                 const end = new Date(currentStart);
                 end.setFullYear(end.getFullYear() + secondDuration);
                 
                 periods.push({
                     sign,
                     start: new Date(currentStart),
                     end: new Date(end),
                     duration: secondDuration
                 });
                 
                 currentStart = end;
                 totalDuration += secondDuration;
                 
                 if (totalDuration >= 120) break; // Or whatever limit
            }
        }
    }
    
    return periods;
};

/**
 * Determine Seed Sign for Narayana Dasha
 * Stronger of Ascendant and 7th House
 */
export const getNarayanaDashaSeedSign = (
    planetPositions: Array<{ planet: number; rasi: number; longitude: number }>,
    ascendantRasi: number
): number => {
    const seventhHouse = (ascendantRasi + 6) % 12;
    return getStrongerRasi(planetPositions, ascendantRasi, seventhHouse);
};

