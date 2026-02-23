# ============================================================
# agents.py — Agent definitions
# Agents are defined here with roles, goals, and backstories.
# No task logic lives here — tasks belong in tasks.py.
# Tools are injected from tools.py — not defined here.
# ============================================================

from crewai import Agent


def create_manager(llm) -> Agent:
    """
    Project Manager — hierarchical crew leader.
    Delegates to specialists, reviews outputs, consolidates report.
    allow_delegation=True is what enables hierarchical process.
    """
    return Agent(
        role="Investment Committee Chair",
        goal=(
            "Orchestrate a rigorous, multi-specialist evaluation of the startup idea. "
            "Delegate market research, financial analysis, and risk assessment to the right specialists. "
            "Consolidate their outputs into a single structured JSON investment decision."
        ),
        backstory=(
            "You chair an investment committee at a Tier-1 VC firm. "
            "You are known for structured, data-driven decisions. "
            "You always delegate research to specialists before making recommendations. "
            "You return clean JSON — never prose."
        ),
        llm=llm,
        allow_delegation=True,
        verbose=False,
    )


def create_market_analyst(llm, tools: list) -> Agent:
    """
    Market Research Specialist.
    Uses MarketSizeTool and CompetitorIntelTool.
    """
    return Agent(
        role="Market Research Specialist",
        goal=(
            "Use available tools to produce a data-backed market analysis. "
            "Always call the Market Size Estimator and Competitor Intelligence tools. "
            "Never estimate market size from memory."
        ),
        backstory=(
            "Senior business intelligence analyst with 10 years in SaaS market research. "
            "Calls tools first, draws conclusions second."
        ),
        llm=llm,
        tools=tools,
        verbose=False,
    )


def create_financial_analyst(llm, tools: list) -> Agent:
    """
    Financial Analyst.
    Uses ROICalculatorTool to ground all financial recommendations.
    """
    return Agent(
        role="Financial Analyst",
        goal=(
            "Use the ROI Calculator tool to evaluate financial viability. "
            "Every recommendation must reference tool output — not estimates."
        ),
        backstory=(
            "Quantitative analyst specializing in SaaS unit economics and startup financials. "
            "Never makes financial recommendations without running the numbers through tools first."
        ),
        llm=llm,
        tools=tools,
        verbose=False,
    )


def create_risk_analyst(llm) -> Agent:
    """
    Risk Analyst — no tools needed.
    Assesses regulatory, competitive, and execution risks from context.
    """
    return Agent(
        role="Risk Assessment Specialist",
        goal=(
            "Identify and score the top risks facing this startup: "
            "regulatory, competitive, technical, and execution. "
            "Return a risk score 0–10 where 10 = extreme risk."
        ),
        backstory=(
            "Former startup founder and risk consultant. "
            "Identifies failure modes that optimistic founders miss. "
            "Scores risk rigorously — never inflates confidence."
        ),
        llm=llm,
        verbose=False,
    )


def create_investment_advisor(llm) -> Agent:
    """
    Investment Advisor — synthesizes all specialist inputs.
    Makes the final Invest / Consider / Reject call.
    """
    return Agent(
        role="Investment Advisor",
        goal=(
            "Synthesize market, financial, and risk analysis into a final investment recommendation. "
            "Return the final_decision as exactly 'Invest', 'Consider', or 'Reject'. "
            "If risk_score > 8, final_decision must not be 'Invest'."
        ),
        backstory=(
            "Portfolio manager with 200+ startup evaluations. "
            "Makes final calls based on specialist inputs, not gut feeling. "
            "Returns structured decisions that can be acted on immediately."
        ),
        llm=llm,
        verbose=False,
    )


# ── Agent registry ────────────────────────────────────────────────────────────
def create_all_agents(llm, research_tools: list, strategy_tools: list) -> dict:
    """
    Creates and returns all agents as a named dict.
    Called by crew_setup.py — not called directly from app.py.
    """
    return {
        "manager":            create_manager(llm),
        "market_analyst":     create_market_analyst(llm, research_tools),
        "financial_analyst":  create_financial_analyst(llm, strategy_tools),
        "risk_analyst":       create_risk_analyst(llm),
        "investment_advisor": create_investment_advisor(llm),
    }
