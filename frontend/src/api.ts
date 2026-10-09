/// <reference types="vite/client" />
import { BestDayResponse, DayPlan, School, WeekPlan } from './types';
import mockDayPlan from './mock/dayplan.json';
import mockWeek from './mock/week.json';
import mockBestDay from './mock/bestday.json';
import mockNoticeEn from './mock/notice_en.json';
import mockNoticeHi from './mock/notice_hi.json';

const USE_MOCK = false;
/** Recorded severe-air day served by the backend (Delhi, 19 Nov 2025). */
export const REPLAY_KEY = 'delhi-nov';
const API_URL = `${(import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '')}/api`;

export const getDayPlan = async (schoolId: string, replay?: string): Promise<DayPlan> => {
  if (USE_MOCK) {
    return mockDayPlan as DayPlan;
  }
  
  const query = replay ? `?replay=${encodeURIComponent(replay)}` : '';
  const response = await fetch(`${API_URL}/schools/${schoolId}/today${query}`);
  if (!response.ok) {
    throw new Error('Failed to fetch day plan');
  }
  return response.json();
};

export const getWeekPlan = async (schoolId: string): Promise<WeekPlan> => {
  if (USE_MOCK) {
    return mockWeek as WeekPlan;
  }
  const response = await fetch(`${API_URL}/schools/${schoolId}/week`);
  if (!response.ok) throw new Error('Failed to fetch week plan');
  return response.json();
};

/** Ranking comes from planner.best_day. The UI must not sort or derive bands. */
export const getBestDay = async (
  schoolId: string,
  start: string,
  end: string,
): Promise<BestDayResponse> => {
  if (USE_MOCK) {
    return mockBestDay as BestDayResponse;
  }
  const params = new URLSearchParams({ start, end });
  const response = await fetch(`${API_URL}/schools/${schoolId}/best-day?${params}`);
  if (!response.ok) throw new Error('Failed to fetch best day');
  return response.json();
};

export const saveSchool = async (school: School): Promise<School> => {
  if (USE_MOCK) {
    return school;
  }
  const response = await fetch(`${API_URL}/schools`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(school),
  });
  if (!response.ok) throw new Error('Failed to save school');
  return response.json();
};

export const getNotice = async (schoolId: string, lang: 'en' | 'hi', replay?: string) => {
  if (USE_MOCK) {
    return lang === 'en' ? mockNoticeEn : mockNoticeHi;
  }
  const params = new URLSearchParams({ lang, polish: 'false', ...(replay ? { replay } : {}) });
  const response = await fetch(`${API_URL}/schools/${schoolId}/notice?${params}`);
  if (!response.ok) throw new Error('Failed to fetch notice');
  return response.json();
};

export interface AskResponse {
  answer: string;
  tools_used: string[];
  /** true = every number >= 20 in the answer was found in this request's planner/tool outputs */
  verified: boolean;
  /** true = the deterministic plan summary was returned instead of the model's answer */
  fallback?: boolean;
  /** model that answered (null when the deterministic plan summary was returned) */
  model?: string | null;
}

export const askSaans = async (schoolId: string, question: string, lang: 'en' | 'hi', replay?: string, signal?: AbortSignal): Promise<AskResponse> => {
  const response = await fetch(`${API_URL}/ask`, {
    signal,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ school_id: schoolId, question, lang, ...(replay ? { replay } : {}) }),
  });
  if (!response.ok) throw new AskError(response.status);
  return response.json();
};

/** Ask failure with the HTTP status, so the UI can explain rate limits (429) and too-long questions (422). */
export class AskError extends Error {
  constructor(public status: number) {
    super(`Ask failed (${status})`);
  }
}

export const MAX_QUESTION = 300;
