import React from 'react';
import { color, inter } from './theme';

// Crystal facets in build order: the three terminal faces first, then the base.
// Animate them in this order for the logo reveal (one facet every few frames).
export const facets = [
  { id: 'left', points: '29,4 7,33 25,40', fill: color.brandDeep },
  { id: 'front', points: '29,4 25,40 52,35', fill: color.brandGlow },
  { id: 'right', points: '29,4 52,35 58,28', fill: color.brand },
  { id: 'base-left', points: '7,33 25,40 23,57 14,54 9,47', fill: color.brand },
  { id: 'base-front', points: '25,40 52,35 50,50 43,56 35,54 29,59 23,57', fill: color.brandLight },
  { id: 'base-right', points: '52,35 58,28 58,41 55,48 50,50', fill: color.brandDeep },
] as const;

// facetOpacity lets a composition fade facets in one by one: facetOpacity[i] in 0..1
export const AmethystMark: React.FC<{ size: number; facetOpacity?: number[]; mono?: string }> = ({ size, facetOpacity, mono }) => (
  <svg width={size} height={size} viewBox="6 3 53 57" role="img" aria-label="Amethyst">
    {facets.map((f, i) => (
      <polygon
        key={f.id}
        points={f.points}
        fill={mono ?? f.fill}
        stroke={mono ? '#FFFFFF' : undefined}
        strokeWidth={mono ? 1.2 : undefined}
        strokeLinejoin="round"
        opacity={facetOpacity ? facetOpacity[i] ?? 1 : 1}
      />
    ))}
  </svg>
);

// Wordmark first, crystal on the right. Never swap the order.
export const AmethystLockup: React.FC<{ height: number; inverse?: boolean; facetOpacity?: number[]; wordOpacity?: number }> = ({
  height,
  inverse = false,
  facetOpacity,
  wordOpacity = 1,
}) => {
  const fontSize = height * 0.86;
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: height * 0.2 }}>
      <span
        style={{
          fontFamily: inter,
          fontWeight: 600,
          fontSize,
          lineHeight: `${height}px`,
          letterSpacing: '-0.02em',
          color: inverse ? '#FFFFFF' : color.ink,
          opacity: wordOpacity,
        }}
      >
        amethyst
      </span>
      <AmethystMark size={height} facetOpacity={facetOpacity} />
    </div>
  );
};
