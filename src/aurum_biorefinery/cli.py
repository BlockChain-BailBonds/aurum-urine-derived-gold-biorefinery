"""Command-line interface for AURUM scenario validation and evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from .model import ScenarioError, evaluate, sensitivity_grid
from .serialization import dumps_result, load_scenario, result_document


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aurum",
        description="Evaluate mass-conserving AURUM gold-recovery scenarios.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    validate = subcommands.add_parser("validate", help="Validate a scenario without evaluating it")
    validate.add_argument("scenario", type=Path)

    run = subcommands.add_parser("run", help="Evaluate a scenario")
    run.add_argument("scenario", type=Path)
    run.add_argument("--pretty", action="store_true", help="Indent JSON output")
    run.add_argument("--output", type=Path, help="Write JSON to this path instead of stdout")

    sensitivity = subcommands.add_parser("sensitivity", help="Run a concentration/affinity grid")
    sensitivity.add_argument("scenario", type=Path)
    sensitivity.add_argument(
        "--concentration-mg-l",
        nargs="+",
        required=True,
        help="One or more nonnegative feed concentrations",
    )
    sensitivity.add_argument(
        "--affinity",
        nargs="+",
        required=True,
        help="One or more capture fractions in [0, 1]",
    )
    sensitivity.add_argument("--pretty", action="store_true", help="Indent JSON output")
    sensitivity.add_argument("--output", type=Path, help="Write JSON to this path")
    return parser


def _emit(payload: str, output: Path | None) -> None:
    if output is None:
        print(payload)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        scenario = load_scenario(args.scenario)
        if args.command == "validate":
            print(f"valid: {scenario.name} ({scenario.evidence_status})")
            return 0
        if args.command == "run":
            _emit(dumps_result(evaluate(scenario), pretty=args.pretty), args.output)
            return 0
        results = sensitivity_grid(
            scenario,
            concentrations_mg_l=args.concentration_mg_l,
            affinity_capture_fractions=args.affinity,
        )
        document = {
            "schema_version": "aurum.sensitivity.v1",
            "results": [result_document(result) for result in results],
        }
        _emit(
            json.dumps(document, indent=2 if args.pretty else None, sort_keys=True),
            args.output,
        )
        return 0
    except ScenarioError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
