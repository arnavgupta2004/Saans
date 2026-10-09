/// <reference types="vite/client" />
import { DayPlan } from './types';
import mockDayPlan from './mock/dayplan.json';

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
