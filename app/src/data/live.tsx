// Live data from the Amethyst demo server (demo_ui/server.py on the laptop).
// The app polls GET /api/state once a second through the Expo dev server, which forwards it
// to the demo server (see metro.config.js), so it works over Wi-Fi and over `--tunnel`. Every reading typed into the demo UI runs
// the agent + XGBoost model there, and the result shows up here a moment later.
// Until the server answers, the screens show the fallback values from mock.ts.
import Constants from 'expo-constants';
import { createContext, ReactNode, useContext, useEffect, useRef, useState } from 'react';
import { Platform } from 'react-native';
import { Risk } from '../theme';
import { alertReading, current, plan as mockPlan, thresholds as mockThresholds, week } from './mock';

const POLL_MS = 1000;

export type Level = Risk | 'fault';

type Reading = { ph: number; temp_c: number; impedance_kohm: number; blood_glucose_mgdl: number; wound_glucose_mM: number };
type Band = [number, number, 'normal' | 'warning' | 'infection'];

// Shape of GET /api/state (fields we use).
type ServerState = {
  seq: number;
  running: boolean;
  hours: number;
  baseline: Reading;
  zones: Record<keyof Reading, { lo: number; hi: number; bands: Band[] }>;
  level?: Level;
  faults?: string[];
  latest_reading?: Reading;
  prediction?: { risk_score: number; risk_score_6h_ago: number | null; tier: string; p_infected: number };
  treatment?: {
    skipped_reason: string | null;
    us_40khz_min: number;
    led_405nm_min: number;
    us_1p5mhz_min: number;
    sessions_per_day: number;
  };
  notes?: { summary: string };
  notes_source?: string; // 'openrouter' | 'gemini' | 'claude' | 'rules'
  risk_series?: { hour: number; risk_score: number }[];
  history?: ({ hour: number } & Reading)[];
};

export type Live = {
  connected: boolean;
  apiUrl: string;
  setApiUrl: (url: string) => void;
  running: boolean; // the server is processing a new reading right now
  seq: number; // bumps on every new assessment, so screens can react
  hasReading: boolean;
  level: Level;
  risk: Risk; // level for the status pill (a sensor fault shows as a warning)
  levelLabel: string;
  headline: string;
  alertTitle: string;
  summary: string;
  source: string | null; // which agent wrote the summary: 'rules' = offline
  score: number;
  score6hAgo: number | null;
  updatedAgo: string;
  ph: number;
  temp: number;
  tempDelta: number;
  moisture: number; // %, relative to this patient's baseline (50% = baseline)
  bloodGlucose: number;
  woundGlucose: number;
  phSeries: number[];
  thresholds: { warningPh: number; infectionPh: number };
  plan: typeof mockPlan;
  trend: { hours: number[]; ph: number[]; tempDelta: number[]; risk: number[] };
  insight: string;
};

function defaultApiUrl(): string {
  if (process.env.EXPO_PUBLIC_API_URL) return process.env.EXPO_PUBLIC_API_URL;
  // In Expo Go, hostUri is the dev server the app was loaded from: "192.168.1.20:8081" on
  // Wi-Fi, or "xxxx-anonymous-8081.exp.direct" with --tunnel (HTTPS, no port).
  const hostUri = Constants.expoConfig?.hostUri;
  if (hostUri) return hostUri.includes(':') ? `http://${hostUri}` : `https://${hostUri}`;
  if (Platform.OS === 'web' && typeof window !== 'undefined') return window.location.origin;
  return 'http://localhost:8081';
}

const HEADLINE: Record<Level, string> = {
  normal: 'Your wound looks healthy',
  warning: 'Early signs of infection',
  infection: 'Infection likely',
  fault: 'Check your patch',
};
const ALERT_TITLE: Record<Level, string> = {
  normal: 'Your wound looks healthy',
  warning: 'Infection risk is rising',
  infection: 'Infection detected',
  fault: 'Your patch needs attention',
};
const LABEL: Record<Level, string> = { normal: 'Normal', warning: 'Warning', infection: 'Infection', fault: 'Check patch' };

const firstSentences = (s: string, n: number) => (s.match(/[^.!?]+[.!?]+(\s|$)/g) ?? [s]).slice(0, n).join('').trim();
const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));
const round1 = (v: number) => Math.round(v * 10) / 10;

function ago(ms: number): string {
  const s = Math.max(0, Math.round(ms / 1000));
  if (s < 5) return 'just now';
  if (s < 60) return `${s}s ago`;
  return `${Math.round(s / 60)} min ago`;
}

function bandStart(z: ServerState['zones']['ph'] | undefined, lvl: Band[2]): number | undefined {
  return z?.bands.find((b) => b[2] === lvl)?.[0];
}

function toLive(st: ServerState | null, receivedAt: number, now: number): Omit<Live, 'connected' | 'apiUrl' | 'setApiUrl'> {
  const r = st?.latest_reading;
  if (!st || !r || !st.level || !st.prediction) {
    // Nothing from the server yet: demo values.
    const base = st?.baseline;
    return {
      running: st?.running ?? false,
      seq: st?.seq ?? 0,
      hasReading: false,
      level: 'normal',
      risk: 'normal',
      levelLabel: LABEL.normal,
      headline: HEADLINE.normal,
      alertTitle: ALERT_TITLE.normal,
      summary: st ? 'Connected. Waiting for the first reading from the patch.' : 'Healing normally.',
      source: null,
      score: st ? 0 : current.score,
      score6hAgo: null,
      updatedAgo: st ? 'waiting' : current.updated,
      ph: base?.ph ?? current.ph,
      temp: base?.temp_c ?? 33.5,
      tempDelta: st ? 0 : current.tempDelta,
      moisture: current.moisture,
      bloodGlucose: base?.blood_glucose_mgdl ?? alertReading.bloodGlucose,
      woundGlucose: base?.wound_glucose_mM ?? alertReading.woundGlucose,
      phSeries: alertReading.phSeries,
      thresholds: mockThresholds,
      plan: mockPlan,
      trend: { hours: week.days.map((_, i) => i * 24), ph: week.ph, tempDelta: week.tempDelta, risk: [] },
      insight: "Thursday's rise triggered 2 therapy sessions. pH was back to normal within 18 hours.",
    };
  }

  const base = st.baseline;
  const level = st.level;
  const hist = st.history ?? [];
  const ph = [...hist.map((h) => h.ph), r.ph];
  const tp = st.treatment;
  const series = st.risk_series ?? [];
  const peak = series.reduce((m, p) => (p.risk_score > m.risk_score ? p : m), { hour: 0, risk_score: 0 });
  const p = st.prediction;

  let insight = 'Risk has stayed in the normal range since the patch went on.';
  if (peak.risk_score >= 55) insight = `Risk peaked at ${Math.round(peak.risk_score)} at hour ${round1(peak.hour)}. Amethyst ran ultrasound and violet light to treat it.`;
  else if (peak.risk_score >= 30) insight = `Risk reached ${Math.round(peak.risk_score)} at hour ${round1(peak.hour)}. Amethyst is watching closely.`;

  return {
    running: st.running,
    seq: st.seq,
    hasReading: true,
    level,
    risk: level === 'fault' ? 'warning' : level,
    levelLabel: LABEL[level],
    headline: HEADLINE[level],
    alertTitle: ALERT_TITLE[level],
    summary: level === 'fault' && st.faults?.length ? st.faults.join(' ') : firstSentences(st.notes?.summary ?? '', 2),
    source: st.notes_source ?? null,
    score: Math.round(p.risk_score),
    score6hAgo: p.risk_score_6h_ago == null ? null : Math.round(p.risk_score_6h_ago),
    updatedAgo: ago(now - receivedAt),
    ph: r.ph,
    temp: r.temp_c,
    tempDelta: r.temp_c - base.temp_c,
    moisture: Math.round(clamp((50 * base.impedance_kohm) / r.impedance_kohm, 0, 100)),
    bloodGlucose: r.blood_glucose_mgdl,
    woundGlucose: r.wound_glucose_mM,
    phSeries: ph.slice(-7), // history is hourly, so the last 6 hours
    thresholds: {
      warningPh: bandStart(st.zones?.ph, 'warning') ?? mockThresholds.warningPh,
      infectionPh: bandStart(st.zones?.ph, 'infection') ?? mockThresholds.infectionPh,
    },
    plan: {
      lightMinutes: tp?.led_405nm_min ?? 0,
      ultrasoundKhz: 40,
      ultrasoundMinutes: tp?.us_40khz_min ?? 0,
      healingMinutes: tp?.us_1p5mhz_min ?? 0,
      sessionsPerDay: tp?.sessions_per_day ?? 3,
      skipped: tp?.skipped_reason ?? null,
    },
    trend: {
      hours: hist.map((h) => h.hour),
      ph: hist.map((h) => h.ph),
      tempDelta: hist.map((h) => h.temp_c - base.temp_c),
      risk: series.filter((_, i) => i % 2 === 0).map((s) => s.risk_score),
    },
    insight,
  };
}

const LiveContext = createContext<Live | null>(null);

export function LiveProvider({ children }: { children: ReactNode }) {
  const [apiUrl, setApiUrl] = useState(defaultApiUrl);
  const [state, setState] = useState<ServerState | null>(null);
  const [connected, setConnected] = useState(false);
  const [now, setNow] = useState(Date.now());
  const receivedAt = useRef(Date.now());
  const lastSeq = useRef(-1);

  useEffect(() => {
    let alive = true;
    const poll = async () => {
      const ctrl = new AbortController();
      const timer = setTimeout(() => ctrl.abort(), 2500);
      try {
        const res = await fetch(`${apiUrl.replace(/\/$/, '')}/api/state`, { signal: ctrl.signal });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const st: ServerState = await res.json();
        if (!alive) return;
        if (st.seq !== lastSeq.current) {
          lastSeq.current = st.seq;
          receivedAt.current = Date.now();
        }
        setState(st);
        setConnected(true);
      } catch {
        if (alive) setConnected(false);
      } finally {
        clearTimeout(timer);
        if (alive) setNow(Date.now());
      }
    };
    poll();
    const id = setInterval(poll, POLL_MS);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, [apiUrl]);

  const value: Live = { connected, apiUrl, setApiUrl, ...toLive(connected ? state : null, receivedAt.current, now) };
  return <LiveContext.Provider value={value}>{children}</LiveContext.Provider>;
}

export function useLive(): Live {
  const v = useContext(LiveContext);
  if (!v) throw new Error('useLive must be used inside <LiveProvider>');
  return v;
}
