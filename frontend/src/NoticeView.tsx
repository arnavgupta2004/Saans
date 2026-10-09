import React, { useEffect, useState } from 'react';
import { getNotice, REPLAY_KEY } from './api';
import { useLanguage } from './LanguageContext';
import { Copy, Share2, Check } from 'lucide-react';

/** Parent notice in the app's current language (EN/HI toggle in the header), for live or replay data. */
export default function NoticeView({ activeSchoolId = 'delhi-anand-vihar', replay = false }: { activeSchoolId?: string; replay?: boolean }) {
  const { lang, t } = useLanguage();
  const [notice, setNotice] = useState<{ text: string; whatsapp_url: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);
    getNotice(activeSchoolId, lang, replay ? REPLAY_KEY : undefined)
      .then((d) => { if (!cancelled) setNotice(d); })
      .catch(() => { if (!cancelled) setError(true); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [activeSchoolId, lang, replay]);

  const copy = () => {
    if (!notice) return;
    navigator.clipboard.writeText(notice.text).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="px-4 pt-5 pb-6">
      <h1 className="text-xl font-semibold text-stone-900">{t('parentNotice')}</h1>
      <p className="text-xs text-stone-500 mt-0.5">{lang === 'hi' ? 'भाषा बदलने के लिए ऊपर EN / हिंदी चुनें' : 'Switch EN / हिंदी at the top to change the language'}</p>

      <div className="mt-4 bg-white rounded-2xl border border-stone-200/80 p-4 min-h-40">
        {loading && !notice ? (
          <div className="animate-pulse space-y-3">
            <div className="h-3.5 bg-stone-200 rounded w-3/4" />
            <div className="h-3.5 bg-stone-200 rounded w-full" />
            <div className="h-3.5 bg-stone-200 rounded w-5/6" />
          </div>
        ) : error && !notice ? (
          <p className="text-sm text-rose-700">Could not load the notice. Please try again.</p>
        ) : notice && (
          <p className={`text-stone-800 whitespace-pre-wrap leading-relaxed text-[15px] break-words ${loading ? 'opacity-60' : ''}`}>{notice.text}</p>
        )}
      </div>

      {notice && (
        <div className="mt-4 space-y-2.5">
          <button onClick={copy} className="w-full bg-white border border-stone-300 text-stone-800 font-medium py-3 rounded-xl flex items-center justify-center gap-2 text-sm">
            {copied ? <Check className="w-4 h-4 text-emerald-600 shrink-0" /> : <Copy className="w-4 h-4 shrink-0" />}
            <span className="truncate">{copied ? t('copied') : t('copyToClipboard')}</span>
          </button>
          <a href={notice.whatsapp_url} target="_blank" rel="noopener noreferrer" className="w-full bg-[#25D366] text-white font-medium py-3 rounded-xl flex items-center justify-center gap-2 text-sm">
            <Share2 className="w-4 h-4 shrink-0" /> <span className="truncate">{t('shareOnWhatsapp')}</span>
          </a>
        </div>
      )}
    </div>
  );
}
