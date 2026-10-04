"""Upload patch readings to Databricks.

Stands in for the phone or gateway that forwards a patch's readings to the cloud.
It takes any existing data source and stores its history in the `readings` table.

Examples:
    python patch_gateway.py --demo-cohort
    python patch_gateway.py --wound wound-006 --scenario infected --seed 2
    python patch_gateway.py --wound wound-007 --history sample_data/simulated_wound_history.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from wound_agent.data_sources import SCENARIOS, get_data_source
from wound_agent.databricks_store import DatabricksConfigError, DatabricksStore

# One wound per simulator scenario, seed 0.
DEMO_COHORT = {
    "wound-001": "healthy",
    "wound-002": "early_infection",
    "wound-003": "infected",
    "wound-004": "sensor_fault",
    "wound-005": "patch_lifted",
}
DEMO_SEED = 0


def main(argv=None, store=None) -> int:
    load_dotenv(Path(__file__).parent / ".env")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--demo-cohort", action="store_true", help="Upload five wounds, one per scenario.")
    parser.add_argument("--wound", help="Wound id to upload.")
    parser.add_argument("--scenario", default="infected", choices=list(SCENARIOS))
    parser.add_argument("--seed", type=int, default=None, help="Make simulated data reproducible.")
    parser.add_argument("--history", help="CSV/JSON of readings every 30 min to upload instead of simulating.")
    args = parser.parse_args(argv)
    if args.demo_cohort == bool(args.wound):
        parser.error("give either --demo-cohort or --wound")
    if args.demo_cohort and args.history:
        parser.error("--demo-cohort cannot be combined with --history")

    if store is None:
        try:
            store = DatabricksStore.from_env()
        except DatabricksConfigError as exc:
            print(exc, file=sys.stderr)
            return 1
    store.ensure_tables()

    if args.demo_cohort:
        uploads = [(wound, get_data_source(None, scenario, DEMO_SEED), "simulated")
                   for wound, scenario in DEMO_COHORT.items()]
    else:
        uploads = [(args.wound, get_data_source(args.history, args.scenario, args.seed),
                    "file" if args.history else "simulated")]

    for wound, source, source_name in uploads:
        rows = store.upload_readings(source.get_history(wound), source_name)
        print(f"{wound}: uploaded {rows} readings ({source_name}) to {store.readings}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
