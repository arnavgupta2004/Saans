export type PeriodType = 'assembly' | 'pe' | 'recess' | 'sports' | 'class';
export type Intensity = 'high' | 'low';
export type ActionLevel = 'go' | 'caution' | 'indoors';

export interface Period {
  id: string;
  label: string;
  start: string;
  end: string;
  type: PeriodType;
  intensity: Intensity;
  outdoor: boolean;
  swappable: boolean;
  grade?: string;
}

export interface School {
  id: string;
  name: string;
  city: string;
  lat: number;
  lon: number;
  timetable: Period[];
  sensitive_count: number;
  students_per_class?: number;
  languages: string[];
}

export interface HourPoint {
  time: string;
  pm25: number;
  pm10: number;
  pm25_cal: number;
  pm10_cal: number;
  aqi: number;
  band: string;
  calibrated: boolean;
}

export interface Action {
  level: ActionLevel;
  text_en: string;
  text_hi: string;
  rule_id: string;
}

/** Estimated outdoor PM2.5 exposure avoided if a swap is applied (indoor infiltration not modelled). */
export interface SwapImpact {
  pm25_before: number;
  pm25_after: number;
  reduction_pct: number;
  minutes: number;
  students: number;
  exposure_avoided: number;
  band_from: string;
  band_to: string;
}

/** Totals over suggested (non-optional) swaps — an estimate, not a measurement. */
export interface DayImpact {
  swaps: number;
  students_moved: number;
  minutes: number;
  student_hours_out_of_poor: number;
  exposure_avoided: number;
  reduction_pct: number;
  worst_band_from?: string | null;
}

export interface Swap {
  to_start: string;
  to_end: string;
  to_aqi: number;
  to_band: string;
  gain_bands: number;
  /** true = period is only 'caution'; a cleaner slot exists but the swap is a suggestion, not a safety action */
  optional?: boolean;
  /** the indoor class period this outdoor period exchanges slots with */
  with_period_id?: string | null;
  with_label?: string | null;
  impact?: SwapImpact | null;
}

export interface PeriodPlan {
  period: Period;
  aqi: number;
  band: string;
  action: Action;
  sensitive_action: Action;
  swap?: Swap;
}

export interface Sources {
  forecast: string;
  observation: string;
  station?: string;
  distance_km?: number;
  /** why the forecast is not calibrated, e.g. "Not calibrated: ...; nearest CPCB monitor via OpenAQ last reported 50 h ago" */
  note?: string | null;
}

export interface DayPlan {
  school_id: string;
  date: string;
  now?: HourPoint;
  periods: PeriodPlan[];
  worst_hour: string;
  best_hour: string;
  sources: Sources;
  mode: 'live' | 'cached' | 'fixture' | 'replay';
  generated_at: string;
  replay_date?: string | null;
  impact?: DayImpact;
}

/** GET /api/schools/{id}/week — planner owns AQI/band fields */
export interface WeekDaySummary {
  date: string;
  worst_aqi: number;
  worst_band: string;
  best_hour: string;
  worst_hour: string;
  impact?: DayImpact;
}

export interface WeekPlan {
  days: WeekDaySummary[];
  hourly: HourPoint[];
  impact?: DayImpact & { days_with_swaps: number };
}

/** GET /api/schools/{id}/best-day — ranking is produced by planner.best_day */
export interface BestDayRank {
  date: string;
  max_aqi: number;
  mean_aqi: number;
  band: string;
}

export interface BestDayResponse {
  ranking: BestDayRank[];
  reason: string;
}
