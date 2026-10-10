// Single source of truth for the demo video: timing, on-screen caption and voice-over line per scene.
// `vo` is written the way it should be SPOKEN (numbers spelled out) so it can be read aloud as-is.
export const SCENES = [
  { id: 'title', dur: 12, kind: 'slide', image: 'docs/assets/title-card.png',
    vo: 'It is a winter morning in Delhi. The air is at its worst. And at eight forty, Class Seven B goes out for P.E.' },
  { id: 'problem', dur: 17, kind: 'slide', image: 'problem',
    vo: 'Children breathe more air for their size than adults. But on bad-air days, schools get two options. A normal day, or school closed. Nothing tells the principal what to do with period two.' },
  { id: 'hero', dur: 15, kind: 'app', kicker: 'Replay · recorded data', caption: 'Delhi, 19 Nov 2025',
    sub: 'A real bad-air day at Anand Vihar · AQI 351, Very Poor · 2 changes needed today',
    vo: 'This is Saans. Here is a real bad day, recorded in Delhi on the nineteenth of November, twenty twenty-five. Air quality: three hundred fifty-one. Very Poor. Two changes needed today.' },
  { id: 'swap', dur: 26, kind: 'app', kicker: 'Rules decide', caption: 'Same day, different hour: AQI 351 → 127',
    sub: 'Hourly forecast → India’s National AQI → a tested school protocol. Students with asthma get stricter advice.',
    vo: 'Saans reads the hourly forecast for the school. It applies India’s A.Q.I., and a clear school protocol. Assembly moves indoors. And for P.E., Saans finds a cleaner hour. Swap with Period Eight, at one forty. The A.Q.I. drops from three fifty-one to one twenty-seven. Students with asthma get their own, stricter advice.' },
  { id: 'impact', dur: 14, kind: 'app', kicker: 'Estimate, with its formula', caption: '40 students out of Very Poor air',
    sub: '≈ 60% lower PM2.5 during PE · outdoor air only, labelled as an estimate',
    vo: 'Saans also estimates the benefit. This swap would move forty students out of Very Poor air, with about sixty percent less P.M. two point five. And it shows the formula.' },
  { id: 'source', dur: 9, kind: 'app', kicker: 'Honest by default', caption: 'Every number shows its source',
    sub: 'Indoor classes stay as they are',
    vo: 'Indoor classes stay as they are. And every screen says where its numbers come from.' },
  { id: 'notice', dur: 19, kind: 'app', kicker: 'For parents', caption: 'Parent notice · English / हिंदी',
    sub: 'Offers the swap, never claims it is decided · one tap to WhatsApp',
    vo: 'One tap gives parents a notice. In English, or in Hindi. It offers the swap. It does not pretend it is decided. Then share it on WhatsApp.' },
  { id: 'ask', dur: 28, kind: 'app', kicker: 'AI explains · rules decide', caption: 'Every number checked against the plan',
    sub: 'Strands Agents with the planner as tools · a number guard on every answer',
    vo: 'Ask Saans is an A.I. agent, built with Strands Agents. It answers from the same plan, using tools. And then we check its work. Every number in the answer must match the plan. If it does not, Saans shows the plan itself.' },
  { id: 'live', dur: 14, kind: 'app', kicker: 'Live today', caption: 'Calibrated only with fresh monitor data',
    sub: 'Otherwise it says so · the week view plans ahead',
    vo: 'On a live day, Saans calibrates against government monitors, only when their reading is fresh. If not, it says so. The week view plans ahead.' },
  { id: 'aws', dur: 18, kind: 'slide', image: 'docs/assets/architecture.png',
    vo: 'It runs on A.W.S. Lambda and A.P.I. Gateway for the A.P.I. DynamoDB for schools and daily plans. EventBridge Scheduler runs it at six A.M., India time. CloudWatch and S.N.S. alert us. Amplify hosts the app. All deployed with A.W.S. SAM.' },
  { id: 'end', dur: 6, kind: 'slide', image: 'docs/assets/end-card.png',
    vo: 'Saans. Cleaner hours for every child. Team Chernobyl.' },
];

export const XFADE = 0.4; // seconds of cross-fade between scenes (does not shift scene start times)

export const starts = () => {
  let t = 0;
  return SCENES.map((s) => { const at = t; t += s.dur; return at; });
};

export const mmss = (sec) => `${Math.floor(sec / 60)}:${String(Math.round(sec % 60)).padStart(2, '0')}`;
