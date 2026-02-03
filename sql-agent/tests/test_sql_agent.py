"""Parametrized pytest integration for SQL agent evaluation."""

import sys
from pathlib import Path

import pytest

# Ensure sql-agent root is on path when running tests
_sql_agent_root = Path(__file__).resolve().parent.parent
if str(_sql_agent_root) not in sys.path:
    sys.path.insert(0, str(_sql_agent_root))

from eval.evaluator import SQLAgentEvaluator
from eval.test_cases import TEST_CASES
from sql_agent import db, get_eval_agent


@pytest.fixture
def evaluator():
    """Create an evaluator using the eval agent (no HITL)."""
    agent = get_eval_agent()
    return SQLAgentEvaluator(agent, db)


@pytest.mark.asyncio
@pytest.mark.parametrize("test_case", TEST_CASES, ids=lambda tc: tc["id"])
async def test_sql_agent(evaluator, test_case):
    """Run a single test case and assert it passes."""
    result = await evaluator.run_single_test(test_case)
    assert result.passed, (
        f"Test {test_case['id']} failed: "
        f"error={result.error!r}, "
        f"answer_correct={result.answer_correct}. "
        f"Response: {(result.agent_response or '')[:200]}..."
    )
