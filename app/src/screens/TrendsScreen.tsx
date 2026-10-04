import { useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { Icon } from '../components/Icon';
import { LineChart } from '../components/LineChart';
import { Card } from '../components/ui';
import { useLive } from '../data/live';
import { color, font, radius, type } from '../theme';

const ranges = ['6h', '24h', 'All'] as const;
const POINTS: Record<(typeof ranges)[number], number> = { '6h': 7, '24h': 25, All: Infinity }; // history is hourly

export function TrendsScreen() {
  const live = useLive();
  const thresholds = live.thresholds;
  const [range, setRange] = useState<(typeof ranges)[number]>('All');
  const n = POINTS[range];
  const tail = <T,>(a: T[]) => (a.length > n ? a.slice(-n) : a);
  const ph = tail(live.trend.ph);
  const tempDelta = tail(live.trend.tempDelta);
  const hours = tail(live.trend.hours);
  const risk = tail(live.trend.risk);
  const avg = ph.reduce((a, b) => a + b, 0) / Math.max(1, ph.length);
  const peak = ph.indexOf(Math.max(...ph));
  // Axis labels: hours since the patch went on (or weekdays for the offline demo data)
  const labels = live.hasReading
    ? [hours[0], hours[Math.floor(hours.length / 2)], hours[hours.length - 1]].map((h) => `H${Math.round(h ?? 0)}`)
    : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

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
        <LineChart values={ph} min={Math.min(6.2, ...ph) - 0.1} max={Math.max(7.6, ...ph) + 0.1} height={120} rules={[{ at: thresholds.warningPh }, { at: thresholds.infectionPh }]} highlightIndex={peak} />
        <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
          {labels.map((d) => (
            <Text key={d} style={[type.eyebrow, { color: color.inkMuted }]}>
              {d.toUpperCase()}
            </Text>
          ))}
        </View>
        <Text style={type.caption}>{`Lines mark pH ${thresholds.warningPh.toFixed(2)} (warning) and ${thresholds.infectionPh.toFixed(2)} (infection) for this patient.`}</Text>
      </Card>

      <Card style={{ gap: 10 }}>
        <Text style={type.headline}>Temperature vs. baseline</Text>
        <LineChart values={tempDelta} min={Math.min(-0.5, ...tempDelta)} max={Math.max(2, ...tempDelta)} height={100} baseline={0} />
        <View style={{ flexDirection: 'row', gap: 16 }}>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
            <View style={{ width: 14, height: 2, backgroundColor: color.brand }} />
            <Text style={type.caption}>Wound</Text>
          </View>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
            <View style={{ width: 14, height: 0, borderTopWidth: 2, borderStyle: 'dashed', borderColor: color.inkMuted }} />
            <Text style={type.caption}>First-day baseline</Text>
          </View>
        </View>
      </Card>

      {risk.length > 1 && (
        <Card style={{ gap: 10 }}>
          <Text style={type.headline}>Infection risk</Text>
          <LineChart
            values={risk}
            min={0}
            max={100}
            height={100}
            bands={[
              { from: 55, to: 100, fill: color.riskInfectionBg },
              { from: 30, to: 55, fill: color.riskWarningBg },
            ]}
          />
        </Card>
      )}

      <Card tint="brand" style={{ flexDirection: 'row', alignItems: 'center', gap: 10, borderRadius: radius.md }}>
        <Icon name="zap" size={18} color={color.brand} />
        <Text style={[type.caption, { color: color.ink, flex: 1 }]}>{live.insight}</Text>
      </Card>
    </ScrollView>
  );
}
