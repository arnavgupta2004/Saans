import React, { useEffect, useState } from 'react';
import { getDayPlan, REPLAY_KEY } from './api';
import { DayPlan, PeriodPlan } from './types';
import { getBandTextColor, getBandColor } from './utils/colors';
import { modeBanner, BANNER_STYLE } from './utils/banner';
import { aqiDisplay, bandLabel, outdoorPeriods, swapText, verdict } from './utils/plan';
import { useLanguage, TKey } from './LanguageContext';
import { CheckCircle2, AlertTriangle, Home, ArrowLeftRight, HeartPulse, Info, Clock, BookOpen } from 'lucide-react';

const LEVEL = {
  go: { icon: CheckCircle2, ring: 'text-emerald-600', bg: 'bg-emerald-50', text: 'text-emerald-900' },
  caution: { icon: AlertTriangle, ring: 'text-amber-600', bg: 'bg-amber-50', text: 'text-amber-900' },
  indoors: { icon: Home, ring: 'text-rose-600', bg: 'bg-rose-50', text: 'text-rose-900' },
} as const;

function PeriodCard({ p, lang, t }: { p: PeriodPlan; lang: 'en' | 'hi'; t: (k: TKey) => string }) {
  const L = LEVEL[p.action.level];
  const Icon = L.icon;
  const hi = lang === 'hi';
  return (
    <article data-testid="period-card" className="bg-white rounded-2xl border border-stone-200/80 overflow-hidden">
      <div className="px-4 pt-3.5 pb-3 flex items-start gap-3">
        <Icon className={`w-6 h-6 shrink-0 mt-0.5 ${L.ring}`} strokeWidth={2.2} aria-label={p.action.level} />
        <div className="min-w-0 flex-1">
          <div className="flex items-baseline justify-between gap-2">
            <h3 className="font-semibold text-stone-900 truncate">{p.period.label}</h3>
            <span className={`shrink-0 px-2 py-0.5 rounded-md text-xs font-semibold ${getBandColor(p.band)}`}>AQI {p.aqi}</span>
          </div>
          <p className="text-xs text-stone-500 flex items-center gap-1 mt-0.5">
            <Clock className="w-3 h-3" /> {p.period.start}–{p.period.end} · {bandLabel(p.band, lang)}
          </p>
          <p className={`mt-2 text-[15px] leading-snug font-medium ${L.text}`}>{hi ? p.action.text_hi : p.action.text_en}</p>
          {p.sensitive_action.level !== 'go' && (
            <p className="mt-1.5 text-[13px] text-stone-600 flex gap-1.5">
              <HeartPulse className="w-3.5 h-3.5 mt-0.5 shrink-0 text-rose-500" />
              <span><span className="font-medium">{t('studentsAsthma')}:</span> {hi ? p.sensitive_action.text_hi : p.sensitive_action.text_en}</span>
            </p>
          )}
        </div>
      </div>
      {p.swap && (p.swap.optional ? (
        <div className="px-4 py-2.5 bg-stone-50 border-t border-stone-200/80 text-[13px] text-stone-600 flex items-start gap-2">
          <ArrowLeftRight className="w-4 h-4 mt-0.5 shrink-0 text-stone-400" />
          <span><span className="font-medium">{t('betterSlot')}</span> · {swapText(p)}</span>
        </div>
      ) : (
        <div className="px-4 py-3 bg-sky-50 border-t border-sky-100 flex items-start gap-2.5">
          <ArrowLeftRight className="w-5 h-5 mt-0.5 shrink-0 text-sky-700" />
          <div>
            <p className="text-[11px] uppercase tracking-wide font-semibold text-sky-700">{t('suggestedSwap')}</p>
            <p className="text-sm font-semibold text-sky-950">{swapText(p)}</p>
          </div>
        </div>
      ))}
    </article>
  );
}

export default function TodayView({
  activeSchoolId = 'delhi-anand-vihar',
  replay = false,
  setReplay = () => {},
}: { activeSchoolId?: string; replay?: boolean; setReplay?: (v: boolean) => void }) {
  const { lang, t } = useLanguage();
  const [plan, setPlan] = useState<DayPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getDayPlan(activeSchoolId, replay ? REPLAY_KEY : undefined)
      .then((d) => { if (!cancelled) setPlan(d); })
      .catch(() => { if (!cancelled) setError('Could not load plan'); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [activeSchoolId, replay, retry]);

  if (loading && !plan) {
    return (
      <div className="px-4 pt-6 space-y-3 animate-pulse" aria-busy="true">
        <div className="h-36 rounded-3xl bg-stone-200/70" />
        <div className="h-24 rounded-2xl bg-stone-200/60" />
        <div className="h-24 rounded-2xl bg-stone-200/50" />
      </div>
    );
  }

  if (error || !plan) {
    // Never a blank screen: explain, offer a retry.
    return (
      <div className="flex flex-col items-center justify-center gap-3 px-6 py-24 text-center">
        <p className="text-rose-700 font-semibold">{error || 'No plan available'}</p>
        <p className="text-sm text-stone-500">The Saans server could not be reached. Follow your school's standard air-quality protocol meanwhile.</p>
        <button onClick={() => setRetry((n) => n + 1)} className="text-sm font-semibold text-white bg-stone-900 rounded-lg px-4 py-2">Retry</button>
      </div>
    );
  }

  const { now, sources } = plan;
  const banner = modeBanner(plan);
  const v = verdict(plan, lang);
  const outdoor = outdoorPeriods(plan);
  const indoorCount = plan.periods.length - outdoor.length;
  const shown = now ? aqiDisplay(now) : null;

  return (
    <div className={loading ? 'opacity-60 transition-opacity' : 'transition-opacity'}>
      {banner && (
        <div className={`${BANNER_STYLE[banner.kind]} px-4 py-2.5 text-sm font-medium flex items-center justify-between gap-3`} role="status">
          <span>{banner.text}</span>
          {banner.kind === 'replay' && (
            <button onClick={() => setReplay(false)} className="text-xs underline underline-offset-2 shrink-0">{t('backToLive')}</button>
          )}
        </div>
      )}

      {/* Hero: air now + verdict */}
      <section className="px-4 pt-5">
        <div className="bg-white rounded-3xl border border-stone-200/80 px-5 pt-4 pb-5">
          <div className="flex items-center justify-between text-xs text-stone-500">
            <span>{t('airNow')}{now ? ` · ${now.time.slice(11, 16)}` : ''}</span>
            <span>{plan.mode === 'replay' ? plan.replay_date : plan.date}</span>
          </div>
          {now && shown ? (
            <div className="mt-1 flex items-baseline gap-3">
              <span className={`text-6xl font-semibold tracking-tight tabular-nums ${getBandTextColor(now.band)}`}>{shown.value}</span>
              <span className={`text-lg font-medium ${getBandTextColor(now.band)}`}>{bandLabel(now.band, lang)}</span>
            </div>
          ) : (
            <p className="mt-2 text-stone-500">—</p>
          )}
          {shown?.beyond && <p className="text-xs text-stone-500 mt-0.5">{shown.beyond}</p>}
          <p className={`mt-3 text-base font-semibold ${v.tone === 'indoors' ? 'text-rose-700' : v.tone === 'caution' ? 'text-amber-700' : 'text-emerald-700'}`}>{v.text}</p>
        </div>
        {!replay && (
          <div className="mt-2 text-right">
            <button onClick={() => setReplay(true)} className="text-xs font-medium text-violet-700 underline underline-offset-2">{t('tryBadAir')}</button>
          </div>
        )}
      </section>

      {/* Outdoor activities */}
      <section className="px-4 mt-4 space-y-3">
        <h2 className="text-xs font-semibold text-stone-500 uppercase tracking-wider">{t('outdoorActivities')}</h2>
        {plan.periods.length === 0 && <p className="text-sm text-stone-500">No periods in this school's timetable yet. Add them under Setup.</p>}
        {outdoor.map((p) => <PeriodCard key={p.period.id} p={p} lang={lang} t={t} />)}
        {indoorCount > 0 && (
          <p className="flex items-center gap-2 text-sm text-stone-500 px-1">
            <BookOpen className="w-4 h-4" /> {indoorCount} {t('indoorClasses')}
          </p>
        )}
      </section>

      {/* Provenance */}
      <footer className="px-5 mt-6 pb-6 text-center space-y-1">
        <p className="text-xs text-stone-500">
          {plan.mode === 'replay'
            ? `Source: recorded Open-Meteo data for ${plan.replay_date ?? plan.date} (not live, not calibrated)`
            : `Source: Open-Meteo (CAMS) forecast${now?.calibrated ? ` calibrated with ${sources.station ?? sources.observation}` : ' · not calibrated'}`}
        </p>
        {plan.mode !== 'replay' && !now?.calibrated && sources.note && (
          <p className="text-[11px] text-amber-700 flex items-start justify-center gap-1"><Info className="w-3 h-3 mt-0.5 shrink-0" />{sources.note}</p>
        )}
        <p className="text-[11px] text-stone-400">Hourly indicator using CPCB NAQI breakpoints · updated {new Date(plan.generated_at).toLocaleString('en-IN', { hour: '2-digit', minute: '2-digit', day: 'numeric', month: 'short' })}</p>
      </footer>
    </div>
  );
}
