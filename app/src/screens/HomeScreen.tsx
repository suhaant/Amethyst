import { ActivityIndicator, Pressable, ScrollView, Text, View } from 'react-native';
import { AmethystLockup, AmethystMark } from '../components/Logo';
import { Card, IconButton, Metric, PrimaryButton, StatusPill } from '../components/ui';
import { useLive } from '../data/live';
import { patch, Route } from '../data/mock';
import { color, font, radius, riskStyle, type } from '../theme';

export function HomeScreen({ go }: { go: (r: Route) => void }) {
  const live = useLive();
  const sign = live.tempDelta >= 0 ? '+' : '';
  return (
    <ScrollView contentContainerStyle={{ padding: 16, gap: 16 }}>
      <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingTop: 8 }}>
        <AmethystLockup height={28} />
        <IconButton icon="bell" label="Notifications" onPress={() => go('alert')} />
      </View>

      <View style={{ gap: 4 }}>
        <Text style={type.caption}>
          {patch.location} · Day {patch.padDay} of this pad
        </Text>
        <Text style={[type.title, { fontSize: 24, lineHeight: 30 }]}>{live.headline}</Text>
      </View>

      <Card tint="raised" style={{ padding: 20, gap: 16 }}>
        <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
          <StatusPill risk={live.risk} label={live.levelLabel} />
          {live.running ? (
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
              <ActivityIndicator size="small" color={color.brand} />
              <Text style={type.reading}>Analyzing</Text>
            </View>
          ) : (
            <Text style={type.reading}>Updated {live.updatedAgo}</Text>
          )}
        </View>
        <View style={{ flexDirection: 'row', alignItems: 'baseline', gap: 8 }}>
          <Text style={type.display}>{live.score}</Text>
          <Text style={type.body}>/ 100 infection risk</Text>
        </View>
        <View style={{ height: 8, borderRadius: radius.pill, backgroundColor: color.line, overflow: 'hidden' }}>
          <View style={{ width: `${Math.max(2, live.score)}%`, height: 8, backgroundColor: riskStyle[live.risk].fg }} />
        </View>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
          {['NORMAL', 'WARNING', 'INFECTION'].map((l) => (
            <Text key={l} style={[type.eyebrow, { color: color.inkMuted }]}>
              {l}
            </Text>
          ))}
        </View>
      </Card>

      <View style={{ flexDirection: 'row', gap: 12 }}>
        <Metric icon="droplet" label="pH" value={live.ph.toFixed(2)} />
        <Metric icon="thermometer" label="vs. baseline" value={`${sign}${live.tempDelta.toFixed(1)}°`} />
        <Metric icon="waves" label="Moisture" value={`${live.moisture}%`} />
      </View>

      <Card style={{ flexDirection: 'row', alignItems: 'center', gap: 14 }}>
        <AmethystMark size={36} />
        <View style={{ flex: 1, gap: 2 }}>
          <Text style={type.headline}>Amethyst patch</Text>
          <Text style={type.caption}>
            {live.connected ? 'Connected' : 'Offline'} · Battery {patch.battery}% · Last therapy {patch.lastTherapy}
          </Text>
        </View>
      </Card>

      <PrimaryButton label="View trends" onPress={() => go('trends')} />

      {/* Only needed when the demo server isn't reachable */}
      {!live.connected && (
        <Pressable accessibilityRole="button" onPress={() => go('alert')} style={{ alignSelf: 'center', padding: 8 }}>
          <Text style={{ fontFamily: font.medium, fontSize: 13, color: color.brand }}>Demo: simulate rising risk</Text>
        </Pressable>
      )}
    </ScrollView>
  );
}
