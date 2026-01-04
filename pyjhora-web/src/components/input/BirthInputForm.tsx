/**
 * Birth Input Form Component
 * Form for entering birth date, time, and place
 */

import { useState } from 'react';
import './BirthInputForm.css';

interface BirthData {
  date: string;
  time: string;
  placeName: string;
  latitude: number;
  longitude: number;
  timezone: number;
}

interface BirthInputFormProps {
  onSubmit: (data: BirthData) => void;
  initialData?: Partial<BirthData>;
}

// Some preset places for quick selection
const PRESET_PLACES = [
  { name: 'Bangalore, India', lat: 12.972, lon: 77.594, tz: 5.5 },
  { name: 'Delhi, India', lat: 28.679, lon: 77.217, tz: 5.5 },
  { name: 'Mumbai, India', lat: 19.076, lon: 72.878, tz: 5.5 },
  { name: 'Chennai, India', lat: 13.083, lon: 80.27, tz: 5.5 },
  { name: 'New York, USA', lat: 40.714, lon: -74.006, tz: -5 },
  { name: 'London, UK', lat: 51.507, lon: -0.127, tz: 0 },
];

export function BirthInputForm({ onSubmit, initialData }: BirthInputFormProps) {
  const [date, setDate] = useState(initialData?.date ?? '2000-01-01');
  const [time, setTime] = useState(initialData?.time ?? '12:00');
  const [placeName, setPlaceName] = useState(initialData?.placeName ?? 'Bangalore, India');
  const [latitude, setLatitude] = useState(initialData?.latitude ?? 12.972);
  const [longitude, setLongitude] = useState(initialData?.longitude ?? 77.594);
  const [timezone, setTimezone] = useState(initialData?.timezone ?? 5.5);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handlePresetSelect = (preset: typeof PRESET_PLACES[0]) => {
    setPlaceName(preset.name);
    setLatitude(preset.lat);
    setLongitude(preset.lon);
    setTimezone(preset.tz);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      date,
      time,
      placeName,
      latitude,
      longitude,
      timezone
    });
  };

  return (
    <form className="birth-input-form card" onSubmit={handleSubmit}>
      <h3 className="form-title">Birth Details</h3>
      
      <div className="form-row">
        <div className="form-group">
          <label className="label" htmlFor="birth-date">Date</label>
          <input
            id="birth-date"
            type="date"
            className="input"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label className="label" htmlFor="birth-time">Time</label>
          <input
            id="birth-time"
            type="time"
            className="input"
            value={time}
            onChange={(e) => setTime(e.target.value)}
            required
          />
        </div>
      </div>
      
      <div className="form-group">
        <label className="label" htmlFor="place-select">Place</label>
        <select
          id="place-select"
          className="select"
          value={placeName}
          onChange={(e) => {
            const preset = PRESET_PLACES.find(p => p.name === e.target.value);
            if (preset) {
              handlePresetSelect(preset);
            }
          }}
        >
          {PRESET_PLACES.map(place => (
            <option key={place.name} value={place.name}>{place.name}</option>
          ))}
        </select>
      </div>
      
      <button
        type="button"
        className="btn btn-secondary toggle-advanced"
        onClick={() => setShowAdvanced(!showAdvanced)}
      >
        {showAdvanced ? 'Hide' : 'Show'} Coordinates
      </button>
      
      {showAdvanced && (
        <div className="advanced-fields animate-fadeIn">
          <div className="form-row">
            <div className="form-group">
              <label className="label" htmlFor="latitude">Latitude</label>
              <input
                id="latitude"
                type="number"
                className="input"
                value={latitude}
                onChange={(e) => setLatitude(parseFloat(e.target.value))}
                step="0.001"
                min="-90"
                max="90"
              />
            </div>
            
            <div className="form-group">
              <label className="label" htmlFor="longitude">Longitude</label>
              <input
                id="longitude"
                type="number"
                className="input"
                value={longitude}
                onChange={(e) => setLongitude(parseFloat(e.target.value))}
                step="0.001"
                min="-180"
                max="180"
              />
            </div>
          </div>
          
          <div className="form-group">
            <label className="label" htmlFor="timezone">Timezone (hours from UTC)</label>
            <input
              id="timezone"
              type="number"
              className="input"
              value={timezone}
              onChange={(e) => setTimezone(parseFloat(e.target.value))}
              step="0.5"
              min="-12"
              max="14"
            />
          </div>
        </div>
      )}
      
      <button type="submit" className="btn btn-primary submit-btn">
        Calculate Horoscope
      </button>
    </form>
  );
}

export default BirthInputForm;
