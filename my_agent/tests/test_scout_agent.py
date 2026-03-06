"""
ScoutAgent test script (v1.1).
Validates job search tools, Markdown table output, and state handoff.
"""

import asyncio
import json
import sys
from pathlib import Path
from inspect import iscoroutinefunction

if __name__ == "__main__":
    _root = Path(__file__).resolve().parent.parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

try:
    from my_agent.agents.scout_agent import scout_agent, search_jobs_on_web, format_jobs_as_table
except ImportError as e:
    print(f"Import error: cannot import from my_agent.agents.scout_agent. Details: {e}")
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

async def simulate_scout_workflow():
    """Simulate ScoutAgent receiving confirmed_resume_profile from IdentityAgent."""
    print("\n" + "="*60)
    print("Check 3: ScoutAgent logic flow (search & match)")
    print("="*60 + "\n")
    
    mock_confirmed_profile = {
        "target_position": "Python Backend Developer",
        "location": "Biot, France",
        "core_skills": ["Python", "FastAPI", "PostgreSQL", "Google ADK"]
    }
    print(f"[Handoff] Received {{confirmed_resume_profile}}...")
    print(f"   Target: {mock_confirmed_profile['target_position']} @ {mock_confirmed_profile['location']}")

    search_res = await run_test_step(
        "search_jobs_on_web", 
        search_jobs_on_web(mock_confirmed_profile['target_position'], mock_confirmed_profile['location'])
    )
    
    if search_res:
        table_res = await run_test_step("format_jobs_as_table", format_jobs_as_table(search_res))
        if table_res:
            print("\nTable preview:")
            print("-" * 30)
            print(table_res.get('markdown_table', '')[:200] + "...")
            print("-" * 30)

    return True

async def main():
    print("\nScoutAgent precheck (v1.1)")
    
    print("\nCheck 1: Agent attributes")
    required_attrs = ['name', 'description', 'instruction', 'model']
    for attr in required_attrs:
        status = "OK" if hasattr(scout_agent, attr) else "Missing"
        print(f"  {attr}: {status}")
    
    print("\nCheck 2: Tool async (Async/Await)")
    tools_to_check = [
        ('search_jobs_on_web', search_jobs_on_web),
        ('format_jobs_as_table', format_jobs_as_table)
    ]
    for name, func in tools_to_check:
        status = "OK" if iscoroutinefunction(func) else "Not async"
        print(f"  {name}: {status}")

    success = await simulate_scout_workflow()
    
    print("\nCheck 4: Handoff chain")
    instr = getattr(scout_agent, 'instruction', '')
    input_key = "{confirmed_resume_profile}"
    
    if input_key in instr:
        print(f"  OK variable ref: {input_key}")
    else:
        print(f"  Fail: missing ref; ScoutAgent cannot get upstream data")
        success = False

    if success:
        print("\n" + "="*60)
        print("ScoutAgent precheck passed.")
        print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())