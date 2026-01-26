/**
 * Dasha Table Component
 * Displays Vimsottari dasha periods
 */

import './DashaTable.css';

interface DashaPeriod {
  lord: number;
  lordName: string;
  startDate: string;
  durationYears: number;
}

interface BhuktiPeriod {
  dashaLord: number;
  bhuktiLord: number;
  bhuktiLordName: string;
  startDate: string;
}

interface DashaTableProps {
  title?: string;
  mahadashas: DashaPeriod[];
  bhuktis?: BhuktiPeriod[] | undefined;
  balance?: {
    years: number;
    months: number;
    days: number;
  } | undefined;
  selectedDasha?: number | undefined;
  onDashaSelect?: ((lordIndex: number) => void) | undefined;
}

// Planet class for coloring
const PLANET_CLASS: Record<number, string> = {
  0: 'planet-sun',
  1: 'planet-moon',
  2: 'planet-mars',
  3: 'planet-mercury',
  4: 'planet-jupiter',
  5: 'planet-venus',
  6: 'planet-saturn',
  7: 'planet-rahu',
  8: 'planet-ketu'
};

// Rasi class for coloring
const RASI_CLASS: Record<number, string> = {
  1: 'rasi-aries',
  2: 'rasi-taurus',
  3: 'rasi-gemini',
  4: 'rasi-cancer',
  5: 'rasi-leo',
  6: 'rasi-virgo',
  7: 'rasi-libra',
  8: 'rasi-scorpio',
  9: 'rasi-sagittarius',
  10: 'rasi-capricorn',
  11: 'rasi-aquarius',
  12: 'rasi-pisces',
  // Handling 0-indexed rasis just in case
  0: 'rasi-aries'
};

export function DashaTable({ 
  title = 'Dasha',
  mahadashas, 
  bhuktis,
  balance,
  selectedDasha,
  onDashaSelect,
  coloringMode = 'planet'
}: DashaTableProps & { coloringMode?: 'planet' | 'rasi' }) {
  // Get bhuktis for selected dasha
  const selectedBhuktis = selectedDasha !== undefined && bhuktis
    ? bhuktis.filter(b => b.dashaLord === selectedDasha)
    : [];

  const getClass = (id: number) => {
    if (coloringMode === 'rasi') {
      // Map 0-11 to 1-12 or 1-12 to 1-12. 
      // Assuming Input Rasi IDs will be 0-11 per codebase standard, or 1-12?
      // Let's assume input matches the key. 
      // If system returns 0 for Aries, we need to handle it.
      // Let's safe check based on range.
      if (id === 0 && mahadashas.some(m => m.lord === 11)) return RASI_CLASS[1]; // If 0 and 11 exist, 0 is Aries?
      // Standardize: If id <= 11 and >= 0, treat as 0-indexed Rasi if mode is rasi?
      // Actually, constant.ts defines ARIES=0. So we should use 0-11 map.
      const rasiKey = (id % 12) + 1; // 0->1, 11->12
      return RASI_CLASS[rasiKey];
    }
    return PLANET_CLASS[id];
  };

  return (
    <div className={`dasha-table card ${coloringMode}-mode`}>
      <h3 className="dasha-title">{title}</h3>
      
      {balance && (
        <div className="dasha-balance">
          <span className="balance-label">Balance at Birth:</span>
          <span className="balance-value">
            {balance.years}y {balance.months}m {balance.days}d
          </span>
        </div>
      )}
      
      <div className="dasha-content">
        <div className="mahadasha-list">
          <div className="list-header">Mahadasha</div>
          {mahadashas.map((dasha, index) => (
            <div
              key={index}
              className={`mahadasha-item ${selectedDasha === dasha.lord ? 'active' : ''}`}
              onClick={() => onDashaSelect?.(dasha.lord)}
            >
              <span className={`dasha-lord ${getClass(dasha.lord) ?? ''}`}>
                {dasha.lordName}
              </span>
              <span className="dasha-duration">{dasha.durationYears}y</span>
              <span className="dasha-date">{formatDate(dasha.startDate)}</span>
            </div>
          ))}
        </div>
        
        {selectedBhuktis.length > 0 && (
          <div className="bhukti-list">
            <div className="list-header">Bhuktis</div>
            {selectedBhuktis.map((bhukti, index) => (
              <div key={index} className="bhukti-item">
                <span className={`bhukti-lord ${getClass(bhukti.bhuktiLord) ?? ''}`}>
                  {bhukti.bhuktiLordName}
                </span>
                <span className="bhukti-date">{formatDate(bhukti.startDate)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function formatDate(dateStr: string): string {
  // Extract just YYYY-MM-DD from full date string
  const match = dateStr.match(/^(\d{4}|\d+ BC)-(\d{2})-(\d{2})/);
  if (match) {
    return `${match[1]}-${match[2]}-${match[3]}`;
  }
  return dateStr;
}

export default DashaTable;
