// Amethyst design tokens (light theme). Mirrors the Amethyst design system.
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

export const space = { 1: 4, 2: 8, 3: 12, 4: 16, 6: 24, 8: 32, 12: 48, 16: 64 } as const;

export const radius = { sm: 4, md: 10, lg: 16, pill: 999 } as const;

export const font = {
  regular: 'Inter_400Regular',
  medium: 'Inter_500Medium',
  semibold: 'Inter_600SemiBold',
  mono: 'JetBrainsMono_500Medium',
} as const;

export const type = {
  display: { fontFamily: font.semibold, fontSize: 56, lineHeight: 58, letterSpacing: -1.7, color: color.ink },
  title: { fontFamily: font.semibold, fontSize: 28, lineHeight: 34, letterSpacing: -0.5, color: color.ink },
  headline: { fontFamily: font.semibold, fontSize: 15, lineHeight: 22, color: color.ink },
  body: { fontFamily: font.regular, fontSize: 15, lineHeight: 22, color: color.inkMuted },
  caption: { fontFamily: font.medium, fontSize: 13, lineHeight: 18, color: color.inkMuted },
  eyebrow: { fontFamily: font.semibold, fontSize: 11, lineHeight: 14, letterSpacing: 0.9, color: color.brand },
  reading: { fontFamily: font.mono, fontSize: 13, lineHeight: 18, color: color.inkMuted },
} as const;

export type Risk = 'normal' | 'warning' | 'infection';

export const riskStyle: Record<Risk, { fg: string; bg: string; label: string }> = {
  normal: { fg: color.riskNormal, bg: color.riskNormalBg, label: 'Normal' },
  warning: { fg: color.riskWarning, bg: color.riskWarningBg, label: 'Warning' },
  infection: { fg: color.riskInfection, bg: color.riskInfectionBg, label: 'Infection' },
};
