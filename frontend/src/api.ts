/// <reference types="vite/client" />
import { BestDayResponse, DayPlan, WeekPlan } from './types';
import mockDayPlan from './mock/dayplan.json';
import mockWeek from './mock/week.json';
import mockBestDay from './mock/bestday.json';
import mockNoticeEn from './mock/notice_en.json';
import mockNoticeHi from './mock/notice_hi.json';

const USE_MOCK = true;
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const getDayPlan = async (schoolId: string, replayDate?: string): Promise<DayPlan> => {
  if (USE_MOCK) {
    return mockDayPlan as DayPlan;
  }
  
  const query = replayDate ? `?replay=${replayDate}` : '';
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

export const getNotice = async (schoolId: string, lang: 'en' | 'hi') => {
  if (USE_MOCK) {
    return lang === 'en' ? mockNoticeEn : mockNoticeHi;
  }
  const response = await fetch(`${API_URL}/schools/${schoolId}/notice?lang=${lang}&polish=false`);
  if (!response.ok) throw new Error('Failed to fetch notice');
  return response.json();
};
