import React, { useEffect, useState } from 'react';
import { getWeekPlan, getBestDay } from './api';
import { BestDayResponse, WeekPlan } from './types';
import { getBandColor } from './utils/colors';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useLanguage } from './LanguageContext';
import { Calendar, Search } from 'lucide-react';

export default function WeekView({ activeSchoolId = 'delhi-anand-vihar' }: { activeSchoolId?: string }) {
  const { lang, t } = useLanguage();
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
    return <div className="px-4 pt-6 space-y-3 animate-pulse"><div className="h-16 rounded-xl bg-stone-200/70" /><div className="h-52 rounded-2xl bg-stone-200/60" /></div>;
  }

  if (!weekData) return <p className="px-6 py-24 text-center text-sm text-rose-700">Could not load the week forecast. Please try again.</p>;

  return (
    <div className="pb-6">
      <header className="px-4 pt-5">
        <h1 className="text-xl font-semibold text-stone-900">{t('weekOverview')}</h1>
        <p className="text-xs text-stone-500 mt-0.5">{lang === 'hi' ? 'हर दिन का सबसे खराब स्कूल-समय AQI' : 'Worst school-hours AQI for each day'}</p>
      </header>

      <main className="px-4 mt-4 space-y-5">
        <section>
          <div className="grid gap-2" style={{ gridTemplateColumns: `repeat(${weekData.days.length}, minmax(0, 1fr))` }}>
            {weekData.days.map((day) => {
              const dateObj = new Date(day.date);
              const dayName = dateObj.toLocaleDateString(lang === 'hi' ? 'hi-IN' : 'en-US', { weekday: 'short' });
              const dayNum = dateObj.getDate();
              return (
                <div key={day.date} className={`flex flex-col items-center py-2.5 rounded-xl min-w-0 ${getBandColor(day.worst_band)}`}>
                  <span className="text-xs font-semibold opacity-80 uppercase">{dayName}</span>
                  <span className="text-lg font-black">{dayNum}</span>
                  <span className="text-xs font-bold mt-1 opacity-90">{day.worst_aqi}</span>
                </div>
              );
            })}
          </div>
        </section>

        <section className="bg-white p-4 rounded-2xl border border-stone-200/80">
          <h2 className="text-xs font-semibold text-stone-500 uppercase tracking-wider mb-3">{t('hourlyPm25Days')}</h2>
          <div className="h-52 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={weekData.hourly} margin={{ top: 4, right: 4, left: -18, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E7E5E4" />
                <XAxis
                  dataKey="time"
                  ticks={weekData.hourly.filter((h) => h.time.endsWith('T12:00')).map((h) => h.time)}
                  tickFormatter={(time: string) => new Date(time).toLocaleDateString(lang === 'hi' ? 'hi-IN' : 'en-US', { weekday: 'short' })}
                  tick={{ fontSize: 11, fill: '#78716C' }}
                  tickLine={false}
                />
                <YAxis tick={{ fontSize: 11, fill: '#78716C' }} tickLine={false} axisLine={false} />
                <Tooltip labelFormatter={(label) => String(label).replace('T', ' ')} formatter={(v) => [`${v} µg/m³`, 'PM2.5']} />
                <Line type="monotone" dataKey="pm25_cal" stroke="#0F766E" strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] text-stone-400 mt-1">
            Open-Meteo (CAMS) · {weekData.hourly.some((h) => h.calibrated) ? 'calibrated with the nearest station' : 'not calibrated'}
          </p>
        </section>

        <section className="bg-white p-4 rounded-2xl border border-stone-200/80">
          <div className="flex items-center gap-2 mb-4">
            <Calendar className="w-5 h-5 text-teal-700" />
            <h2 className="text-base font-semibold text-stone-900">{t('bestDayForEvent')}</h2>
          </div>
          <div className="flex gap-3 mb-4">
            <div className="flex-1">
              <label className="block text-xs font-medium text-stone-500 mb-1">{t('startTime')}</label>
              <select className="w-full bg-stone-50 border border-stone-200 rounded-lg p-2 text-sm font-medium" value={bestDayStart} onChange={(e) => setBestDayStart(e.target.value)}>
                <option value="08:00">08:00</option>
                <option value="09:00">09:00</option>
                <option value="10:00">10:00</option>
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-xs font-medium text-stone-500 mb-1">{t('endTime')}</label>
              <select className="w-full bg-stone-50 border border-stone-200 rounded-lg p-2 text-sm font-medium" value={bestDayEnd} onChange={(e) => setBestDayEnd(e.target.value)}>
                <option value="11:00">11:00</option>
                <option value="12:00">12:00</option>
                <option value="13:00">13:00</option>
              </select>
            </div>
          </div>
          <button 
            onClick={handleFindBestDay}
            className="w-full bg-teal-700 text-white font-medium py-2.5 rounded-xl hover:bg-teal-800 transition flex items-center justify-center gap-2"
          >
            {bestDayLoading ? <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span> : <Search className="w-4 h-4" />}
            {t('findBestDay')}
          </button>
          {bestDayError && <p className="text-sm text-red-600 mt-2">{bestDayError}</p>}

          {bestDayData && (
            <div className="mt-5 pt-5 border-t border-stone-100">
              <p className="text-sm text-stone-700 font-medium mb-4">
                {bestDayData.ranking[0]
                  ? `${new Date(bestDayData.ranking[0].date).toLocaleDateString(lang === 'hi' ? 'hi-IN' : 'en-IN', { weekday: 'long', day: 'numeric', month: 'short' })}: lowest maximum AQI (${bestDayData.ranking[0].max_aqi}) between ${bestDayStart} and ${bestDayEnd}.`
                  : bestDayData.reason}
              </p>
              <div className="space-y-2">
                {bestDayData.ranking.map((rank, i) => (
                  <div key={rank.date} className="flex justify-between items-center p-3 bg-stone-50 rounded-lg border border-stone-100">
                    <div className="flex items-center gap-3">
                      <span className="font-black text-stone-400 w-4">{i + 1}</span>
                      <div>
                        <p className="font-bold text-stone-900">{new Date(rank.date).toLocaleDateString('en-US', {weekday: 'short', month: 'short', day: 'numeric'})}</p>
                        <p className="text-xs text-stone-500">{rank.band} · mean {rank.mean_aqi}</p>
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
