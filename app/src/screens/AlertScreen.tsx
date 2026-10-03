import { ScrollView, Text, View } from 'react-native';
import { LineChart } from '../components/LineChart';
import { Card, IconButton, PrimaryButton, SecondaryButton, StatusPill } from '../components/ui';
import { alertReading, Route, thresholds } from '../data/mock';
import { color, font, type } from '../theme';

export function AlertScreen({ go }: { go: (r: Route) => void }) {
  const r = alertReading;
  return (
    <ScrollView contentContainerStyle={{ padding: 16, gap: 20, flexGrow: 1 }}>
      <View style={{ paddingTop: 8 }}>
        <IconButton icon="back" label="Back" onPress={() => go('home')} />
      </View>

      <View style={{ gap: 12 }}>
        <StatusPill risk={r.risk} />
        <Text style={type.title}>Infection risk is rising</Text>
        <Text style={type.body}>Your wound has become less acidic over the last 6 hours, and it is warmer than the skin around it.</Text>
      </View>

      <Card tint="raised" style={{ gap: 12 }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
          <Text style={type.caption}>pH, last 6 hours</Text>
          <Text style={[type.reading, { color: color.ink }]}>
            {r.phFrom} → {r.phTo}
          </Text>
        </View>
        <LineChart
          values={r.phSeries}
          min={5.5}
          max={8}
          height={96}
          bands={[
            { from: thresholds.infectionPh, to: 8, fill: color.riskInfectionBg },
            { from: thresholds.warningPh, to: thresholds.infectionPh, fill: color.riskWarningBg },
          ]}
          rules={[{ at: thresholds.warningPh }, { at: thresholds.infectionPh }]}
          highlightIndex={r.phSeries.length - 1}
        />
        <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
          <Text style={[type.eyebrow, { color: color.inkMuted }]}>6H AGO</Text>
          <Text style={[type.eyebrow, { color: color.inkMuted }]}>NOW</Text>
        </View>
      </Card>

      <View style={{ flexDirection: 'row', gap: 12 }}>
        <Card style={{ flex: 1, gap: 6 }}>
          <Text style={type.caption}>Wound vs. skin</Text>
          <Text style={{ fontFamily: font.mono, fontSize: 22, color: color.riskWarning }}>+{r.tempDelta.toFixed(1)}°C</Text>
        </Card>
        <Card style={{ flex: 1, gap: 6 }}>
          <Text style={type.caption}>Risk score</Text>
          <Text style={{ fontFamily: font.mono, fontSize: 22, color: color.riskWarning }}>{r.score} / 100</Text>
        </Card>
      </View>

      <View style={{ flexDirection: 'row', gap: 12 }}>
        {[
          { label: 'Moisture', value: `${r.moisture}%` },
          { label: 'Heart rate', value: `${r.heartRate} bpm` },
          { label: 'Glucose var.', value: `${r.glycemicCv}%` },
        ].map((m) => (
          <Card key={m.label} style={{ flex: 1, gap: 4, paddingHorizontal: 12, paddingVertical: 12 }}>
            <Text style={type.caption}>{m.label}</Text>
            <Text style={{ fontFamily: font.mono, fontSize: 17, color: color.ink }}>{m.value}</Text>
          </Card>
        ))}
      </View>

      <View style={{ flex: 1 }} />

      <Text style={type.caption}>This is an early warning, not a diagnosis. If risk stays high for 24 hours, book a visit with your care team.</Text>

      <View style={{ gap: 12 }}>
        <PrimaryButton label="Start therapy now" onPress={() => go('therapy')} />
        <SecondaryButton label="Share with my care team" />
      </View>
    </ScrollView>
  );
}
