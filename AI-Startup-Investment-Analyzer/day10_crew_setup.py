# ============================================================
# crew_setup.py — Crew assembly
# Pulls from agents.py, tasks.py, and tools.py.
# app.py calls create_startup_crew() — nothing else.
# This is the single integration point.
# ============================================================

from crewai import Crew, Process

from agents import create_all_agents
from tasks import (
    create_market_research_task,
    create_financial_task,
    create_risk_task,
    create_main_evaluation_task,
)
from tools import get_research_tools, get_strategy_tools


def create_startup_crew(
    startup_idea: str,
    llm,
    revenue: float = 500000.0,
    cost: float = 150000.0,
    industry: str = "AI SaaS",
    persona: str = "Venture Capital Partner",
    stage: str = "Seed",
    risk_tolerance: str = "Balanced",
    use_specialists: bool = True,
) -> Crew:
    """
    Assembles and returns a fully configured CrewAI crew.

    Two modes:
    - use_specialists=True  → 5-agent hierarchical crew with specialist context
    - use_specialists=False → 1-agent direct crew (faster, lower cost)

    The crew is returned — not executed here.
    Execution happens in execution.py via run_startup_analysis().
    """
    research_tools = get_research_tools()
    strategy_tools = get_strategy_tools()
    agents         = create_all_agents(llm, research_tools, strategy_tools)

    if use_specialists:
        # Build specialist tasks
        market_task   = create_market_research_task(
            startup_idea, industry, agents["market_analyst"]
        )
        financial_task = create_financial_task(
            startup_idea, revenue, cost, agents["financial_analyst"]
        )
        risk_task = create_risk_task(
            startup_idea, agents["risk_analyst"]
        )
        # Final synthesis task — receives specialist context
        main_task = create_main_evaluation_task(
            startup_idea=startup_idea,
            persona=persona,
            stage=stage,
            risk_tolerance=risk_tolerance,
            agent=agents["investment_advisor"],
            context_tasks=[market_task, financial_task, risk_task],
        )
        crew = Crew(
            agents=[
                agents["manager"],
                agents["market_analyst"],
                agents["financial_analyst"],
                agents["risk_analyst"],
                agents["investment_advisor"],
            ],
            tasks=[market_task, financial_task, risk_task, main_task],
            process=Process.sequential,
            verbose=False,
        )
    else:
        # Single-agent direct mode — faster, lower cost
        main_task = create_main_evaluation_task(
            startup_idea=startup_idea,
            persona=persona,
            stage=stage,
            risk_tolerance=risk_tolerance,
            agent=agents["investment_advisor"],
        )
        crew = Crew(
            agents=[agents["investment_advisor"]],
            tasks=[main_task],
            verbose=False,
        )

    return crew, main_task
