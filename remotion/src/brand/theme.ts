// Amethyst brand tokens for Remotion (web React). Same values as the
// Amethyst design system and the Expo app's src/theme.ts.
import { loadFont as loadInter } from '@remotion/google-fonts/Inter';
import { loadFont as loadMono } from '@remotion/google-fonts/JetBrainsMono';

export const { fontFamily: inter } = loadInter('normal', { weights: ['400', '500', '600'], subsets: ['latin'] });
export const { fontFamily: mono } = loadMono('normal', { weights: ['500'], subsets: ['latin'] });

export const color = {
  surface: '#FFFFFF',
  surfaceRaised: '#F5F5F7',
  surfaceTint: '#F3EEFA',
  line: '#E6E6EA',
  ink: '#0A0A0B',
  inkMuted: '#5B5B66',
  brand: '#6B3FA0',
  brandDeep: '#4E2B7C',
  brandLight: '#8E66CC',
  brandGlow: '#B79BE0',
  onBrand: '#FFFFFF',
  riskNormal: '#1F7A5A',
  riskNormalBg: '#E8F5EF',
  riskWarning: '#B45309',
  riskWarningBg: '#FDF3E6',
  riskInfection: '#C2253D',
  riskInfectionBg: '#FCEBEE',
} as const;

// Slide layout at 1920×1080
export const slide = {
  width: 1920,
  height: 1080,
  fps: 30,
  marginX: 64,
  marginTop: 56,
} as const;

// Type sizes for 1920×1080 slides (px)
export const type = {
  eyebrow: { fontFamily: inter, fontWeight: 600, fontSize: 18, letterSpacing: '0.08em', textTransform: 'uppercase' as const, color: color.brand },
  title: { fontFamily: inter, fontWeight: 600, fontSize: 72, lineHeight: 1.05, letterSpacing: '-0.035em', color: color.ink },
  bigStat: { fontFamily: inter, fontWeight: 600, fontSize: 200, lineHeight: 0.95, letterSpacing: '-0.04em', color: color.brand },
  body: { fontFamily: inter, fontWeight: 400, fontSize: 32, lineHeight: 1.4, color: color.inkMuted },
  label: { fontFamily: inter, fontWeight: 500, fontSize: 24, lineHeight: 1.35, color: color.inkMuted },
  source: { fontFamily: inter, fontWeight: 400, fontSize: 16, color: color.inkMuted },
  reading: { fontFamily: mono, fontWeight: 500, fontSize: 28, color: color.ink },
} as const;

// Motion: quick and precise, nothing bounces.
export const motion = {
  ui: 0.2, // seconds, ease-out
  stagger: 4, // frames between items
  spring: { damping: 200 }, // Remotion spring config with no overshoot
} as const;
