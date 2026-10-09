import { DayPlan, HourPoint, PeriodPlan } from '../types';

type Lang = 'en' | 'hi';

export const BAND_HI: Record<string, string> = {
  Good: 'अच्छी', Satisfactory: 'संतोषजनक', Moderate: 'मध्यम', Poor: 'खराब', 'Very Poor': 'बहुत खराब', Severe: 'गंभीर', 'No data': 'डेटा नहीं',
};

export const bandLabel = (band: string, lang: Lang) => (lang === 'hi' ? BAND_HI[band] ?? band : band);

export const outdoorPeriods = (plan: Pick<DayPlan, 'periods'>) => plan.periods.filter((p) => p.period.outdoor);

/** One-line verdict for the Today header. Counts come straight from the planner's action levels. */
export function verdict(plan: Pick<DayPlan, 'periods'>, lang: Lang): { tone: 'go' | 'caution' | 'indoors'; text: string } {
  const outdoor = outdoorPeriods(plan);
  const changes = outdoor.filter((p) => p.action.level === 'indoors').length;
  const careful = outdoor.filter((p) => p.action.level === 'caution').length;
  if (changes > 0) {
    return { tone: 'indoors', text: lang === 'hi' ? `आज ${changes} बदलाव ज़रूरी` : `${changes} ${changes === 1 ? 'change' : 'changes'} needed today` };
  }
  if (careful > 0) {
    return { tone: 'caution', text: lang === 'hi' ? `कोई बदलाव नहीं · ${careful} में सावधानी` : `No changes needed · ${careful} with precautions` };
  }
  return { tone: 'go', text: lang === 'hi' ? 'सभी बाहरी गतिविधियाँ ठीक हैं' : 'All outdoor activities can go ahead' };
}

/** NAQI caps at 500. Above that, say so and show the concentration that is off the scale. */
export function aqiDisplay(now: Pick<HourPoint, 'aqi' | 'pm25_cal' | 'pm10_cal'>): { value: string; beyond: string | null } {
  if (now.aqi < 500) return { value: String(now.aqi), beyond: null };
  const parts: string[] = [];
  if (now.pm10_cal > 500) parts.push(`PM10 ${Math.round(now.pm10_cal)} µg/m³`);
  if (now.pm25_cal > 350) parts.push(`PM2.5 ${Math.round(now.pm25_cal)} µg/m³`);
  return { value: '500+', beyond: parts.length ? `${parts.join(', ')} — beyond the AQI scale` : 'Beyond the AQI scale' };
}

/** "Class 7B PE 08:40 ⇄ Period 8 13:40 · AQI 351 → 127" */
export const swapText = (p: PeriodPlan) =>
  p.swap ? `${p.period.label} ${p.period.start} ⇄ ${p.swap.with_label ?? 'slot'} ${p.swap.to_start} · AQI ${p.aqi} → ${p.swap.to_aqi}` : '';

/** Deterministic plan summary (same content as the backend's fallback answer); every number is from the plan. */
export function planSummary(plan: DayPlan, lang: Lang): string {
  const hi = lang === 'hi';
  const when = plan.mode === 'replay'
    ? (hi ? `${plan.replay_date ?? plan.date} का रिकॉर्ड किया गया डेटा` : `recorded data from ${plan.replay_date ?? plan.date}`)
    : `${plan.date}`;
  const lines = [`${hi ? 'आज की योजना' : "Today's plan"} (${when}):`];
  for (const p of outdoorPeriods(plan)) {
    const text = hi ? p.action.text_hi : p.action.text_en;
    let line = `• ${p.period.label} ${p.period.start}–${p.period.end}: AQI ${p.aqi} (${bandLabel(p.band, lang)}) — ${text}`;
    if (p.swap && !p.swap.optional) line += ` ⇄ ${p.swap.with_label} ${p.swap.to_start} (AQI ${p.swap.to_aqi})`;
    lines.push(line);
  }
  return lines.join('\n');
}
