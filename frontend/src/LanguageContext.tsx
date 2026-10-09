import React, { createContext, useContext, useState } from 'react';

type Lang = 'en' | 'hi';

const dictionary = {
  en: {
    today: 'Today',
    week: 'Week',
    notice: 'Notice',
    ask: 'Ask',
    todayTitle: 'Today at School',
    outdoorSchedule: 'Outdoor Schedule',
    currentAirQuality: 'Current Air Quality',
    swapTo: 'Swap to',
    applySwap: 'Apply Swap',
    why: 'Why',
    source: 'Source',
    lastUpdated: 'Last updated',
    weekOverview: 'Week Overview',
    fiveDayForecast: '5-Day Forecast',
    hourlyPM25: 'Hourly PM2.5',
    bestDayForEvent: 'Best Day for Event',
    startTime: 'Start Time',
    endTime: 'End Time',
    findBestDay: 'Find Best Day',
    parentNotice: 'Parent Notice',
    copyToClipboard: 'Copy to Clipboard',
    copied: 'Copied!',
    shareOnWhatsapp: 'Share on WhatsApp',
  },
  hi: {
    today: 'आज',
    week: 'सप्ताह',
    notice: 'सूचना',
    ask: 'पूछें',
    todayTitle: 'आज स्कूल में',
    outdoorSchedule: 'बाहरी कार्यक्रम',
    currentAirQuality: 'वर्तमान वायु गुणवत्ता',
    swapTo: 'बदलें',
    applySwap: 'लागू करें',
    why: 'क्यों',
    source: 'स्रोत',
    lastUpdated: 'अंतिम अपडेट',
    weekOverview: 'साप्ताहिक अवलोकन',
    fiveDayForecast: '5-दिन का पूर्वानुमान',
    hourlyPM25: 'प्रति घंटा PM2.5',
    bestDayForEvent: 'आयोजन के लिए सबसे अच्छा दिन',
    startTime: 'प्रारंभ समय',
    endTime: 'समाप्ति समय',
    findBestDay: 'सबसे अच्छा दिन खोजें',
    parentNotice: 'अभिभावक सूचना',
    copyToClipboard: 'क्लिपबोर्ड पर कॉपी करें',
    copied: 'कॉपी किया गया!',
    shareOnWhatsapp: 'WhatsApp पर शेयर करें',
  }
};

const LanguageContext = createContext<{ lang: Lang; setLang: (l: Lang) => void; t: (key: keyof typeof dictionary.en) => string }>({
  lang: 'en',
  setLang: () => {},
  t: () => '',
});

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [lang, setLang] = useState<Lang>('en');

  const t = (key: keyof typeof dictionary.en) => {
    return dictionary[lang][key] || dictionary.en[key];
  };

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
