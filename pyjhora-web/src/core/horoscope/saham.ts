/**
 * Saham (Arabic Parts) calculations
 * Port of Python jhora/horoscope/transit/saham.py
 *
 * Each saham follows formula: A - B + C
 * If C is not between B and A zodiacally, add 30 degrees.
 * For night births, most sahams swap A and B.
 */

import {
    SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN,
} from '../constants';
import { getHouseOwnerFromPlanetPositions } from './house';

// Minimal planet position type for saham calculations
type SahamPlanetPos = { planet: number; rasi: number; longitude: number };

// ============================================================================
// HELPERS
// ============================================================================

/** Get absolute longitude for a planet from positions array */
const getPlanetLong = (positions: SahamPlanetPos[], planet: number): number => {
    const pos = positions.find(p => p.planet === planet);
    if (!pos) throw new Error(`Planet ${planet} not found in positions`);
    return pos.longitude;
};

/**
 * Check if C's rasi lies zodiacally between B and A.
 * Iterates from B's rasi forward; if C is found before A, returns true.
 */
const isCBetweenBToA = (aLong: number, bLong: number, cLong: number): boolean => {
    const aRasi = Math.floor(aLong / 30);
    const bRasi = Math.floor(bLong / 30);
    const cRasi = Math.floor(cLong / 30);
    for (let n = bRasi; n < bRasi + 11; n++) {
        const nextN = (n + 1) % 12;
        if (nextN === cRasi) return true;
        if (nextN === aRasi) break;
    }
    return false;
};

/**
 * Common saham calculation: A - B + C with zodiacal check.
 * If nightTimeBirth, swaps A and B.
 */
const computeSaham = (
    aLong: number, bLong: number, cLong: number,
    nightTimeBirth: boolean
): number => {
    let result: number;
    if (nightTimeBirth) {
        result = bLong - aLong + cLong;
        if (!isCBetweenBToA(bLong, aLong, cLong)) result += 30;
    } else {
        result = aLong - bLong + cLong;
        if (!isCBetweenBToA(aLong, bLong, cLong)) result += 30;
    }
    return ((result % 360) + 360) % 360;
};

/**
 * Same-day-and-night saham (no swap): A - B + C
 */
const computeSahamNoSwap = (
    aLong: number, bLong: number, cLong: number
): number => {
    let result = aLong - bLong + cLong;
    if (!isCBetweenBToA(aLong, bLong, cLong)) result += 30;
    return ((result % 360) + 360) % 360;
};

// ============================================================================
// SAHAM FUNCTIONS
// ============================================================================

/** 1. Punya (Fortune) - Moon - Sun + Lagna */
export const punyaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, MOON), getPlanetLong(positions, SUN), lagnaLong, nightTimeBirth
);

/** 2. Vidya (Education) - Sun - Moon + Lagna */
export const vidyaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, SUN), getPlanetLong(positions, MOON), lagnaLong, nightTimeBirth
);

/** 3. Yasas (Fame) - Jupiter - PunyaSaham + Lagna */
export const yasasSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, JUPITER),
    punyaSaham(positions, lagnaLong, nightTimeBirth),
    lagnaLong, nightTimeBirth
);

/** 4. Mitra (Friend) - Jupiter - PunyaSaham + Venus */
export const mitraSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, JUPITER),
    punyaSaham(positions, lagnaLong, nightTimeBirth),
    getPlanetLong(positions, VENUS), nightTimeBirth
);

/** 5. Mahatmya (Greatness) - PunyaSaham - Mars + Lagna */
export const mahatmyaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    punyaSaham(positions, lagnaLong, nightTimeBirth),
    getPlanetLong(positions, MARS),
    lagnaLong, nightTimeBirth
);

/** 6. Asha (Desires) - Saturn - Mars + Lagna */
export const ashaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, SATURN), getPlanetLong(positions, MARS), lagnaLong, nightTimeBirth
);

/** 7. Samartha (Enterprise) - Mars - LagnaLord + Lagna
 *  If Mars owns lagna, use Jupiter as LagnaLord and flip night_time_birth */
export const samarthaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, lagnaRasi: number, nightTimeBirth = false
): number => {
    let lagnaLord = getHouseOwnerFromPlanetPositions(positions, lagnaRasi);
    let effectiveNight = nightTimeBirth;
    if (lagnaLord === MARS) {
        lagnaLord = JUPITER;
        effectiveNight = !effectiveNight;
    }
    const lagnaLordLong = getPlanetLong(positions, lagnaLord);
    return computeSaham(
        getPlanetLong(positions, MARS), lagnaLordLong, lagnaLong, effectiveNight
    );
};

/** 8. Bhratri (Brothers) - Jupiter - Saturn + Lagna (same day/night) */
export const bhratriSaham = (
    positions: SahamPlanetPos[], lagnaLong: number
): number => computeSahamNoSwap(
    getPlanetLong(positions, JUPITER), getPlanetLong(positions, SATURN), lagnaLong
);

/** 9. Gaurava (Respect) - Jupiter - Moon + Sun */
export const gauravaSaham = (
    positions: SahamPlanetPos[], nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, JUPITER), getPlanetLong(positions, MOON),
    getPlanetLong(positions, SUN), nightTimeBirth
);

/** 10. Pithri (Father) - Saturn - Sun + Lagna */
export const pithriSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, SATURN), getPlanetLong(positions, SUN), lagnaLong, nightTimeBirth
);

/** 11. Rajya (Kingdom) - same as Pithri */
export const rajyaSaham = pithriSaham;

/** 12. Maathri (Mother) - Moon - Venus + Lagna */
export const maathriSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, MOON), getPlanetLong(positions, VENUS), lagnaLong, nightTimeBirth
);

/** 13. Puthra (Children) - Jupiter - Moon + Lagna */
export const puthraSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, JUPITER), getPlanetLong(positions, MOON), lagnaLong, nightTimeBirth
);

/** 14. Jeeva (Life) - Saturn - Jupiter + Lagna */
export const jeevaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, SATURN), getPlanetLong(positions, JUPITER), lagnaLong, nightTimeBirth
);

/** 15. Karma (Action) - Mars - Mercury + Lagna */
export const karmaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, MARS), getPlanetLong(positions, MERCURY), lagnaLong, nightTimeBirth
);

/** 16. Roga (Disease) - Lagna - Moon + Lagna (same day/night, no between check) */
export const rogaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number
): number => {
    const moonLong = getPlanetLong(positions, MOON);
    return ((lagnaLong - moonLong + lagnaLong) % 360 + 360) % 360;
};

/** 16a. Roga alternate - Saturn - Moon + Lagna */
export const rogaSaham1 = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, SATURN), getPlanetLong(positions, MOON), lagnaLong, nightTimeBirth
);

/** 17. Kali (Great misfortune) - Jupiter - Mars + Lagna */
export const kaliSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, JUPITER), getPlanetLong(positions, MARS), lagnaLong, nightTimeBirth
);

/** 18. Sastra (Sciences) - Jupiter - Saturn + Mercury */
export const sastraSaham = (
    positions: SahamPlanetPos[], nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, JUPITER), getPlanetLong(positions, SATURN),
    getPlanetLong(positions, MERCURY), nightTimeBirth
);

/** 19. Bandhu (Relatives) - Mercury - Moon + Lagna */
export const bandhuSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, MERCURY), getPlanetLong(positions, MOON), lagnaLong, nightTimeBirth
);

/** 20. Mrithyu (Death) - 8th house - Moon + Lagna (same day/night) */
export const mrithyuSaham = (
    positions: SahamPlanetPos[], lagnaLong: number
): number => {
    const eighthHouseLong = lagnaLong + 210; // (8-1)*30
    return computeSahamNoSwap(
        eighthHouseLong, getPlanetLong(positions, MOON), lagnaLong
    );
};

/** 21. Paradesa (Foreign countries) - 9th house - 9th lord + Lagna */
export const paradesaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, lagnaRasi: number
): number => {
    const ninthHouse = (lagnaRasi + 8) % 12;
    const ninthLord = getHouseOwnerFromPlanetPositions(positions, ninthHouse);
    const longNinthHouse = lagnaLong + 240; // (9-1)*30
    const longNinthLord = getPlanetLong(positions, ninthLord);
    return computeSahamNoSwap(longNinthHouse, longNinthLord, lagnaLong);
};

/** 22. Artha (Money) - 2nd house - 2nd lord + Lagna */
export const arthaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, lagnaRasi: number
): number => {
    const secondHouse = (lagnaRasi + 1) % 12;
    const secondLord = getHouseOwnerFromPlanetPositions(positions, secondHouse);
    const longSecondHouse = lagnaLong + 30;
    const longSecondLord = getPlanetLong(positions, secondLord);
    return computeSahamNoSwap(longSecondHouse, longSecondLord, lagnaLong);
};

/** 23. Paradara (Adultery) - Venus - Sun + Lagna */
export const paradaraSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, VENUS), getPlanetLong(positions, SUN), lagnaLong, nightTimeBirth
);

/** 24. Vanika (Commerce) - Moon - Mercury + Lagna */
export const vanikaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, MOON), getPlanetLong(positions, MERCURY), lagnaLong, nightTimeBirth
);

/** 25. Karyasiddhi (Success) - Saturn - Sun + Lord(SunSign); Night: Saturn - Moon + Lord(MoonSign) */
export const karyasiddhiSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => {
    const saturnLong = getPlanetLong(positions, SATURN);
    if (nightTimeBirth) {
        const moonLong = getPlanetLong(positions, MOON);
        const moonRasi = Math.floor(moonLong / 30);
        const lordOfMoonSign = getHouseOwnerFromPlanetPositions(positions, moonRasi);
        const signLong = getPlanetLong(positions, lordOfMoonSign);
        let result = saturnLong - moonLong + signLong;
        if (!isCBetweenBToA(saturnLong, moonLong, signLong)) result += 30;
        return ((result % 360) + 360) % 360;
    }
    const sunLong = getPlanetLong(positions, SUN);
    const sunRasi = Math.floor(sunLong / 30);
    const lordOfSunSign = getHouseOwnerFromPlanetPositions(positions, sunRasi);
    const signLong = getPlanetLong(positions, lordOfSunSign);
    let result = saturnLong - sunLong + signLong;
    if (!isCBetweenBToA(saturnLong, sunLong, signLong)) result += 30;
    return ((result % 360) + 360) % 360;
};

/** 26. Vivaha (Marriage) - Venus - Saturn + Lagna */
export const vivahaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, VENUS), getPlanetLong(positions, SATURN), lagnaLong, nightTimeBirth
);

/** 27. Santapa (Sadness) - Saturn - Moon + 6th house */
export const santapaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => {
    const sixthHouseLong = lagnaLong + 150; // (6-1)*30
    return computeSaham(
        getPlanetLong(positions, SATURN), getPlanetLong(positions, MOON),
        sixthHouseLong, nightTimeBirth
    );
};

/** 28. Sraddha (Devotion) - Venus - Mars + Lagna */
export const sraddhaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, VENUS), getPlanetLong(positions, MARS), lagnaLong, nightTimeBirth
);

/** 29. Preethi (Love) - SastraSaham - PunyaSaham + Lagna */
export const preethiSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    sastraSaham(positions, nightTimeBirth),
    punyaSaham(positions, lagnaLong, nightTimeBirth),
    lagnaLong, nightTimeBirth
);

/** 30. Jadya (Chronic disease) - Mars - Saturn + Mercury
 *  Note: Python has a subtle bug where %360 is inside the night block only.
 *  We replicate this behavior for parity. */
export const jadyaSaham = (
    positions: SahamPlanetPos[], nightTimeBirth = false
): number => {
    const marsLong = getPlanetLong(positions, MARS);
    const saturnLong = getPlanetLong(positions, SATURN);
    const mercuryLong = getPlanetLong(positions, MERCURY);
    let result = marsLong - saturnLong + mercuryLong;
    if (!isCBetweenBToA(marsLong, saturnLong, mercuryLong)) result += 30;
    if (nightTimeBirth) {
        result = saturnLong - marsLong + mercuryLong;
        if (!isCBetweenBToA(saturnLong, marsLong, mercuryLong)) result += 30;
        result = ((result % 360) + 360) % 360;
    }
    return result;
};

/** 31. Vyaapaara (Business) - Mars - Saturn + Lagna (same day/night) */
export const vyaapaaraSaham = (
    positions: SahamPlanetPos[], lagnaLong: number
): number => computeSahamNoSwap(
    getPlanetLong(positions, MARS), getPlanetLong(positions, SATURN), lagnaLong
);

/** 32. Sathru (Enemy) - Mars - Saturn + Lagna */
export const sathruSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    getPlanetLong(positions, MARS), getPlanetLong(positions, SATURN), lagnaLong, nightTimeBirth
);

/** 33. Jalapatna (Ocean crossing) - Cancer 15 deg - Saturn + Lagna */
export const jalapatnaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    105.0, // Cancer 15 degrees = 3*30 + 15
    getPlanetLong(positions, SATURN), lagnaLong, nightTimeBirth
);

/** 34. Bandhana (Imprisonment) - PunyaSaham - Saturn + Lagna */
export const bandhanaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    punyaSaham(positions, lagnaLong, nightTimeBirth),
    getPlanetLong(positions, SATURN),
    lagnaLong, nightTimeBirth
);

/** 35. Apamrithyu (Bad death) - 8th house - Mars + Lagna */
export const apamrithyuSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, nightTimeBirth = false
): number => computeSaham(
    lagnaLong + 210, // 8th house
    getPlanetLong(positions, MARS), lagnaLong, nightTimeBirth
);

/** 36. Laabha (Material gains) - 11th house - 11th lord + Lagna */
export const laabhaSaham = (
    positions: SahamPlanetPos[], lagnaLong: number, lagnaRasi: number,
    nightTimeBirth = false
): number => {
    const eleventhHouse = (lagnaRasi + 10) % 12;
    const eleventhLord = getHouseOwnerFromPlanetPositions(positions, eleventhHouse);
    const longEleventhHouse = lagnaLong + 300; // (11-1)*30
    const longEleventhLord = getPlanetLong(positions, eleventhLord);
    if (nightTimeBirth) {
        let result = longEleventhLord - longEleventhHouse + lagnaLong;
        if (!isCBetweenBToA(longEleventhLord, longEleventhHouse, lagnaLong)) result += 30;
        return ((result % 360) + 360) % 360;
    }
    let result = longEleventhHouse - longEleventhLord + lagnaLong;
    if (!isCBetweenBToA(longEleventhHouse, longEleventhLord, lagnaLong)) result += 30;
    return ((result % 360) + 360) % 360;
};

// Re-export helper for testing
export { isCBetweenBToA };
