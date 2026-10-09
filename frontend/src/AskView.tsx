import React, { useState } from 'react';
import { askSaans, AskResponse, REPLAY_KEY } from './api';
import { useLanguage } from './LanguageContext';
import { Send, CheckCircle2, Info } from 'lucide-react';

/** Ask Saans: answers come from the same context as the Today screen (live or replay). */
export default function AskView({ activeSchoolId, replay }: { activeSchoolId: string; replay: boolean }) {
  const { lang } = useLanguage();
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    setLoading(true); setError(null); setResult(null);
    try {
      setResult(await askSaans(activeSchoolId, question.trim(), lang, replay ? REPLAY_KEY : undefined));
    } catch {
      setError('Could not reach Saans. Please use the Today plan.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 px-5 pt-6 pb-24">
      <h1 className="text-xl font-bold text-slate-900">Ask Saans</h1>
      {replay && (
        <p className="mt-2 text-xs font-semibold text-purple-700 bg-purple-50 rounded-md px-2 py-1 inline-block">Replay: answering from recorded data</p>
      )}
      <form onSubmit={submit} className="mt-4 flex gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={lang === 'hi' ? 'जैसे: क्या आज सुबह PE सुरक्षित है?' : 'e.g. Is PE safe this morning?'}
          className="flex-1 min-w-0 border border-slate-200 rounded-lg px-3 py-2 text-sm bg-white outline-none focus:border-blue-400"
        />
        <button disabled={loading} className="bg-blue-600 text-white rounded-lg px-3 py-2 disabled:opacity-50" aria-label="Ask">
          <Send className="w-4 h-4" />
        </button>
      </form>
      {loading && <p className="mt-4 text-sm text-slate-500">Thinking…</p>}
      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
      {result && (
        <div className="mt-4 bg-white rounded-xl border border-slate-100 shadow-sm p-4">
          <p className="text-sm text-slate-800 whitespace-pre-line">{result.answer}</p>
          {result.verified ? (
            <p className="mt-3 text-[11px] text-emerald-700 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> numbers checked against {replay ? 'the replayed plan' : "today's plan"}
            </p>
          ) : result.fallback ? (
            <p className="mt-3 text-[11px] text-slate-500 flex items-center gap-1">
              <Info className="w-3.5 h-3.5" /> Shown directly from the plan (assistant answer unavailable or not verifiable)
            </p>
          ) : null}
        </div>
      )}
    </div>
  );
}
