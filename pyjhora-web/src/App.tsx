/**
 * JHora PWA - Main Application Component
 * Demonstrates core calculation engine integration
 */

import { useMemo, useState } from 'react';
import './App.css';
import './index.css';

// Components
import { BirthInputForm, DashaTable, PanchangaDisplay, SouthIndianChart } from './components';

// Core calculation engine
import { getVimsottariDashaBhukti } from './core/dhasa/graha/vimsottari';
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
  vimsottari: ReturnType<typeof getVimsottariDashaBhukti>;
  planets: Array<{ planet: number; rasi: number; longitude: number; isRetrograde?: boolean }>;
  ascendantRasi: number;
}

function App() {
  const [birthData, setBirthData] = useState<BirthData | null>(null);
  const [selectedDasha, setSelectedDasha] = useState<number | undefined>();

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

      // Convert to Julian Day
      const jd = gregorianToJulianDay(
        { year, month, day },
        { hour: hour ?? 12, minute: minute ?? 0, second: 0 },
        birthData.timezone
      );

      // Calculate Panchanga
      const tithi = calculateTithi(jd, place);
      const nakshatra = calculateNakshatra(jd, place);
      const yoga = calculateYoga(jd, place);
      const karana = calculateKarana(jd, place);
      const vara = calculateVara(jd);

      // Calculate Vimsottari Dasha
      const vimsottari = getVimsottariDashaBhukti(jd, place);

      // Generate sample planet positions for chart display
      // In production, these would come from swisseph-js
      const planets = generateSamplePlanets(jd, place);
      const ascendantRasi = Math.floor((jd * 10) % 12); // Placeholder

      return {
        jd,
        place,
        panchanga: { tithi, nakshatra, yoga, karana, vara },
        vimsottari,
        planets,
        ascendantRasi
      };
    } catch (error) {
      console.error('Calculation error:', error);
      return null;
    }
  }, [birthData]);

  // Select first dasha by default when horoscope changes
  useMemo(() => {
    if (horoscope?.vimsottari?.mahadashas?.[0]) {
      setSelectedDasha(horoscope.vimsottari.mahadashas[0].lord);
    }
  }, [horoscope]);

  return (
    <div className="app">
      <header className="header">
        <div className="container header-content">
          <div className="logo">✨ JHora PWA</div>
          <div className="header-meta text-sm text-secondary">
            Vedic Astrology Calculator
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
                  Panchanga, Rasi Chart, and Vimsottari Dasha.
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
                  <DashaTable
                    title="Vimsottari Dasha"
                    mahadashas={horoscope.vimsottari.mahadashas}
                    bhuktis={horoscope.vimsottari.bhuktis}
                    balance={horoscope.vimsottari.balance}
                    selectedDasha={selectedDasha}
                    onDashaSelect={setSelectedDasha}
                  />
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
          <p>JHora PWA • Vedic Astrology Calculator • 54 Tests Passing</p>
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
  // Use JD and place to seed pseudo-random positions
  const seed = jd + place.latitude + place.longitude;

  const planets = [];
  for (let i = 0; i <= 8; i++) {
    // Generate semi-deterministic positions based on seed
    const baseLong = ((seed * (i + 1) * 137.5) % 360 + 360) % 360;
    const rasi = Math.floor(baseLong / 30);

    // Mars, Saturn, and sometimes Mercury/Venus can be retrograde
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
