import { DayPlan } from '../types';

export type BannerKind = 'replay' | 'fixture' | 'cached';
export interface Banner {
  kind: BannerKind;
  text: string;
}

/** Which data-honesty banner the Today screen must show for a plan (null = live data, no banner). */
export function modeBanner(plan: Pick<DayPlan, 'mode' | 'date' | 'generated_at' | 'replay_date'>): Banner | null {
  switch (plan.mode) {
    case 'replay':
      return { kind: 'replay', text: `Replay: recorded Delhi air from ${plan.replay_date ?? plan.date}` };
    case 'fixture':
      return { kind: 'fixture', text: "Sample data: the live forecast is unavailable right now. This is not today's air." };
    case 'cached': {
      const hhmm = /T(\d{2}:\d{2})/.exec(plan.generated_at)?.[1];
      return { kind: 'cached', text: `Plan prepared${hhmm ? ` at ${hhmm} IST` : ''} today by the daily job (cached forecast)` };
    }
    default:
      return null;
  }
}

export const BANNER_STYLE: Record<BannerKind, string> = {
  replay: 'bg-purple-600 text-white',
  fixture: 'bg-amber-500 text-white',
  cached: 'bg-stone-200 text-stone-800',
};
