"""
IdentityAgent test script (v2.5).
Validates async tools, agent attributes, and state handoff (output_key).
"""

import asyncio
import json
from pathlib import Path
from inspect import iscoroutinefunction
from my_agent.agents.identity_agent import identity_agent

try:
    from my_agent.agents.identity_agent import read_resume_file, save_resume_profile
except ImportError as e:
    print(f"Import error: check identity_agent.py. Details: {e}")

async def run_test_step(name, coro):
    """Generic test step runner."""
    print(f"Run: {name}...", end=" ", flush=True)
    try:
        result = await coro
        if result and result.get("status") == "success":
            print("OK")
            return result
        else:
            print(f"Fail ({result.get('message', 'logic error')})")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

async def simulate_logic_workflow():
    """Simulate: read file -> confirm -> save; check handoff key."""
    print("\n" + "="*50)
    print("IdentityAgent logic flow (handoff chain)")
    print("="*50)
    
    current_dir = Path(__file__).parent
    json_path = current_dir / "sample_resume.json"
    
    read_res = await run_test_step("1. Read tool", read_resume_file(str(json_path)))
    if not read_res: return False
    
    mock_confirmed_data = {
        "target_position": "Python Developer",
        "location": "Biot, France",
        "skills": ["Python", "ADK", "Mistral"]
    }
    
    save_res = await run_test_step("2. Save tool (to State)", save_resume_profile(mock_confirmed_data))
    
    print("\nHandoff check:")
    actual_key = getattr(identity_agent, 'output_key', None)
    expected_key = "confirmed_resume_profile"
    
    if actual_key == expected_key:
        print(f"   OK output_key: '{actual_key}' ready.")
        print(f"   Downstream ScoutAgent can read {{{actual_key}}}.")
    else:
        print(f"   Fail: expected '{expected_key}', got '{actual_key}'.")
        return False

    return True

async def main():
    print("\nIdentityAgent precheck (v2.5)")
    
    print(f"\nAgent name: {identity_agent.name}")
    print(f"Model: {identity_agent.model.model if hasattr(identity_agent.model, 'model') else 'Unknown'}")
    
    success = await simulate_logic_workflow()
    
    if success:
        print("\n" + "="*50)
        print("Precheck passed. IdentityAgent handoff ready.")
        print("You can run 'adk web' for live chat.")
        print("="*50 + "\n")
    else:
        print("\nPrecheck failed. Check errors above.")

if __name__ == "__main__":
    asyncio.run(main())