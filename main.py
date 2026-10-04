"""Run a wound-infection assessment over a wound's sensor history.

Examples:
    python main.py                               # dummy "infected" wound, Opus agent
    python main.py --scenario healthy --seed 1
    python main.py --history sample_data/simulated_wound_history.csv
    python main.py --offline                     # skip the LLM (no API key needed)
    python main.py --databricks --wound wound-003   # read readings from Databricks, save the assessment back
    python main.py --databricks --all               # assess every wound stored in Databricks
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from wound_agent.agent import AgentRefusedError, run_assessment, run_offline
from wound_agent.data_sources import SCENARIOS, get_data_source
from wound_agent.model import RiskModel


def main(argv=None, store=None) -> int:
    load_dotenv(Path(__file__).parent / ".env")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--wound", default="wound-001")
    parser.add_argument("--scenario", default="infected", choices=list(SCENARIOS))
    parser.add_argument("--seed", type=int, default=None, help="Make dummy data reproducible.")
    parser.add_argument("--history", help="CSV/JSON of readings every 30 min (real data).")
    parser.add_argument("--offline", action="store_true", help="Run without the LLM agent.")
    parser.add_argument("--out", help="Also write the assessment JSON to this path.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print agent tool calls.")
    parser.add_argument("--databricks", action="store_true",
                        help="Read the history from Databricks and save the assessment back.")
    parser.add_argument("--all", action="store_true", help="Assess every wound in Databricks (needs --databricks).")
    args = parser.parse_args(argv)
    if args.all and not args.databricks:
        parser.error("--all requires --databricks")
    if args.all and args.out:
        parser.error("--all cannot be combined with --out")
    if args.databricks and args.history:
        parser.error("--databricks cannot be combined with --history")

    if args.databricks:
        from wound_agent.databricks_store import DatabricksConfigError, DatabricksStore

        if store is None:
            try:
                store = DatabricksStore.from_env()
            except DatabricksConfigError as exc:
                print(exc, file=sys.stderr)
                return 1
        source = store
    else:
        source = get_data_source(args.history, args.scenario, args.seed)
    model = RiskModel()

    if not args.offline and not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set. Add it to .env (see .env.example) or use --offline.", file=sys.stderr)
        return 1

    wounds = store.list_wounds() if args.all else [args.wound]
    sys.stdout.reconfigure(encoding="utf-8")
    exit_code = 0
    for wound in wounds:
        if args.offline:
            assessment = run_offline(wound, source, model)
        else:
            try:
                assessment = run_assessment(wound, source, model, verbose=args.verbose)
            except AgentRefusedError as exc:
                print(exc, file=sys.stderr)
                if not args.all:
                    return 2
                exit_code = 2
                continue

        output = assessment.model_dump_json(indent=2)
        print(output)
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        if args.databricks:
            # Printed first, so a failed save never loses the result.
            try:
                store.save_assessment(assessment)
            except Exception as exc:
                print(f"Could not save the assessment for {wound} to Databricks: {exc}", file=sys.stderr)
                exit_code = exit_code or 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
