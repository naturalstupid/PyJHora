/**
 * Core constants ported from PyJHora const.py
 * Contains all astrological constants, planet IDs, rasi names, etc.
 */

// ============================================================================
// PLANET IDENTIFIERS
// ============================================================================

/** Planet indices matching Swiss Ephemeris */
export const SUN = 0;
export const MOON = 1;
export const MARS = 2;
export const MERCURY = 3;
export const JUPITER = 4;
export const VENUS = 5;
export const SATURN = 6;
export const RAHU = 7;
export const KETU = 8;
export const URANUS = 9;
export const NEPTUNE = 10;
export const PLUTO = 11;

/** Aliases for convenience */
export const SURYA = SUN;
export const CHANDRA = MOON;
export const MANGAL = MARS;
export const BUDHA = MERCURY;
export const GURU = JUPITER;
export const SUKRA = VENUS;
export const SANI = SATURN;

/** Planet ranges */
export const SUN_TO_SATURN = [0, 1, 2, 3, 4, 5, 6];
export const SUN_TO_KETU = [0, 1, 2, 3, 4, 5, 6, 7, 8];
export const PLANETS_EXCEPT_NODES = [0, 1, 2, 3, 4, 5, 6];
export const OUTER_PLANETS = [9, 10, 11];
export const ALL_PLANETS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];

export const PLANET_NAMES_EN = [
  'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu',
  'Uranus', 'Neptune', 'Pluto'
];

export const PLANET_NAMES_SA = [
  'Surya', 'Chandra', 'Mangal', 'Budha', 'Guru', 'Sukra', 'Sani', 'Rahu', 'Ketu',
  'Uranus', 'Neptune', 'Pluto'
];

// ============================================================================
// RASI (ZODIAC SIGN) CONSTANTS
// ============================================================================

export const ARIES = 0;
export const TAURUS = 1;
export const GEMINI = 2;
export const CANCER = 3;
export const LEO = 4;
export const VIRGO = 5;
export const LIBRA = 6;
export const SCORPIO = 7;
export const SAGITTARIUS = 8;
export const CAPRICORN = 9;
export const AQUARIUS = 10;
export const PISCES = 11;

export const RASI_NAMES_EN = [
  'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
  'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
];

export const RASI_NAMES_SA = [
  'Mesha', 'Vrishabha', 'Mithuna', 'Karka', 'Simha', 'Kanya',
  'Tula', 'Vrischika', 'Dhanu', 'Makara', 'Kumbha', 'Meena'
];

/** Sign classifications */
export const ODD_SIGNS = [0, 2, 4, 6, 8, 10];
export const EVEN_SIGNS = [1, 3, 5, 7, 9, 11];
export const MOVABLE_SIGNS = [0, 3, 6, 9];
export const FIXED_SIGNS = [1, 4, 7, 10];
export const DUAL_SIGNS = [2, 5, 8, 11];
export const FIRE_SIGNS = [0, 4, 8];
export const EARTH_SIGNS = [1, 5, 9];
export const AIR_SIGNS = [2, 6, 10];
export const WATER_SIGNS = [3, 7, 11];

/** Footedness for Dasha counting (Samapada/Vishamapada) */
export const ODD_FOOTED_SIGNS = [0, 1, 2, 6, 7, 8]; // Aries, Taurus, Gemini, Libra, Scorpio, Sagittarius
export const EVEN_FOOTED_SIGNS = [3, 4, 5, 9, 10, 11]; // Cancer, Leo, Virgo, Capricorn, Aquarius, Pisces

/** Sign lords (rulers) */
export const SIGN_LORDS = [MARS, VENUS, MERCURY, MOON, SUN, MERCURY, VENUS, MARS, JUPITER, SATURN, SATURN, JUPITER];

// ============================================================================
// HOUSE CONSTANTS
// ============================================================================

export const HOUSE_1 = 0;
export const HOUSE_2 = 1;
export const HOUSE_3 = 2;
export const HOUSE_4 = 3;
export const HOUSE_5 = 4;
export const HOUSE_6 = 5;
export const HOUSE_7 = 6;
export const HOUSE_8 = 7;
export const HOUSE_9 = 8;
export const HOUSE_10 = 9;
export const HOUSE_11 = 10;
export const HOUSE_12 = 11;

export const KENDRA_HOUSES = [0, 3, 6, 9]; // 1, 4, 7, 10
export const TRIKONA_HOUSES = [0, 4, 8]; // 1, 5, 9
export const DUSTHANA_HOUSES = [5, 7, 11]; // 6, 8, 12
export const UPACHAYA_HOUSES = [2, 5, 9, 10]; // 3, 6, 10, 11
export const MARAKA_HOUSES = [1, 6]; // 2, 7

// ============================================================================
// NAKSHATRA CONSTANTS
// ============================================================================

export const NAKSHATRA_NAMES_EN = [
  'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
  'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
  'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
  'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
  'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
];

/** Nakshatra span in degrees */
export const NAKSHATRA_SPAN = 360 / 27; // 13.333... degrees

/** Nakshatra lords for Vimsottari dasha */
export const VIMSOTTARI_LORDS = [KETU, VENUS, SUN, MOON, MARS, RAHU, JUPITER, SATURN, MERCURY];

/** Vimsottari dasha durations in years */
export const VIMSOTTARI_YEARS: Record<number, number> = {
  [KETU]: 7,
  [VENUS]: 20,
  [SUN]: 6,
  [MOON]: 10,
  [MARS]: 7,
  [RAHU]: 18,
  [JUPITER]: 16,
  [SATURN]: 19,
  [MERCURY]: 17
};

/** Total Vimsottari cycle */
export const VIMSOTTARI_TOTAL_YEARS = 120;

// ============================================================================
// AYANAMSA MODES
// ============================================================================

export const AYANAMSA_MODES = {
  LAHIRI: 1,
  RAMAN: 3,
  KRISHNAMURTI: 5,
  KP: 5,                 // Alias for KRISHNAMURTI (Python: available_ayanamsa_modes)
  FAGAN_BRADLEY: 0,
  FAGAN: 0,              // Alias for FAGAN_BRADLEY (Python: available_ayanamsa_modes)
  TRUE_CITRA: 27,
  TRUE_LAHIRI: 27,       // Alias for TRUE_CITRA (Python: available_ayanamsa_modes)
  TRUE_REVATI: 28,
  TRUE_PUSHYA: 29,
  TRUE_MULA: 47,
  YUKTESHWAR: 7,
  USHASHASHI: 4,
  JN_BHASIN: 8,
  ARYABHATA: 17,
  ARYABHATA_MSUN: 18,
  SURYASIDDHANTA: 21,
  SURYASIDDHANTA_MSUN: 22,
  SS_CITRA: 26,
  SS_REVATI: 30,
  KP_SENTHIL: 39,        // Python: KP-SENTHIL → SIDM_KRISHNAMURTI_VP291
  SIDM_USER: 255,
  SASSANIAN: 16,
  GALACTIC_CENTER: 17,
  USER_DEFINED: 255
} as const;

export const DEFAULT_AYANAMSA_MODE = 'LAHIRI';

// ============================================================================
// ASPECT CONSTANTS
// ============================================================================

/** Houses causing Argala (Intervention) */
export const ARGALA_HOUSES = [2, 4, 5, 11];
export const VIRODHARGALA_HOUSES = [12, 10, 9, 3];

/** Full aspects (100% drishti) */
export const GRAHA_DRISHTI: Record<number, number[]> = {
  [SUN]: [6], // 7th house aspect
  [MOON]: [6],
  [MARS]: [3, 6, 7], // 4th, 7th, 8th
  [MERCURY]: [6],
  [JUPITER]: [4, 6, 8], // 5th, 7th, 9th
  [VENUS]: [6],
  [SATURN]: [2, 6, 9] // 3rd, 7th, 10th
};

// ============================================================================
// BENEFIC/MALEFIC CLASSIFICATION
// ============================================================================

export const NATURAL_BENEFICS = [JUPITER, VENUS];
export const NATURAL_MALEFICS = [SUN, MARS, SATURN, RAHU, KETU];
// Mercury and Moon are conditional benefics

// ============================================================================
// KARAKA (SIGNIFICATOR) CONSTANTS
// ============================================================================

/** Sthira (fixed) karakas */
export const STHIRA_KARAKAS: Record<string, number> = {
  ATMA: SUN,
  MANA: MOON,
  BHRATRA: MARS,
  VIDYA: MERCURY,
  PUTRA: JUPITER,
  KALATRA: VENUS,
  AYUSH: SATURN
};

// ============================================================================
// TIMING CONSTANTS
// ============================================================================

export const AVERAGE_GREGORIAN_YEAR = 365.2425;
export const TROPICAL_YEAR = 365.242190;
export const SIDEREAL_YEAR = 365.256364;
export const SYNODIC_MONTH = 29.530589;
export const SIDEREAL_MONTH = 27.321661;

/** Julian day of the Mahabharata epoch (Kali Yuga start) */
export const MAHABHARATHA_TITHI_JULIAN_DAY = 588465.5;

/** Julian day of J2000.0 epoch */
export const J2000 = 2451545.0;

// ============================================================================
// TITHI CONSTANTS
// ============================================================================

export const TITHI_NAMES_EN = [
  'Pratipada', 'Dwitiya', 'Tritiya', 'Chaturthi', 'Panchami',
  'Shashthi', 'Saptami', 'Ashtami', 'Navami', 'Dashami',
  'Ekadashi', 'Dwadashi', 'Trayodashi', 'Chaturdashi', 'Purnima',
  'Pratipada', 'Dwitiya', 'Tritiya', 'Chaturthi', 'Panchami',
  'Shashthi', 'Saptami', 'Ashtami', 'Navami', 'Dashami',
  'Ekadashi', 'Dwadashi', 'Trayodashi', 'Chaturdashi', 'Amavasya'
];

export const TITHI_SPAN = 12; // degrees between Sun and Moon for each tithi

// ============================================================================
// YOGA (PANCHANGA) CONSTANTS
// ============================================================================

export const YOGA_NAMES_EN = [
  'Vishkumbha', 'Priti', 'Ayushman', 'Saubhagya', 'Shobhana',
  'Atiganda', 'Sukarman', 'Dhriti', 'Shula', 'Ganda',
  'Vriddhi', 'Dhruva', 'Vyaghata', 'Harshana', 'Vajra',
  'Siddhi', 'Vyatipata', 'Variyan', 'Parigha', 'Shiva',
  'Siddha', 'Sadhya', 'Shubha', 'Shukla', 'Brahma',
  'Indra', 'Vaidhriti'
];

export const YOGA_SPAN = 360 / 27; // 13.333... degrees

// ============================================================================
// KARANA CONSTANTS
// ============================================================================

export const KARANA_NAMES_EN = [
  'Kimstughna', 'Bava', 'Balava', 'Kaulava', 'Taitila',
  'Garija', 'Vanija', 'Vishti', 'Shakuni', 'Chatushpada',
  'Naga'
];

// ============================================================================
// DIVISIONAL CHART FACTORS
// ============================================================================

export const DIVISIONAL_CHART_FACTORS = [
  1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 20, 24, 27, 30, 40, 45, 60, 81, 108, 144
];

export const VARGA_NAMES: Record<number, string> = {
  1: 'Rasi (D-1)',
  2: 'Hora (D-2)',
  3: 'Drekkana (D-3)',
  4: 'Chaturthamsa (D-4)',
  5: 'Panchamsa (D-5)',
  6: 'Shashthamsa (D-6)',
  7: 'Saptamsa (D-7)',
  8: 'Ashtamsa (D-8)',
  9: 'Navamsa (D-9)',
  10: 'Dasamsa (D-10)',
  11: 'Rudramsa (D-11)',
  12: 'Dwadasamsa (D-12)',
  16: 'Shodasamsa (D-16)',
  20: 'Vimsamsa (D-20)',
  24: 'Chaturvimsamsa (D-24)',
  27: 'Bhamsa (D-27)',
  30: 'Trimsamsa (D-30)',
  40: 'Khavedamsa (D-40)',
  45: 'Akshavedamsa (D-45)',
  60: 'Shashtiamsa (D-60)'
};

// ============================================================================
// ASCENDANT SYMBOL
// ============================================================================

export const ASCENDANT_SYMBOL = 'L';

// ============================================================================
// CALCULATION PRECISION
// ============================================================================


// ============================================================================
// NARAYANA DHASA PROGRESSIONS
// ============================================================================

export const NARAYANA_DHASA_NORMAL_PROGRESSION = [
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
  [1, 8, 3, 10, 5, 0, 7, 2, 9, 4, 11, 6],
  [2, 10, 6, 5, 1, 9, 8, 4, 0, 11, 7, 3],
  [3, 2, 1, 0, 11, 10, 9, 8, 7, 6, 5, 4],
  [4, 9, 2, 7, 0, 5, 10, 3, 8, 1, 6, 11],
  [5, 9, 1, 2, 6, 10, 11, 3, 7, 8, 0, 4],
  [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5],
  [7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5, 0],
  [8, 4, 0, 11, 7, 3, 2, 10, 6, 5, 1, 9],
  [9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10],
  [10, 3, 8, 1, 6, 11, 4, 9, 2, 7, 0, 5],
  [11, 3, 7, 8, 0, 4, 5, 9, 1, 2, 6, 10]
];

export const NARAYANA_DHASA_SATURN_EXCEPTION_PROGRESSION = [
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0],
  [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1],
  [3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2],
  [4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3],
  [5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4],
  [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5],
  [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6],
  [8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7],
  [9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8],
  [10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
  [11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
];

export const NARAYANA_DHASA_KETU_EXCEPTION_PROGRESSION = [
  [0, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
  [1, 6, 11, 4, 9, 2, 7, 0, 5, 10, 3, 8],
  [2, 6, 10, 11, 3, 7, 8, 0, 4, 5, 9, 1],
  [3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2],
  [4, 11, 6, 1, 8, 3, 10, 5, 0, 7, 2, 9],
  [5, 1, 9, 8, 4, 0, 11, 7, 3, 2, 10, 6],
  [6, 5, 4, 3, 2, 1, 0, 11, 10, 9, 8, 7],
  [7, 0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2],
  [8, 0, 4, 5, 9, 1, 2, 6, 10, 11, 3, 7],
  [9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8],
  [10, 5, 0, 7, 2, 9, 4, 11, 6, 1, 8, 3],
  [11, 7, 3, 2, 10, 6, 5, 1, 9, 8, 4, 0]
];

// ============================================================================
// PLANET STRENGTHS (FRIENDSHIP TABLE)
// ============================================================================

// Columns: Aries to Pisces. Rows: Sun(0) to Ketu(8)
// 4=Exalted, 1=Enemy, 2=Neutral, 3=Friend, 5=Own, 0=Debilitated
export const HOUSE_STRENGTHS_OF_PLANETS = [
  [4, 1, 2, 2, 5, 2, 0, 3, 3, 1, 1, 3], // 0 Sun
  [2, 4, 3, 5, 3, 3, 2, 0, 2, 2, 2, 2], // 1 Moon
  [5, 2, 1, 0, 3, 1, 2, 5, 3, 4, 2, 3], // 2 Mars
  [2, 3, 5, 1, 3, 5, 3, 2, 2, 2, 2, 0], // 3 Mercury
  [3, 1, 1, 4, 3, 3, 1, 3, 5, 0, 2, 5], // 4 Jupiter
  [2, 5, 3, 1, 1, 0, 5, 2, 3, 3, 3, 4], // 5 Venus
  [0, 3, 3, 1, 1, 3, 4, 1, 2, 5, 5, 2], // 6 Saturn
  [1, 4, 4, 1, 1, 3, 3, 0, 0, 3, 1, 3], // 7 Rahu (Exalted 1,2 | Debilitated 7,8)
  [1, 0, 0, 1, 1, 3, 3, 4, 4, 3, 1, 3]  // 8 Ketu (Debilitated 1,2 | Exalted 7,8)
];

// Strength Codes
export const STRENGTH_EXALTED = 4;
export const STRENGTH_OWN_SIGN = 5;
export const STRENGTH_FRIEND = 3;
export const STRENGTH_NEUTRAL = 2;
export const STRENGTH_ENEMY = 1;
export const STRENGTH_DEBILITATED = 0;

export const DEFAULT_PRECISION = 10; // Decimal places for comparisons
export const TIME_TOLERANCE_SECONDS = 35; // Tolerance for time comparisons

// ============================================================================
// ASHTAKAVARGA CONSTANTS
// ============================================================================

/**
 * Ashtakavarga benefic houses for each planet
 * Key: Planet index (0=Sun, 1=Moon, ..., 7=Lagna)
 * Value: Array of 8 arrays, each containing house numbers (1-12) where that planet
 *        contributes a benefic point from Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Lagna
 *
 * Example: ASHTAKA_VARGA_DICT[0][0] = [1,2,4,7,8,9,10,11] means:
 *   For Sun's Ashtakavarga, Sun itself contributes benefic points when transiting
 *   houses 1,2,4,7,8,9,10,11 from its natal position.
 */
export const ASHTAKA_VARGA_DICT: Record<number, number[][]> = {
  // Sun's Ashtakavarga
  0: [
    [1, 2, 4, 7, 8, 9, 10, 11],    // From Sun
    [3, 6, 10, 11],                // From Moon
    [1, 2, 4, 7, 8, 9, 10, 11],    // From Mars
    [3, 5, 6, 9, 10, 11, 12],      // From Mercury
    [5, 6, 9, 11],                 // From Jupiter
    [6, 7, 12],                    // From Venus
    [1, 2, 4, 7, 8, 9, 10, 11],    // From Saturn
    [3, 4, 6, 10, 11, 12]          // From Lagna
  ],
  // Moon's Ashtakavarga
  1: [
    [3, 6, 7, 8, 10, 11],          // From Sun
    [1, 3, 6, 7, 9, 10, 11],       // From Moon
    [2, 3, 5, 6, 10, 11],          // From Mars
    [1, 3, 4, 5, 7, 8, 10, 11],    // From Mercury
    [1, 2, 4, 7, 8, 10, 11],       // From Jupiter
    [3, 4, 5, 7, 9, 10, 11],       // From Venus
    [3, 5, 6, 11],                 // From Saturn
    [3, 6, 10, 11]                 // From Lagna
  ],
  // Mars' Ashtakavarga
  2: [
    [3, 5, 6, 10, 11],             // From Sun
    [3, 6, 11],                    // From Moon
    [1, 2, 4, 7, 8, 10, 11],       // From Mars
    [3, 5, 6, 11],                 // From Mercury
    [6, 10, 11, 12],               // From Jupiter
    [6, 8, 11, 12],                // From Venus
    [1, 4, 7, 8, 9, 10, 11],       // From Saturn
    [1, 3, 6, 10, 11]              // From Lagna
  ],
  // Mercury's Ashtakavarga
  3: [
    [5, 6, 9, 11, 12],             // From Sun
    [2, 4, 6, 8, 10, 11],          // From Moon
    [1, 2, 4, 7, 8, 9, 10, 11],    // From Mars
    [1, 3, 5, 6, 9, 10, 11, 12],   // From Mercury
    [6, 8, 11, 12],                // From Jupiter
    [1, 2, 3, 4, 5, 8, 9, 11],     // From Venus
    [1, 2, 4, 7, 8, 9, 10, 11],    // From Saturn
    [1, 2, 4, 6, 8, 10, 11]        // From Lagna
  ],
  // Jupiter's Ashtakavarga
  4: [
    [1, 2, 3, 4, 7, 8, 9, 10, 11], // From Sun
    [2, 5, 7, 9, 11],              // From Moon
    [1, 2, 4, 7, 8, 10, 11],       // From Mars
    [1, 2, 4, 5, 6, 9, 10, 11],    // From Mercury
    [1, 2, 3, 4, 7, 8, 10, 11],    // From Jupiter
    [2, 5, 6, 9, 10, 11],          // From Venus
    [3, 5, 6, 12],                 // From Saturn
    [1, 2, 4, 5, 6, 7, 9, 10, 11]  // From Lagna
  ],
  // Venus' Ashtakavarga
  5: [
    [8, 11, 12],                   // From Sun
    [1, 2, 3, 4, 5, 8, 9, 11, 12], // From Moon
    [3, 4, 6, 9, 11, 12],          // From Mars
    [3, 5, 6, 9, 11],              // From Mercury
    [5, 8, 9, 10, 11],             // From Jupiter
    [1, 2, 3, 4, 5, 8, 9, 10, 11], // From Venus
    [3, 4, 5, 8, 9, 10, 11],       // From Saturn
    [1, 2, 3, 4, 5, 8, 9, 11]      // From Lagna
  ],
  // Saturn's Ashtakavarga
  6: [
    [1, 2, 4, 7, 8, 10, 11],       // From Sun
    [3, 6, 11],                    // From Moon
    [3, 5, 6, 10, 11, 12],         // From Mars
    [6, 8, 9, 10, 11, 12],         // From Mercury
    [5, 6, 11, 12],                // From Jupiter
    [6, 11, 12],                   // From Venus
    [3, 5, 6, 11],                 // From Saturn
    [1, 3, 4, 6, 10, 11]           // From Lagna
  ],
  // Lagna's Ashtakavarga
  7: [
    [3, 4, 6, 10, 11, 12],         // From Sun
    [3, 6, 10, 11, 12],            // From Moon
    [1, 3, 6, 10, 11],             // From Mars
    [1, 2, 4, 6, 8, 10, 11],       // From Mercury
    [1, 2, 4, 5, 6, 7, 9, 10, 11], // From Jupiter
    [1, 2, 3, 4, 5, 8, 9],         // From Venus
    [1, 3, 4, 6, 10, 11],          // From Saturn
    [3, 6, 10, 11]                 // From Lagna
  ]
};

/**
 * Rasimana multipliers for Sodhya Pinda calculation
 * One value per rasi (Aries to Pisces)
 */
export const RASIMANA_MULTIPLIERS = [7, 10, 8, 4, 10, 6, 7, 8, 9, 5, 11, 12];

/**
 * Grahamana multipliers for Sodhya Pinda calculation
 * One value per planet (Sun to Saturn)
 */
export const GRAHAMANA_MULTIPLIERS = [5, 5, 8, 5, 10, 7, 5];

/**
 * Rasi owners for Ekadhipatya Sodhana
 * Index 0-1: Leo (owned by Sun), Cancer (owned by Moon) - single owners
 * Index 2-6: Dual-owned signs - Mars (Aries/Scorpio), Mercury (Gemini/Virgo),
 *            Jupiter (Sagittarius/Pisces), Venus (Taurus/Libra), Saturn (Capricorn/Aquarius)
 */
export const RASI_OWNERS_FOR_EKADHIPATYA: (number | [number, number])[] = [
  LEO,                // Sun's sign (single)
  CANCER,             // Moon's sign (single)
  [ARIES, SCORPIO],   // Mars' signs
  [GEMINI, VIRGO],    // Mercury' signs
  [SAGITTARIUS, PISCES], // Jupiter's signs
  [TAURUS, LIBRA],    // Venus' signs
  [CAPRICORN, AQUARIUS]  // Saturn's signs
];

// ============================================================================
// PLANET SIGN OWNERSHIP (for Arudhas calculation)
// ============================================================================

/**
 * Signs owned by each planet (used for Graha Arudhas)
 * Maps planet ID to array of sign indices they own
 * Note: Mars/Ketu co-own Scorpio, Saturn/Rahu co-own Aquarius
 */
export const PLANET_SIGNS_OWNED: Record<number, number[]> = {
  [SUN]: [LEO],                     // 0: Sun owns Leo (4)
  [MOON]: [CANCER],                 // 1: Moon owns Cancer (3)
  [MARS]: [ARIES, SCORPIO],         // 2: Mars owns Aries (0), Scorpio (7)
  [MERCURY]: [GEMINI, VIRGO],       // 3: Mercury owns Gemini (2), Virgo (5)
  [JUPITER]: [SAGITTARIUS, PISCES], // 4: Jupiter owns Sagittarius (8), Pisces (11)
  [VENUS]: [TAURUS, LIBRA],         // 5: Venus owns Taurus (1), Libra (6)
  [SATURN]: [CAPRICORN, AQUARIUS],  // 6: Saturn owns Capricorn (9), Aquarius (10)
  [RAHU]: [AQUARIUS],               // 7: Rahu owns Aquarius (10)
  [KETU]: [SCORPIO],                // 8: Ketu owns Scorpio (7)
};

/** Number of planet positions including Lagna up to Ketu (Lagna + Sun through Ketu = 10) */
export const PP_COUNT_UPTO_KETU = 10;

// ============================================================================
// VIMSOTTARI DHASA CONSTANTS
// ============================================================================

/** Vimsottari dhasa lord sequence: Ketu, Venus, Sun, Moon, Mars, Jupiter, Saturn, Mercury, Rahu */
export const VIMSOTTARI_ADHIPATI_LIST = [8, 5, 0, 1, 2, 7, 4, 6, 3];

/** Vimsottari dhasa periods in years */
export const VIMSOTTARI_DICT: Record<number, number> = { 8: 7, 5: 20, 0: 6, 1: 10, 2: 7, 7: 18, 4: 16, 6: 19, 3: 17 };

// ============================================================================
// VARSHA (ANNUAL) VIMSOTTARI DHASA CONSTANTS
// ============================================================================

/** Varsha Vimsottari dhasa periods in days (planet → days) */
export const VARSHA_VIMSOTTARI_DAYS: Record<number, number> = {
  0: 18, 1: 30, 2: 21, 7: 54, 4: 48, 6: 57, 3: 51, 8: 21, 5: 60,
};

/** Varsha Vimsottari adhipati list: Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury, Ketu, Venus */
export const VARSHA_VIMSOTTARI_ADHIPATI_LIST = [0, 1, 2, 7, 4, 6, 3, 8, 5];

/** Total cycle for Varsha Vimsottari = 360 days */
export const HUMAN_LIFE_SPAN_VARSHA_VIMSOTTARI = 360;

// ============================================================================
// LONGEVITY (AAYU) CONSTANTS
// ============================================================================

/** Pindayu full longevity of planets in years (Sun to Saturn) */
export const PINDAYU_FULL_LONGEVITY = [19, 25, 15, 12, 15, 21, 20];

/** Nisargayu full longevity of planets in years (Sun to Saturn) */
export const NISARGAYU_FULL_LONGEVITY = [20, 1, 2, 9, 18, 20, 50];

/** Deep exaltation longitudes of planets in absolute degrees (Sun to Saturn) */
export const PLANET_DEEP_EXALTATION_LONGITUDES = [10.0, 33.0, 298.0, 165.0, 95.0, 357.0, 200.0];

/** Deep debilitation longitudes = (exaltation + 180) % 360 */
export const PLANET_DEEP_DEBILITATION_LONGITUDES = [190.0, 213.0, 118.0, 345.0, 275.0, 177.0, 20.0];

// ============================================================================
// INDU LAGNA CONSTANTS
// ============================================================================

/** Indu Lagna factors for Sun to Saturn */
export const IL_FACTORS = [30, 16, 6, 8, 10, 12, 1];

// ============================================================================
// PACHAKADI SAMBHANDHA
// ============================================================================

/**
 * Pachakadi sambhandha relationships.
 * Each planet maps to 4 tuples: [related_planet, house_offset, relation_type].
 * 'E' marks inimical relations.
 * Order: Pachaka, Bodhaka, Karaka, Vedhaka
 */
export const PAACHAKAADI_SAMBHANDHA: Record<number, [number, number, string][]> = {
  0: [[6, 6, 'E'], [2, 7, ''], [4, 9, ''], [5, 11, '']],
  1: [[5, 7, ''], [2, 9, ''], [6, 11, ''], [0, 3, '']],
  2: [[0, 2, ''], [1, 6, ''], [6, 11, ''], [3, 12, 'E']],
  3: [[1, 2, ''], [4, 4, ''], [5, 5, ''], [2, 3, 'E']],
  4: [[6, 6, 'E'], [2, 5, ''], [1, 7, ''], [0, 12, '']],
  5: [[1, 2, ''], [3, 6, ''], [0, 12, ''], [6, 4, 'E']],
  6: [[5, 3, ''], [1, 11, ''], [4, 6, 'E'], [2, 7, '']],
};

export const PAACHAADI_RELATIONS = ['paachaka', 'bodhaka', 'kaaraka', 'vedhaka'];

// ============================================================================
// LATTA STARS
// ============================================================================

/**
 * Latta stars of planets: [count, direction].
 * Count = nth star from planet's star; direction = 1 (forward) or -1 (backward).
 * Index: Sun=0, Moon=1, Mars=2, Mercury=3, Jupiter=4, Venus=5, Saturn=6, Rahu=7, Ketu=8
 */
export const LATTA_STARS_OF_PLANETS: [number, number][] = [
  [12, 1], [22, -1], [3, 1], [7, -1], [6, 1], [5, -1], [8, 1], [9, -1], [9, -1],
];

/** Number of planets from Sun to Ketu (0-8 = 9 planets) */
export const PLANETS_UPTO_KETU = 9;

// ============================================================================
// TEMPORARY FRIEND/ENEMY RAASI POSITIONS
// ============================================================================

/**
 * House offsets (from a planet's rasi) considered temporary friends.
 * Houses 2,3,4,10,11,12 (0-based offsets: 1,2,3,9,10,11)
 * Python: temporary_friend_raasi_positions = [1,2,3,9,10,11]
 */
export const TEMPORARY_FRIEND_RAASI_POSITIONS = [1, 2, 3, 9, 10, 11];

/**
 * House offsets (from a planet's rasi) considered temporary enemies.
 * Houses 1,5,6,7,8,9 (0-based offsets: 0,4,5,6,7,8)
 * Python: temporary_enemy_raasi_positions = [0,4,5,6,7,8]
 */
export const TEMPORARY_ENEMY_RAASI_POSITIONS = [0, 4, 5, 6, 7, 8];

// ============================================================================
// RUDRA EIGHTH HOUSE
// ============================================================================

/**
 * The 8th house sign for Rudra calculation, indexed by lagna sign.
 * Python: rudra_eighth_house = [7,2,9,8,3,10,1,8,3,2,9,4]
 * e.g. If lagna is Aries (0), 8th house for Rudra is Scorpio (7)
 */
export const RUDRA_EIGHTH_HOUSE = [7, 2, 9, 8, 3, 10, 1, 8, 3, 2, 9, 4];

// ============================================================================
// LONGEVITY CONSTANTS
// ============================================================================

/**
 * Longevity pair lookup.
 * Key: longevity category (0=Short, 1=Middle, 2=Long)
 * Value: pairs of (rasi_type1, rasi_type2) that produce this longevity
 * rasi_type: 0=Fixed, 1=Movable, 2=Dual
 * Python: longevity = {0:[(0,0),(1,2),(2,1)],1:[(0,1),(1,0),(2,2)],2:[(0,2),(1,1),(2,0)]}
 */
export const LONGEVITY: Record<number, [number, number][]> = {
  0: [[0, 0], [1, 2], [2, 1]], // Short life
  1: [[0, 1], [1, 0], [2, 2]], // Middle life
  2: [[0, 2], [1, 1], [2, 0]], // Long life
};

/**
 * Longevity years matrix.
 * Row: first pair result (0=Short, 1=Middle, 2=Long)
 * Col: second pair result
 * Python: longevity_years = [[32,36,40],[64,72,80],[96,108,120]]
 */
export const LONGEVITY_YEARS = [
  [32, 36, 40],
  [64, 72, 80],
  [96, 108, 120],
];

// ============================================================================
// MOOLA TRIKONA OF PLANETS
// ============================================================================

/**
 * Moola trikona sign for each planet (Sun=0 to Ketu=8)
 * Python: moola_trikona_of_planets = [4,1,0,5,8,6,10,5,11]
 */
export const MOOLA_TRIKONA_OF_PLANETS = [4, 1, 0, 5, 8, 6, 10, 5, 11];

// ============================================================================
// HOUSE OWNERS (Standard, without co-lord exceptions)
// ============================================================================

/**
 * Standard house owners for each sign (derived from house_strengths_of_planets).
 * Python: house_owners = [2,5,3,1,0,3,5,2,4,6,6,4]
 * Same as SIGN_LORDS.
 */
export const HOUSE_OWNERS = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4];

/**
 * Houses where Rahu/Ketu are co-lords.
 * Python: houses_of_rahu_kethu = {7:10, 8:7}
 * Rahu co-lords Aquarius(10), Ketu co-lords Scorpio(7)
 */
export const HOUSES_OF_RAHU_KETU: Record<number, number> = {
  7: 10, // Rahu -> Aquarius
  8: 7,  // Ketu -> Scorpio
};

/**
 * Compound relation codes.
 * Python: 4=AdhiMitra, 3=Mitra, 2=Neutral, 1=Enemy, 0=AdhiSatru
 */
export const COMPOUND_ADHIMITRA = 4;
export const COMPOUND_MITRA = 3;
export const COMPOUND_NEUTRAL = 2;
export const COMPOUND_SATRU = 1;
export const COMPOUND_ADHISATRU = 0;

// ============================================================================
// COMBUSTION RANGES
// ============================================================================

/**
 * Combustion range (in degrees from Sun) for each planet.
 * Index: 0=Moon, 1=Mars, 2=Mercury, 3=Jupiter, 4=Venus, 5=Saturn
 * Python: combustion_range_of_planets_from_sun = [12,17,14,10,11,15]
 */
export const COMBUSTION_RANGE_OF_PLANETS_FROM_SUN = [12, 17, 14, 10, 11, 15];

/**
 * Combustion range (in degrees from Sun) for planets while retrograde.
 * Index: 0=Moon, 1=Mars, 2=Mercury, 3=Jupiter, 4=Venus, 5=Saturn
 * Python: combustion_range_of_planets_from_sun_while_in_retrogade = [12,8,12,11,8,16]
 */
export const COMBUSTION_RANGE_OF_PLANETS_FROM_SUN_WHILE_RETROGRADE = [12, 8, 12, 11, 8, 16];

// ============================================================================
// RETROGRADE LIMITS
// ============================================================================

/**
 * Retrograde limits (in degrees from Sun) for each planet.
 * Map from planet index to (min_degrees, max_degrees) from Sun.
 * Python: planets_retrograde_limits_from_sun = {2:(164,196),3:(144,216),4:(130,230),5:(163,197),6:(115,245)}
 */
export const PLANETS_RETROGRADE_LIMITS_FROM_SUN: Record<number, [number, number]> = {
  [MARS]: [164, 196],
  [MERCURY]: [144, 216],
  [JUPITER]: [130, 230],
  [VENUS]: [163, 197],
  [SATURN]: [115, 245],
};

/**
 * Planet retrogression calculation method.
 * 1 = Old method (house-based), 2 = Wiki calculations (degree-based)
 * Python: planet_retrogression_calculation_method = 1
 */
export const PLANET_RETROGRESSION_CALCULATION_METHOD = 1;

// ============================================================================
// MARANA KARAKA STHANA
// ============================================================================

/**
 * Marana karaka sthana of planets (the house where each planet is weakest).
 * Index: 0=Sun/12th, 1=Moon/8th, 2=Mars/7th, 3=Mercury/7th, 4=Jupiter/3rd,
 *        5=Venus/6th, 6=Saturn/1st, 7=Rahu/9th, 8=Ketu/4th
 * Python: marana_karaka_sthana_of_planets = [12,8,7,7,3,6,1,9,4]
 */
export const MARANA_KARAKA_STHANA_OF_PLANETS = [12, 8, 7, 7, 3, 6, 1, 9, 4];

// ============================================================================
// PUSHKARA CONSTANTS
// ============================================================================

/**
 * Pushkara navamsa starting degrees for each sign.
 * Python: pushkara_navamsa = [20,6+40/60,16+40/60,0,20,6+40/60,16+40/60,0,20,6+40/60,16+40/60,0]
 */
export const PUSHKARA_NAVAMSA = [20, 6 + 40 / 60, 16 + 40 / 60, 0, 20, 6 + 40 / 60, 16 + 40 / 60, 0, 20, 6 + 40 / 60, 16 + 40 / 60, 0];

/**
 * Pushkara bhaga degrees for each sign.
 * Python: pushkara_bhagas = [21,14,24,7,21,14,24,7,21,14,24,7]
 */
export const PUSHKARA_BHAGAS = [21, 14, 24, 7, 21, 14, 24, 7, 21, 14, 24, 7];

// ============================================================================
// DIVISIONAL CHART CONSTANTS
// ============================================================================

/** Python: division_chart_factors */
export const DIVISION_CHART_FACTORS = [1,2,3,4,5,6,7,8,9,10,11,12,16,20,24,27,30,40,45,60,81,108,144];

/**
 * Number of chart methods available per divisional chart factor.
 * Python: varga_option_dict = {factor: (num_methods, default_method), ...}
 * We store just [num_methods, default_method].
 */
export const VARGA_OPTION_DICT: Record<number, [number, number]> = {
  2: [6, 1], 3: [5, 1], 4: [4, 1], 5: [4, 1], 6: [4, 1], 7: [6, 1], 8: [4, 1],
  9: [5, 1], 10: [6, 1], 11: [5, 1], 12: [5, 1], 16: [4, 1], 20: [4, 1],
  24: [3, 1], 27: [4, 1], 30: [5, 1], 40: [4, 1], 45: [4, 1], 60: [4, 1],
  81: [3, 1], 108: [4, 1], 144: [4, 1],
};

/** Python: hora_list_raman - Raman method hora chart lookup per sign [hora0, hora1] */
export const HORA_LIST_RAMAN: [number, number][] = [
  [7, 9], [1, 11], [5, 0], [3, 6], [4, 2], [2, 3],
  [6, 4], [0, 5], [11, 1], [9, 7], [10, 8], [8, 10],
];

/** Python: drekkana_jagannatha - Jagannatha drekkana lookup per sign [part0, part1, part2] */
export const DREKKANA_JAGANNATHA: [number, number, number][] = [
  [0, 4, 8], [9, 1, 5], [6, 10, 2], [3, 7, 11],
  [0, 4, 8], [9, 1, 5], [6, 10, 2], [3, 7, 11],
  [0, 4, 8], [9, 1, 5], [6, 10, 2], [3, 7, 11],
];

/**
 * Python: kalachakra_navamsa - Maps nakshatra-pada (0-26) to array of 4 navamsa rasis.
 * Key = nakshatra_pada index (0-26), value = [nav0, nav1, nav2, nav3]
 */
export const KALACHAKRA_NAVAMSA: Record<number, number[]> = {
  0: [0, 1, 2, 3], 1: [4, 5, 6, 7], 2: [8, 9, 10, 11], 3: [7, 6, 5, 3],
  4: [4, 2, 1, 0], 5: [11, 10, 9, 8], 6: [0, 1, 2, 3], 7: [4, 5, 6, 7],
  8: [8, 9, 10, 11], 9: [7, 6, 5, 3], 10: [4, 2, 1, 0], 11: [11, 10, 9, 8],
  12: [0, 1, 2, 3], 13: [4, 5, 6, 7], 14: [8, 9, 10, 11], 15: [7, 6, 5, 3],
  16: [4, 2, 1, 0], 17: [11, 10, 9, 8], 18: [0, 1, 2, 3], 19: [4, 5, 6, 7],
  20: [8, 9, 10, 11], 21: [7, 6, 5, 3], 22: [4, 2, 1, 0], 23: [11, 10, 9, 8],
  24: [0, 1, 2, 3], 25: [4, 5, 6, 7], 26: [8, 9, 10, 11],
};

// ============================================================================
// HOUSE SYSTEM CONSTANTS
// ============================================================================

/**
 * Indian house systems.
 * Python: indian_house_systems = {1:'Equal Housing - Lagna in the middle', ...}
 */
export const INDIAN_HOUSE_SYSTEMS: Record<number, string> = {
  1: 'Equal Housing - Lagna in the middle',
  2: 'Equal Housing - Lagna as start',
  3: 'Sripati method',
  4: 'KP Method (aka Placidus Houses method)',
  5: 'Each Rasi is the house',
};

/**
 * Western house systems (Swiss Ephemeris house codes).
 * Python: western_house_systems = {'P':'Placidus', ...}
 */
export const WESTERN_HOUSE_SYSTEMS: Record<string, string> = {
  'P': 'Placidus',
  'K': 'Koch',
  'O': 'Porphyrius',
  'R': 'Regiomontanus',
  'C': 'Campanus',
  'A': 'Equal (cusp 1 is Ascendant)',
  'V': 'Vehlow equal (Asc. in middle of house 1)',
  'X': 'axial rotation system',
  'H': 'azimuthal or horizontal system',
  'T': 'Polich/Page (topocentric system)',
  'B': 'Alcabitus',
  'M': 'Morinus',
};

/**
 * All available house systems (Indian + Western).
 * Python: available_house_systems = {**indian_house_systems, **western_house_systems}
 */
export const AVAILABLE_HOUSE_SYSTEMS: Record<number | string, string> = {
  ...INDIAN_HOUSE_SYSTEMS,
  ...WESTERN_HOUSE_SYSTEMS,
};

/**
 * Default bhava madhya method.
 * Python: bhaava_madhya_method = 1
 */
export const BHAAVA_MADHYA_METHOD = 1;

// ============================================================================
// UPAGRAHA & DAY/NIGHT RULERS
// ============================================================================

/** Day rulers for each weekday (Sun=0..Sat=6), 8 parts of daytime. -1 = no planet. */
export const DAY_RULERS = [
  [0,1,2,3,4,5,6,-1],
  [1,2,3,4,5,6,-1,0],
  [2,3,4,5,6,-1,0,1],
  [3,4,5,6,-1,0,1,2],
  [4,5,6,-1,0,1,2,3],
  [5,6,-1,0,1,2,3,4],
  [6,-1,0,1,2,3,4,5],
];

/** Night rulers for each weekday (Sun=0..Sat=6), 8 parts of nighttime. */
export const NIGHT_RULERS = [
  [4,5,6,-1,0,1,2,3],
  [5,6,-1,0,1,2,3,4],
  [6,-1,0,1,2,3,4,5],
  [0,1,2,3,4,5,6,-1],
  [1,2,3,4,5,6,-1,0],
  [2,3,4,5,6,-1,0,1],
  [3,4,5,6,-1,0,1,2],
];

/** Conjunction search increment */
export const CONJUNCTION_INCREMENT = 0.00001;

/** Minimum separation for conjunction detection */
export const MINIMUM_SEPARATION_LONGITUDE = 0.00001;

/** Graha Yudh criteria thresholds */
export const GRAHA_YUDH_CRITERIA_1 = 20;    // seconds of arc for Ullekh-yuti
export const GRAHA_YUDH_CRITERIA_2 = 1.0;   // degrees for Apsavya-yuti
export const GRAHA_YUDH_CRITERIA_3 = 2.0;   // degrees for Anshumard-yuti

/** Drekkana table (standard) - planet index for each 10° division of each sign */
export const DREKKANA_TABLE = [
  [MARS, SUN, JUPITER],     // Aries
  [MERCURY, MOON, SATURN],  // Taurus
  [JUPITER, VENUS, MARS],   // Gemini
  [MOON, MARS, JUPITER],    // Cancer
  [SUN, JUPITER, MARS],     // Leo
  [MERCURY, SATURN, VENUS], // Virgo
  [VENUS, SATURN, MERCURY], // Libra
  [MARS, JUPITER, MOON],    // Scorpio
  [JUPITER, MARS, SUN],     // Sagittarius
  [SATURN, VENUS, MERCURY], // Capricorn
  [SATURN, MERCURY, VENUS], // Aquarius
  [JUPITER, MOON, MARS],    // Pisces
];

/** Drekkana table (BV Raman version) */
export const DREKKANA_TABLE_BVRAMAN = [
  [MARS, SUN, JUPITER],     // Aries
  [VENUS, MOON, SATURN],    // Taurus
  [MERCURY, VENUS, SATURN], // Gemini
  [MOON, MARS, JUPITER],    // Cancer
  [SUN, JUPITER, MARS],     // Leo
  [MERCURY, SATURN, VENUS], // Virgo
  [VENUS, SATURN, MERCURY], // Libra
  [MARS, JUPITER, MOON],    // Scorpio
  [JUPITER, MARS, SUN],     // Sagittarius
  [SATURN, VENUS, MERCURY], // Capricorn
  [SATURN, MERCURY, VENUS], // Aquarius
  [JUPITER, MOON, MARS],    // Pisces
];

// ============================================================================
// FORCE / PATCHING CONSTANTS
// ============================================================================

/** Whether to increase tithi by one before Kali Yuga for Mahabharata date validation */
export const INCREASE_TITHI_BY_ONE_BEFORE_KALI_YUGA = false;

/** Whether to use ahargana for vaara calculation */
export const USE_AHARGHANA_FOR_VAARA_CALCULATION = false;

/** Whether to use planet speed for panchangam end timings */
export const USE_PLANET_SPEED_FOR_PANCHANGAM_END_TIMINGS = false;

/** Kali start year offset */
export const KALI_START_YEAR = 27;
export const FORCE_KALI_START_YEAR_FOR_YEARS_BEFORE_KALI_YEAR_4009 = true;

// ============================================================================
// GAURI CHOGHADIYA & SHUBHA HORA TABLES
// ============================================================================

/** Gauri Choghadiya day table - rows=weekdays(Sun=0..Sat=6), cols=8 parts of day */
export const GAURI_CHOGHADIYA_DAY_TABLE = [
  [0,1,2,3,4,5,6,0], // Sunday
  [3,4,5,6,0,1,2,3], // Monday
  [6,0,1,2,3,4,5,6], // Tuesday
  [2,3,4,5,6,0,1,2], // Wednesday
  [5,6,0,1,2,3,4,5], // Thursday
  [1,2,3,4,5,6,0,1], // Friday
  [4,5,6,0,1,2,3,4], // Saturday
];

/** Gauri Choghadiya night table */
export const GAURI_CHOGHADIYA_NIGHT_TABLE = [
  [5,3,1,6,4,2,0,5], // Sunday
  [1,6,4,2,0,5,3,1], // Monday
  [4,2,0,5,3,1,6,4], // Tuesday
  [0,5,3,1,6,4,2,0], // Wednesday
  [3,1,6,4,2,0,5,3], // Thursday
  [6,4,2,0,5,3,1,6], // Friday
  [2,0,5,3,1,6,4,2], // Saturday
];

/** Shubha Hora day table - 12 rows (hora periods) x 7 cols (weekdays) */
export const SHUBHA_HORA_DAY_TABLE = [
  [0,1,2,3,4,5,6],[5,6,0,1,2,3,4],[3,4,5,6,0,1,2],[1,2,3,4,5,6,0],
  [6,0,1,2,3,4,5],[4,5,6,0,1,2,3],[2,3,4,5,6,0,1],[0,1,2,3,4,5,6],
  [5,6,0,1,2,3,4],[3,4,5,6,0,1,2],[1,2,3,4,5,6,0],[6,0,1,2,3,4,5],
];

/** Shubha Hora night table */
export const SHUBHA_HORA_NIGHT_TABLE = [
  [4,5,6,0,1,2,3],[2,3,4,5,6,0,1],[0,1,2,3,4,5,6],[5,6,0,1,2,3,4],
  [3,4,5,6,0,1,2],[1,2,3,4,5,6,0],[6,0,1,2,3,4,5],[4,5,6,0,1,2,3],
  [2,3,4,5,6,0,1],[0,1,2,3,4,5,6],[5,6,0,1,2,3,4],[3,4,5,6,0,1,2],
];

// ============================================================================
// AMRITA GADIYA / VARJYAM STAR MAP
// ============================================================================

/** Amrita Gadiya & Varjyam starting time factors for each nakshatra [amrita_factor, varjyam_factor] */
export const AMRITA_GADIYA_VARJYAM_STAR_MAP: Array<[number, number | [number, number]]> = [
  [16.8,20],[19.2,9.6],[21.6,12],[20.8,16],[15.2,5.6],[14,8.4],[21.6,12],[17.6,8],
  [22.4,12.8],[21.6,12],[17.6,8],[16.8,7.2],[18,8.4],[17.6,8],[15.2,5.6],[15.2,5.6],
  [13.6,4],[15.2,5.6],[17.6,[8,22.4]],[19.2,9.6],[17.6,8],[13.6,4],[13.6,4],
  [16.8,7.2],[16,6.4],[19.2,9.6],[21.6,12],
];

// ============================================================================
// TAMIL YOGA & ANANDHAADHI YOGA CONSTANTS
// ============================================================================

/** Tamil yoga names */
export const TAMIL_YOGA_NAMES = [
  'siddha','prabalarishta','marana','amirtha','amirtha_siddha','mrithyu','daghda','yamaghata','uthpatha','sarvartha_siddha',
];

/** Tamil basic yoga list - rows=weekdays, cols=nakshatras(0-26) */
export const TAMIL_BASIC_YOGA_LIST = [
  [0,1,0,0,0,0,0,0,0,2,0,3,0,0,0,2,2,2,3,0,3,3,2,0,0,3,3], // Sunday
  [0,0,2,3,0,0,3,0,0,2,0,0,0,1,3,2,0,0,0,2,2,3,0,0,0,0,0], // Monday
  [0,0,0,3,0,2,0,0,0,0,0,3,0,0,0,2,0,2,3,0,1,0,0,2,2,3,0], // Tuesday
  [2,0,3,0,0,0,0,0,0,0,3,3,2,0,0,0,0,0,2,3,3,0,1,0,3,0,2], // Wednesday
  [3,0,2,2,2,2,3,0,0,3,0,2,0,0,3,0,0,1,0,0,0,0,0,2,0,0,0], // Thursday
  [3,0,0,2,0,0,0,2,2,2,0,0,3,0,0,0,0,2,3,1,0,2,0,0,0,0,0], // Friday
  [0,0,0,3,0,0,0,0,2,3,0,2,2,2,0,0,0,0,0,0,0,0,0,3,2,0,1], // Saturday
];

/** Tamil basic yoga list (Sringeri Panchanga version) */
export const TAMIL_BASIC_YOGA_SRINGERI_LIST = [
  [0,0,0,3,0,0,0,0,0,2,0,3,3,0,0,2,2,2,3,0,3,3,2,0,0,3,3], // Sunday
  [0,0,2,3,3,0,3,0,0,2,0,0,0,0,3,2,0,0,0,0,2,3,0,0,2,0,0], // Monday
  [0,0,0,3,0,2,0,0,0,0,0,3,0,0,0,2,0,0,3,0,0,0,0,2,2,3,0], // Tuesday
  [2,0,3,0,0,0,0,0,0,0,3,3,2,0,0,0,0,0,2,3,3,0,1,0,3,0,2], // Wednesday
  [3,0,2,2,2,2,3,3,0,3,0,2,0,0,3,0,0,0,0,0,0,0,0,2,0,0,0], // Thursday
  [3,0,0,2,0,0,0,2,2,2,0,0,3,0,0,0,0,2,3,0,0,2,0,0,0,0,3], // Friday
  [0,0,3,3,0,0,0,0,2,3,0,2,2,2,3,0,0,0,0,0,0,0,0,3,2,0,2], // Saturday
];

/** Special yoga dicts: day → nakshatra index */
export const AMRITA_SIDDHA_YOGA_DICT: Record<number, number> = {0:12,1:4,2:0,3:16,4:7,5:26,6:3};
export const MRITYU_YOGA_DICT: Record<number, number> = {0:16,1:20,2:23,3:0,4:4,5:17,6:12};
export const DAGHDA_YOGA_DICT: Record<number, number> = {0:1,1:13,2:20,3:22,4:11,5:8,6:26};
export const YAMAGHATA_YOGA_DICT: Record<number, number> = {0:9,1:15,2:5,3:18,4:2,5:3,6:12};
export const UTPATA_YOGA_DICT: Record<number, number> = {0:15,1:19,2:22,3:26,4:3,5:7,6:11};

/** Sarvartha Siddha Yoga: day → tuple of nakshatra indices */
export const SARVARTHA_SIDDHA_YOGA: Record<number, number[]> = {
  0:[12,18,20,11,25,0,7],1:[21,3,4,7,16],2:[0,25,2,8],3:[3,16,12,2,4],
  4:[26,16,0,6,7],5:[26,16,0,6,21],6:[21,3,14],
};

/** Abhijit order of stars */
export const ABHIJIT_ORDER_OF_STARS = [...Array(21).keys(), 27, ...Array.from({length: 6}, (_, i) => 21 + i)];

/** Generate abhijit order from a starting nakshatra */
export function getAbhijithOrderOfStars(startNak: number = 1): number[] {
  if (startNak < 21) {
    return [...Array.from({length: 21 - startNak}, (_, i) => startNak + i), 27,
            ...Array.from({length: 6}, (_, i) => 21 + i), ...Array.from({length: startNak}, (_, i) => i)];
  }
  return [...Array.from({length: 27 - startNak}, (_, i) => startNak + i),
          ...Array.from({length: 21}, (_, i) => i), 27,
          ...Array.from({length: startNak - 21}, (_, i) => 21 + i)];
}

/** Anandhaadhi yoga day star list */
export const ANANDHAADHI_YOGA_DAY_STAR_LIST = [
  getAbhijithOrderOfStars(0),  // Sunday
  getAbhijithOrderOfStars(4),  // Monday
  getAbhijithOrderOfStars(7),  // Tuesday
  getAbhijithOrderOfStars(12), // Wednesday
  getAbhijithOrderOfStars(16), // Thursday
  getAbhijithOrderOfStars(20), // Friday
  getAbhijithOrderOfStars(23), // Saturday
];

/** Disha Shool map: weekday → direction index */
export const DISHA_SHOOL_MAP = [2,0,3,3,1,2,0]; // Sunday to Saturday

/** Yogini Vaasa tithi map (30 tithis) */
export const YOGINI_VAASA_TITHI_MAP = [0,3,7,5,1,2,5,6,0,3,7,5,1,2,5,0,3,7,5,1,2,5,6,0,3,7,5,1,2,6];

/** Muhurthas of the day: name → 0(inauspicious)/1(auspicious) */
export const MUHURTHAS_OF_THE_DAY: Record<string, number> = {
  'rudra':0,'aahi':0,'mithra':1,'pithra':0,'vasu':1,'varaaha':1,'vishvedeva':1,'vidhi':1,
  'sathamukhi':1,'puruhootha':0,'vaahini':0,'nakthanakaara':0,'varuna':1,'aaryaman':1,'bhaga':0,
  'girisha':1,'ajapaadha':0,'aahirbhudhnya':1,'pushya':1,'ashvini':1,'yama':0,'agni':1,
  'vidharth':1,'kanda':1,'adhithi':1,'jeeva':1,'vishnu':1,'dhyumadadhyuthi':1,
  'brahma':1,'samudhra':1,
};

/** Nakshathra lords for nava thaara */
export const NAKSHATHRA_LORDS: Record<number, number[]> = {
  8:[0,9,18], 5:[1,10,19], 0:[2,11,20], 1:[3,12,21], 2:[4,13,22], 7:[5,14,23],
  4:[6,15,24], 6:[7,16,25], 3:[8,17,26],
};

/** Special thaara map */
export const SPECIAL_THAARA_MAP = [1,10,18,16,4,7,12,27,19,22,25];

/** Special thaara lords */
export const SPECIAL_THAARA_LORDS_1: Record<number, number[]> = {
  8:[0,9,18], 5:[1,10,19], 0:[2,11,20], 1:[3,12,21,22], 2:[4,13,23], 7:[5,14,24],
  4:[6,15,25], 6:[7,16,26], 3:[8,17,27],
};

/** Abhijit star index */
export const ABHIJITH_STAR_INDEX = 21;

/** Triguna days dict: hour_boundary → triguna indices for each weekday */
export const TRIGUNA_DAYS_DICT: Record<number, number[]> = {
  1.3:[2,0,1,2,0,1,2], 3:[0,1,2,0,1,2,0], 4.5:[1,2,0,1,2,0,1], 6:[2,0,1,2,0,1,2],
  7.5:[0,1,2,0,1,2,0], 9:[1,2,0,1,2,0,1], 10.5:[2,0,1,2,0,1,2], 12:[0,1,2,0,1,2,0],
  13.3:[1,2,0,1,2,0,1], 15:[2,0,1,2,0,1,2], 16.5:[0,1,2,0,1,2,0], 18:[1,2,0,1,2,0,1],
  19.5:[2,0,1,2,0,1,2], 21:[0,1,2,0,1,2,0], 22.5:[1,2,0,1,2,0,1], 24:[2,0,1,2,0,1,2],
};

/** Tamil month method: 0=Ravi Annasamy, 1=V4.3.5, 2=V4.3.8, 3=Midday/UTC */
export const TAMIL_MONTH_METHOD = 3;

