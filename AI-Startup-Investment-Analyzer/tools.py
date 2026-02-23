# ============================================================
# tools.py — Custom tool definitions
# All tools are self-contained and importable independently.
# Agents receive tool instances — never raw functions.
# ============================================================

from crewai.tools import BaseTool
from typing import ClassVar, Dict


class MarketSizeTool(BaseTool):
    """
    Returns TAM, CAGR, and key players for a given industry.
    The agent calls this when evaluating market opportunity.
    """
    name: str = "Market Size Estimator"
    description: str = (
        "Returns the global market size, growth rate (CAGR), and key competitors "
        "for a given industry. Use this when you need market data to support analysis. "
        "Input: industry name as a string."
    )

    MARKET_DATA: ClassVar[Dict] = {
        "AI Fitness":       {"size": "$22B", "cagr": "28%", "players": "Whoop, Noom, Future"},
        "Real Estate AI":   {"size": "$18B", "cagr": "32%", "players": "Zillow, CoStar, Reonomy"},
        "AI Marketing":     {"size": "$107B","cagr": "35%", "players": "Jasper, Copy.ai, AdCreative"},
        "AI SaaS":          {"size": "$115B","cagr": "38%", "players": "Salesforce Einstein, HubSpot AI"},
        "EdTech AI":        {"size": "$31B", "cagr": "22%", "players": "Coursera, Duolingo, Khanmigo"},
        "HealthTech AI":    {"size": "$45B", "cagr": "41%", "players": "Tempus, Viz.ai, Babylon"},
        "FinTech AI":       {"size": "$78B", "cagr": "29%", "players": "Stripe, Plaid, Brex"},
        "LegalTech AI":     {"size": "$12B", "cagr": "26%", "players": "Clio, ContractPodAi, Harvey"},
        "Logistics AI":     {"size": "$75B", "cagr": "14%", "players": "Flexport, project44, FourKites"},
        "HR Tech AI":       {"size": "$28B", "cagr": "19%", "players": "Workday, Greenhouse, Lever"},
    }

    def _run(self, industry: str) -> str:
        for key, val in self.MARKET_DATA.items():
            if key.lower() in industry.lower() or industry.lower() in key.lower():
                return (
                    f"Industry: {key} | "
                    f"Global TAM: {val['size']} | "
                    f"CAGR: {val['cagr']} | "
                    f"Key Players: {val['players']}"
                )
        keys = ", ".join(self.MARKET_DATA.keys())
        return f"No data for '{industry}'. Available industries: {keys}"


class ROICalculatorTool(BaseTool):
    """
    Calculates ROI, payback period, and 3-year projection.
    Strategist calls this before making financial recommendations.
    """
    name: str = "ROI Calculator"
    description: str = (
        "Calculates return on investment (ROI %), payback period in months, "
        "profit margin, and 3-year net profit projection. "
        "Input format: 'revenue,cost' as comma-separated numbers (e.g. '500000,150000')."
    )

    def _run(self, inputs: str) -> str:
        try:
            parts = inputs.replace(" ", "").split(",")
            revenue = float(parts[0])
            cost    = float(parts[1])
            if cost <= 0:
                return "Error: cost must be greater than 0"
            roi            = round(((revenue - cost) / cost) * 100, 1)
            profit_margin  = round(((revenue - cost) / revenue) * 100, 1)
            payback_months = round((cost / (revenue - cost)) * 12, 1) if revenue > cost else None
            net_3yr        = round((revenue - cost) * 3, 0)
            payback_str    = f"{payback_months} months" if payback_months else "N/A (revenue ≤ cost)"
            return (
                f"ROI: {roi}% | "
                f"Payback Period: {payback_str} | "
                f"Profit Margin: {profit_margin}% | "
                f"3-Year Net Profit: ${net_3yr:,.0f}"
            )
        except (IndexError, ValueError) as e:
            return f"Input error: {str(e)}. Expected format: 'revenue,cost' (e.g. '500000,150000')"


class CompetitorIntelTool(BaseTool):
    """
    Returns competitor pricing and identified market gaps per industry.
    """
    name: str = "Competitor Intelligence"
    description: str = (
        "Returns known competitors with pricing tiers and an identified market gap "
        "for a given industry. Use this to find differentiation opportunities. "
        "Input: industry name as a string."
    )

    COMPETITOR_DATA: ClassVar[Dict] = {
        "AI Fitness":     {"comps": "Future $149/mo, Noom $70/mo, Whoop $30/mo",    "gap": "No B2B/corporate wellness focus"},
        "Real Estate AI": {"comps": "Reonomy $500/mo, CoStar $1200/mo",             "gap": "Too expensive for independent investors"},
        "AI Marketing":   {"comps": "Jasper $49/mo, Copy.ai $49/mo",               "gap": "None specialized for DTC product catalog workflows"},
        "AI SaaS":        {"comps": "Harvey (custom), Clio $39/mo",                "gap": "Harvey priced out of solo lawyers — underserved segment"},
        "LegalTech AI":   {"comps": "Clio $39/mo, Harvey (custom), Ironclad (custom)", "gap": "No mid-market between cheap and enterprise"},
        "Logistics AI":   {"comps": "project44 (custom), Flexport (custom)",        "gap": "SMB logistics companies underserved by enterprise pricing"},
        "HR Tech AI":     {"comps": "Greenhouse $6K/yr, Lever (custom)",            "gap": "SMB hiring teams can't afford enterprise ATS"},
        "FinTech AI":     {"comps": "Mint (free), YNAB $14/mo, Copilot $13/mo",    "gap": "No proactive AI intervention — all reactive dashboards"},
    }

    def _run(self, industry: str) -> str:
        for key, val in self.COMPETITOR_DATA.items():
            if key.lower() in industry.lower() or industry.lower() in key.lower():
                return (
                    f"Competitors: {val['comps']} | "
                    f"Market Gap: {val['gap']}"
                )
        return f"No competitor data for '{industry}'."


# ── Tool registry — used by crew_setup.py to assign tools to agents ──────────
def get_research_tools():
    """Returns tool instances for the Market Research agent."""
    return [MarketSizeTool(), CompetitorIntelTool()]


def get_strategy_tools():
    """Returns tool instances for the Strategy agent."""
    return [ROICalculatorTool()]


def get_all_tools():
    """Returns all tool instances — used for testing."""
    return [MarketSizeTool(), ROICalculatorTool(), CompetitorIntelTool()]
