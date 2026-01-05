
import {
    EVEN_FOOTED_SIGNS,
    HOUSE_STRENGTHS_OF_PLANETS,
    RASI_NAMES_EN,
    STRENGTH_DEBILITATED,
    STRENGTH_EXALTED
} from '../../constants';

import {
    getHouseOwnerFromPlanetPositions,
    getPlanetToHouseDict
} from '../../horoscope/house';

import { getDivisionalChart, PlanetPosition } from '../../horoscope/charts';
import { getPlanetLongitude } from '../../panchanga/drik';
import { type Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// Count Rasis inclusive/exclusive?
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
    // KN Rao Method Logic
    const lordOfSign = getHouseOwnerFromPlanetPositions(planetPositions, sign, false); 
    const pToH = getPlanetToHouseDict(planetPositions);
    const houseOfLord = pToH[lordOfSign];
    
    // Safety check if planet missing
    if (houseOfLord === undefined) return 12;

    let dhasaPeriod = 0;
    
    // Check footedness
    if (EVEN_FOOTED_SIGNS.includes(sign)) {
        dhasaPeriod = countRasis(houseOfLord, sign);
    } else {
        dhasaPeriod = countRasis(sign, houseOfLord);
    }
    
    dhasaPeriod -= 1; // Subtract 1

    if (dhasaPeriod <= 0) {
        dhasaPeriod = 12;
    }

    const strength = HOUSE_STRENGTHS_OF_PLANETS[lordOfSign]?.[houseOfLord];
    if (strength === STRENGTH_EXALTED) {
        dhasaPeriod += 1;
    }
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
    const ninthHouse = (seedHouse + 8) % 12;
    
    let progression: number[] = [];
    
    if (EVEN_FOOTED_SIGNS.includes(ninthHouse)) {
        progression = Array.from({ length: 12 }, (_, h) => (seedHouse + 12 - h) % 12);
    } else {
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

// ===================================
// WRAPPER
// ===================================

function getPositions(jd: number, place: Place, divFactor: number = 1): PlanetPosition[] {
    const d1: PlanetPosition[] = [];
    for (let i = 0; i <= 8; i++) {
        const l = getPlanetLongitude(jd, place, i);
        d1.push({ planet: i, rasi: Math.floor(l / 30), longitude: l % 30 });
    }
    if (divFactor > 1) return getDivisionalChart(d1, divFactor);
    return d1;
}

function fmtDate(d: Date): string {
    const pad = (n: number) => n.toString().padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

export function getCharaDashaBhukti(
    jd: number,
    place: Place,
    options: { divisionalChartFactor?: number, includeBhuktis?: boolean } = {}
): { mahadashas: any[], bhuktis?: any[] } {
    const { divisionalChartFactor = 1 } = options;
    const positions = getPositions(jd, place, divisionalChartFactor);
    const asc = positions[0]?.rasi ?? 0;

    const { date, time } = julianDayToGregorian(jd);
    const dob = new Date(date.year, date.month - 1, date.day, time.hour, time.minute, time.second);

    const periods = calculateCharaDasha(positions, asc, dob);

    return {
        mahadashas: periods.map(p => ({
            rasi: p.sign,
            rasiName: RASI_NAMES_EN[p.sign],
            startDate: fmtDate(p.start),
            durationYears: p.duration
        }))
    };
}
