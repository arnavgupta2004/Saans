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

export interface Swap {
  to_start: string;
  to_end: string;
  to_aqi: number;
  to_band: string;
  gain_bands: number;
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
}
