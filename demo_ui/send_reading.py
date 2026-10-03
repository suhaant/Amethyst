"""Pretend to be the patch: send readings to the demo server's hardware API.

Each reading goes to POST /api/readings, runs through the agent and the model, animates
in the demo UI and shows up in the app, exactly like a real patch would.

    python demo_ui/send_reading.py                      # one healthy reading
    python demo_ui/send_reading.py --scenario infection --count 8 --every 3
    python demo_ui/send_reading.py --ph 7.3 --temp 35.2 --impedance 6.5 --bg 115 --wg 2.6

Scenarios walk from the patient's baseline toward the target over --count readings.
Each reading stands for 30 minutes of patch data unless --hours says otherwise.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

KEYS = ["ph", "temp_c", "impedance_kohm", "blood_glucose_mgdl", "wound_glucose_mM"]


def call(url: str, method: str = "GET", body: dict | None = None) -> dict:
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"{e.code} from {url}: {e.read().decode()[:300]}")
    except urllib.error.URLError as e:
        sys.exit(f"Can't reach {url} ({e.reason}). Is demo_ui/server.py running?")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--server", default="http://localhost:8000")
    ap.add_argument("--scenario", default="healthy",
                    choices=["healthy", "early", "infection", "lifted", "fault"])
    ap.add_argument("--count", type=int, default=1, help="number of readings to send")
    ap.add_argument("--every", type=float, default=2.0, help="seconds between readings")
    ap.add_argument("--hours", type=float, default=0.5, help="patch time each reading covers")
    ap.add_argument("--agent", action="store_true", help="use the Claude Opus agent (slower)")
    for flag, key in [("--ph", "ph"), ("--temp", "temp_c"), ("--impedance", "impedance_kohm"),
                      ("--bg", "blood_glucose_mgdl"), ("--wg", "wound_glucose_mM")]:
        ap.add_argument(flag, type=float, dest=key, help="send this exact value")
    a = ap.parse_args()

    # Targets come from the server, so they match the model's own zones for this patient.
    cfg = call(f"{a.server}/api/config")
    name = {"healthy": "Healthy", "early": "Early infection", "infection": "Infection",
            "lifted": "Patch lifted", "fault": "Sensor fault"}[a.scenario]
    base, target = cfg["baseline"], cfg["presets"][name]["values"]

    for i in range(1, a.count + 1):
        f = i / a.count  # walk from baseline to the target
        body = {k: round(base[k] + (target[k] - base[k]) * f, 3) for k in KEYS}
        body.update({k: getattr(a, k) for k in KEYS if getattr(a, k) is not None})
        body.update(advance_hours=a.hours, use_agent=a.agent)
        out = call(f"{a.server}/api/readings", "POST", body)
        vals = "  ".join(f"{k}={body[k]:g}" for k in KEYS)
        print(f"[{i}/{a.count}] {vals}\n        -> risk {out['risk_score']:.0f} · {out['tier']} · {out['level']} · {out['therapy']}")
        if i < a.count:
            time.sleep(a.every)


if __name__ == "__main__":
    main()
