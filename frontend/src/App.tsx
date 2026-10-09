import React, { useEffect, useState } from 'react';
import TodayView from './TodayView';
import WeekView from './WeekView';
import NoticeView from './NoticeView';
import AskView from './AskView';
import OnboardingView from './OnboardingView';
import { LanguageProvider, useLanguage } from './LanguageContext';
import { Calendar, MessageCircle, Bell, CalendarDays, Settings, Wind } from 'lucide-react';
import { School } from './types';

const DEMO_SCHOOLS = [
  { id: 'delhi-anand-vihar', name: 'Anand Vihar' },
  { id: 'delhi-dwarka', name: 'Dwarka' },
  { id: 'bengaluru-indiranagar', name: 'Indiranagar' },
];

type Tab = 'today' | 'week' | 'notice' | 'ask' | 'setup';
const TABS: Tab[] = ['today', 'week', 'notice', 'ask', 'setup'];

/** Demo deep links: ?replay=delhi-nov  ?tab=ask  ?lang=hi  ?school=delhi-dwarka */
const params = new URLSearchParams(window.location.search);
const initialTab = (TABS as string[]).includes(params.get('tab') ?? '') ? (params.get('tab') as Tab) : 'today';
const initialSchool = DEMO_SCHOOLS.some((s) => s.id === params.get('school')) ? params.get('school')! : DEMO_SCHOOLS[0].id;

function AppContent() {
  const [tab, setTab] = useState<Tab>(initialTab);
  const [activeSchoolId, setActiveSchoolId] = useState(initialSchool);
  const [replay, setReplay] = useState(params.get('replay') === 'delhi-nov'); // shared by Today, Notice and Ask
  const { lang, setLang, t } = useLanguage();

  useEffect(() => {
    if (params.get('lang') === 'hi') setLang('hi');
  }, [setLang]);

  const nav: { id: Tab; icon: typeof Calendar; label: string }[] = [
    { id: 'today', icon: Calendar, label: t('today') },
    { id: 'week', icon: CalendarDays, label: t('week') },
    { id: 'notice', icon: Bell, label: t('notice') },
    { id: 'ask', icon: MessageCircle, label: t('ask') },
    { id: 'setup', icon: Settings, label: t('setup') },
  ];

  const content = () => {
    switch (tab) {
      case 'week': return <WeekView activeSchoolId={activeSchoolId} />;
      case 'notice': return <NoticeView activeSchoolId={activeSchoolId} replay={replay} />;
      case 'ask': return <AskView activeSchoolId={activeSchoolId} replay={replay} />;
      case 'setup': return <OnboardingView activeSchoolId={activeSchoolId} onSave={(s: School) => console.log('Saved', s)} />;
      default: return <TodayView activeSchoolId={activeSchoolId} replay={replay} setReplay={setReplay} />;
    }
  };

  return (
    <div className="min-h-screen bg-stone-100 flex justify-center">
      <div className="w-full max-w-md bg-stone-50 relative pb-20 min-h-screen sm:shadow-xl">
        <header className="sticky top-0 z-40 bg-stone-50/90 backdrop-blur border-b border-stone-200/70 px-4 pt-3 pb-2.5">
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 shrink-0" aria-label="Saans">
              <span className="grid place-items-center w-7 h-7 rounded-full bg-teal-600 text-white">
                <Wind className="w-4 h-4" strokeWidth={2.5} />
              </span>
              <span className="text-lg font-semibold tracking-tight text-stone-900">Saans</span>
            </div>
            <select
              value={activeSchoolId}
              onChange={(e) => setActiveSchoolId(e.target.value)}
              aria-label="School"
              className="ml-auto min-w-0 max-w-[46%] truncate bg-white border border-stone-200 pl-2 pr-6 py-1.5 rounded-lg text-xs font-medium text-stone-700 outline-none"
            >
              {DEMO_SCHOOLS.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
            <div className="shrink-0 flex rounded-lg border border-stone-200 bg-white p-0.5 text-xs font-semibold" role="group" aria-label="Language">
              <button onClick={() => setLang('en')} className={`px-2 py-1 rounded-md ${lang === 'en' ? 'bg-stone-900 text-white' : 'text-stone-500'}`}>EN</button>
              <button onClick={() => setLang('hi')} className={`px-2 py-1 rounded-md ${lang === 'hi' ? 'bg-stone-900 text-white' : 'text-stone-500'}`}>हिंदी</button>
            </div>
          </div>
          <p className="mt-0.5 pl-[2.375rem] text-[11px] text-stone-500">{t('tagline')}</p>
        </header>

        {content()}

        <nav data-nav className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-white/95 backdrop-blur border-t border-stone-200 grid grid-cols-5 h-16 z-40">
          {nav.map(({ id, icon: Icon, label }) => (
            <button
              key={id}
              data-tab={id}
              onClick={() => setTab(id)}
              aria-current={tab === id ? 'page' : undefined}
              className={`flex flex-col items-center justify-center gap-1 min-w-0 ${tab === id ? 'text-teal-700' : 'text-stone-400'}`}
            >
              <Icon className="w-5 h-5" strokeWidth={tab === id ? 2.4 : 1.8} />
              <span className="text-[11px] font-medium leading-none truncate max-w-full px-1">{label}</span>
            </button>
          ))}
        </nav>
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
