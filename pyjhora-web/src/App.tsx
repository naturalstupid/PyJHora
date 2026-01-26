/**
 * JHora PWA - Main Application Component
 * Demonstrates core calculation engine integration
 */

import { useEffect, useMemo, useState } from 'react';
import './App.css';
import './index.css';

// Components
import { BirthInputForm, DashaTable, DivisionalChartSelector, PanchangaDisplay, PlanetPositionTable, SouthIndianChart } from './components';

// Core calculation engine
import SwissEph from 'swisseph-wasm';
import { VARGA_NAMES } from './core/constants';
import { getAshtottariDashaBhukti } from './core/dhasa/graha/ashtottari';
import { getChaturaseethiDashaBhukti } from './core/dhasa/graha/chaturaseethi';
import { getDwadasottariDashaBhukti } from './core/dhasa/graha/dwadasottari';
import { getDwisatpathiDashaBhukti } from './core/dhasa/graha/dwisatpathi';
import { getNaisargikaDashaBhukti } from './core/dhasa/graha/naisargika';
import { getPanchottariDashaBhukti } from './core/dhasa/graha/panchottari';
import { getSaptharishiDashaBhukti } from './core/dhasa/graha/saptharishi';
import { getSataabdikaDashaBhukti } from './core/dhasa/graha/sataabdika';
import { getShastihayaniDashaBhukti } from './core/dhasa/graha/shastihayani';
import { getShattrimsaDashaBhukti } from './core/dhasa/graha/shattrimsa';
import { getShodasottariDashaBhukti } from './core/dhasa/graha/shodasottari';
import { getTaraDashaBhukti } from './core/dhasa/graha/tara';
import { getVimsottariDashaBhukti } from './core/dhasa/graha/vimsottari';
import { getYoginiDashaBhukti } from './core/dhasa/graha/yogini';
import {
  getChakraDashaBhukti,
  getCharaDashaBhukti,
  getDrigDashaBhukti,
  getKendradhiDashaBhukti,
  getLagnamsakaDashaBhukti,
  getMandookaDashaBhukti,
  getMoolaDashaBhukti,
  getNarayanaDashaBhukti,
  getNavamsaDashaBhukti,
  getNirayanaShoolaDashaBhukti,
  getShoolaDashaBhukti,
  getTrikonaDashaBhukti,
  getYogardhaDashaBhukti
} from './core/dhasa/raasi';
import { getDivisionalChart } from './core/horoscope/charts';
import { calculateKarana, calculateNakshatra, calculateTithi, calculateVara, calculateYoga } from './core/panchanga/drik';
import type { Place } from './core/types';
import { gregorianToJulianDay } from './core/utils/julian';

// ==========================================
// Swiss Ephemeris Integration
// ==========================================
let sweInstance: SwissEph | null = null;

const PYJHORA_TO_SWE: Record<number, number> = {
  0: 0, 1: 1, 2: 4, 3: 2, 4: 5, 5: 3, 6: 6, 7: 10, 8: -1
};

async function initSwissEph(): Promise<SwissEph> {
  if (!sweInstance) {
    sweInstance = new SwissEph();
    await sweInstance.initSwissEph();
  }
  return sweInstance;
}

async function calculateRealPlanetPositions(jdUtc: number): Promise<Array<{
  planet: number; rasi: number; longitude: number; isRetrograde: boolean;
}>> {
  const swe = await initSwissEph();

  // Get ayanamsa for sidereal conversion
  swe.set_sid_mode(1, 0, 0); // Lahiri ayanamsa
  const ayanamsa = swe.get_ayanamsa(jdUtc);

  // Use SEFLG_MOSEPH (4) for Moshier ephemeris + SEFLG_SPEED (256)
  // Get tropical positions, then subtract ayanamsa manually for sidereal
  const flags = 4 | 256; // SEFLG_MOSEPH | SEFLG_SPEED

  const positions = [];
  let rahuLong = 0;

  for (let p = 0; p <= 8; p++) {
    const sweP = PYJHORA_TO_SWE[p];
    let long: number, speed: number;

    if (sweP === -1) {
      // Ketu is opposite to Rahu
      long = (rahuLong + 180) % 360;
      speed = 0;
    } else {
      try {
        const r = swe.calc_ut(jdUtc, sweP ?? 0, flags);
        // Result: [longitude, latitude, distance, long_speed, lat_speed, dist_speed]
        if (!r || typeof r[0] !== 'number') {
          console.warn(`calc_ut returned invalid result for planet ${p}:`, r);
          long = 0;
          speed = 0;
        } else {
          // Convert tropical to sidereal by subtracting ayanamsa
          const tropical = ((r[0] % 360) + 360) % 360;
          long = ((tropical - ayanamsa) % 360 + 360) % 360;
          speed = r[3] ?? 0;
        }
        if (p === 7) rahuLong = long;
      } catch (err) {
        console.error(`Error calculating planet ${p} (sweP=${sweP}):`, err);
        long = 0;
        speed = 0;
      }
    }

    positions.push({
      planet: p,
      rasi: Math.floor(long / 30),
      longitude: long % 30,
      isRetrograde: p < 7 && speed < 0
    });
  }

  return positions;
}

async function calculateRealAscendant(jd: number, place: Place): Promise<{ rasi: number; longitude: number }> {
  const swe = await initSwissEph();
  swe.set_sid_mode(1, 0, 0); // Lahiri ayanamsa
  const jdUtc = jd - place.timezone / 24;

  // The swisseph-wasm houses() and houses_ex() functions don't return cusps properly.
  // We need to call the underlying WASM module directly with swe_houses_ex
  // Using SEFLG_SIDEREAL flag (65536) to get sidereal ascendant directly
  const SweModule = (swe as any).SweModule;
  const cuspsPtr = SweModule._malloc(13 * Float64Array.BYTES_PER_ELEMENT);
  const ascmcPtr = SweModule._malloc(10 * Float64Array.BYTES_PER_ELEMENT);
  const SEFLG_SIDEREAL = 65536;

  try {
    // Call swe_houses_ex with sidereal flag
    // C signature: int swe_houses_ex(double tjd_ut, int32 iflag, double geolat, double geolon, int hsys, double *cusps, double *ascmc)
    const retCode = SweModule.ccall(
      'swe_houses_ex',
      'number',
      ['number', 'number', 'number', 'number', 'number', 'pointer', 'pointer'],
      [jdUtc, SEFLG_SIDEREAL, place.latitude, place.longitude, 'P'.charCodeAt(0), cuspsPtr, ascmcPtr]
    );

    // Read the ascmc array using Float64Array view (similar to calc_ut)
    const ascmcArray = new Float64Array(SweModule.HEAPF64.buffer, ascmcPtr, 10);
    const siderealAsc = ascmcArray[0];

    // Check if we got a valid result
    if (retCode < 0 || !isFinite(siderealAsc) || siderealAsc === 0) {
      // Fallback: calculate using tropical ascendant and ayanamsa
      const ayanamsa = swe.get_ayanamsa(jdUtc);
      const cuspsArray = new Float64Array(SweModule.HEAPF64.buffer, cuspsPtr, 13);
      const tropicalAsc = cuspsArray[1]; // cusps[1] is 1st house cusp
      const fallbackAsc = ((tropicalAsc - ayanamsa) % 360 + 360) % 360;
      return { rasi: Math.floor(fallbackAsc / 30), longitude: fallbackAsc % 30 };
    }

    // Normalize to 0-360 range
    const normalizedAsc = ((siderealAsc % 360) + 360) % 360;

    return { rasi: Math.floor(normalizedAsc / 30), longitude: normalizedAsc % 30 };
  } finally {
    // Free allocated memory
    SweModule._free(cuspsPtr);
    SweModule._free(ascmcPtr);
  }
}
// ==========================================

interface BirthData {
  date: string;
  time: string;
  placeName: string;
  latitude: number;
  longitude: number;
  timezone: number;
}

// Dasha system configuration
const DASHA_SYSTEMS = [
  // GRAHA DASHAS
  { id: 'vimsottari', name: 'Vimsottari (120y)', description: 'Classic Nakshatra Dasha', type: 'graha' },
  { id: 'ashtottari', name: 'Ashtottari (108y)', description: '8 lords', type: 'graha' },
  { id: 'yogini', name: 'Yogini (36y x 3)', description: '8 Yoginis', type: 'graha' },
  { id: 'shodasottari', name: 'Shodasottari (116y)', description: '8 lords', type: 'graha' },
  { id: 'dwadasottari', name: 'Dwadasottari (112y)', description: '8 lords', type: 'graha' },
  { id: 'panchottari', name: 'Panchottari (105y)', description: '7 lords', type: 'graha' },
  { id: 'sataabdika', name: 'Sataabdika (100y)', description: '7 lords', type: 'graha' },
  { id: 'chaturaseethi', name: 'Chaturaseethi (84y)', description: '7 lords', type: 'graha' },
  { id: 'dwisatpathi', name: 'Dwisatpathi (144y)', description: '8 lords', type: 'graha' },
  { id: 'shattrimsa', name: 'Shattrimsa (108y)', description: '8 lords', type: 'graha' },
  { id: 'shastihayani', name: 'Shastihayani (60y)', description: '8 lords', type: 'graha' },
  { id: 'saptharishi', name: 'Saptharishi (100y)', description: 'Nakshatra lords', type: 'graha' },
  { id: 'naisargika', name: 'Naisargika (132y)', description: 'Age-based', type: 'graha' },
  { id: 'tara', name: 'Tara (120y)', description: '9 lords', type: 'graha' },

  // RAASI DASHAS
  { id: 'narayana', name: 'Narayana Dasha', description: 'Major Rasi Dasha', type: 'rasi' },
  { id: 'chara', name: 'Chara Dasha (K.N. Rao)', description: 'Jaimini Rasi Dasha', type: 'rasi' },
  { id: 'lagnamsaka', name: 'Lagnamsaka Dasha', description: 'Based on D-9 Lagna', type: 'rasi' },
  { id: 'navamsa', name: 'Navamsa Dasha', description: 'Rasi Dasha in D-9 (Fixed)', type: 'rasi' },
  { id: 'moola', name: 'Moola Dasha', description: 'Past Karma', type: 'rasi' },
  { id: 'kendradhi', name: 'Kendradhi Rasi Dasha', description: 'Uses Kendras from Stronger of Asc/7th', type: 'rasi' },
  { id: 'mandooka', name: 'Mandooka Dasha', description: 'Frog Jump progression', type: 'rasi' },
  { id: 'shoola', name: 'Shoola Dasha', description: 'For death/suffering (Fixed 9y)', type: 'rasi' },
  { id: 'nirayana', name: 'Nirayana Shoola Dasha', description: 'For longevity', type: 'rasi' },
  { id: 'drig', name: 'Drig Dasha', description: 'Aspect-based', type: 'rasi' },
  { id: 'trikona', name: 'Trikona Dasha', description: 'Trines-based', type: 'rasi' },
  { id: 'chakra', name: 'Chakra Dasha', description: 'Fixed 10y per sign', type: 'rasi' },
  { id: 'yogardha', name: 'Yogardha Dasha', description: 'Combines Chara/Sthira', type: 'rasi' },
] as const;

type DashaSystemId = typeof DASHA_SYSTEMS[number]['id'];

interface DashaResult {
  mahadashas: Array<{
    lord: number;
    lordName: string;
    startDate: string;
    durationYears: number;
  }>;
  bhuktis?: Array<{
    dashaLord: number;
    bhuktiLord: number;
    bhuktiLordName: string;
    startDate: string;
  }>;
  balance?: {
    years: number;
    months: number;
    days: number;
  };
}

interface HoroscopeData {
  jd: number;
  place: Place;
  panchanga: {
    tithi: { number: number; name: string; paksha: 'shukla' | 'krishna' };
    nakshatra: { number: number; name: string; pada: number };
    yoga: { number: number; name: string };
    karana: { number: number; name: string };
    vara: { number: number; name: string };
  };
  planets: Array<{ planet: number; rasi: number; longitude: number; isRetrograde?: boolean }>;
  ascendantRasi: number;
  ascendantLongitude: number;
}

function calculateDasha(systemId: DashaSystemId, jd: number, place: Place): DashaResult {
  const options = { includeBhuktis: true };

  let rawResult: any;

  switch (systemId) {
    // Graha Dashas
    case 'vimsottari': rawResult = getVimsottariDashaBhukti(jd, place); break;
    case 'ashtottari': rawResult = getAshtottariDashaBhukti(jd, place, options); break;
    case 'yogini': rawResult = getYoginiDashaBhukti(jd, place, { ...options, cycles: 3 }); break;
    case 'shastihayani': rawResult = getShastihayaniDashaBhukti(jd, place, options); break;
    case 'shodasottari': rawResult = getShodasottariDashaBhukti(jd, place, options); break;
    case 'panchottari': rawResult = getPanchottariDashaBhukti(jd, place, options); break;
    case 'dwadasottari': rawResult = getDwadasottariDashaBhukti(jd, place, options); break;
    case 'sataabdika': rawResult = getSataabdikaDashaBhukti(jd, place, options); break;
    case 'dwisatpathi': rawResult = getDwisatpathiDashaBhukti(jd, place, { ...options, cycles: 2 }); break;
    case 'chaturaseethi': rawResult = getChaturaseethiDashaBhukti(jd, place, options); break;
    case 'naisargika': rawResult = getNaisargikaDashaBhukti(jd, place, { includeBhuktis: false }); break;
    case 'tara': rawResult = getTaraDashaBhukti(jd, place, options); break;
    case 'shattrimsa': rawResult = getShattrimsaDashaBhukti(jd, place, { ...options, cycles: 3 }); break;
    case 'saptharishi': rawResult = getSaptharishiDashaBhukti(jd, place, options); break;

    // Raasi Dashas
    case 'narayana': rawResult = getNarayanaDashaBhukti(jd, place, options); break;
    case 'chara': rawResult = getCharaDashaBhukti(jd, place, options); break;
    case 'lagnamsaka': rawResult = getLagnamsakaDashaBhukti(jd, place, options); break;
    case 'navamsa': rawResult = getNavamsaDashaBhukti(jd, place, options); break;
    case 'moola': rawResult = getMoolaDashaBhukti(jd, place, options); break;
    case 'kendradhi': rawResult = getKendradhiDashaBhukti(jd, place, options); break; // Updated name
    case 'mandooka': rawResult = getMandookaDashaBhukti(jd, place, options); break;
    case 'shoola': rawResult = getShoolaDashaBhukti(jd, place, options); break;
    case 'nirayana': rawResult = getNirayanaShoolaDashaBhukti(jd, place, options); break;
    case 'drig': rawResult = getDrigDashaBhukti(jd, place, options); break;
    case 'trikona': rawResult = getTrikonaDashaBhukti(jd, place, options); break;
    case 'chakra': rawResult = getChakraDashaBhukti(jd, place, options); break;
    case 'yogardha': rawResult = getYogardhaDashaBhukti(jd, place, options); break;

    default: rawResult = getVimsottariDashaBhukti(jd, place); break;
  }

  // Map to standardized DashaResult
  return {
    mahadashas: rawResult.mahadashas.map((m: any) => ({
      lord: m.lord ?? m.rasi ?? 0,
      lordName: m.lordName ?? m.rasiName ?? m.yoginiName ?? 'Unknown',
      startDate: m.startDate,
      durationYears: m.durationYears
    })),
    bhuktis: rawResult.bhuktis?.map((b: any) => ({
      dashaLord: b.dashaLord ?? b.dashaRasi ?? 0,
      bhuktiLord: b.bhuktiLord ?? b.bhuktiRasi ?? 0,
      bhuktiLordName: b.bhuktiLordName ?? b.bhuktiRasiName ?? b.bhuktiYoginiName ?? 'Unknown',
      startDate: b.startDate
    })),
    balance: rawResult.balance
  };
}

function App() {
  const [birthData, setBirthData] = useState<BirthData | null>(null);
  const [selectedDasha, setSelectedDasha] = useState<number | undefined>();
  const [selectedSystem, setSelectedSystem] = useState<DashaSystemId>('vimsottari');
  const [selectedVarga, setSelectedVarga] = useState<number>(1); // Default to Rasi (D1)

  const [horoscope, setHoroscope] = useState<HoroscopeData | null>(null);

  // Calculate horoscope when birth data changes (async for ephemeris)
  useEffect(() => {
    if (!birthData) { setHoroscope(null); return; }
    const calc = async () => {
      try {
        const [year, month, day] = birthData.date.split('-').map(Number);
        const [hour, minute] = birthData.time.split(':').map(Number);
        if (!year || !month || !day) { setHoroscope(null); return; }
        const place: Place = {
          name: birthData.placeName, latitude: birthData.latitude,
          longitude: birthData.longitude, timezone: birthData.timezone
        };
        const jd = gregorianToJulianDay({ year, month, day }, { hour: hour ?? 12, minute: minute ?? 0, second: 0 });
        const jdUtc = jd - place.timezone / 24;
        const planets = await calculateRealPlanetPositions(jdUtc);
        const ascendant = await calculateRealAscendant(jd, place);
        const tithi = calculateTithi(jd, place);
        const nakshatra = calculateNakshatra(jd, place);
        const yoga = calculateYoga(jd, place);
        const karana = calculateKarana(jd, place);
        const vara = calculateVara(jd);
        setHoroscope({
          jd, place, panchanga: { tithi, nakshatra, yoga, karana, vara },
          planets, ascendantRasi: ascendant.rasi,
          ascendantLongitude: ascendant.rasi * 30 + ascendant.longitude
        });
      } catch (error) { console.error('Calculation error:', error); setHoroscope(null); }
    };
    calc();
  }, [birthData]);

  // Calculate Divisional Chart Positions
  const chartData = useMemo(() => {
    if (!horoscope) return null;

    if (selectedVarga === 1) {
      return {
        planets: horoscope.planets.map(p => ({
          ...p,
          isRetrograde: p.isRetrograde ?? false
        })),
        ascendantRasi: horoscope.ascendantRasi,
        title: 'Rasi Chart (D-1)'
      };
    }

    // Calculate Varga positions for planets
    const vargaPlanets = getDivisionalChart(
      horoscope.planets,
      selectedVarga
    ).map((p, i) => ({
      ...p,
      isRetrograde: horoscope.planets[i]?.isRetrograde ?? false // Safe access
    }));

    // Calculate Varga position for Ascendant
    // We treat Ascendant as a "planet" with ID 100 for calculation
    const ascP = [{ planet: 100, rasi: horoscope.ascendantRasi, longitude: horoscope.ascendantLongitude % 30 }];
    const vargaAscList = getDivisionalChart(ascP, selectedVarga);
    const vargaAscRasi = vargaAscList[0]?.rasi ?? horoscope.ascendantRasi;

    const title = VARGA_NAMES[selectedVarga] || `Divisional Chart D-${selectedVarga}`;

    return {
      planets: vargaPlanets,
      ascendantRasi: vargaAscRasi,
      title
    };
  }, [horoscope, selectedVarga]);

  // Calculate dasha based on selected system
  const dashaResult = useMemo<DashaResult | null>(() => {
    if (!horoscope) return null;
    try {
      return calculateDasha(selectedSystem, horoscope.jd, horoscope.place);
    } catch (error) {
      console.error('Dasha calculation error:', error);
      return null;
    }
  }, [horoscope, selectedSystem]);

  // Select first dasha by default when dasha result changes
  useEffect(() => {
    if (dashaResult?.mahadashas?.[0]) {
      const lord = dashaResult.mahadashas[0].lord;
      setSelectedDasha(typeof lord === 'number' ? lord : 0);
    }
  }, [dashaResult]);

  const systemInfo = DASHA_SYSTEMS.find(s => s.id === selectedSystem);

  return (
    <div className="app">
      <header className="header">
        <div className="container header-content">
          <div className="logo">✨ JHora PWA</div>
          <div className="header-meta text-sm text-secondary">
            Vedic Astrology Calculator • 14 Dasha Systems • 16 Varga Charts
          </div>
        </div>
      </header>

      <main className="main">
        <div className="container">
          {!horoscope ? (
            <div className="intro-section">
              <div className="intro-content">
                <h1 className="intro-title">Vedic Horoscope Calculator</h1>
                <p className="intro-subtitle text-secondary">
                  Enter your birth details to generate a complete Vedic horoscope with
                  Panchanga, Divisional Charts, and 14 different Dasha systems.
                </p>
                <BirthInputForm onSubmit={setBirthData} />
              </div>
            </div>
          ) : (
            <div className="horoscope-section animate-fadeIn">
              <div className="horoscope-header">
                <div>
                    <h2>{birthData?.placeName}</h2>
                    <p className="text-secondary">
                      {birthData?.date} at {birthData?.time}
                    </p>
                  </div>
                  <button
                    className="btn btn-secondary"
                    onClick={() => setBirthData(null)}
                  >
                    New Chart
                  </button>
              </div>

              <div className="horoscope-grid">
                <div className="section">
                    {/* Varga Selector */}
                    {/* Varga Selector */}
                    <DivisionalChartSelector
                      selectedVarga={selectedVarga}
                      onSelect={setSelectedVarga}
                    />

                  <SouthIndianChart
                      planets={chartData?.planets || []}
                      ascendantRasi={chartData?.ascendantRasi || 0}
                      title={chartData?.title || ''}
                  />
                </div>

                <div className="section">
                  <PanchangaDisplay panchanga={horoscope.panchanga} />
                </div>

                  <div className="section section-wide">
                    <h3>Planet Positions</h3>
                    <PlanetPositionTable
                      d1Positions={horoscope.planets}
                      vargas={[1, 9, 10, 12]}
                      showDegrees={true}
                    />
                  </div>

                <div className="section section-wide">
                    {/* Dasha System Selector */}
                    <div className="dasha-selector card">
                      <label htmlFor="dasha-system" className="dasha-selector-label">
                        Select Dasha System:
                      </label>
                      <select
                        id="dasha-system"
                        className="dasha-system-select"
                        value={selectedSystem}
                        onChange={(e) => setSelectedSystem(e.target.value as DashaSystemId)}
                      >
                        {DASHA_SYSTEMS.map(system => (
                          <option key={system.id} value={system.id}>
                            {system.name}
                          </option>
                        ))}
                      </select>
                      {systemInfo && (
                        <p className="dasha-system-desc text-sm text-secondary">
                          {systemInfo.description}
                        </p>
                      )}
                    </div>

                    {dashaResult && (
                      <DashaTable
                        title={systemInfo?.name ?? 'Dasha'}
                        mahadashas={dashaResult.mahadashas.map(m => ({
                          lord: typeof m.lord === 'number' ? m.lord : 0,
                          lordName: m.lordName,
                          startDate: m.startDate,
                          durationYears: m.durationYears
                        }))}
                        bhuktis={dashaResult.bhuktis?.map(b => ({
                          dashaLord: typeof b.dashaLord === 'number' ? b.dashaLord : 0,
                          bhuktiLord: typeof b.bhuktiLord === 'number' ? b.bhuktiLord : 0,
                          bhuktiLordName: b.bhuktiLordName,
                          startDate: b.startDate
                        }))}
                        balance={dashaResult.balance}
                        selectedDasha={selectedDasha}
                        onDashaSelect={setSelectedDasha}
                        coloringMode={systemInfo?.type === 'rasi' ? 'rasi' : 'planet'}
                      />
                    )}
                </div>
              </div>

              <div className="tech-info card mt-md">
                <h4>Technical Info</h4>
                <div className="tech-grid">
                  <div>
                    <span className="text-secondary">Julian Day:</span>
                    <span className="font-mono">{horoscope.jd.toFixed(6)}</span>
                  </div>
                  <div>
                    <span className="text-secondary">Latitude:</span>
                    <span className="font-mono">{horoscope.place.latitude.toFixed(4)}°</span>
                  </div>
                  <div>
                    <span className="text-secondary">Longitude:</span>
                    <span className="font-mono">{horoscope.place.longitude.toFixed(4)}°</span>
                  </div>
                  <div>
                    <span className="text-secondary">Timezone:</span>
                    <span className="font-mono">UTC{horoscope.place.timezone >= 0 ? '+' : ''}{horoscope.place.timezone}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="footer">
        <div className="container text-center text-sm text-muted">
          <p>JHora PWA • Vedic Astrology Calculator • 77 Tests Passing • 14 Dasha Systems</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
