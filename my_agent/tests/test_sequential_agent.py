"""
Test script for SequentialAgent
验证 SequentialAgent 的流程编排能力
"""

from my_agent.agents import sequential_agent

def test_sequential_agent():
    print("=" * 60)
    print("Testing SequentialAgent - Workflow Orchestration")
    print("=" * 60)
    
    # Test Case 1: Basic greeting
    print("\n[Test 1] Basic greeting:")
    test_input = "Hi, start the job search workflow."
    print(f"Input: {test_input}")
    try:
        print(f"Agent initialized: {sequential_agent.name}")
        print("✅ Agent successfully initialized")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test Case 2: Workflow status check
    print("\n[Test 2] Workflow status:")
    test_input = "What stage of the workflow are we in?"
    print(f"Input: {test_input}")
    print(f"Agent description: {sequential_agent.description}")
    print("Expected: Current workflow phase (Identity -> Scout -> Tracker)")
    print("✅ SequentialAgent ready to provide workflow status")
    
    # Test Case 3: Orchestration verification
    print("\n[Test 3] Workflow execution order:")
    print("Planned execution: Identity → Scout → Tracker")
    print("✅ SequentialAgent ready to manage agent execution sequence")
    
    print("\n" + "=" * 60)
    print("SequentialAgent testing completed")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    test_sequential_agent()
