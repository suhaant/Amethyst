import { useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { Icon } from '../components/Icon';
import { LineChart } from '../components/LineChart';
import { Card } from '../components/ui';
import { thresholds, week } from '../data/mock';
import { color, font, radius, type } from '../theme';

const ranges = ['24h', '7 days', '30 days'] as const;

export function TrendsScreen() {
  const [range, setRange] = useState<(typeof ranges)[number]>('7 days');
  const avg = week.ph.reduce((a, b) => a + b, 0) / week.ph.length;
  const peak = week.ph.indexOf(Math.max(...week.ph));

  return (
    <ScrollView contentContainerStyle={{ padding: 16, gap: 16 }}>
      <Text style={[type.title, { paddingTop: 8 }]}>Trends</Text>

      <View accessibilityRole="tablist" style={{ flexDirection: 'row', gap: 4, padding: 4, backgroundColor: color.surfaceRaised, borderRadius: radius.md }}>
        {ranges.map((r) => {
          const on = r === range;
          return (
            <Pressable
              key={r}
              accessibilityRole="tab"
              accessibilityState={{ selected: on }}
              onPress={() => setRange(r)}
              style={{ flex: 1, height: 36, borderRadius: 8, alignItems: 'center', justifyContent: 'center', backgroundColor: on ? color.surface : 'transparent' }}
            >
              <Text style={{ fontFamily: font.semibold, fontSize: 13, color: on ? color.ink : color.inkMuted }}>{r}</Text>
            </Pressable>
          );
        })}
      </View>

      <Card style={{ gap: 10 }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' }}>
          <Text style={type.headline}>Wound pH</Text>
          <Text style={type.reading}>avg {avg.toFixed(1)}</Text>
        </View>
        <LineChart values={week.ph} min={5} max={8} height={120} rules={[{ at: thresholds.warningPh }, { at: thresholds.infectionPh }]} highlightIndex={peak} />
        <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
          {week.days.map((d) => (
            <Text key={d} style={[type.eyebrow, { color: color.inkMuted }]}>
              {d.toUpperCase()}
            </Text>
          ))}
        </View>
        <Text style={type.caption}>Lines mark pH 6.0 (warning) and 7.5 (infection).</Text>
      </Card>

      <Card style={{ gap: 10 }}>
        <Text style={type.headline}>Temperature vs. healthy skin</Text>
        <LineChart values={week.tempDelta} min={-0.5} max={2} height={100} baseline={0} />
        <View style={{ flexDirection: 'row', gap: 16 }}>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
            <View style={{ width: 14, height: 2, backgroundColor: color.brand }} />
            <Text style={type.caption}>Wound</Text>
          </View>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
            <View style={{ width: 14, height: 0, borderTopWidth: 2, borderStyle: 'dashed', borderColor: color.inkMuted }} />
            <Text style={type.caption}>Healthy skin</Text>
          </View>
        </View>
      </Card>

      <Card tint="brand" style={{ flexDirection: 'row', alignItems: 'center', gap: 10, borderRadius: radius.md }}>
        <Icon name="zap" size={18} color={color.brand} />
        <Text style={[type.caption, { color: color.ink, flex: 1 }]}>Thursday's rise triggered 2 therapy sessions. pH was back to normal within 18 hours.</Text>
      </Card>
    </ScrollView>
  );
}
