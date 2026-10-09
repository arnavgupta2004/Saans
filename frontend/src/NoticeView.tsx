import React, { useEffect, useState } from 'react';
import { getNotice } from './api';
import { useLanguage } from './LanguageContext';
import { Copy, Share2, Check } from 'lucide-react';

export default function NoticeView({ activeSchoolId = 'demo-delhi' }: { activeSchoolId?: string }) {
  const { lang, t } = useLanguage();
  const [noticeLang, setNoticeLang] = useState<'en'|'hi'>(lang);
  const [noticeData, setNoticeData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const fetchNotice = async () => {
      setLoading(true);
      try {
        const data = await getNotice(activeSchoolId, noticeLang);
        setNoticeData(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchNotice();
  }, [noticeLang, activeSchoolId]);

  const handleCopy = () => {
    if (noticeData) {
      navigator.clipboard.writeText(noticeData.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading && !noticeData) {
    return <div className="flex h-screen items-center justify-center bg-slate-50"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div></div>;
  }

  return (
    <div className="min-h-screen bg-slate-50 pb-20 w-full max-w-md mx-auto shadow-xl overflow-hidden sm:rounded-2xl sm:my-8 border border-slate-200 flex flex-col">
      <header className="bg-white px-5 pt-6 pb-4 border-b border-slate-100 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">{t('parentNotice')}</h1>
        <div className="flex bg-slate-100 p-1 rounded-lg">
          <button 
            className={`px-3 py-1 rounded-md text-sm font-bold transition ${noticeLang === 'en' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-500'}`}
            onClick={() => setNoticeLang('en')}
          >
            EN
          </button>
          <button 
            className={`px-3 py-1 rounded-md text-sm font-bold transition ${noticeLang === 'hi' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-500'}`}
            onClick={() => setNoticeLang('hi')}
          >
            हिंदी
          </button>
        </div>
      </header>

      <main className="px-5 mt-6 flex-1">
        {loading ? (
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-slate-200 rounded w-3/4"></div>
            <div className="h-4 bg-slate-200 rounded w-full"></div>
            <div className="h-4 bg-slate-200 rounded w-5/6"></div>
          </div>
        ) : noticeData && (
          <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5 relative">
            <p className="text-slate-700 whitespace-pre-wrap leading-relaxed text-[15px]">
              {noticeData.text}
            </p>
          </div>
        )}

        {noticeData && (
          <div className="mt-6 space-y-3">
            <button 
              onClick={handleCopy}
              className="w-full bg-white border-2 border-slate-200 text-slate-700 font-bold py-3 rounded-xl hover:bg-slate-50 transition flex items-center justify-center gap-2"
            >
              {copied ? <Check className="w-5 h-5 text-green-600" /> : <Copy className="w-5 h-5" />}
              {copied ? t('copied') : t('copyToClipboard')}
            </button>
            
            <a 
              href={noticeData.whatsapp_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="w-full bg-[#25D366] text-white font-bold py-3 rounded-xl hover:bg-[#128C7E] transition flex items-center justify-center gap-2"
            >
              <Share2 className="w-5 h-5" />
              {t('shareOnWhatsapp')}
            </a>
          </div>
        )}
      </main>
    </div>
  );
}
