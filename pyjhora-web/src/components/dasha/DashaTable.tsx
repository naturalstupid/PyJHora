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

export function DashaTable({ 
  title = 'Vimsottari Dasha',
  mahadashas, 
  bhuktis,
  balance,
  selectedDasha,
  onDashaSelect 
}: DashaTableProps) {
  // Get bhuktis for selected dasha
  const selectedBhuktis = selectedDasha !== undefined && bhuktis
    ? bhuktis.filter(b => b.dashaLord === selectedDasha)
    : [];

  return (
    <div className="dasha-table card">
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
              <span className={`dasha-lord ${PLANET_CLASS[dasha.lord] ?? ''}`}>
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
                <span className={`bhukti-lord ${PLANET_CLASS[bhukti.bhuktiLord] ?? ''}`}>
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
