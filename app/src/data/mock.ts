// Fallback demo readings, shown until the app reaches the demo server (see live.tsx).
import { Risk } from '../theme';

export type Route = 'pair' | 'home' | 'alert' | 'therapy' | 'trends';

export const patch = {
  id: 'AM-7F3A',
  location: 'Left shin',
  padDay: 2,
  battery: 86,
  lastTherapy: '9:40 AM',
};

// pH lines on the charts. live.tsx replaces these with the patient's own zones from the server.
export const thresholds = { warningPh: 6.86, infectionPh: 7.16 };

export const current = {
  risk: 'normal' as Risk,
  updated: '2 min ago',
  score: 12,
  ph: 6.7,
  tempDelta: 0.2,
  moisture: 50,
};

export const alertReading = {
  risk: 'warning' as Risk,
  phFrom: 6.7,
  phTo: 7.0,
  phSeries: [6.7, 6.72, 6.75, 6.8, 6.86, 6.93, 7.0],
  tempDelta: 0.9,
  score: 41,
  moisture: 62,
  bloodGlucose: 112,
  woundGlucose: 3.4,
};

export const plan = {
  lightMinutes: 9,
  ultrasoundKhz: 40,
  ultrasoundMinutes: 5,
  healingMinutes: 0,
  sessionsPerDay: 3,
  skipped: null as string | null,
};

export const week = {
  days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  ph: [6.7, 6.68, 6.72, 7.1, 6.9, 6.75, 6.7],
  tempDelta: [0.1, 0.0, 0.2, 1.4, 0.8, 0.3, 0.2],
};
