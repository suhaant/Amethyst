import { useEffect, useState } from 'react';
import { ScrollView, Text, View } from 'react-native';
import Svg, { Circle } from 'react-native-svg';
import { Icon } from '../components/Icon';
import { Card, Eyebrow, IconButton, PrimaryButton, SecondaryButton } from '../components/ui';
import { useLive } from '../data/live';
import { Route } from '../data/mock';
import { color, font, type } from '../theme';

export function TherapyScreen({ go }: { go: (r: Route) => void }) {
  const live = useLive();
  const plan = live.plan;
  // The main step: violet light when the model calls for it, otherwise healing ultrasound.
  const light = plan.lightMinutes > 0;
  const mainMinutes = light ? plan.lightMinutes : plan.healingMinutes;
  const DOSE_SECONDS = Math.max(1, Math.round(mainMinutes * 60));
  const fmt = (m: number) => (Number.isInteger(m) ? `${m}` : m.toFixed(1));

  // Live countdown so the demo moves on stage; restarts when the model sends a new plan.
  const [remaining, setRemaining] = useState(DOSE_SECONDS);
  const [paused, setPaused] = useState(false);
  useEffect(() => {
    setRemaining(DOSE_SECONDS);
    setPaused(false);
  }, [DOSE_SECONDS, live.seq]);
  useEffect(() => {
    if (paused || remaining <= 0) return;
    const t = setInterval(() => setRemaining((s) => Math.max(0, s - 1)), 1000);
    return () => clearInterval(t);
  }, [paused, remaining]);

  const done = remaining === 0;
  const progress = 1 - remaining / DOSE_SECONDS;
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

      <Text style={type.title}>
        {plan.skipped ? 'Therapy paused' : mainMinutes === 0 ? 'No therapy needed' : !light ? (done ? 'Healing session complete' : 'Healing support') : done ? 'Therapy complete' : 'Therapy in progress'}
      </Text>
      {!light && !plan.skipped && mainMinutes > 0 && <Text style={type.body}>No infection treatment needed. Gentle ultrasound helps the wound heal.</Text>}
      {plan.skipped && <Text style={type.body}>The patch is off the skin, so Amethyst won't run ultrasound or light. Press it back down.</Text>}

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
        <Text style={type.headline}>{light ? '405 nm violet light' : '1.5 MHz healing ultrasound'}</Text>
        <Text style={type.caption}>{light ? 'Killing bacteria exposed by ultrasound' : 'Low-intensity ultrasound to speed healing'}</Text>
      </Card>

      <Card style={{ padding: 0 }}>
        {plan.ultrasoundMinutes > 0 && (
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12, padding: 16, borderBottomWidth: 1, borderBottomColor: color.line }}>
            <Icon name="check" color={color.riskNormal} strokeWidth={2} />
            <View style={{ flex: 1 }}>
              <Text style={type.headline}>Ultrasound</Text>
              <Text style={type.caption}>{`Biofilm broken up · ${plan.ultrasoundKhz} kHz · ${fmt(plan.ultrasoundMinutes)} min`}</Text>
            </View>
            <Text style={{ fontFamily: font.semibold, fontSize: 13, color: color.riskNormal }}>Done</Text>
          </View>
        )}
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12, padding: 16 }}>
          <Icon name={done ? 'check' : 'sun'} color={done ? color.riskNormal : color.brand} />
          <View style={{ flex: 1 }}>
            <Text style={type.headline}>{light ? 'Violet light' : 'Healing ultrasound'}</Text>
            <Text style={type.caption}>{light ? `405 nm · ${fmt(plan.lightMinutes)} min dose` : `1.5 MHz · ${fmt(plan.healingMinutes)} min`}</Text>
          </View>
          <Text style={{ fontFamily: font.semibold, fontSize: 13, color: done ? color.riskNormal : color.brand }}>{done ? 'Done' : paused ? 'Paused' : 'Running'}</Text>
        </View>
      </Card>

      <Card tint="raised" style={{ flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 12, borderRadius: 10 }}>
        <Icon name="thermometer" size={18} color={color.inkMuted} />
        <Text style={type.caption}>
          Skin temp <Text style={{ fontFamily: font.mono, color: color.ink }}>{live.temp.toFixed(1)}°C</Text> · auto-stops at <Text style={{ fontFamily: font.mono, color: color.ink }}>39°C</Text>
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
