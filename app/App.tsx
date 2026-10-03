import { Inter_400Regular } from '@expo-google-fonts/inter/400Regular';
import { Inter_500Medium } from '@expo-google-fonts/inter/500Medium';
import { Inter_600SemiBold } from '@expo-google-fonts/inter/600SemiBold';
import { JetBrainsMono_500Medium } from '@expo-google-fonts/jetbrains-mono/500Medium';
import { useFonts } from 'expo-font';
import { StatusBar } from 'expo-status-bar';
import { useState } from 'react';
import { ActivityIndicator, Pressable, Text, View } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { Icon, IconName } from './src/components/Icon';
import { Route } from './src/data/mock';
import { AlertScreen } from './src/screens/AlertScreen';
import { HomeScreen } from './src/screens/HomeScreen';
import { PairScreen } from './src/screens/PairScreen';
import { TherapyScreen } from './src/screens/TherapyScreen';
import { TrendsScreen } from './src/screens/TrendsScreen';
import { color, font } from './src/theme';

const tabs: { route: Route; label: string; icon: IconName }[] = [
  { route: 'home', label: 'Home', icon: 'home' },
  { route: 'trends', label: 'Trends', icon: 'chart' },
  { route: 'therapy', label: 'Therapy', icon: 'zap' },
  { route: 'pair', label: 'Patch', icon: 'bluetooth' },
];

export default function App() {
  const [fontsLoaded] = useFonts({ Inter_400Regular, Inter_500Medium, Inter_600SemiBold, JetBrainsMono_500Medium });
  // Start on pairing, like a first launch. Change to 'home' to skip it.
  const [route, setRoute] = useState<Route>('pair');

  if (!fontsLoaded) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: color.surface }}>
        <ActivityIndicator color={color.brand} />
      </View>
    );
  }

  const showTabs = route !== 'pair' && route !== 'alert';

  return (
    <SafeAreaProvider>
      <SafeAreaView style={{ flex: 1, backgroundColor: color.surface }} edges={['top', 'left', 'right']}>
        <StatusBar style="dark" />
        <View style={{ flex: 1 }}>
          {route === 'home' && <HomeScreen go={setRoute} />}
          {route === 'trends' && <TrendsScreen />}
          {route === 'therapy' && <TherapyScreen go={setRoute} />}
          {route === 'pair' && <PairScreen go={setRoute} />}
          {route === 'alert' && <AlertScreen go={setRoute} />}
        </View>
      </SafeAreaView>
      {showTabs && (
        <SafeAreaView edges={['bottom']} style={{ backgroundColor: color.surface, borderTopWidth: 1, borderTopColor: color.line }}>
          <View accessibilityRole="tablist" style={{ flexDirection: 'row', paddingHorizontal: 8, paddingTop: 8 }}>
            {tabs.map((t) => {
              const on = t.route === route;
              const c = on ? color.brand : color.inkMuted;
              return (
                <Pressable
                  key={t.route}
                  accessibilityRole="tab"
                  accessibilityState={{ selected: on }}
                  onPress={() => setRoute(t.route)}
                  style={{ flex: 1, alignItems: 'center', gap: 4, paddingVertical: 6 }}
                >
                  <Icon name={t.icon} size={22} color={c} />
                  <Text style={{ fontFamily: font.semibold, fontSize: 11, color: c }}>{t.label}</Text>
                </Pressable>
              );
            })}
          </View>
        </SafeAreaView>
      )}
    </SafeAreaProvider>
  );
}
