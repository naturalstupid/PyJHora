/**
 * Chara Dasha System
 * Ported from PyJHora chara.py
 *
 * chara_method = 1 => Parasara/PVN Rao Method with two cycles (default)
 * chara_method = 2 => KN Rao Single Cycle
 */

import {
    EVEN_FOOTED_SIGNS,
    HOUSE_STRENGTHS_OF_PLANETS,
    RASI_NAMES_EN,
    SIDEREAL_YEAR,
    STRENGTH_DEBILITATED,
    STRENGTH_EXALTED
} from '../../constants';

import {
    getHouseOwnerFromPlanetPositions,
    getStrongerPlanetFromPositions,
    getPlanetToHouseDict
} from '../../horoscope/house';

import { getDivisionalChart, PlanetPosition } from '../../horoscope/charts';
import { getPlanetLongitude } from '../../panchanga/drik';
import { type Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

// Count Rasis inclusive
const countRasis = (fromHouse: number, toHouse: number): number => {
  return (toHouse - fromHouse + 12) % 12 + 1;
};

// ============================================================================
// DURATION FUNCTIONS
// ============================================================================

/**
 * Calculate duration of Chara Dasha for a sign (KN Rao Method)
 * Also used by Yogardha as chara component.
 */
export const getCharaDhasaDuration = (
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>,
  sign: number
): number => {
    const lordOfSign = getHouseOwnerFromPlanetPositions(planetPositions, sign, false);
    const pToH = getPlanetToHouseDict(planetPositions);
    const houseOfLord = pToH[lordOfSign];

    if (houseOfLord === undefined) return 12;

    let dhasaPeriod = 0;

    if (EVEN_FOOTED_SIGNS.includes(sign)) {
        dhasaPeriod = countRasis(houseOfLord, sign);
    } else {
        dhasaPeriod = countRasis(sign, houseOfLord);
    }

    dhasaPeriod -= 1;

    if (dhasaPeriod <= 0) {
        dhasaPeriod = 12;
    }

    const strength = HOUSE_STRENGTHS_OF_PLANETS[lordOfSign]?.[houseOfLord];
    if (strength === STRENGTH_EXALTED) {
        dhasaPeriod += 1;
    } else if (strength === STRENGTH_DEBILITATED) {
        dhasaPeriod -= 1;
    }

    return dhasaPeriod;
};

// ============================================================================
// PROGRESSION FUNCTIONS
// ============================================================================

/**
 * KN Rao progression: from ascendant, direction based on 9th house footedness
 */
export const getCharaDhasaProgression = (ascendantRasi: number): number[] => {
    const seedHouse = ascendantRasi;
    const ninthHouse = (seedHouse + 8) % 12;

    if (EVEN_FOOTED_SIGNS.includes(ninthHouse)) {
        return Array.from({ length: 12 }, (_, h) => (seedHouse + 12 - h) % 12);
    } else {
        return Array.from({ length: 12 }, (_, h) => (seedHouse + h) % 12);
    }
};

/**
 * PVN Rao progression (Python default):
 * Takes Sun, Moon, Asc houses - finds strongest lord among them.
 * Seed = house of strongest lord. Direction based on 9th house footedness.
 */
function getPvnRaoProgression(
    planetPositions: Array<{ planet: number; rasi: number; longitude: number }>
): number[] {
    // Sun=0, Moon=1 in planet indices; Asc uses planetPositions[0] (Sun as proxy)
    const sunHouse = planetPositions.find(p => p.planet === 0)?.rasi ?? 0;
    const ascHouse = sunHouse; // Using Sun as Lagna proxy
    const moonHouse = planetPositions.find(p => p.planet === 1)?.rasi ?? 0;

    const sunHouseLord = getHouseOwnerFromPlanetPositions(planetPositions, sunHouse, false);
    const ascHouseLord = getHouseOwnerFromPlanetPositions(planetPositions, ascHouse, false);
    const moonHouseLord = getHouseOwnerFromPlanetPositions(planetPositions, moonHouse, false);

    // Find strongest lord among asc, sun, moon house lords
    const sh = getStrongerPlanetFromPositions(planetPositions, sunHouseLord, ascHouseLord);
    let seedHouse = sh === ascHouseLord ? ascHouse : sunHouse;

    const strongerLord = getStrongerPlanetFromPositions(planetPositions, sh, moonHouseLord);
    if (moonHouseLord === strongerLord) {
        seedHouse = moonHouse;
    }

    const ninthHouse = (seedHouse + 8) % 12;
    if (EVEN_FOOTED_SIGNS.includes(ninthHouse)) {
        return Array.from({ length: 12 }, (_, h) => (seedHouse + 12 - h) % 12);
    } else {
        return Array.from({ length: 12 }, (_, h) => (seedHouse + h) % 12);
    }
}

/**
 * Antardhasa: rotate dasha progression list by 1 (KN Rao method)
 * Python: _antardhasas = dhasas[1:]+[dhasas[0]]
 */
export function getCharaAntardhasa(dhasaProgression: number[]): number[] {
    if (dhasaProgression.length <= 1) return [...dhasaProgression];
    return [...dhasaProgression.slice(1), dhasaProgression[0]!];
}

// ============================================================================
// HELPERS
// ============================================================================

function getPositions(jd: number, place: Place, divFactor: number = 1): PlanetPosition[] {
    const d1: PlanetPosition[] = [];
    for (let i = 0; i <= 8; i++) {
        const l = getPlanetLongitude(jd, place, i);
        d1.push({ planet: i, rasi: Math.floor(l / 30), longitude: l % 30 });
    }
    if (divFactor > 1) return getDivisionalChart(d1, divFactor);
    return d1;
}

function formatJdAsDate(jd: number): string {
    const { date, time } = julianDayToGregorian(jd);
    const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
    const hour12 = time.hour % 12 || 12;
    const ampm = time.hour < 12 ? 'AM' : 'PM';
    const yearStr = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
    return `${yearStr}-${pad(date.month)}-${pad(date.day)} ${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

// Keep legacy function for backward compatibility
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

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Chara Dasha periods (PVN Rao method by default, matching Python)
 *
 * chara_method=1 (default): PVN Rao progression, KN Rao duration, 2 cycles
 * chara_method=2: KN Rao single cycle
 */
export function getCharaDashaBhukti(
    jd: number,
    place: Place,
    options: {
        divisionalChartFactor?: number;
        includeBhuktis?: boolean;
        charaMethod?: number;
    } = {}
): { mahadashas: any[]; bhuktis?: any[] } {
    const {
        divisionalChartFactor = 1,
        includeBhuktis = true,
        charaMethod = 1
    } = options;

    const positions = getPositions(jd, place, divisionalChartFactor);

    // PVN Rao progression is always used (matching Python line 235)
    const dhasaProgression = getPvnRaoProgression(positions);

    const dhasaCycles = charaMethod === 2 ? 1 : 2;

    const mahadashas: any[] = [];
    const bhuktis: any[] = [];
    let startJd = jd;
    const firstCycleDurations: number[] = [];

    for (let dc = 0; dc < dhasaCycles; dc++) {
        for (let i = 0; i < dhasaProgression.length; i++) {
            const lord = dhasaProgression[i]!;

            let dd: number;
            if (dc === 0) {
                dd = getCharaDhasaDuration(positions, lord);
                firstCycleDurations.push(dd);
            } else {
                // Second cycle: 12 - first cycle duration
                dd = 12.0 - (firstCycleDurations[i] ?? 0);
            }

            const rasiName = RASI_NAMES_EN[lord] ?? `Rasi ${lord}`;
            mahadashas.push({
                rasi: lord,
                rasiName,
                startJd,
                startDate: formatJdAsDate(startJd),
                durationYears: dd
            });

            if (includeBhuktis) {
                const bhuktiLords = getCharaAntardhasa(dhasaProgression);
                const ddb = dd / 12;
                let bhuktiStartJd = startJd;

                for (const bhukthi of bhuktiLords) {
                    bhuktis.push({
                        dashaRasi: lord,
                        bhuktiRasi: bhukthi,
                        bhuktiRasiName: RASI_NAMES_EN[bhukthi] ?? `Rasi ${bhukthi}`,
                        startJd: bhuktiStartJd,
                        startDate: formatJdAsDate(bhuktiStartJd),
                        durationYears: ddb
                    });
                    bhuktiStartJd += ddb * YEAR_DURATION;
                }
            }

            startJd += dd * YEAR_DURATION;
        }
    }

    return includeBhuktis ? { mahadashas, bhuktis } : { mahadashas };
}
