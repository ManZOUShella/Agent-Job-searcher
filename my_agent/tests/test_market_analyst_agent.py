"""
MarketAnalystAgent test script (v1.0).
Validates market salary tool, return structure, and state handoff.
"""

import asyncio
import sys
from pathlib import Path
from inspect import iscoroutinefunction

if __name__ == "__main__":
    _root = Path(__file__).resolve().parent.parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

try:
    from my_agent.agents.market_analyst_agent import (
        market_analyst_agent,
        fetch_market_salary_range,
    )
except ImportError as e:
    print(f"Import error: cannot import from my_agent.agents.market_analyst_agent. Details: {e}")
    sys.exit(1)


async def run_test_step(name, coro):
    """Generic test step runner."""
    print(f"Run: {name}...", end=" ", flush=True)
    try:
        result = await coro
        if result and result.get("status") == "success":
            print("OK")
            return result
        else:
            print(f"Fail: {result.get('message', 'logic error')}")
            return None
    except Exception as e:
        print(f"Crash: {str(e)}")
        return None


async def simulate_market_analyst_workflow():
    """Simulate MarketAnalystAgent receiving confirmed_resume_profile from IdentityAgent."""
    print("\n" + "=" * 60)
    print("Check 3: MarketAnalystAgent logic flow (salary range)")
    print("=" * 60 + "\n")

    mock_confirmed_profile = {
        "target_position": "Python Backend Developer",
        "location": "Biot, France",
        "core_skills": ["Python", "FastAPI", "PostgreSQL"],
    }
    print(f"[Handoff] Received {{confirmed_resume_profile}}...")
    print(f"   Role: {mock_confirmed_profile['target_position']} @ {mock_confirmed_profile['location']}")

    salary_res = await run_test_step(
        "fetch_market_salary_range",
        fetch_market_salary_range(
            mock_confirmed_profile["target_position"],
            mock_confirmed_profile["location"],
        ),
    )

    if salary_res:
        sr = salary_res.get("salary_range", {})
        has_min = "min" in sr
        has_max = "max" in sr
        has_period = "period" in sr
        has_currency = "currency" in salary_res
        print(f"\nReturn structure: salary_range.min/max/period={has_min and has_max and has_period}, currency={has_currency}")
        if has_min and has_max:
            print(f"   Sample: {salary_res.get('role')} @ {salary_res.get('location')} -> {sr.get('min')}-{sr.get('max')} {salary_res.get('currency')}/{sr.get('period', 'year')}")
        else:
            print("   Missing salary_range.min/max or period")
    else:
        return False

    return True


async def main():
    print("\nMarketAnalystAgent precheck (v1.0)")

    print("\nCheck 1: Agent attributes")
    required_attrs = ["name", "description", "instruction", "model"]
    for attr in required_attrs:
        status = "OK" if hasattr(market_analyst_agent, attr) else "Missing"
        print(f"  {attr}: {status}")

    print("\nCheck 2: Tool async (Async/Await)")
    tools_to_check = [("fetch_market_salary_range", fetch_market_salary_range)]
    for name, func in tools_to_check:
        status = "OK" if iscoroutinefunction(func) else "Not async"
        print(f"  {name}: {status}")

    success = await simulate_market_analyst_workflow()

    print("\nCheck 4: Handoff chain")
    instr = getattr(market_analyst_agent, "instruction", "")
    input_ref = "{confirmed_resume_profile}"
    output_key = getattr(market_analyst_agent, "output_key", None)

    if input_ref in instr:
        print(f"  OK variable ref: {input_ref}")
    else:
        print(f"  Fail: missing ref; MarketAnalystAgent cannot get upstream data")
        success = False

    if output_key == "market_salary_report":
        print(f"  OK output_key: {output_key}")
    else:
        print(f"  Fail output_key: expected 'market_salary_report', got {output_key!r}")
        success = False

    if success:
        print("\n" + "=" * 60)
        print("MarketAnalystAgent precheck passed.")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
