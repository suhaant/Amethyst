import { useEffect, useState } from 'react';
import { ScrollView, Text, View } from 'react-native';
import Svg, { Circle } from 'react-native-svg';
import { Icon } from '../components/Icon';
import { Card, Eyebrow, IconButton, PrimaryButton, SecondaryButton } from '../components/ui';
import { plan, Route } from '../data/mock';
import { color, font, type } from '../theme';

const LIGHT_DOSE_SECONDS = plan.lightMinutes * 60;

export function TherapyScreen({ go }: { go: (r: Route) => void }) {
  // Live countdown so the demo moves on stage.
  const [remaining, setRemaining] = useState(540);
  const [paused, setPaused] = useState(false);
  useEffect(() => {
    if (paused || remaining <= 0) return;
    const t = setInterval(() => setRemaining((s) => Math.max(0, s - 1)), 1000);
    return () => clearInterval(t);
  }, [paused, remaining]);

  const done = remaining === 0;
  const progress = 1 - remaining / LIGHT_DOSE_SECONDS;
  const mm = String(Math.floor(remaining / 60)).padStart(2, '0');
  const ss = String(remaining % 60).padStart(2, '0');
  const size = 180;
  const r = 78;
  const circ = 2 * Math.PI * r;

  return (
    <ScrollView contentContainerStyle={{ padding: 16, gap: 20, flexGrow: 1 }}>
      <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingTop: 8 }}>
        <IconButton icon="back" label="Back" onPress={() => go('home')} />
        <Eyebrow>{`Session 1 of ${plan.sessionsPerDay} today`}</Eyebrow>
      </View>

      <Text style={type.title}>{done ? 'Therapy complete' : 'Therapy in progress'}</Text>

      <Card tint="brand" style={{ padding: 24, alignItems: 'center', gap: 8 }}>
        <View style={{ width: size, height: size, alignItems: 'center', justifyContent: 'center' }}>
          <Svg width={size} height={size} style={{ position: 'absolute' }}>
            <Circle cx={size / 2} cy={size / 2} r={r} stroke={color.line} strokeWidth={10} fill="none" />
            <Circle
              cx={size / 2}
              cy={size / 2}
              r={r}
              stroke={color.brand}
              strokeWidth={10}
              fill="none"
              strokeLinecap="round"
              strokeDasharray={`${circ * progress} ${circ}`}
              transform={`rotate(-90 ${size / 2} ${size / 2})`}
            />
          </Svg>
          <Text style={{ fontFamily: font.mono, fontSize: 30, color: color.ink }}>
            {mm}:{ss}
          </Text>
          <Text style={type.caption}>remaining</Text>
        </View>
        <Text style={type.headline}>405 nm violet light</Text>
        <Text style={type.caption}>Killing bacteria exposed by ultrasound</Text>
      </Card>

      <Card style={{ padding: 0 }}>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12, padding: 16, borderBottomWidth: 1, borderBottomColor: color.line }}>
          <Icon name="check" color={color.riskNormal} strokeWidth={2} />
          <View style={{ flex: 1 }}>
            <Text style={type.headline}>Ultrasound</Text>
            <Text style={type.caption}>{`Biofilm broken up · ${plan.ultrasoundKhz} kHz · ${plan.ultrasoundMinutes} min`}</Text>
          </View>
          <Text style={{ fontFamily: font.semibold, fontSize: 13, color: color.riskNormal }}>Done</Text>
        </View>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12, padding: 16 }}>
          <Icon name={done ? 'check' : 'sun'} color={done ? color.riskNormal : color.brand} />
          <View style={{ flex: 1 }}>
            <Text style={type.headline}>Violet light</Text>
            <Text style={type.caption}>{`405 nm · ${plan.lightMinutes} min dose`}</Text>
          </View>
          <Text style={{ fontFamily: font.semibold, fontSize: 13, color: done ? color.riskNormal : color.brand }}>{done ? 'Done' : paused ? 'Paused' : 'Running'}</Text>
        </View>
      </Card>

      <Card tint="raised" style={{ flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 12, borderRadius: 10 }}>
        <Icon name="thermometer" size={18} color={color.inkMuted} />
        <Text style={type.caption}>
          Skin temp <Text style={{ fontFamily: font.mono, color: color.ink }}>34.6°C</Text> · auto-stops at <Text style={{ fontFamily: font.mono, color: color.ink }}>39°C</Text>
        </Text>
      </Card>

      <View style={{ flex: 1 }} />

      {done ? (
        <PrimaryButton label="Back to home" onPress={() => go('home')} />
      ) : (
        <SecondaryButton label={paused ? 'Resume session' : 'Pause session'} onPress={() => setPaused((p) => !p)} />
      )}
    </ScrollView>
  );
}
