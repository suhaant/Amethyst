import { Text, View } from 'react-native';
import Svg, { Polygon } from 'react-native-svg';
import { color, font } from '../theme';

// The Amethyst crystal: broad faceted point on a broken base (64-unit grid).
const facets: { points: string; fill: string }[] = [
  { points: '29,4 7,33 25,40', fill: color.brandDeep },
  { points: '29,4 25,40 52,35', fill: color.brandGlow },
  { points: '29,4 52,35 58,28', fill: color.brand },
  { points: '7,33 25,40 23,57 14,54 9,47', fill: color.brand },
  { points: '25,40 52,35 50,50 43,56 35,54 29,59 23,57', fill: color.brandLight },
  { points: '52,35 58,28 58,41 55,48 50,50', fill: color.brandDeep },
];

export function AmethystMark({ size = 32 }: { size?: number }) {
  return (
    <Svg width={size} height={size} viewBox="6 3 53 57" accessibilityLabel="Amethyst">
      {facets.map((f) => (
        <Polygon key={f.points} points={f.points} fill={f.fill} />
      ))}
    </Svg>
  );
}

// Wordmark first, crystal on the right.
export function AmethystLockup({ height = 28, inverse = false }: { height?: number; inverse?: boolean }) {
  const fontSize = height * 0.86;
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', gap: height * 0.2 }} accessibilityRole="header" accessibilityLabel="Amethyst">
      <Text
        style={{
          fontFamily: font.semibold,
          fontSize,
          lineHeight: height,
          letterSpacing: -fontSize * 0.02,
          color: inverse ? '#FFFFFF' : color.ink,
        }}
      >
        amethyst
      </Text>
      <AmethystMark size={height} />
    </View>
  );
}
