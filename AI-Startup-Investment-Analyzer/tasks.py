# ============================================================
# tasks.py — Task definitions
# Tasks are defined here — separate from agents and tools.
# Each task function takes the relevant agent as a parameter.
# Schema enforcement lives here — not in agents.py.
# ============================================================

from crewai import Task


# ── Output schema — single source of truth ────────────────────────────────────
JSON_SCHEMA = """{
  "market_score": <integer 0-10>,
  "market_summary": "<2-sentence market assessment>",
  "financial_score": <integer 0-10>,
  "financial_summary": "<2-sentence financial viability assessment>",
  "risk_score": <integer 0-10, where 10 = extreme risk>,
  "risk_summary": "<2-sentence risk assessment>",
  "final_decision": "<exactly: Invest OR Consider OR Reject>",
  "confidence_level": "<exactly: Low OR Medium OR High>",
  "recommended_actions": ["action1", "action2", "action3", "action4", "action5"],
  "total_score": <float: (market_score + financial_score + (10 - risk_score)) / 3>
}"""


def create_market_research_task(startup_idea: str, industry: str, agent) -> Task:
    """
    Assigns market research to the Market Research Specialist.
    Instructs the agent to call both market and competitor tools.
    """
    return Task(
        description=(
            f"Research the market opportunity for this startup:\n'{startup_idea}'\n\n"
            f"You MUST call the Market Size Estimator tool with industry: '{industry}'\n"
            f"You MUST call the Competitor Intelligence tool with industry: '{industry}'\n"
            f"Incorporate both tool outputs into your analysis."
        ),
        expected_output=(
            "Market research report covering: "
            "TAM and growth rate (from tool), "
            "target customer profile, "
            "competitor landscape with pricing (from tool), "
            "and top 3 market opportunities."
        ),
        agent=agent,
    )


def create_financial_task(startup_idea: str, revenue: float, cost: float, agent) -> Task:
    """
    Assigns financial analysis to the Financial Analyst.
    Passes actual revenue and cost figures for ROI tool.
    """
    return Task(
        description=(
            f"Evaluate the financial viability of:\n'{startup_idea}'\n\n"
            f"You MUST call the ROI Calculator tool with input: '{revenue},{cost}'\n"
            f"Base all financial conclusions on the tool's output."
        ),
        expected_output=(
            "Financial analysis covering: "
            "ROI and payback period (from tool), "
            "unit economics, "
            "revenue model assessment, "
            "and 3-year financial outlook."
        ),
        agent=agent,
    )


def create_risk_task(startup_idea: str, agent) -> Task:
    """
    Assigns risk assessment to the Risk Analyst.
    No tools required — draws from domain knowledge and context.
    """
    return Task(
        description=(
            f"Assess the top risks for:\n'{startup_idea}'\n\n"
            f"Evaluate: regulatory, competitive, technical, and execution risks. "
            f"Score overall risk 0–10 where 10 = near-certain failure."
        ),
        expected_output=(
            "Risk report covering: "
            "top 5 specific risks with severity, "
            "regulatory and compliance exposure, "
            "competitive threats, "
            "and overall risk score with justification."
        ),
        agent=agent,
    )


def create_main_evaluation_task(
    startup_idea: str,
    persona: str,
    stage: str,
    risk_tolerance: str,
    agent,
    context_tasks: list = None
) -> Task:
    """
    Final synthesis task — assigned to Investment Advisor or Manager.
    Enforces strict JSON schema output.
    Context tasks feed specialist outputs into this task.
    """
    strictness = {
        "Conservative": "Apply strict conservative criteria. Heavily penalize uncertainty.",
        "Balanced":     "Apply balanced criteria — weigh upside and downside equally.",
        "Aggressive":   "Apply growth-focused criteria. Accept higher risk for large markets.",
    }.get(risk_tolerance, "Apply balanced criteria.")

    return Task(
        description=(
            f"You are a {persona} evaluating a {stage} investment.\n"
            f"{strictness}\n\n"
            f"Startup: {startup_idea}\n\n"
            f"Synthesize all specialist analysis and return ONLY valid JSON:\n\n"
            f"{JSON_SCHEMA}\n\n"
            f"Rules:\n"
            f"- All scores: integers 0–10\n"
            f"- If risk_score > 8, final_decision MUST be 'Consider' or 'Reject'\n"
            f"- recommended_actions: exactly 5 specific actionable strings\n"
            f"- Return ONLY the JSON object — no prose, no markdown"
        ),
        expected_output="A single valid JSON object matching the defined schema. No other text.",
        agent=agent,
        context=context_tasks or [],
    )
