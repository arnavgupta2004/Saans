import React, { useEffect, useState } from 'react';
import { getDayPlan } from './api';
import { DayPlan, PeriodPlan } from './types';
import { getBandColor, getActionColor } from './utils/colors';
import { Clock, AlertTriangle, ArrowRightLeft, Wind, MapPin, Info } from 'lucide-react';

export default function TodayView() {
  const [plan, setPlan] = useState<DayPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlan = async () => {
      try {
        const data = await getDayPlan('demo-delhi');
        setPlan(data);
      } catch (err) {
        setError('Could not load plan');
      } finally {
        setLoading(false);
      }
    };
    fetchPlan();
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !plan) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 p-4 text-center text-red-600">
        {error || 'No plan available'}
      </div>
    );
  }

  const { now, periods, sources } = plan;

  return (
    <div className="min-h-screen bg-slate-50 pb-12 w-full max-w-md mx-auto shadow-xl overflow-hidden sm:rounded-2xl sm:my-8 border border-slate-200 relative">
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

      {/* Main Content */}
      <main className="px-5 mt-6 space-y-4 relative z-0">
        <h2 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">Outdoor Schedule</h2>
        
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

            {/* Swap Suggestion */}
            {p.swap && (
              <div className="px-4 py-3 bg-blue-50/80 border-t border-blue-100">
                <div className="flex items-center gap-3">
                  <div className="bg-blue-100 p-2 rounded-full shrink-0">
                    <ArrowRightLeft className="w-4 h-4 text-blue-700" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-blue-900">
                      Swap to {p.swap.to_start} 
                      <span className="text-blue-700 font-normal ml-1">(AQI drops to {p.swap.to_aqi})</span>
                    </p>
                    <button className="mt-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 py-1.5 px-3 rounded-md transition-colors shadow-sm">
                      Apply Swap
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </main>

      {/* Footer */}
      <footer className="mt-8 px-6 text-center pb-6">
        <p className="text-xs text-slate-400 font-medium">
          Source: {sources.forecast} forecast calibrated with {sources.observation} 
          {sources.station ? ` (${sources.station})` : ''}
        </p>
        <p className="text-[10px] text-slate-300 mt-1">
          Last updated: {new Date(plan.generated_at).toLocaleString()}
        </p>
      </footer>
    </div>
  );
}
