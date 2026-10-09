import React, { useState } from 'react';
import { Period, School } from './types';
import { saveSchool } from './api';
import { MapPin, Plus, Trash2, Save } from 'lucide-react';
import { useLanguage } from './LanguageContext';

const CITY_PRESETS = [
  { id: 'delhi-anand-vihar', label: 'Delhi – Anand Vihar', lat: 28.6469, lon: 77.3159 },
  { id: 'delhi-dwarka', label: 'Delhi – Dwarka', lat: 28.5823, lon: 77.0500 },
  { id: 'bengaluru-indiranagar', label: 'Bengaluru – Indiranagar', lat: 12.9784, lon: 77.6408 },
];

const DEFAULT_PERIODS: Period[] = [
  { id: '1', label: 'Morning Assembly', start: '08:00', end: '08:30', type: 'assembly', intensity: 'low', outdoor: true, swappable: false },
  { id: '2', label: 'Class 7B PE', start: '08:40', end: '09:20', type: 'pe', intensity: 'high', outdoor: true, swappable: true },
];

export default function OnboardingView({ activeSchoolId, onSave }: { activeSchoolId: string, onSave: (s: School) => void }) {
  const { lang } = useLanguage();
  const initialPreset = CITY_PRESETS.find(p => p.id === activeSchoolId) ?? CITY_PRESETS[0];
  const [name, setName] = useState('Demo School');
  const [cityPreset, setCityPreset] = useState(initialPreset.id);
  const [lat, setLat] = useState(initialPreset.lat);
  const [lon, setLon] = useState(initialPreset.lon);
  const [usingMyLocation, setUsingMyLocation] = useState(false);
  const [geoError, setGeoError] = useState<string | null>(null);
  const [asthmaCount, setAsthmaCount] = useState(38);
  const [saveState, setSaveState] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [periods, setPeriods] = useState<Period[]>(DEFAULT_PERIODS);

  const handleLocation = () => {
    setGeoError(null);
    if (!('geolocation' in navigator)) {
      setGeoError('Geolocation is not available in this browser.');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLat(pos.coords.latitude);
        setLon(pos.coords.longitude);
        setUsingMyLocation(true);
      },
      () => {
        setGeoError('Could not read location. Choose a city preset instead.');
      },
    );
  };

  const handleCityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setCityPreset(val);
    setUsingMyLocation(false);
    const preset = CITY_PRESETS.find(p => p.id === val);
    if (preset) {
      setLat(preset.lat);
      setLon(preset.lon);
    }
  };

  const addPeriod = () => {
    setPeriods([...periods, {
      id: Date.now().toString(),
      label: 'New Period',
      start: '10:00',
      end: '10:40',
      type: 'class',
      intensity: 'low',
      outdoor: false,
      swappable: true
    }]);
  };

  const removePeriod = (id: string) => {
    setPeriods(periods.filter(p => p.id !== id));
  };

  const updatePeriod = (id: string, field: keyof Period, value: Period[keyof Period]) => {
    setPeriods(periods.map(p => p.id === id ? { ...p, [field]: value } : p));
  };

  const handleSave = async () => {
    // Demo schools are read-only on the server; a new school gets its own id.
    const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'school';
    const school: School = {
      id: `custom-${slug}`,
      name,
      city: usingMyLocation
        ? 'My location'
        : CITY_PRESETS.find(p => p.id === cityPreset)?.label || '',
      lat,
      lon,
      timetable: periods,
      sensitive_count: asthmaCount,
      languages: ['en', 'hi']
    };
    setSaveState('saving');
    try {
      const saved = await saveSchool(school);
      onSave(saved);
      setSaveState('saved');
    } catch {
      setSaveState('error');
    }
  };

  return (
    <div className="pb-6">
      <header className="px-4 pt-5">
        <h1 className="text-xl font-semibold text-stone-900">{lang === 'hi' ? 'स्कूल सेटअप' : 'School setup'}</h1>
        <p className="text-xs text-stone-500 mt-0.5">{lang === 'hi' ? 'स्थान, बाहरी समय-सारणी और अस्थमा वाले विद्यार्थियों की संख्या (केवल संख्या)।' : 'Location, outdoor timetable and number of students with asthma (a count only).'}</p>
      </header>

      <main className="px-4 mt-4 space-y-6">
        <section className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-stone-500 uppercase tracking-wider mb-1">School Name</label>
            <input type="text" value={name} onChange={e => setName(e.target.value)} className="w-full bg-white border border-stone-200 rounded-lg p-2.5 text-sm font-semibold" />
          </div>

          <div>
            <label className="block text-xs font-bold text-stone-500 uppercase tracking-wider mb-1">Location</label>
            <select value={cityPreset} onChange={handleCityChange} className="w-full bg-white border border-stone-200 rounded-lg p-2.5 text-sm font-semibold">
              {CITY_PRESETS.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
            </select>
            <button
              type="button"
              onClick={handleLocation}
              className="mt-2 w-full bg-stone-100 hover:bg-stone-200 p-2.5 rounded-lg text-stone-700 text-sm font-semibold transition flex items-center justify-center gap-2"
            >
              <MapPin className="w-4 h-4" />
              Use my location
            </button>
            {usingMyLocation && (
              <p className="text-xs text-stone-400 mt-1">Lat: {lat.toFixed(4)}, Lon: {lon.toFixed(4)}</p>
            )}
            {geoError && <p className="text-xs text-red-600 mt-1">{geoError}</p>}
          </div>

          <div>
            <label className="block text-xs font-bold text-stone-500 uppercase tracking-wider mb-1">Students with Asthma</label>
            <input type="number" min={0} value={asthmaCount} onChange={e => setAsthmaCount(parseInt(e.target.value) || 0)} className="w-full bg-white border border-stone-200 rounded-lg p-2.5 text-sm font-semibold" />
            <p className="text-[10px] text-stone-400 mt-1 font-medium italic">count only — no names or health records</p>
          </div>
        </section>

        <section>
          <div className="flex justify-between items-center mb-3">
            <h2 className="text-xs font-bold text-stone-500 uppercase tracking-wider">Timetable Editor</h2>
            <button type="button" onClick={addPeriod} className="text-teal-700 flex items-center gap-1 text-xs font-bold bg-teal-50 px-2 py-1 rounded-md">
              <Plus className="w-3 h-3" /> Add Row
            </button>
          </div>
          
          <div className="space-y-3">
            {periods.map((p) => (
              <div key={p.id} className="bg-white border border-stone-200 p-3 rounded-xl shadow-sm relative">
                <button type="button" onClick={() => removePeriod(p.id)} className="absolute top-2 right-2 text-stone-300 hover:text-red-500 transition" aria-label="Remove period">
                  <Trash2 className="w-4 h-4" />
                </button>
                <div className="grid grid-cols-2 gap-2 mb-2 pr-6">
                  <input type="text" value={p.label} onChange={e => updatePeriod(p.id, 'label', e.target.value)} placeholder="Period Label" className="col-span-2 bg-stone-50 border border-stone-100 rounded p-1.5 text-sm font-semibold w-full" />
                  <label className="text-[10px] font-bold text-stone-400 uppercase">
                    Start
                    <input type="time" value={p.start} onChange={e => updatePeriod(p.id, 'start', e.target.value)} className="mt-0.5 bg-stone-50 border border-stone-100 rounded p-1.5 text-xs font-medium w-full text-stone-800" />
                  </label>
                  <label className="text-[10px] font-bold text-stone-400 uppercase">
                    End
                    <input type="time" value={p.end} onChange={e => updatePeriod(p.id, 'end', e.target.value)} className="mt-0.5 bg-stone-50 border border-stone-100 rounded p-1.5 text-xs font-medium w-full text-stone-800" />
                  </label>
                  <label className="text-[10px] font-bold text-stone-400 uppercase">
                    Type
                    <select value={p.type} onChange={e => updatePeriod(p.id, 'type', e.target.value as Period['type'])} className="mt-0.5 bg-stone-50 border border-stone-100 rounded p-1.5 text-xs font-medium w-full text-stone-800">
                      <option value="class">Class</option>
                      <option value="pe">PE</option>
                      <option value="assembly">Assembly</option>
                      <option value="recess">Recess</option>
                      <option value="sports">Sports</option>
                    </select>
                  </label>
                  <label className="text-[10px] font-bold text-stone-400 uppercase">
                    Intensity
                    <select value={p.intensity} onChange={e => updatePeriod(p.id, 'intensity', e.target.value as Period['intensity'])} className="mt-0.5 bg-stone-50 border border-stone-100 rounded p-1.5 text-xs font-medium w-full text-stone-800">
                      <option value="low">Low</option>
                      <option value="high">High</option>
                    </select>
                  </label>
                </div>
                <div className="flex gap-4 items-center">
                  <label className="flex items-center gap-1.5 text-xs font-medium text-stone-600">
                    <input type="checkbox" checked={p.outdoor} onChange={e => updatePeriod(p.id, 'outdoor', e.target.checked)} className="rounded border-stone-300 text-teal-700 focus:ring-teal-500" />
                    Outdoor
                  </label>
                  <label className="flex items-center gap-1.5 text-xs font-medium text-stone-600">
                    <input type="checkbox" checked={p.swappable} onChange={e => updatePeriod(p.id, 'swappable', e.target.checked)} className="rounded border-stone-300 text-teal-700 focus:ring-teal-500" />
                    Swappable
                  </label>
                </div>
              </div>
            ))}
          </div>
        </section>

        <button type="button" onClick={handleSave} disabled={saveState === 'saving'} className="w-full bg-teal-700 text-white font-bold py-3 rounded-xl hover:bg-teal-800 transition flex items-center justify-center gap-2 disabled:opacity-60">
          <Save className="w-5 h-5" /> {saveState === 'saving' ? 'Saving…' : 'Save Configuration'}
        </button>
        {saveState === 'saved' && <p className="text-center text-sm text-emerald-700 font-medium">Saved as a new school. The three demo schools stay unchanged.</p>}
        {saveState === 'error' && <p className="text-center text-sm text-red-600 font-medium">Could not save school.</p>}
      </main>
    </div>
  );
}
