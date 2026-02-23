# ============================================================
# execution.py — Clean execution layer
# This is the only file app.py needs to import.
# It orchestrates: crew_setup → safe_kickoff → extract → validate
# ============================================================

from crewai import LLM

from crew_setup import create_startup_crew
from utils import (
    validate_input,
    extract_json_safe,
    validate_output,
    safe_kickoff,
    estimate_cost,
    all_passed,
)


def run_startup_analysis(
    startup_idea: str,
    model_id: str,
    api_key: str,
    revenue: float = 500000.0,
    cost: float = 150000.0,
    industry: str = "AI SaaS",
    persona: str = "Venture Capital Partner",
    stage: str = "Seed",
    risk_tolerance: str = "Balanced",
    temperature: float = 0.2,
    use_specialists: bool = True,
    max_retries: int = 3,
    retry_delay: float = 2.0,
    min_input_len: int = 30,
    auto_regen: bool = True,
) -> dict:
    """
    Single entry point for the entire analysis pipeline.

    app.py calls this function — nothing else.

    Returns a dict with:
    - success: bool
    - data: parsed JSON dict (or None)
    - validation: list of validation results
    - attempts: int
    - cost_estimate: dict
    - error: str (if failed)
    - stage: str (which layer failed, if any)
    """

    # ── Layer 1: Input validation ──────────────────────────────────────────
    is_valid, reason = validate_input(startup_idea, min_input_len)
    if not is_valid:
        return {
            "success":       False,
            "error":         reason,
            "stage":         "input_validation",
            "data":          None,
            "validation":    [],
            "attempts":      0,
            "cost_estimate": {},
        }

    # ── Layer 2: Build LLM + crew ──────────────────────────────────────────
    import os
    is_gemini = model_id.startswith("gemini/")
    if is_gemini:
        os.environ["GEMINI_API_KEY"] = api_key

    try:
        llm = LLM(model=model_id, api_key=api_key, temperature=temperature)
        crew, main_task = create_startup_crew(
            startup_idea    = startup_idea,
            llm             = llm,
            revenue         = revenue,
            cost            = cost,
            industry        = industry,
            persona         = persona,
            stage           = stage,
            risk_tolerance  = risk_tolerance,
            use_specialists = use_specialists,
        )
    except Exception as e:
        return {
            "success":       False,
            "error":         f"Crew initialization failed: {str(e)}",
            "stage":         "crew_setup",
            "data":          None,
            "validation":    [],
            "attempts":      0,
            "cost_estimate": {},
        }

    # ── Layer 3: Retry-wrapped execution ───────────────────────────────────
    result, attempts_used, success = safe_kickoff(
        crew, retries=max_retries, delay=retry_delay
    )

    if not success:
        return {
            "success":       False,
            "error":         f"All {max_retries} attempts failed: {str(result)}",
            "stage":         "crew_execution",
            "data":          None,
            "validation":    [],
            "attempts":      attempts_used,
            "cost_estimate": {},
        }

    # ── Layer 4: JSON extraction ───────────────────────────────────────────
    raw_text = str(main_task.output.raw) if main_task.output else str(result)
    parsed   = extract_json_safe(raw_text)

    if "error" in parsed and auto_regen:
        # Auto-regenerate once on extraction failure
        result2, attempts2, success2 = safe_kickoff(
            crew, retries=2, delay=retry_delay
        )
        attempts_used += attempts2
        if success2:
            raw_text2 = str(main_task.output.raw) if main_task.output else str(result2)
            parsed = extract_json_safe(raw_text2)

    if "error" in parsed:
        return {
            "success":       False,
            "error":         f"JSON extraction failed: {parsed['error']}",
            "stage":         "json_extraction",
            "data":          parsed,
            "validation":    [],
            "attempts":      attempts_used,
            "cost_estimate": estimate_cost(str(main_task.description), attempts_used),
        }

    # ── Layer 5: Schema + business logic validation ────────────────────────
    val_results = validate_output(parsed)

    # Compute total_score if missing or wrong
    try:
        ms = float(parsed.get("market_score", 0))
        fs = float(parsed.get("financial_score", 0))
        rs = float(parsed.get("risk_score", 0))
        parsed["total_score"] = round((ms + fs + (10 - rs)) / 3, 1)
    except Exception:
        pass

    return {
        "success":       True,
        "error":         None,
        "stage":         "complete",
        "data":          parsed,
        "validation":    val_results,
        "all_passed":    all_passed(val_results),
        "attempts":      attempts_used,
        "cost_estimate": estimate_cost(str(main_task.description), attempts_used),
        "raw_text":      raw_text,
    }
