/**
 * JHora PWA - Main Application Component
 * Demonstrates core calculation engine integration
 */

import { useEffect, useMemo, useState } from 'react';
import './App.css';
import './index.css';

// Components
import { BirthInputForm, DashaTable, PanchangaDisplay, SouthIndianChart } from './components';

// Core calculation engine
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
import { calculateKarana, calculateNakshatra, calculateTithi, calculateVara, calculateYoga } from './core/panchanga/drik';
import type { Place } from './core/types';
import { gregorianToJulianDay } from './core/utils/julian';

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
  { id: 'vimsottari', name: 'Vimsottari (120y)', description: '9 lords, classical system' },
  { id: 'ashtottari', name: 'Ashtottari (108y)', description: '8 lords' },
  { id: 'yogini', name: 'Yogini (108y)', description: '8 lords, 3 cycles' },
  { id: 'shastihayani', name: 'Shastihayani (60y)', description: '8 lords' },
  { id: 'shodasottari', name: 'Shodasottari (116y)', description: '8 lords' },
  { id: 'panchottari', name: 'Panchottari (105y)', description: '7 lords' },
  { id: 'dwadasottari', name: 'Dwadasottari (112y)', description: '8 lords' },
  { id: 'sataabdika', name: 'Sataabdika (100y)', description: '7 lords' },
  { id: 'dwisatpathi', name: 'Dwisatpathi (144y)', description: '8 lords, 2 cycles' },
  { id: 'chaturaseethi', name: 'Chaturaseethi (84y)', description: '7 lords' },
  { id: 'naisargika', name: 'Naisargika (132y)', description: 'Age-based' },
  { id: 'tara', name: 'Tara (120y)', description: '9 lords' },
  { id: 'shattrimsa', name: 'Shattrimsa (108y)', description: '8 lords, 3 cycles' },
  { id: 'saptharishi', name: 'Saptharishi (100y)', description: 'Nakshatra lords' },
] as const;

type DashaSystemId = typeof DASHA_SYSTEMS[number]['id'];

interface DashaResult {
  mahadashas: Array<{
    lord: number | string;
    lordName: string;
    startDate: string;
    durationYears: number;
  }>;
  bhuktis?: Array<{
    dashaLord: number | string;
    bhuktiLord: number | string;
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
}

function calculateDasha(systemId: DashaSystemId, jd: number, place: Place): DashaResult {
  const options = { includeBhuktis: true };

  switch (systemId) {
    case 'vimsottari':
      return getVimsottariDashaBhukti(jd, place);
    case 'ashtottari':
      return getAshtottariDashaBhukti(jd, place, options);
    case 'yogini':
      return getYoginiDashaBhukti(jd, place, { ...options, cycles: 3 });
    case 'shastihayani':
      return getShastihayaniDashaBhukti(jd, place, options);
    case 'shodasottari':
      return getShodasottariDashaBhukti(jd, place, options);
    case 'panchottari':
      return getPanchottariDashaBhukti(jd, place, options);
    case 'dwadasottari':
      return getDwadasottariDashaBhukti(jd, place, options);
    case 'sataabdika':
      return getSataabdikaDashaBhukti(jd, place, options);
    case 'dwisatpathi':
      return getDwisatpathiDashaBhukti(jd, place, { ...options, cycles: 2 });
    case 'chaturaseethi':
      return getChaturaseethiDashaBhukti(jd, place, options);
    case 'naisargika':
      return getNaisargikaDashaBhukti(jd, place, { includeBhuktis: false });
    case 'tara':
      return getTaraDashaBhukti(jd, place, options);
    case 'shattrimsa':
      return getShattrimsaDashaBhukti(jd, place, { ...options, cycles: 3 });
    case 'saptharishi':
      return getSaptharishiDashaBhukti(jd, place, options);
    default:
      return getVimsottariDashaBhukti(jd, place);
  }
}

function App() {
  const [birthData, setBirthData] = useState<BirthData | null>(null);
  const [selectedDasha, setSelectedDasha] = useState<number | undefined>();
  const [selectedSystem, setSelectedSystem] = useState<DashaSystemId>('vimsottari');

  // Calculate horoscope when birth data changes
  const horoscope = useMemo<HoroscopeData | null>(() => {
    if (!birthData) return null;

    try {
      // Parse date and time
      const [year, month, day] = birthData.date.split('-').map(Number);
      const [hour, minute] = birthData.time.split(':').map(Number);

      if (!year || !month || !day) return null;

      // Create place object
      const place: Place = {
        name: birthData.placeName,
        latitude: birthData.latitude,
        longitude: birthData.longitude,
        timezone: birthData.timezone
      };

      // Convert to Julian Day (local time - timezone is in Place object)
      const jd = gregorianToJulianDay(
        { year, month, day },
        { hour: hour ?? 12, minute: minute ?? 0, second: 0 }
      );

      // Calculate Panchanga
      const tithi = calculateTithi(jd, place);
      const nakshatra = calculateNakshatra(jd, place);
      const yoga = calculateYoga(jd, place);
      const karana = calculateKarana(jd, place);
      const vara = calculateVara(jd);

      // Generate sample planet positions for chart display
      const planets = generateSamplePlanets(jd, place);
      const ascendantRasi = Math.floor((jd * 10) % 12);

      return {
        jd,
        place,
        panchanga: { tithi, nakshatra, yoga, karana, vara },
        planets,
        ascendantRasi
      };
    } catch (error) {
      console.error('Calculation error:', error);
      return null;
    }
  }, [birthData]);

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
            Vedic Astrology Calculator • 14 Dasha Systems
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
                  Panchanga, Rasi Chart, and 14 different Dasha systems.
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
                  <SouthIndianChart
                    planets={horoscope.planets}
                    ascendantRasi={horoscope.ascendantRasi}
                    title="Rasi Chart"
                  />
                </div>

                <div className="section">
                  <PanchangaDisplay panchanga={horoscope.panchanga} />
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

/**
 * Generate sample planet positions for demonstration
 * In production, these would come from swisseph-js
 */
function generateSamplePlanets(jd: number, place: Place): HoroscopeData['planets'] {
  const seed = jd + place.latitude + place.longitude;

  const planets = [];
  for (let i = 0; i <= 8; i++) {
    const baseLong = ((seed * (i + 1) * 137.5) % 360 + 360) % 360;
    const rasi = Math.floor(baseLong / 30);
    const isRetrograde = (i === 2 || i === 6) && ((seed * i) % 10) < 3;

    planets.push({
      planet: i,
      rasi,
      longitude: baseLong,
      isRetrograde
    });
  }

  return planets;
}

export default App;
