# Amethyst app (Expo)

The Amethyst wound-patch companion app, coded from the Amethyst App Mockups canvas. Five screens: Pair, Home, Risk alert, Therapy, Trends.

## Run it on your phone with Expo Go

1. Install **Node.js 20+** on your laptop and the **Expo Go** app on your phone.
2. In this folder:
   ```bash
   npm install
   npx expo start
   ```
3. Scan the QR code: Camera app on iPhone, or the scanner inside Expo Go on Android. Phone and laptop must be on the same Wi-Fi. On campus Wi-Fi that blocks device-to-device traffic, use `npx expo start --tunnel` instead.

This project uses **Expo SDK 57**. If Expo Go says the project is incompatible, update Expo Go from the App Store / Play Store; if it still complains, run `npx expo install --fix`.

## Demo tips for the pitch

- The app opens on **Pair** and "finds" the patch after about 2 seconds. Tap **Connect patch**.
- On **Home**, tap **Demo: simulate rising risk** (or the bell) to jump to the warning alert.
- **Start therapy now** opens the therapy screen with a live countdown; you can pause it.
- To skip pairing, change `useState<Route>('pair')` to `'home'` in `App.tsx`.

## Where things live

| Path | What |
| --- | --- |
| `src/theme.ts` | Amethyst colors, type, spacing, radii (same values as the design system) |
| `src/components/Logo.tsx` | The crystal mark and the wordmark lockup (crystal on the right) |
| `src/components/Icon.tsx` | Lucide icons drawn with react-native-svg |
| `src/components/ui.tsx` | Status pill, buttons, cards, metric tile |
| `src/components/LineChart.tsx` | Small chart for pH and temperature |
| `src/data/mock.ts` | **All demo readings.** Replace these with live Bluetooth data later |
| `src/screens/*` | One file per screen |

Navigation is a simple state switch in `App.tsx` so nothing extra can break in Expo Go. If the app grows, move to Expo Router (see `AGENTS.md`).

## Connecting the real patch later

Expo Go can't talk to custom Bluetooth hardware. When the nRF52 board is streaming, add `react-native-ble-plx`, make a development build (`npx expo run:ios` or `eas build --profile development`), and feed its readings into the shapes in `src/data/mock.ts`.
