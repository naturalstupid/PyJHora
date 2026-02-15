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
  FAGAN_BRADLEY: 0,
  TRUE_CITRA: 27,
  TRUE_REVATI: 28,
  TRUE_PUSHYA: 29,
  YUKTESHWAR: 7,
  JN_BHASIN: 8,
  ARYABHATA: 17,
  SURYASIDDHANTA: 21,
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

