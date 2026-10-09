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
    setup: 'Setup',
    tagline: 'Air-smart school day',
    airNow: 'Air now',
    outdoorActivities: 'Outdoor activities',
    indoorClasses: 'indoor classes — no change needed',
    tryBadAir: 'Try a bad-air day',
    backToLive: 'Back to live',
    studentsAsthma: 'Students with asthma',
    betterSlot: 'Better slot available',
    suggestedSwap: 'Suggested swap',
    askTitle: 'Ask Saans',
    askHint: 'Answers come from the same plan you see on Today.',
    askPlaceholder: 'e.g. Is PE at 8:40 safe?',
    stepReading: "Reading today's plan…",
    stepForecast: 'Checking the forecast…',
    stepWriting: 'Writing the answer…',
    showSummary: 'Show plan summary now',
    numbersChecked: "numbers checked against today's plan",
    numbersCheckedReplay: 'numbers checked against the replayed plan',
    fromPlan: 'Shown directly from the plan',
    replayAnswering: 'Replay: answering from recorded data',
    hourlyPm25Days: 'PM2.5 by hour · next days',
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
    setup: 'सेटअप',
    tagline: 'हवा के हिसाब से स्कूल का दिन',
    airNow: 'अभी की हवा',
    outdoorActivities: 'बाहरी गतिविधियाँ',
    indoorClasses: 'कक्षाएँ अंदर — कोई बदलाव नहीं',
    tryBadAir: 'खराब हवा वाला दिन देखें',
    backToLive: 'लाइव पर लौटें',
    studentsAsthma: 'अस्थमा वाले विद्यार्थी',
    betterSlot: 'बेहतर समय उपलब्ध',
    suggestedSwap: 'सुझाया गया बदलाव',
    askTitle: 'Saans से पूछें',
    askHint: 'जवाब उसी योजना से आते हैं जो आज वाले पेज पर है।',
    askPlaceholder: 'जैसे: क्या 8:40 का PE सुरक्षित है?',
    stepReading: 'आज की योजना पढ़ रहे हैं…',
    stepForecast: 'पूर्वानुमान देख रहे हैं…',
    stepWriting: 'जवाब लिख रहे हैं…',
    showSummary: 'अभी योजना का सार दिखाएँ',
    numbersChecked: 'आँकड़े आज की योजना से जाँचे गए',
    numbersCheckedReplay: 'आँकड़े रिकॉर्ड की गई योजना से जाँचे गए',
    fromPlan: 'सीधे योजना से दिखाया गया',
    replayAnswering: 'रीप्ले: रिकॉर्ड किए गए डेटा से जवाब',
    hourlyPm25Days: 'प्रति घंटा PM2.5 · आने वाले दिन',
  }
};

export type TKey = keyof typeof dictionary.en;

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
