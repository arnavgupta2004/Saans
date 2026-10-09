import { describe, expect, it } from 'vitest';
import { modeBanner } from './banner';

const base = { date: '2026-10-09', generated_at: '2026-10-09T06:00:12+05:30', replay_date: null };

describe('modeBanner', () => {
  it('live: no banner', () => {
    expect(modeBanner({ ...base, mode: 'live' })).toBeNull();
  });
  it('replay: recorded date', () => {
    expect(modeBanner({ ...base, mode: 'replay', replay_date: '2025-11-19' })).toEqual({ kind: 'replay', text: 'Replay: recorded Delhi air, 19 Nov 2025' });
  });
  it('fixture (Open-Meteo down): says sample, not today', () => {
    const b = modeBanner({ ...base, mode: 'fixture' });
    expect(b?.kind).toBe('fixture');
    expect(b?.text).toContain("not today's air");
  });
  it('cached: shows when the daily job prepared it', () => {
    expect(modeBanner({ ...base, mode: 'cached' })?.text).toContain('06:00 IST');
  });
});
