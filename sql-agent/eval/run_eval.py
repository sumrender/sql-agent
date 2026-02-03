"""CLI runner for SQL agent evaluation."""

import argparse
import asyncio
import sys
from pathlib import Path

# Ensure sql-agent root is on path when run as script
_sql_agent_root = Path(__file__).resolve().parent.parent
if str(_sql_agent_root) not in sys.path:
    sys.path.insert(0, str(_sql_agent_root))

from eval.evaluator import SQLAgentEvaluator
from eval.test_cases import TEST_CASES
from sql_agent import db, get_eval_agent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run SQL agent evaluation against Chinook test cases."
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Run only test cases in this category (e.g. aggregation, join, simple, filter, complex).",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("eval_results/eval_results.json"),
        help="Output path for JSON results (default: eval_results/eval_results.json).",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress per-test progress output.",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    test_cases = TEST_CASES
    if args.category:
        test_cases = [tc for tc in TEST_CASES if tc.get("category") == args.category]
        if not test_cases:
            print(f"No test cases found for category: {args.category}")
            sys.exit(1)
        print(f"Running {len(test_cases)} tests in category: {args.category}")
    else:
        print(f"Running all {len(test_cases)} tests")

    print("=" * 60)
    print("SQL Agent Evaluation")
    print("=" * 60)

    agent = get_eval_agent()
    evaluator = SQLAgentEvaluator(agent, db)
    summary = await evaluator.run_all_tests(test_cases, verbose=not args.quiet)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total tests:      {summary.total}")
    if summary.total > 0:
        pct = summary.passed / summary.total * 100
        print(f"Passed:           {summary.passed} ({pct:.1f}%)")
    print(f"Failed:           {summary.failed}")
    print(f"Answer accuracy: {summary.answer_accuracy * 100:.1f}%")
    print(f"Avg latency:     {summary.avg_latency_ms:.0f} ms")

    print("\nBy category:")
    for cat, stats in summary.by_category.items():
        total = stats["total"]
        passed = stats["passed"]
        pct = passed / total * 100 if total > 0 else 0
        print(f"  {cat}: {passed}/{total} ({pct:.0f}%)")

    out_path = args.output
    if not out_path.is_absolute():
        out_path = _sql_agent_root / out_path
    evaluator.export_results(out_path)
    print(f"\nDetailed results exported to {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
