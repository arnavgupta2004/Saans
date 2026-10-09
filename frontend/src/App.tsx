import React, { useState } from 'react';
import TodayView from './TodayView';
import WeekView from './WeekView';
import NoticeView from './NoticeView';
import AskView from './AskView';
import OnboardingView from './OnboardingView';
import { LanguageProvider, useLanguage } from './LanguageContext';
import { Calendar, MessageSquare, Bell, CalendarDays, Globe, Settings } from 'lucide-react';
import { School } from './types';

const DEMO_SCHOOLS = [
  { id: 'delhi-anand-vihar', name: 'Delhi – Anand Vihar' },
  { id: 'delhi-dwarka', name: 'Delhi – Dwarka' },
  { id: 'bengaluru-indiranagar', name: 'Bengaluru – Indiranagar' },
];

function AppContent() {
  const [tab, setTab] = useState<'today' | 'week' | 'notice' | 'ask' | 'setup'>('today');
  const [activeSchoolId, setActiveSchoolId] = useState(DEMO_SCHOOLS[0].id);
  const [replay, setReplay] = useState(false); // shared by Today and Ask so both use the same context
  const { lang, setLang, t } = useLanguage();

  const renderContent = () => {
    switch (tab) {
      case 'today': return <TodayView activeSchoolId={activeSchoolId} replay={replay} setReplay={setReplay} />;
      case 'week': return <WeekView activeSchoolId={activeSchoolId} />;
      case 'notice': return <NoticeView activeSchoolId={activeSchoolId} />;
      case 'setup': return <OnboardingView activeSchoolId={activeSchoolId} onSave={(s: School) => console.log('Saved', s)} />;
      case 'ask': return <AskView activeSchoolId={activeSchoolId} replay={replay} />;
      default: return <TodayView activeSchoolId={activeSchoolId} replay={replay} setReplay={setReplay} />;
    }
  };

  return (
    <div className="relative min-h-screen bg-slate-100 flex justify-center">
      <div className="w-full max-w-md bg-slate-50 relative pb-16 shadow-2xl">
        <div className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-slate-200 px-3 py-2 flex items-center gap-2">
          <select 
            value={activeSchoolId}
            onChange={(e) => setActiveSchoolId(e.target.value)}
            aria-label="Demo school"
            className="flex-1 min-w-0 bg-slate-50 border border-slate-200 px-2 py-1.5 rounded-lg text-xs font-bold text-slate-700 outline-none"
          >
            {DEMO_SCHOOLS.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <button 
            onClick={() => setLang(lang === 'en' ? 'hi' : 'en')}
            className="shrink-0 flex items-center gap-1 bg-white border border-slate-200 px-3 py-1.5 rounded-lg text-xs font-bold text-slate-700 hover:bg-slate-50"
          >
            <Globe className="w-3.5 h-3.5" />
            {lang === 'en' ? 'हिंदी' : 'EN'}
          </button>
        </div>

        {renderContent()}

        <div className="fixed bottom-0 w-full max-w-md bg-white border-t border-slate-200 flex justify-around items-center h-16 pb-safe z-50 px-1 rounded-t-2xl shadow-[0_-4px_20px_-10px_rgba(0,0,0,0.1)]">
          <button onClick={() => setTab('today')} className={`flex flex-col items-center flex-1 py-2 ${tab === 'today' ? 'text-blue-600' : 'text-slate-400'}`}>
            <Calendar className={`w-5 h-5 mb-1 ${tab === 'today' ? 'fill-blue-50 text-blue-600' : ''}`} strokeWidth={tab === 'today' ? 2.5 : 2} />
            <span className="text-[9px] font-bold">{t('today')}</span>
          </button>
          
          <button onClick={() => setTab('week')} className={`flex flex-col items-center flex-1 py-2 ${tab === 'week' ? 'text-blue-600' : 'text-slate-400'}`}>
            <CalendarDays className={`w-5 h-5 mb-1 ${tab === 'week' ? 'fill-blue-50 text-blue-600' : ''}`} strokeWidth={tab === 'week' ? 2.5 : 2} />
            <span className="text-[9px] font-bold">{t('week')}</span>
          </button>
          
          <button onClick={() => setTab('notice')} className={`flex flex-col items-center flex-1 py-2 ${tab === 'notice' ? 'text-blue-600' : 'text-slate-400'}`}>
            <Bell className={`w-5 h-5 mb-1 ${tab === 'notice' ? 'fill-blue-50 text-blue-600' : ''}`} strokeWidth={tab === 'notice' ? 2.5 : 2} />
            <span className="text-[9px] font-bold">{t('notice')}</span>
          </button>
          
          <button onClick={() => setTab('ask')} className={`flex flex-col items-center flex-1 py-2 ${tab === 'ask' ? 'text-blue-600' : 'text-slate-400'}`}>
            <MessageSquare className={`w-5 h-5 mb-1 ${tab === 'ask' ? 'fill-blue-50 text-blue-600' : ''}`} strokeWidth={tab === 'ask' ? 2.5 : 2} />
            <span className="text-[9px] font-bold">{t('ask')}</span>
          </button>

          <button onClick={() => setTab('setup')} className={`flex flex-col items-center flex-1 py-2 ${tab === 'setup' ? 'text-blue-600' : 'text-slate-400'}`}>
            <Settings className={`w-5 h-5 mb-1 ${tab === 'setup' ? 'fill-blue-50 text-blue-600' : ''}`} strokeWidth={tab === 'setup' ? 2.5 : 2} />
            <span className="text-[9px] font-bold">Setup</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  );
}
