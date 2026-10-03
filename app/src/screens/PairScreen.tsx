import { useEffect, useState } from 'react';
import { ActivityIndicator, Text, View } from 'react-native';
import { Icon } from '../components/Icon';
import { AmethystLockup, AmethystMark } from '../components/Logo';
import { Card, Eyebrow, PrimaryButton, SecondaryButton, StatusPill } from '../components/ui';
import { patch, Route } from '../data/mock';
import { color, font, radius, type } from '../theme';

export function PairScreen({ go }: { go: (r: Route) => void }) {
  // Fake a short Bluetooth scan so the demo feels real.
  const [found, setFound] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setFound(true), 1600);
    return () => clearTimeout(t);
  }, []);

  return (
    <View style={{ flex: 1, padding: 16, gap: 24 }}>
      <View style={{ paddingTop: 8 }}>
        <AmethystLockup height={28} />
      </View>

      <View style={{ height: 220, borderRadius: radius.lg, backgroundColor: color.surfaceTint, alignItems: 'center', justifyContent: 'center' }}>
        <AmethystMark size={132} />
      </View>

      <View style={{ gap: 8 }}>
        <Eyebrow>Step 2 of 3</Eyebrow>
        <Text style={type.title}>Pair your patch</Text>
        <Text style={type.body}>Snap the pod onto a fresh pad, then hold its button for 3 seconds until the light blinks violet.</Text>
      </View>

      <Card style={{ flexDirection: 'row', alignItems: 'center', gap: 14 }}>
        <View style={{ width: 44, height: 44, borderRadius: radius.md, backgroundColor: color.surfaceTint, alignItems: 'center', justifyContent: 'center' }}>
          <Icon name="bluetooth" size={22} color={color.brand} />
        </View>
        <View style={{ flex: 1, gap: 2 }}>
          <Text style={type.headline}>Amethyst patch</Text>
          <Text style={type.reading}>{found ? `ID ${patch.id} · Signal strong` : 'Searching…'}</Text>
        </View>
        {found ? <StatusPill risk="normal" label="Found" /> : <ActivityIndicator color={color.brand} />}
      </Card>

      <View style={{ flex: 1 }} />

      <View style={{ gap: 12 }}>
        <PrimaryButton label={found ? 'Connect patch' : 'Searching for patch…'} onPress={found ? () => go('home') : undefined} />
        <SecondaryButton label="I need help pairing" />
      </View>
      <Text style={{ fontFamily: font.regular, fontSize: 11, color: color.inkMuted, textAlign: 'center' }}>Demo mode · no real Bluetooth connection yet</Text>
    </View>
  );
}
