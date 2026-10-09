import React, { useEffect, useState } from 'react';
import { getWeekPlan, getBestDay } from './api';
import { BestDayResponse, WeekPlan } from './types';
import { getBandColor } from './utils/colors';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Calendar, Search } from 'lucide-react';

export default function WeekView({ activeSchoolId = 'delhi-anand-vihar' }: { activeSchoolId?: string }) {
  const [weekData, setWeekData] = useState<WeekPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [bestDayStart, setBestDayStart] = useState('09:00');
  const [bestDayEnd, setBestDayEnd] = useState('12:00');
  const [bestDayData, setBestDayData] = useState<BestDayResponse | null>(null);
  const [bestDayLoading, setBestDayLoading] = useState(false);
  const [bestDayError, setBestDayError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWeek = async () => {
      setLoading(true);
      try {
        const data = await getWeekPlan(activeSchoolId);
        setWeekData(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchWeek();
  }, [activeSchoolId]);

  const handleFindBestDay = async () => {
    setBestDayLoading(true);
    setBestDayError(null);
    try {
      const data = await getBestDay(activeSchoolId, bestDayStart, bestDayEnd);
      setBestDayData(data);
    } catch (err) {
      console.error(err);
      setBestDayError('Could not load best-day ranking');
    } finally {
      setBestDayLoading(false);
    }
  };

  if (loading) {
    return <div className="flex h-screen items-center justify-center bg-slate-50"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div></div>;
  }

  if (!weekData) return null;

  return (
    <div className="min-h-screen bg-slate-50 pb-20 w-full max-w-md mx-auto shadow-xl overflow-hidden sm:rounded-2xl sm:my-8 border border-slate-200">
      <header className="bg-white px-5 pt-6 pb-5 border-b border-slate-100">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Week Overview</h1>
      </header>

      <main className="px-5 mt-6 space-y-6">
        <section>
          <h2 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-3">5-Day Forecast</h2>
          <div className="flex justify-between space-x-2">
            {weekData.days.map((day) => {
              const dateObj = new Date(day.date);
              const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short' });
              const dayNum = dateObj.getDate();
              return (
                <div key={day.date} className={`flex-1 flex flex-col items-center p-2 rounded-xl border border-transparent shadow-sm ${getBandColor(day.worst_band)}`}>
                  <span className="text-xs font-semibold opacity-80 uppercase">{dayName}</span>
                  <span className="text-lg font-black">{dayNum}</span>
                  <span className="text-xs font-bold mt-1 opacity-90">{day.worst_aqi}</span>
                </div>
              );
            })}
          </div>
        </section>

        <section className="bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
          <h2 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Hourly PM2.5 (Today)</h2>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={weekData.hourly}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="time" tickFormatter={(time: string) => new Date(time).toLocaleTimeString([], {hour: '2-digit'})} tick={{fontSize: 12, fill: '#64748B'}} />
                <YAxis tick={{fontSize: 12, fill: '#64748B'}} />
                <Tooltip labelFormatter={(label) => new Date(String(label)).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} />
                <Legend iconType="circle" wrapperStyle={{fontSize: '12px'}} />
                <Line type="monotone" dataKey="pm25" name="Raw PM2.5" stroke="#94A3B8" strokeWidth={2} dot={false} strokeDasharray="5 5" />
                <Line type="monotone" dataKey="pm25_cal" name="Calibrated" stroke="#0EA5E9" strokeWidth={3} dot={{r: 4}} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
          <div className="flex items-center gap-2 mb-4">
            <Calendar className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-bold text-slate-900">Best Day for Event</h2>
          </div>
          <div className="flex gap-3 mb-4">
            <div className="flex-1">
              <label className="block text-xs font-semibold text-slate-500 mb-1">Start Time</label>
              <select className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm font-medium" value={bestDayStart} onChange={(e) => setBestDayStart(e.target.value)}>
                <option value="08:00">08:00</option>
                <option value="09:00">09:00</option>
                <option value="10:00">10:00</option>
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-xs font-semibold text-slate-500 mb-1">End Time</label>
              <select className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm font-medium" value={bestDayEnd} onChange={(e) => setBestDayEnd(e.target.value)}>
                <option value="11:00">11:00</option>
                <option value="12:00">12:00</option>
                <option value="13:00">13:00</option>
              </select>
            </div>
          </div>
          <button 
            onClick={handleFindBestDay}
            className="w-full bg-blue-600 text-white font-bold py-2.5 rounded-xl hover:bg-blue-700 transition flex items-center justify-center gap-2"
          >
            {bestDayLoading ? <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span> : <Search className="w-4 h-4" />}
            Find Best Day
          </button>
          {bestDayError && <p className="text-sm text-red-600 mt-2">{bestDayError}</p>}

          {bestDayData && (
            <div className="mt-5 pt-5 border-t border-slate-100">
              <p className="text-sm text-slate-700 font-medium mb-4">{bestDayData.reason}</p>
              <div className="space-y-2">
                {bestDayData.ranking.map((rank, i) => (
                  <div key={rank.date} className="flex justify-between items-center p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="flex items-center gap-3">
                      <span className="font-black text-slate-400 w-4">{i + 1}</span>
                      <div>
                        <p className="font-bold text-slate-900">{new Date(rank.date).toLocaleDateString('en-US', {weekday: 'short', month: 'short', day: 'numeric'})}</p>
                        <p className="text-xs text-slate-500">{rank.band} · mean {rank.mean_aqi}</p>
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded-md text-xs font-bold ${getBandColor(rank.band)}`}>
                      AQI {rank.max_aqi}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
