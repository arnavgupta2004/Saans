import React, { useEffect, useRef, useState } from 'react';
import { askSaans, AskError, AskResponse, getDayPlan, MAX_QUESTION, REPLAY_KEY } from './api';
import { useLanguage } from './LanguageContext';
import { planSummary } from './utils/plan';
import { Send, CheckCircle2, Info } from 'lucide-react';

type Turn = { q: string; answer?: AskResponse & { summary?: boolean }; error?: string };

const SUGGESTIONS = {
  en: ['Is PE at 8:40 safe?', 'Should recess be indoors?', 'Best day this week for Sports Day?'],
  hi: ['क्या 8:40 का PE सुरक्षित है?', 'क्या रिसेस अंदर होनी चाहिए?', 'इस हफ़्ते खेल दिवस के लिए सबसे अच्छा दिन?'],
};

/** Ask Saans: answers come from the same context as the Today screen (live or replay). */
export default function AskView({ activeSchoolId, replay }: { activeSchoolId: string; replay: boolean }) {
  const { lang, t } = useLanguage();
  const [question, setQuestion] = useState('');
  const [turns, setTurns] = useState<Turn[]>([]);
  const [pending, setPending] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const abort = useRef<AbortController | null>(null);
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!pending) return;
    const start = Date.now();
    const id = setInterval(() => setElapsed((Date.now() - start) / 1000), 250);
    return () => clearInterval(id);
  }, [pending]);

  useEffect(() => { bottom.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }); }, [turns, pending]);
  useEffect(() => () => abort.current?.abort(), []);

  const finish = (patch: Partial<Turn>) => {
    setTurns((all) => all.map((turn, i) => (i === all.length - 1 ? { ...turn, ...patch } : turn)));
    setPending(false);
    setElapsed(0);
  };

  const ask = async (q: string) => {
    if (!q.trim() || pending) return;
    abort.current?.abort();
    const ctrl = new AbortController();
    abort.current = ctrl;
    setTurns((all) => [...all, { q: q.trim() }]);
    setQuestion('');
    setPending(true);
    try {
      const answer = await askSaans(activeSchoolId, q.trim(), lang, replay ? REPLAY_KEY : undefined, ctrl.signal);
      if (!ctrl.signal.aborted) finish({ answer });
    } catch (e) {
      if (ctrl.signal.aborted) return;
      const status = e instanceof AskError ? e.status : 0;
      const hi = lang === 'hi';
      const msg =
        status === 429 ? (hi ? 'एक मिनट में बहुत सारे सवाल। कृपया एक मिनट रुककर फिर पूछें।' : 'Lots of questions from your network in the last minute. Please wait a minute and ask again.')
        : status === 422 ? (hi ? `सवाल ${MAX_QUESTION} अक्षरों से छोटा रखें।` : `Please keep the question under ${MAX_QUESTION} characters.`)
        : (hi ? 'Saans तक नहीं पहुँच सके। कृपया आज की योजना देखें।' : 'Could not reach Saans. Please use the Today plan.');
      finish({ error: msg });
    }
  };

  /** Stop waiting for the model and show the deterministic plan summary (numbers straight from the planner). */
  const showSummary = async () => {
    abort.current?.abort();
    try {
      const plan = await getDayPlan(activeSchoolId, replay ? REPLAY_KEY : undefined);
      finish({ answer: { answer: planSummary(plan, lang), tools_used: [], verified: false, fallback: true, model: null, summary: true } });
    } catch {
      finish({ error: 'Could not load the plan.' });
    }
  };

  const step = elapsed < 2.5 ? t('stepReading') : elapsed < 5.5 ? t('stepForecast') : t('stepWriting');

  return (
    <div className="px-4 pt-5 pb-40">
      <h1 className="text-xl font-semibold text-stone-900">{t('askTitle')}</h1>
      <p className="text-xs text-stone-500 mt-0.5">{t('askHint')}</p>
      {replay && <p className="mt-2 inline-block text-xs font-medium text-violet-800 bg-violet-100 rounded-md px-2 py-1">{t('replayAnswering')}</p>}

      {turns.length === 0 && (
        <div className="mt-5 flex flex-wrap gap-2">
          {SUGGESTIONS[lang].map((s) => (
            <button key={s} onClick={() => ask(s)} className="text-sm bg-white border border-stone-200 rounded-full px-3 py-1.5 text-stone-700 hover:border-teal-400">{s}</button>
          ))}
        </div>
      )}

      <div className="mt-5 space-y-4">
        {turns.map((turn, i) => (
          <div key={i} className="space-y-2">
            <div className="flex justify-end">
              <p className="max-w-[85%] bg-stone-900 text-white text-sm rounded-2xl rounded-br-md px-3.5 py-2 break-words">{turn.q}</p>
            </div>
            {turn.answer && (
              <div data-testid="ask-answer" className="max-w-[92%] bg-white border border-stone-200/80 rounded-2xl rounded-bl-md px-3.5 py-3">
                <p className="text-sm text-stone-800 whitespace-pre-line leading-relaxed break-words">{turn.answer.answer.replace(/\*+/g, '')}</p>
                <div className="mt-2.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px]">
                  {turn.answer.verified ? (
                    <span className="text-emerald-700 flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" />{replay ? t('numbersCheckedReplay') : t('numbersChecked')}</span>
                  ) : turn.answer.fallback ? (
                    <span className="text-stone-500 flex items-center gap-1"><Info className="w-3.5 h-3.5" />{t('fromPlan')}</span>
                  ) : null}
                  {turn.answer.model && <span className="text-stone-400">{turn.answer.model}</span>}
                </div>
              </div>
            )}
            {turn.error && <p className="text-sm text-rose-700">{turn.error}</p>}
          </div>
        ))}

        {pending && (
          <div className="max-w-[92%] bg-white border border-stone-200/80 rounded-2xl rounded-bl-md px-3.5 py-3" aria-live="polite">
            <div className="flex items-center gap-2 text-sm text-stone-600">
              <span className="flex gap-1" aria-hidden>
                {[0, 150, 300].map((d) => <span key={d} className="w-1.5 h-1.5 rounded-full bg-teal-600 animate-bounce" style={{ animationDelay: `${d}ms` }} />)}
              </span>
              {step}
            </div>
            {elapsed >= 8 && (
              <button onClick={showSummary} className="mt-2.5 text-xs font-medium text-teal-800 border border-teal-200 bg-teal-50 rounded-lg px-2.5 py-1.5">{t('showSummary')}</button>
            )}
          </div>
        )}
        <div ref={bottom} />
      </div>

      <form
        onSubmit={(e) => { e.preventDefault(); ask(question); }}
        className="fixed bottom-16 left-1/2 -translate-x-1/2 w-full max-w-md px-4 py-3 bg-stone-50/95 backdrop-blur border-t border-stone-200/70 flex gap-2"
      >
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          maxLength={MAX_QUESTION}
          placeholder={t('askPlaceholder')}
          className="flex-1 min-w-0 border border-stone-300 rounded-xl px-3 py-2.5 text-sm bg-white outline-none focus:border-teal-500"
        />
        {question.length > MAX_QUESTION - 50 && (
          <span className="self-center text-[11px] text-stone-500 tabular-nums shrink-0">{question.length}/{MAX_QUESTION}</span>
        )}
        <button disabled={pending || !question.trim()} className="bg-teal-700 text-white rounded-xl px-3.5 disabled:opacity-40" aria-label="Ask">
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
