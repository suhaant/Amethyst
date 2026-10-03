// Metro config: default Expo setup, plus a pass-through for the live demo.
// GET /api/state on the Expo dev server is forwarded to the Amethyst demo server
// (demo_ui/server.py, default http://localhost:8000). The phone already reaches the dev
// server to load the app (over Wi-Fi or `npx expo start --tunnel`), so live data takes the
// same path and works even on networks that block phone-to-laptop traffic.
const http = require('http');
const { getDefaultConfig } = require('expo/metro-config');

const DEMO_SERVER = process.env.AMETHYST_SERVER || 'http://localhost:8000';

const config = getDefaultConfig(__dirname);

config.server = {
  ...config.server,
  enhanceMiddleware: (metroMiddleware) => (req, res, next) => {
    if (req.method !== 'GET' || !req.url.startsWith('/api/state')) return metroMiddleware(req, res, next);
    http
      .get(`${DEMO_SERVER}/api/state`, (up) => {
        res.writeHead(up.statusCode || 502, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
        up.pipe(res);
      })
      .on('error', () => {
        res.writeHead(502, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ detail: `Demo server not reachable at ${DEMO_SERVER}` }));
      });
  },
};

module.exports = config;
