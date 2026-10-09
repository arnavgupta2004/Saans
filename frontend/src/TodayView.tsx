import React, { useEffect, useState } from 'react';
import { getDayPlan, REPLAY_KEY } from './api';
import { DayPlan, PeriodPlan } from './types';
import { getBandColor, getActionColor } from './utils/colors';
import { modeBanner, BANNER_STYLE } from './utils/banner';
import { Clock, AlertTriangle, ArrowRightLeft, Wind, MapPin, Info } from 'lucide-react';

/** e.g. "Class 7B PE 08:40 ⇄ Period 8 13:40 · AQI 351 → 127" */
const swapText = (p: PeriodPlan) =>
  `${p.period.label} ${p.period.start} ⇄ ${p.swap?.with_label ?? 'slot'} ${p.swap?.to_start} · AQI ${p.aqi} → ${p.swap?.to_aqi}`;

export default function TodayView({
  activeSchoolId = 'delhi-anand-vihar',
  replay = false,
  setReplay = () => {},
}: { activeSchoolId?: string; replay?: boolean; setReplay?: (v: boolean) => void }) {
  const [plan, setPlan] = useState<DayPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    const fetchPlan = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getDayPlan(activeSchoolId, replay ? REPLAY_KEY : undefined);
        setPlan(data);
      } catch (err) {
        setError('Could not load plan');
      } finally {
        setLoading(false);
      }
    };
    fetchPlan();
  }, [activeSchoolId, replay, retry]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !plan) {
    // Never a blank screen: explain, offer a retry, and point to the recorded replay day.
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-3 bg-slate-50 p-6 text-center">
        <p className="text-red-600 font-semibold">{error || 'No plan available'}</p>
        <p className="text-sm text-slate-500">The Saans server could not be reached. Follow your school's standard air-quality protocol meanwhile.</p>
        <button onClick={() => setRetry((n) => n + 1)} className="text-sm font-bold text-white bg-blue-600 rounded-md px-4 py-2">Retry</button>
      </div>
    );
  }

  const { now, periods, sources } = plan;
  const banner = modeBanner(plan);

  return (
    <div className="min-h-screen bg-slate-50 pb-12 w-full max-w-md mx-auto shadow-xl overflow-hidden sm:rounded-2xl sm:my-8 border border-slate-200 relative">
      {banner && (
        <div className={`${BANNER_STYLE[banner.kind]} px-5 py-2.5 text-sm font-semibold flex items-center justify-between gap-3`} role="status">
          <span>{banner.text}</span>
          {banner.kind === 'replay' && (
            <button onClick={() => setReplay(false)} className="text-xs underline underline-offset-2 shrink-0">Back to live</button>
          )}
        </div>
      )}
      {/* Header Banner */}
      <header className="bg-white px-5 pt-6 pb-5 rounded-b-3xl shadow-sm relative z-10">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Today at School</h1>
            <p className="text-sm font-medium text-slate-500 mt-1 flex items-center">
              <MapPin className="w-3 h-3 mr-1 inline" /> 
              {plan.date} • Delhi
            </p>
          </div>
          {plan.mode === 'replay' && (
            <span className="bg-purple-100 text-purple-700 text-[10px] uppercase tracking-wider font-bold px-2 py-1 rounded-full">
              Replay
            </span>
          )}
        </div>

        {/* Current AQI Hero */}
        {now && (
          <div className={`mt-2 p-5 rounded-2xl flex items-center justify-between ${getBandColor(now.band)} shadow-sm`}>
            <div>
              <p className="text-sm font-semibold opacity-90 uppercase tracking-wide">Current Air Quality</p>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-5xl font-black tracking-tighter">{now.aqi}</span>
                <span className="text-lg font-bold opacity-90">{now.band}</span>
              </div>
            </div>
            <Wind className="w-12 h-12 opacity-80" />
          </div>
        )}
      </header>

      {!replay && (
        <div className="px-5 mt-4 text-right">
          <button onClick={() => setReplay(true)} className="text-xs font-semibold text-purple-700 underline underline-offset-2">
            Try a bad-air day
          </button>
        </div>
      )}

      {/* Main Content */}
      <main className="px-5 mt-6 space-y-4 relative z-0">
        <h2 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">Outdoor Schedule</h2>
        
        {periods.length === 0 && (
          <p className="text-sm text-slate-500">No periods in this school's timetable yet. Add them under Setup.</p>
        )}
        {periods.map((p: PeriodPlan) => (
          <div key={p.period.id} className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden transition-all hover:shadow-md">
            {/* Top row: Time + Activity */}
            <div className="px-4 pt-4 pb-3 flex justify-between items-center">
              <div>
                <h3 className="font-bold text-slate-900 text-lg">{p.period.label}</h3>
                <p className="text-slate-500 text-sm flex items-center mt-0.5 font-medium">
                  <Clock className="w-3.5 h-3.5 mr-1.5" />
                  {p.period.start} - {p.period.end}
                </p>
              </div>
              <div className="flex flex-col items-end">
                <div className={`px-2.5 py-1 rounded-lg text-sm font-bold shadow-sm ${getBandColor(p.band)}`}>
                  AQI {p.aqi}
                </div>
              </div>
            </div>

            {/* Action Box */}
            <div className={`px-4 py-3 border-t ${getActionColor(p.action.level)}`}>
              <div className="flex items-start gap-2.5">
                <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5 opacity-80" />
                <div>
                  <p className="font-bold text-[15px]">{p.action.text_en}</p>
                  <p className="text-xs opacity-75 mt-1 font-medium flex items-center">
                    <Info className="w-3 h-3 mr-1 inline" /> 
                    Why: Forecast is {p.band} ({p.aqi}) during this hour.
                  </p>
                </div>
              </div>
            </div>

            {/* Sensitive Action */}
            {p.sensitive_action && (
              <div className="px-4 py-2.5 border-t border-slate-100 bg-slate-50/50">
                <p className="text-sm font-medium flex items-start gap-2 text-slate-700">
                  <span className="text-rose-500 font-bold shrink-0 mt-0.5">•</span>
                  {p.sensitive_action.text_en}
                </p>
              </div>
            )}

            {/* Swap Suggestion: required (indoors) is prominent; optional (caution) is softer */}
            {p.swap && (p.swap.optional ? (
              <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-100 flex items-center justify-between gap-3">
                <p className="text-xs text-slate-600">
                  <span className="font-semibold">Better slot available:</span> {swapText(p)}
                </p>
                <button className="text-xs font-semibold text-slate-600 border border-slate-300 hover:bg-slate-100 py-1 px-2.5 rounded-md shrink-0">
                  Optional swap
                </button>
              </div>
            ) : (
              <div className="px-4 py-3 bg-blue-50/80 border-t border-blue-100">
                <div className="flex items-center gap-3">
                  <div className="bg-blue-100 p-2 rounded-full shrink-0">
                    <ArrowRightLeft className="w-4 h-4 text-blue-700" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-blue-900">{swapText(p)}</p>
                    <button className="mt-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 py-1.5 px-3 rounded-md transition-colors shadow-sm">
                      Apply Swap
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ))}
      </main>

      {/* Footer */}
      <footer className="mt-8 px-6 text-center pb-6">
        <p className="text-xs text-slate-400 font-medium">
          {plan.mode === 'replay'
            ? `Source: recorded Open-Meteo data for ${plan.replay_date ?? plan.date} (not live, not calibrated)`
            : `Source: ${sources.forecast} forecast${now?.calibrated ? ` calibrated with ${sources.observation}${sources.station ? ` (${sources.station})` : ''}` : ' (not calibrated)'}`}
        </p>
        {plan.mode !== 'replay' && !now?.calibrated && sources.note && (
          <p className="text-[11px] text-amber-600 mt-1">{sources.note}</p>
        )}
        <p className="text-[10px] text-slate-300 mt-1">
          Last updated: {new Date(plan.generated_at).toLocaleString()}
        </p>
      </footer>
    </div>
  );
}
