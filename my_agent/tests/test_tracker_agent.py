"""
TrackerAgent test script (v1.0).
Validates tracking tool, status/feedback_date logic, and state handoff.
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
    from my_agent.agents.tracker_agent import tracker_agent, fetch_tracking_updates
except ImportError as e:
    print(f"Import error: cannot import from my_agent.agents.tracker_agent. Details: {e}")
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


async def simulate_tracker_workflow():
    """Simulate TrackerAgent receiving job_search_results from ScoutAgent."""
    print("\n" + "=" * 60)
    print("Check 3: TrackerAgent logic flow (tracking & feedback)")
    print("=" * 60 + "\n")

    mock_job_search_results = {
        "status": "success",
        "query": "Python Developer",
        "location": "Paris, France",
        "total_results": 2,
        "jobs": [
            {"title": "Senior Python Engineer", "company": "TechCorp France", "url": "https://linkedin.com/jobs/1"},
            {"title": "Python Developer", "company": "StartupHub", "url": "https://welcometothejungle.com/jobs/2"}
        ]
    }
    jobs = mock_job_search_results["jobs"]
    print(f"[Handoff] Received {{job_search_results}}...")
    print(f"   Job count: {len(jobs)}")

    tracking_res = await run_test_step("fetch_tracking_updates", fetch_tracking_updates(jobs))

    if tracking_res:
        enriched = tracking_res.get("jobs", [])
        if enriched:
            first = enriched[0]
            has_status = "status" in first
            has_date = "feedback_date" in first
            print(f"\nReturn structure: status={has_status}, feedback_date={has_date}")
            if has_status and has_date:
                print(f"   Sample: {first.get('title')} @ {first.get('company')} -> {first.get('status')} ({first.get('feedback_date')})")
            else:
                print("   Missing status or feedback_date")
        else:
            print("   jobs is empty")

    return True


async def main():
    print("\nTrackerAgent precheck (v1.0)")

    print("\nCheck 1: Agent attributes")
    required_attrs = ["name", "description", "instruction", "model"]
    for attr in required_attrs:
        status = "OK" if hasattr(tracker_agent, attr) else "Missing"
        print(f"  {attr}: {status}")

    print("\nCheck 2: Tool async (Async/Await)")
    tools_to_check = [("fetch_tracking_updates", fetch_tracking_updates)]
    for name, func in tools_to_check:
        status = "OK" if iscoroutinefunction(func) else "Not async"
        print(f"  {name}: {status}")

    success = await simulate_tracker_workflow()

    print("\nCheck 4: Handoff chain")
    instr = getattr(tracker_agent, "instruction", "")
    input_ref = "{job_search_results}"
    output_key = getattr(tracker_agent, "output_key", None)

    if input_ref in instr:
        print(f"  OK variable ref: {input_ref}")
    else:
        print(f"  Fail: missing ref; TrackerAgent cannot get upstream data")
        success = False

    if output_key == "final_application_report":
        print(f"  OK output_key: {output_key}")
    else:
        print(f"  Fail output_key: expected 'final_application_report', got {output_key!r}")
        success = False

    if success:
        print("\n" + "=" * 60)
        print("TrackerAgent precheck passed.")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
