"""Core evaluation logic for the SQL agent."""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


def _is_parse_error(exc: BaseException) -> bool:
    """True if the exception looks like a transient JSON/parsing error."""
    msg = str(exc).lower()
    return "object key string" in msg or "json" in msg


@dataclass
class EvalResult:
    """Result of a single test case run."""

    test_id: str
    question: str
    passed: bool
    agent_response: Optional[str] = None
    answer_correct: bool = False
    error: Optional[str] = None
    error_debug: Optional[str] = None
    latency_ms: float = 0.0


@dataclass
class EvalSummary:
    """Aggregated metrics across all test runs."""

    total: int = 0
    passed: int = 0
    failed: int = 0
    answer_accuracy: float = 0.0
    avg_latency_ms: float = 0.0
    by_category: dict = field(default_factory=dict)


class SQLAgentEvaluator:
    """Evaluates the SQL agent against a set of test cases."""

    def __init__(self, agent: Any, db: Any = None):
        self.agent = agent
        self.db = db
        self.results: list[EvalResult] = []

    def _get_final_response_text(self, messages: list[BaseMessage]) -> str:
        """Extract the final assistant response from the message list."""
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content:
                content = msg.content
                if isinstance(content, str):
                    return content
                if isinstance(content, list):
                    parts = [
                        p.get("text", p) if isinstance(p, dict) else str(p)
                        for p in content
                    ]
                    return " ".join(parts)
        return ""

    def check_answer_contains(self, response: str, expected: list[str]) -> bool:
        """Check if response contains all expected values (case-insensitive)."""
        if not response:
            return False
        response_lower = response.lower()
        return all(val.lower() in response_lower for val in expected)

    async def run_single_test(self, test_case: dict) -> EvalResult:
        """Run a single test case and return the result. Retries once on JSON/parse errors."""
        result = EvalResult(
            test_id=test_case["id"],
            question=test_case["question"],
            passed=False,
        )

        start = time.perf_counter()
        last_exception = None
        for attempt in range(2):
            try:
                response = await self.agent.ainvoke(
                    {"messages": [HumanMessage(content=test_case["question"])]}
                )

                result.latency_ms = (time.perf_counter() - start) * 1000

                messages = response.get("messages", [])
                final_message = self._get_final_response_text(messages)
                result.agent_response = final_message

                if test_case.get("expected_answer_contains"):
                    result.answer_correct = self.check_answer_contains(
                        final_message, test_case["expected_answer_contains"]
                    )
                else:
                    result.answer_correct = True

                result.passed = result.answer_correct
                return result

            except Exception as e:
                last_exception = e
                result.latency_ms = (time.perf_counter() - start) * 1000
                result.error = str(e)
                if _is_parse_error(e):
                    result.error_debug = "json_parse"
                    if attempt == 0:
                        continue
                break

        if last_exception is not None:
            result.error = str(last_exception)
            if _is_parse_error(last_exception):
                result.error_debug = "json_parse"
        return result

    async def run_all_tests(
        self, test_cases: list[dict], verbose: bool = True
    ) -> EvalSummary:
        """Run all test cases and return summary."""
        self.results = []

        for tc in test_cases:
            result = await self.run_single_test(tc)
            self.results.append(result)
            if verbose:
                status = "PASS" if result.passed else "FAIL"
                short_q = (tc["question"][:50] + "…") if len(tc["question"]) > 50 else tc["question"]
                print(f"  [{status}] {tc['id']}: {short_q}")

        return self.compute_summary(test_cases)

    def compute_summary(self, test_cases: list[dict]) -> EvalSummary:
        """Compute evaluation metrics from results."""
        summary = EvalSummary(total=len(self.results))

        answer_correct_count = 0
        total_latency = 0.0
        category_stats: dict[str, dict] = {}

        for result, tc in zip(self.results, test_cases):
            if result.passed:
                summary.passed += 1
            else:
                summary.failed += 1

            if result.answer_correct:
                answer_correct_count += 1

            total_latency += result.latency_ms

            cat = tc.get("category", "uncategorized")
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "passed": 0}
            category_stats[cat]["total"] += 1
            if result.passed:
                category_stats[cat]["passed"] += 1

        summary.answer_accuracy = (
            answer_correct_count / summary.total if summary.total > 0 else 0.0
        )
        summary.avg_latency_ms = (
            total_latency / summary.total if summary.total > 0 else 0.0
        )
        summary.by_category = category_stats

        return summary

    def export_results(self, filepath: str | Path) -> None:
        """Export results to JSON for analysis."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(self.results),
                "passed": sum(1 for r in self.results if r.passed),
                "failed": sum(1 for r in self.results if not r.passed),
            },
            "results": [
                {
                    "test_id": r.test_id,
                    "question": r.question,
                    "passed": r.passed,
                    "answer_correct": r.answer_correct,
                    "agent_response": r.agent_response,
                    "error": r.error,
                    "error_debug": r.error_debug,
                    "latency_ms": r.latency_ms,
                }
                for r in self.results
            ],
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
