import React, { useState } from 'react';
import TodayView from './TodayView';
import WeekView from './WeekView';
import NoticeView from './NoticeView';
import OnboardingView from './OnboardingView';
import { LanguageProvider, useLanguage } from './LanguageContext';
import { Calendar, MessageSquare, Bell, CalendarDays, Globe, Settings } from 'lucide-react';
import { School } from './types';

const DEMO_SCHOOLS = [
  { id: 'demo-delhi', name: 'Demo - Anand Vihar' },
  { id: 'demo-dwarka', name: 'Demo - Dwarka' },
  { id: 'demo-blr', name: 'Demo - Bengaluru' },
];

function AppContent() {
  const [tab, setTab] = useState<'today' | 'week' | 'notice' | 'ask' | 'setup'>('today');
  const [activeSchoolId, setActiveSchoolId] = useState('demo-delhi');
  const { lang, setLang, t } = useLanguage();

  const renderContent = () => {
    switch (tab) {
      case 'today': return <TodayView activeSchoolId={activeSchoolId} />;
      case 'week': return <WeekView activeSchoolId={activeSchoolId} />;
      case 'notice': return <NoticeView activeSchoolId={activeSchoolId} />;
      case 'setup': return <OnboardingView activeSchoolId={activeSchoolId} onSave={(s: School) => console.log('Saved', s)} />;
      case 'ask': return <div className="flex h-screen items-center justify-center bg-slate-50"><p className="text-slate-500 font-bold">Ask Saans (Coming Soon)</p></div>;
      default: return <TodayView activeSchoolId={activeSchoolId} />;
    }
  };

  return (
    <div className="relative min-h-screen bg-slate-100 flex justify-center">
      <div className="w-full max-w-md bg-slate-50 relative pb-16 shadow-2xl">
        
        {/* Header Controls */}
        <div className="absolute top-4 right-4 z-50 flex items-center gap-2">
          <select 
            value={activeSchoolId}
            onChange={(e) => setActiveSchoolId(e.target.value)}
            className="bg-white/90 backdrop-blur border border-slate-200 px-2 py-1.5 rounded-lg shadow-sm text-xs font-bold text-slate-700 hover:bg-slate-50 outline-none max-w-[120px] truncate"
          >
            {DEMO_SCHOOLS.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <button 
            onClick={() => setLang(lang === 'en' ? 'hi' : 'en')}
            className="flex items-center gap-1 bg-white/90 backdrop-blur border border-slate-200 px-3 py-1.5 rounded-lg shadow-sm text-xs font-bold text-slate-700 hover:bg-slate-50"
          >
            <Globe className="w-3.5 h-3.5" />
            {lang === 'en' ? 'हिंदी' : 'EN'}
          </button>
        </div>

        {renderContent()}

        {/* Bottom Tab Nav */}
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
