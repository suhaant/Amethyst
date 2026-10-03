import { ReactNode } from 'react';
import { Pressable, StyleProp, Text, View, ViewStyle } from 'react-native';
import { color, font, radius, Risk, riskStyle, type } from '../theme';
import { Icon, IconName } from './Icon';

const riskIcon: Record<Risk, IconName> = { normal: 'check', warning: 'alert', infection: 'shield' };

// Status is never shown by colour alone: always a word and an icon.
export function StatusPill({ risk, label }: { risk: Risk; label?: string }) {
  const s = riskStyle[risk];
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6, alignSelf: 'flex-start', paddingVertical: 6, paddingHorizontal: 12, borderRadius: radius.pill, backgroundColor: s.bg }}>
      <Icon name={riskIcon[risk]} size={16} color={s.fg} strokeWidth={2} />
      <Text style={{ fontFamily: font.semibold, fontSize: 13, color: s.fg }}>{label ?? s.label}</Text>
    </View>
  );
}

export function PrimaryButton({ label, onPress }: { label: string; onPress?: () => void }) {
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      style={({ pressed }) => ({ height: 52, borderRadius: radius.md, alignItems: 'center', justifyContent: 'center', backgroundColor: pressed ? color.brandDeep : color.brand })}
    >
      <Text style={{ fontFamily: font.semibold, fontSize: 15, color: color.onBrand }}>{label}</Text>
    </Pressable>
  );
}

export function SecondaryButton({ label, onPress }: { label: string; onPress?: () => void }) {
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      style={({ pressed }) => ({ height: 52, borderRadius: radius.md, alignItems: 'center', justifyContent: 'center', backgroundColor: pressed ? color.line : color.surfaceRaised })}
    >
      <Text style={{ fontFamily: font.semibold, fontSize: 15, color: color.ink }}>{label}</Text>
    </Pressable>
  );
}

export function IconButton({ icon, label, onPress }: { icon: IconName; label: string; onPress?: () => void }) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      onPress={onPress}
      style={{ width: 44, height: 44, borderRadius: radius.md, borderWidth: 1, borderColor: color.line, alignItems: 'center', justifyContent: 'center' }}
    >
      <Icon name={icon} size={20} color={color.ink} />
    </Pressable>
  );
}

export function Card({ children, style, tint = 'outline' }: { children: ReactNode; style?: StyleProp<ViewStyle>; tint?: 'outline' | 'raised' | 'brand' }) {
  const base: ViewStyle =
    tint === 'raised'
      ? { backgroundColor: color.surfaceRaised, borderRadius: radius.lg }
      : tint === 'brand'
        ? { backgroundColor: color.surfaceTint, borderRadius: radius.lg }
        : { borderWidth: 1, borderColor: color.line, borderRadius: radius.md };
  return <View style={[base, { padding: 16 }, style]}>{children}</View>;
}

export function Eyebrow({ children }: { children: string }) {
  return <Text style={type.eyebrow}>{children.toUpperCase()}</Text>;
}

export function Metric({ icon, label, value, valueColor }: { icon: IconName; label: string; value: string; valueColor?: string }) {
  return (
    <Card style={{ flex: 1, gap: 8, paddingHorizontal: 12, paddingVertical: 14 }}>
      <Icon name={icon} size={20} color={color.brand} />
      <Text style={type.caption}>{label}</Text>
      <Text style={{ fontFamily: font.mono, fontSize: 22, color: valueColor ?? color.ink }}>{value}</Text>
    </Card>
  );
}
