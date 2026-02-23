# ============================================================
# utils.py — Shared utility functions
# Used by execution.py and app.py.
# No CrewAI imports here — pure Python utilities.
# ============================================================

import json
import re
import time


# ── Input validation ─────────────────────────────────────────────────────────

def validate_input(text: str, min_len: int = 30) -> tuple:
    """
    Validates startup idea input before any API call.
    Returns (is_valid: bool, reason: str).

    Fails fast — saves tokens and quota on garbage input.
    """
    if not text or not text.strip():
        return False, "Input is empty"
    if len(text.strip()) < min_len:
        return False, f"Too short — minimum {min_len} characters, got {len(text.strip())}"
    if len(text.strip()) > 3000:
        return False, "Too long — maximum 3000 characters"
    generic = {"test", "hello", "hi", "startup", "idea", "ai startup", "my idea"}
    if text.strip().lower() in generic:
        return False, "Too generic — include market size, pricing model, and key risks"
    return True, "valid"


# ── JSON extraction ───────────────────────────────────────────────────────────

def extract_json_safe(text: str) -> dict:
    """
    Two-pass JSON extraction from LLM output.

    Pass 1: Strip markdown fences, find outermost braces, parse directly.
    Pass 2: Fix common LLM issues (trailing commas, structural noise).

    Never raises — returns {"error": ...} on total failure.
    Never call json.loads() directly on LLM output.
    """
    match = None
    try:
        cleaned = re.sub(r'```json\s*', '', text)
        cleaned = re.sub(r'```\s*', '', cleaned)
        match   = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, Exception):
        pass

    try:
        if match:
            fixed = re.sub(r',\s*}', '}', match.group())
            fixed = re.sub(r',\s*]', ']', fixed)
            return json.loads(fixed)
    except Exception:
        pass

    return {
        "error": "JSON extraction failed after two passes",
        "raw_preview": text[:400] if text else "empty output",
    }


# ── Output validation ─────────────────────────────────────────────────────────

def validate_output(data: dict) -> list:
    """
    Full validation pipeline.
    Returns list of (icon, key, message, passed: bool).

    Checks:
    - Required field presence
    - Score range 0–10
    - Business logic: risk > 8 → no Invest
    - recommended_actions type and length
    """
    results = []

    if "error" in data:
        results.append(("✗", "json_extraction", data["error"], False))
        return results

    required = [
        "market_score", "market_summary",
        "financial_score", "financial_summary",
        "risk_score", "risk_summary",
        "final_decision", "confidence_level",
        "recommended_actions",
    ]
    for key in required:
        if key in data:
            results.append(("✓", key, "present", True))
        else:
            results.append(("✗", key, "MISSING — required field", False))

    for sk in ["market_score", "financial_score", "risk_score"]:
        if sk in data:
            v = data[sk]
            if isinstance(v, (int, float)) and 0 <= float(v) <= 10:
                results.append(("✓", f"{sk} range", f"valid: {v}/10", True))
            else:
                results.append(("✗", f"{sk} range", f"OUT OF RANGE: {v}", False))

    if "risk_score" in data and "final_decision" in data:
        rs = float(data.get("risk_score", 0))
        fd = str(data.get("final_decision", "")).strip().lower()
        if rs > 8 and fd == "invest":
            results.append(("✗", "risk/decision logic",
                             f"CONFLICT — risk {rs} > 8 but decision is 'Invest'", False))
        elif rs > 8:
            results.append(("✓", "risk/decision logic",
                             f"consistent — high risk ({rs}) correctly avoided 'Invest'", True))
        else:
            results.append(("✓", "risk/decision logic", "passed", True))

    if "recommended_actions" in data:
        ra = data["recommended_actions"]
        if isinstance(ra, list) and len(ra) >= 3:
            results.append(("✓", "recommended_actions", f"{len(ra)} actions returned", True))
        elif isinstance(ra, list):
            results.append(("⚠", "recommended_actions",
                             f"only {len(ra)} action(s) — expected 5", len(ra) >= 1))
        else:
            results.append(("✗", "recommended_actions", "not a list", False))

    return results


def all_passed(validation_results: list) -> bool:
    """Returns True if every validation check passed."""
    return all(r[3] for r in validation_results)


# ── Retry wrapper ─────────────────────────────────────────────────────────────

def safe_kickoff(crew, retries: int = 3, delay: float = 2.0) -> tuple:
    """
    Retry-wrapped crew execution.
    Returns (result_or_error, attempts_used: int, success: bool).

    Logs nothing — caller is responsible for UI feedback.
    """
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            result = crew.kickoff()
            return result, attempt, True
        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(delay)
    return last_error, retries, False


# ── Cost estimation ───────────────────────────────────────────────────────────

def estimate_cost(task_description: str, attempts: int,
                  output_tokens: int = 400) -> dict:
    """
    Rough token and cost estimate for a single analysis run.
    Directional — not real billing data.
    Based on Gemini 2.5 Flash pricing (~$0.075 per 1M tokens).
    """
    input_tokens  = round(len(task_description.split()) * 1.3)
    total_tokens  = (input_tokens + output_tokens) * attempts
    cost_usd      = round(total_tokens * 0.000001 * 0.075, 6)
    return {
        "input_tokens":  input_tokens,
        "output_tokens": output_tokens,
        "total_tokens":  total_tokens,
        "attempts":      attempts,
        "cost_usd":      cost_usd,
    }
