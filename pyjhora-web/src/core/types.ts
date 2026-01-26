/**
 * Core type definitions for PyJHora web application
 * TypeScript interfaces matching Python data structures
 */

// ============================================================================
// BASIC TYPES
// ============================================================================

/** Date structure (supports BC dates via negative year) */
export interface JhoraDate {
  year: number;
  month: number;
  day: number;
}

/** Time of day */
export interface JhoraTime {
  hour: number;
  minute: number;
  second: number;
}

/** Geographic location */
export interface Place {
  name: string;
  latitude: number;
  longitude: number;
  timezone: number; // Hours offset from UTC
}

/** Full date-time and place for calculations */
export interface BirthData {
  date: JhoraDate;
  time: JhoraTime;
  place: Place;
}

// ============================================================================
// PLANETARY POSITIONS
// ============================================================================

/** Position of a planet in the zodiac */
export interface PlanetPosition {
  planet: number;
  rasi: number;
  longitude: number; // Total longitude 0-360
  longitudeInSign: number; // Longitude within the sign 0-30
  isRetrograde: boolean;
  nakshatra: number;
  nakshatraPada: number;
}

/** Map of planet index to position */
export type PlanetPositions = Map<number, PlanetPosition>;

/** Simple planet-to-house mapping */
export type PlanetToHouseMap = Record<number, number>;

/** House-to-planets mapping (string format like "0/3/5" for Sun/Mercury/Venus) */
export type HouseChart = string[];

// ============================================================================
// CHART DATA
// ============================================================================

/** Divisional chart data */
export interface DivisionalChart {
  factor: number;
  name: string;
  positions: PlanetPositions;
  houseChart: HouseChart;
  ascendant: {
    rasi: number;
    longitude: number;
  };
}

/** House cusp data */
export interface HouseCusps {
  system: string;
  cusps: number[]; // 12 house cusps in degrees
  ascendant: number;
  mc: number; // Midheaven
}

// ============================================================================
// DASHA (PLANETARY PERIODS)
// ============================================================================

/** Single dasha period */
export interface DashaPeriod {
  planet: number;
  startDate: Date;
  endDate: Date;
  durationYears: number;
  level: 'maha' | 'antar' | 'pratyantar' | 'sukshma' | 'prana';
}

/** Dasha balance at birth */
export interface DashaBalance {
  years: number;
  months: number;
  days: number;
}

/** Complete dasha system data */
export interface DashaData {
  system: string;
  balance: DashaBalance;
  periods: DashaPeriod[];
}

// ============================================================================
// PANCHANGA
// ============================================================================

/** Tithi data */
export interface Tithi {
  index: number; // 1-30
  name: string;
  paksha: 'shukla' | 'krishna';
  endTime: Date;
}

/** Nakshatra data */
export interface Nakshatra {
  index: number; // 1-27
  name: string;
  pada: number; // 1-4
  lord: number; // Planet index
  endTime: Date;
}

/** Yoga (sun-moon combination) */
export interface Yoga {
  index: number; // 1-27
  name: string;
  endTime: Date;
}

/** Karana (half-tithi) */
export interface Karana {
  index: number;
  name: string;
  endTime: Date;
}

/** Vara (weekday) */
export interface Vara {
  index: number; // 0=Sunday, 1=Monday, etc.
  name: string;
  lord: number; // Planet index
}

/** Complete panchanga data for a day */
export interface PanchangaData {
  date: JhoraDate;
  place: Place;
  sunrise: Date;
  sunset: Date;
  tithi: Tithi;
  nakshatra: Nakshatra;
  yoga: Yoga;
  karana: Karana;
  vara: Vara;
  moonSign: number;
  sunSign: number;
}

// ============================================================================
// YOGA (COMBINATIONS)
// ============================================================================

/** Detected yoga (astrological combination) */
export interface DetectedYoga {
  name: string;
  category: string;
  planets: number[];
  houses: number[];
  description: string;
  isPresent: boolean;
}

// ============================================================================
// ASHTAKAVARGA
// ============================================================================

/** Binna Ashtakavarga data */
export interface BinnaAshtakavarga {
  planet: number;
  points: number[]; // 12 values, one per rasi
  total: number;
}

/** Sarva Ashtakavarga (combined) */
export type SarvaAshtakavarga = number[]; // 12 values, one per rasi

// ============================================================================
// HOROSCOPE
// ============================================================================

/** Complete horoscope data */
export interface Horoscope {
  birthData: BirthData;
  julianDay: number;
  ayanamsa: {
    mode: string;
    value: number;
  };
  
  // Charts
  rasiChart: DivisionalChart;
  divisionalCharts: Map<number, DivisionalChart>;
  
  // Panchanga
  panchanga: PanchangaData;
  
  // Dasha
  dashas: Map<string, DashaData>;
  
  // Yogas
  yogas: DetectedYoga[];
  
  // Ashtakavarga
  binnaAshtakavarga: BinnaAshtakavarga[];
  sarvaAshtakavarga: SarvaAshtakavarga;
}

// ============================================================================
// CALCULATION OPTIONS
// ============================================================================

/** Options for horoscope calculation */
export interface CalculationOptions {
  ayanamsaMode: string;
  houseSystem: string;
  includeOuterPlanets: boolean;
  divisionalCharts: number[];
  dashaSystem: string;
  calculateYogas: boolean;
  calculateAshtakavarga: boolean;
}

/** Default calculation options */
export const DEFAULT_CALCULATION_OPTIONS: CalculationOptions = {
  ayanamsaMode: 'LAHIRI',
  houseSystem: 'PLACIDUS',
  includeOuterPlanets: false,
  divisionalCharts: [1, 9],
  dashaSystem: 'vimsottari',
  calculateYogas: true,
  calculateAshtakavarga: true
};

// ============================================================================
// EPHEMERIS
// ============================================================================

/** Ephemeris file metadata */
export interface EphemerisFile {
  filename: string;
  startYear: number;
  endYear: number;
  type: 'planet' | 'moon';
  size: number;
  loaded: boolean;
}

/** Ephemeris loading status */
export interface EphemerisStatus {
  coreLoaded: boolean;
  extendedRanges: Array<{ start: number; end: number }>;
  totalFiles: number;
  loadedFiles: number;
  cachedInIndexedDB: boolean;
}
