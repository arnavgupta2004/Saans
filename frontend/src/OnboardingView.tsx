import React, { useState } from 'react';
import { Period, School } from './types';
import { MapPin, Plus, Trash2, Save } from 'lucide-react';

const CITY_PRESETS = [
  { id: 'delhi-anand-vihar', label: 'Delhi – Anand Vihar', lat: 28.6469, lon: 77.3159 },
  { id: 'delhi-dwarka', label: 'Delhi – Dwarka', lat: 28.5823, lon: 77.0500 },
  { id: 'bengaluru-indiranagar', label: 'Bengaluru – Indiranagar', lat: 12.9784, lon: 77.6408 },
];

export default function OnboardingView({ activeSchoolId, onSave }: { activeSchoolId: string, onSave: (s: School) => void }) {
  const [name, setName] = useState('Demo School');
  const [cityPreset, setCityPreset] = useState(CITY_PRESETS[0].id);
  const [lat, setLat] = useState(CITY_PRESETS[0].lat);
  const [lon, setLon] = useState(CITY_PRESETS[0].lon);
  const [asthmaCount, setAsthmaCount] = useState(38);
  const [periods, setPeriods] = useState<Period[]>([
    { id: '1', label: 'Morning Assembly', start: '08:00', end: '08:30', type: 'assembly', intensity: 'low', outdoor: true, swappable: false },
    { id: '2', label: 'Class 7B PE', start: '08:40', end: '09:20', type: 'pe', intensity: 'high', outdoor: true, swappable: true },
  ]);

  const handleLocation = () => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition((pos) => {
        setLat(pos.coords.latitude);
        setLon(pos.coords.longitude);
        setCityPreset('custom');
      });
    }
  };

  const handleCityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setCityPreset(val);
    if (val !== 'custom') {
      const preset = CITY_PRESETS.find(p => p.id === val);
      if (preset) {
        setLat(preset.lat);
        setLon(preset.lon);
      }
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

  const updatePeriod = (id: string, field: keyof Period, value: any) => {
    setPeriods(periods.map(p => p.id === id ? { ...p, [field]: value } : p));
  };

  const handleSave = () => {
    onSave({
      id: activeSchoolId,
      name,
      city: cityPreset === 'custom' ? 'Custom Location' : CITY_PRESETS.find(p => p.id === cityPreset)?.label || '',
      lat,
      lon,
      timetable: periods,
      sensitive_count: asthmaCount,
      languages: ['en', 'hi']
    });
    alert('Settings saved! (Local only for demo)');
  };

  return (
    <div className="min-h-screen bg-slate-50 pb-24 w-full max-w-md mx-auto sm:rounded-2xl sm:my-8 relative">
      <header className="bg-white px-5 pt-6 pb-4 border-b border-slate-100">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">School Setup</h1>
      </header>

      <main className="px-5 mt-6 space-y-6">
        <section className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">School Name</label>
            <input type="text" value={name} onChange={e => setName(e.target.value)} className="w-full bg-white border border-slate-200 rounded-lg p-2.5 text-sm font-semibold" />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Location</label>
            <div className="flex gap-2">
              <select value={cityPreset} onChange={handleCityChange} className="flex-1 bg-white border border-slate-200 rounded-lg p-2.5 text-sm font-semibold">
                {CITY_PRESETS.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
                <option value="custom">Custom Location</option>
              </select>
              <button onClick={handleLocation} className="bg-slate-100 hover:bg-slate-200 p-2.5 rounded-lg text-slate-600 transition" title="Use my location">
                <MapPin className="w-5 h-5" />
              </button>
            </div>
            {cityPreset === 'custom' && (
              <p className="text-xs text-slate-400 mt-1">Lat: {lat.toFixed(4)}, Lon: {lon.toFixed(4)}</p>
            )}
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Students with Asthma</label>
            <input type="number" value={asthmaCount} onChange={e => setAsthmaCount(parseInt(e.target.value) || 0)} className="w-full bg-white border border-slate-200 rounded-lg p-2.5 text-sm font-semibold" />
            <p className="text-[10px] text-slate-400 mt-1 font-medium italic">Count only — no names or health records are stored.</p>
          </div>
        </section>

        <section>
          <div className="flex justify-between items-center mb-3">
            <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Timetable Editor</h2>
            <button onClick={addPeriod} className="text-blue-600 flex items-center gap-1 text-xs font-bold bg-blue-50 px-2 py-1 rounded-md">
              <Plus className="w-3 h-3" /> Add Row
            </button>
          </div>
          
          <div className="space-y-3">
            {periods.map((p, i) => (
              <div key={p.id} className="bg-white border border-slate-200 p-3 rounded-xl shadow-sm relative">
                <button onClick={() => removePeriod(p.id)} className="absolute top-2 right-2 text-slate-300 hover:text-red-500 transition">
                  <Trash2 className="w-4 h-4" />
                </button>
                <div className="grid grid-cols-2 gap-2 mb-2 pr-6">
                  <input type="text" value={p.label} onChange={e => updatePeriod(p.id, 'label', e.target.value)} placeholder="Period Label" className="col-span-2 bg-slate-50 border border-slate-100 rounded p-1.5 text-sm font-semibold w-full" />
                  <input type="time" value={p.start} onChange={e => updatePeriod(p.id, 'start', e.target.value)} className="bg-slate-50 border border-slate-100 rounded p-1.5 text-xs font-medium w-full" />
                  <input type="time" value={p.end} onChange={e => updatePeriod(p.id, 'end', e.target.value)} className="bg-slate-50 border border-slate-100 rounded p-1.5 text-xs font-medium w-full" />
                  <select value={p.type} onChange={e => updatePeriod(p.id, 'type', e.target.value)} className="bg-slate-50 border border-slate-100 rounded p-1.5 text-xs font-medium w-full">
                    <option value="class">Class</option>
                    <option value="pe">PE</option>
                    <option value="assembly">Assembly</option>
                    <option value="recess">Recess</option>
                    <option value="sports">Sports</option>
                  </select>
                  <select value={p.intensity} onChange={e => updatePeriod(p.id, 'intensity', e.target.value)} className="bg-slate-50 border border-slate-100 rounded p-1.5 text-xs font-medium w-full">
                    <option value="low">Low Intensity</option>
                    <option value="high">High Intensity</option>
                  </select>
                </div>
                <div className="flex gap-4 items-center">
                  <label className="flex items-center gap-1.5 text-xs font-medium text-slate-600">
                    <input type="checkbox" checked={p.outdoor} onChange={e => updatePeriod(p.id, 'outdoor', e.target.checked)} className="rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
                    Outdoor
                  </label>
                  <label className="flex items-center gap-1.5 text-xs font-medium text-slate-600">
                    <input type="checkbox" checked={p.swappable} onChange={e => updatePeriod(p.id, 'swappable', e.target.checked)} className="rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
                    Swappable
                  </label>
                </div>
              </div>
            ))}
          </div>
        </section>

        <button onClick={handleSave} className="w-full bg-blue-600 text-white font-bold py-3 rounded-xl hover:bg-blue-700 transition flex items-center justify-center gap-2">
          <Save className="w-5 h-5" /> Save Configuration
        </button>
      </main>
    </div>
  );
}
