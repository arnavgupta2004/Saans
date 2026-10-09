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

/** "Suggested swaps would move 40 students out of Very Poor air for 40 min (≈ 60% lower PM2.5 during PE)" — or null. */
export function impactText(plan: Pick<DayPlan, 'periods' | 'impact'>, lang: Lang): string | null {
  const im = plan.impact;
  if (!im || im.swaps === 0) return null;
  const moved = plan.periods.filter((p) => p.swap && !p.swap.optional);
  const allPe = moved.every((p) => p.period.type === 'pe');
  const outOf = im.student_hours_out_of_poor > 0 && im.worst_band_from;
  if (lang === 'hi') {
    const what = allPe ? 'PE के दौरान' : 'बदले गए पीरियड में';
    const move = outOf ? `${bandLabel(im.worst_band_from!, lang)} हवा से हटाएँगे` : 'साफ़ हवा में ले जाएँगे';
    return `सुझाए गए बदलाव ${im.students_moved} विद्यार्थियों को ${im.minutes} मिनट के लिए ${move} (${what} PM2.5 ≈ ${im.reduction_pct}% कम)`;
  }
  const what = allPe ? 'during PE' : 'during the moved periods';
  const where = outOf ? `out of ${im.worst_band_from} air` : 'to cleaner air';
  return `Suggested swaps would move ${im.students_moved} students ${where} for ${im.minutes} min (≈ ${im.reduction_pct}% lower PM2.5 ${what})`;
}

/** Plain-language formula for each counted swap, for the "How is this estimated?" expander. */
export function impactFormula(plan: Pick<DayPlan, 'periods'>): string[] {
  return plan.periods
    .filter((p) => p.swap && !p.swap.optional && p.swap.impact)
    .map((p) => {
      const i = p.swap!.impact!;
      const h = (i.minutes / 60).toFixed(2);
      return `${p.period.label}: (${i.pm25_before} − ${i.pm25_after}) µg/m³ × ${h} h × ${i.students} students = ${Math.round(i.exposure_avoided).toLocaleString('en-IN')} µg/m³·h`;
    });
}
