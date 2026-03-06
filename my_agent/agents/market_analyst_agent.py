"""
MarketAnalystAgent - Market salary analyst. Reads target_position/location from {confirmed_resume_profile},
calls fetch_market_salary_range (mock; replaceable with real API). Outputs Markdown salary summary (for user only);
pipeline then continues to TrackerAgent; this agent's result is not consumed downstream.
"""

import random
from datetime import datetime

from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm


async def fetch_market_salary_range(role: str, location: str) -> dict:
    """
    Get market salary range for role/location (mock; replace with real API later). Return shape is stable.
    """
    role = (role or "").strip() or "Unknown role"
    location = (location or "").strip() or "Unknown location"

    base = random.randint(45, 80) * 1000
    spread = random.randint(8, 20) * 1000
    low = base
    high = base + spread

    return {
        "status": "success",
        "role": role,
        "location": location,
        "currency": "EUR",
        "salary_range": {"min": low, "max": high, "period": "year"},
        "notes": "Mock estimate based on role/location heuristics. Replace with a real market data source later.",
        "timestamp": datetime.now().isoformat(),
    }


market_analyst_agent = Agent(
    model=LiteLlm(model="gemini/gemini-2.5-flash-lite"),
    name="market_analyst_agent",
    description=(
        "Market Analyst Agent - Analyze market salary range. "
        "ALLOWED TOOLS (only these): fetch_market_salary_range."
    ),
    instruction="""ALLOWED TOOLS (call only these exact names): fetch_market_salary_range. Any other name will cause an error.
Do NOT call any tool named "Identity Check" or similar; your only allowed tool is fetch_market_salary_range.

You are a market analyst specializing in compensation benchmarking.
You analyze input in English and French, and respond in English only.

Your output is for information only: the user sees the salary summary; no downstream agent (e.g. TrackerAgent) uses it. After you finish, the pipeline automatically continues to TrackerAgent.

Input: {confirmed_resume_profile} (from IdentityAgent after user confirmation).

Workflow:
1. If {confirmed_resume_profile} is missing or empty, do not call any tools. Reply briefly: "Please confirm your resume information first so I can analyze the market salary range." Then stop.
2. Extract target_position and location from {confirmed_resume_profile}.
3. Call fetch_market_salary_range(role, location) to get a market estimate.
4. Present a concise Markdown summary (for information only): Role, Location, estimated salary range (min–max, currency, per year), and one short note that this is an estimate. Then you are done; the workflow will automatically proceed to the tracker step.""",
    tools=[fetch_market_salary_range],
)

market_analyst_agent.output_key = "market_salary_report"

