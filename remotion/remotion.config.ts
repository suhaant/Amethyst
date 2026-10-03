/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import { Config } from "@remotion/cli/config";

Config.setRspack(true);
Config.setOverwriteOutput(true);

// H.264 by default. Quality flags (CRF 14, slow preset, PNG frames, AAC
// 320k) are passed by `npm run final` in scripts/studio.mjs, so audio-only
// stem renders aren't blocked by video-only options.
Config.setCodec("h264");
Config.setPixelFormat("yuv420p");
