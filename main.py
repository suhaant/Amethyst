"""Run a wound-infection assessment for one sensor reading.

Examples:
    python main.py                               # dummy "infected" reading, Opus agent
    python main.py --scenario healthy --seed 1
    python main.py --reading sample_data/reading_example.json
    python main.py --offline                     # skip the LLM (no API key needed)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from wound_agent.agent import AgentRefusedError, run_assessment, run_offline
from wound_agent.data_sources import SCENARIOS, get_data_source
from wound_agent.model import load_model


def main() -> int:
    load_dotenv(Path(__file__).parent / ".env")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--patient", default="patient-001")
    parser.add_argument("--scenario", default="infected", choices=list(SCENARIOS))
    parser.add_argument("--seed", type=int, default=None, help="Make dummy data reproducible.")
    parser.add_argument("--reading", help="Path to a JSON SensorReading (real data).")
    parser.add_argument("--offline", action="store_true", help="Run without the LLM agent.")
    parser.add_argument("--out", help="Also write the assessment JSON to this path.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print agent tool calls.")
    args = parser.parse_args()

    source = get_data_source(args.reading, args.scenario, args.seed)
    model = load_model()

    if not args.offline and not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set. Add it to .env (see .env.example) or use --offline.", file=sys.stderr)
        return 1

    if args.offline:
        assessment = run_offline(args.patient, source, model)
    else:
        try:
            assessment = run_assessment(args.patient, source, model, verbose=args.verbose)
        except AgentRefusedError as exc:
            print(exc, file=sys.stderr)
            return 2

    output = assessment.model_dump_json(indent=2)
    sys.stdout.reconfigure(encoding="utf-8")
    print(output)
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
