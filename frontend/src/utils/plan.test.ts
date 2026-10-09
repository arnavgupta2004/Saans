import { describe, expect, it } from 'vitest';
import { aqiDisplay, impactFormula, impactText, planSummary, swapText, verdict } from './plan';
import { DayPlan, PeriodPlan } from '../types';

const action = (level: 'go' | 'caution' | 'indoors') => ({ level, text_en: `${level} text`, text_hi: `${level} हिंदी`, rule_id: 'R' });
const period = (id: string, label: string, start: string, outdoor: boolean, level: 'go' | 'caution' | 'indoors', aqi = 100, swap?: PeriodPlan['swap']): PeriodPlan => ({
  period: { id, label, start, end: start, type: outdoor ? 'pe' : 'class', intensity: 'high', outdoor, swappable: true },
  aqi, band: 'Moderate', action: action(level), sensitive_action: action(level), swap,
});

describe('verdict', () => {
  it('counts indoors actions as changes; ignores indoor classes', () => {
    const v = verdict({ periods: [period('a', 'PE', '08:40', true, 'indoors'), period('b', 'Asm', '08:00', true, 'indoors'), period('c', 'Maths', '09:20', false, 'go')] }, 'en');
    expect(v).toEqual({ tone: 'indoors', text: '2 changes needed today' });
  });
  it('singular, caution and all-clear', () => {
    expect(verdict({ periods: [period('a', 'PE', '08:40', true, 'indoors')] }, 'en').text).toBe('1 change needed today');
    expect(verdict({ periods: [period('a', 'PE', '08:40', true, 'caution')] }, 'en').text).toBe('No changes needed · 1 with precautions');
    expect(verdict({ periods: [period('a', 'PE', '08:40', true, 'go')] }, 'en').tone).toBe('go');
    expect(verdict({ periods: [period('a', 'PE', '08:40', true, 'indoors')] }, 'hi').text).toBe('आज 1 बदलाव ज़रूरी');
  });
});

describe('aqiDisplay', () => {
  it('shows the number below the cap', () => {
    expect(aqiDisplay({ aqi: 351, pm25_cal: 200, pm10_cal: 300 })).toEqual({ value: '351', beyond: null });
  });
  it('500+ with the off-scale concentration', () => {
    expect(aqiDisplay({ aqi: 500, pm25_cal: 122.9, pm10_cal: 603.5 })).toEqual({ value: '500+', beyond: 'PM10 604 µg/m³ — beyond the AQI scale' });
  });
});

describe('swapText / planSummary', () => {
  const swap = { to_start: '13:40', to_end: '14:20', to_aqi: 127, to_band: 'Moderate', gain_bands: 2, optional: false, with_period_id: 'p9', with_label: 'Period 8' };
  const pe = period('p1', 'Class 7B PE', '08:40', true, 'indoors', 351, swap);
  it('formats the exchange', () => {
    expect(swapText(pe)).toBe('Class 7B PE 08:40 ⇄ Period 8 13:40 · AQI 351 → 127');
  });
  it('summary lists outdoor periods with the required swap', () => {
    const plan = { periods: [pe], mode: 'replay', date: '2025-11-19', replay_date: '2025-11-19' } as unknown as DayPlan;
    expect(planSummary(plan, 'en')).toContain('Class 7B PE 08:40–08:40: AQI 351 (Moderate) — indoors text ⇄ Period 8 13:40 (AQI 127)');
    expect(planSummary(plan, 'en').startsWith("Today's plan (recorded data from 2025-11-19):")).toBe(true);
  });
});

describe('impactText', () => {
  const impact = { swaps: 1, students_moved: 40, minutes: 40, student_hours_out_of_poor: 26.67, exposure_avoided: 2684, reduction_pct: 60, worst_band_from: 'Very Poor' };
  const swap = { to_start: '13:40', to_end: '14:20', to_aqi: 127, to_band: 'Moderate', gain_bands: 2, optional: false, with_period_id: 'p9', with_label: 'Period 8',
    impact: { pm25_before: 167.8, pm25_after: 67.2, reduction_pct: 60, minutes: 40, students: 40, exposure_avoided: 2684, band_from: 'Very Poor', band_to: 'Moderate' } };
  const pe = period('p1', 'Class 7B PE', '08:40', true, 'indoors', 351, swap);
  it('says "would move" (a suggestion), out of the worst band, with the reduction', () => {
    expect(impactText({ periods: [pe], impact }, 'en')).toBe('Suggested swaps would move 40 students out of Very Poor air for 40 min (≈ 60% lower PM2.5 during PE)');
  });
  it('null when there are no counted swaps', () => {
    expect(impactText({ periods: [pe], impact: { ...impact, swaps: 0 } }, 'en')).toBeNull();
  });
  it('says "to cleaner air" when students stay in Poor air', () => {
    expect(impactText({ periods: [pe], impact: { ...impact, student_hours_out_of_poor: 0 } }, 'en')).toContain('to cleaner air');
  });
  it('shows the formula with the actual numbers', () => {
    expect(impactFormula({ periods: [pe] })).toEqual(['Class 7B PE: (167.8 − 67.2) µg/m³ × 0.67 h × 40 students = 2,684 µg/m³·h']);
  });
});
