import { ScrollView, Text, View } from 'react-native';
import { LineChart } from '../components/LineChart';
import { Card, IconButton, PrimaryButton, SecondaryButton, StatusPill } from '../components/ui';
import { useLive } from '../data/live';
import { alertReading, Route } from '../data/mock';
import { color, font, riskStyle, type } from '../theme';

export function AlertScreen({ go }: { go: (r: Route) => void }) {
  const live = useLive();
  // Before the first live reading, show the scripted warning from mock.ts.
  const r = live.hasReading
    ? {
        risk: live.risk,
        label: live.levelLabel,
        title: live.alertTitle,
        body: live.summary,
        phSeries: live.phSeries,
        tempDelta: live.tempDelta,
        score: live.score,
        moisture: live.moisture,
        bloodGlucose: live.bloodGlucose,
        woundGlucose: live.woundGlucose,
      }
    : {
        ...alertReading,
        label: undefined,
        title: 'Infection risk is rising',
        body: 'Your wound has become less acidic over the last 6 hours, and it is warmer than usual.',
      };
  const t = live.thresholds;
  const accent = riskStyle[r.risk].fg;
  const phFrom = r.phSeries[0];
  const phTo = r.phSeries[r.phSeries.length - 1];
  const sign = r.tempDelta >= 0 ? '+' : '';
  // Therapy only when the model's plan includes antibacterial treatment (treat tier and up).
  const canTreat = live.hasReading ? live.plan.lightMinutes > 0 || live.plan.ultrasoundMinutes > 0 : true;

  return (
    <ScrollView contentContainerStyle={{ padding: 16, gap: 20, flexGrow: 1 }}>
      <View style={{ paddingTop: 8 }}>
        <IconButton icon="back" label="Back" onPress={() => go('home')} />
      </View>

      <View style={{ gap: 12 }}>
        <StatusPill risk={r.risk} label={r.label} />
        <Text style={type.title}>{r.title}</Text>
        <Text style={type.body}>{r.body}</Text>
        {live.source === 'opus' && <Text style={type.reading}>Assessed by Claude with the Amethyst risk model</Text>}
      </View>

      <Card tint="raised" style={{ gap: 12 }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
          <Text style={type.caption}>pH, last 6 hours</Text>
          <Text style={[type.reading, { color: color.ink }]}>
            {phFrom.toFixed(2)} → {phTo.toFixed(2)}
          </Text>
        </View>
        <LineChart
          values={r.phSeries}
          min={Math.min(6.2, ...r.phSeries) - 0.1}
          max={Math.max(7.6, ...r.phSeries) + 0.1}
          height={96}
          bands={[
            { from: t.infectionPh, to: 9, fill: color.riskInfectionBg },
            { from: t.warningPh, to: t.infectionPh, fill: color.riskWarningBg },
          ]}
          rules={[{ at: t.warningPh }, { at: t.infectionPh }]}
          highlightIndex={r.phSeries.length - 1}
          highlightColor={accent}
        />
        <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
          <Text style={[type.eyebrow, { color: color.inkMuted }]}>6H AGO</Text>
          <Text style={[type.eyebrow, { color: color.inkMuted }]}>NOW</Text>
        </View>
      </Card>

      <View style={{ flexDirection: 'row', gap: 12 }}>
        <Card style={{ flex: 1, gap: 6 }}>
          <Text style={type.caption}>Temp vs. baseline</Text>
          <Text style={{ fontFamily: font.mono, fontSize: 22, color: accent }}>
            {sign}
            {r.tempDelta.toFixed(1)}°C
          </Text>
        </Card>
        <Card style={{ flex: 1, gap: 6 }}>
          <Text style={type.caption}>Risk score</Text>
          <Text style={{ fontFamily: font.mono, fontSize: 22, color: accent }}>{r.score} / 100</Text>
        </Card>
      </View>

      <View style={{ flexDirection: 'row', gap: 12 }}>
        {[
          { label: 'Moisture', value: `${r.moisture}%` },
          { label: 'Blood glucose', value: `${Math.round(r.bloodGlucose)}` },
          { label: 'Wound gluc.', value: `${r.woundGlucose.toFixed(1)} mM` },
        ].map((m) => (
          <Card key={m.label} style={{ flex: 1, gap: 4, paddingHorizontal: 12, paddingVertical: 12 }}>
            <Text style={type.caption}>{m.label}</Text>
            <Text style={{ fontFamily: font.mono, fontSize: 17, color: color.ink }}>{m.value}</Text>
          </Card>
        ))}
      </View>

      <View style={{ flex: 1 }} />

      <Text style={type.caption}>
        {canTreat
          ? 'This is an early warning, not a diagnosis. If risk stays high for 24 hours, book a visit with your care team.'
          : live.level === 'fault'
            ? 'Amethyst pauses all therapy until the patch readings look normal again.'
            : 'No treatment needed yet. Amethyst checks again every 30 minutes and starts therapy automatically if risk keeps rising.'}
      </Text>

      <View style={{ gap: 12 }}>
        {canTreat ? <PrimaryButton label="Start therapy now" onPress={() => go('therapy')} /> : <PrimaryButton label="Back to home" onPress={() => go('home')} />}
        <SecondaryButton label="Share with my care team" />
      </View>
    </ScrollView>
  );
}
