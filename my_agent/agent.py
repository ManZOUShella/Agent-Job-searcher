"""
JobFlow-ADK Agent Entry Point.
Pipeline: Identity → (Scout ∥ MarketAnalyst) → Tracker. ADK looks for root_agent.
"""

from google.adk.agents import ParallelAgent, SequentialAgent
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

from .agents import identity_agent, market_analyst_agent, scout_agent, tracker_agent

parallel_stage = ParallelAgent(
    name="jobflow_parallel_stage",
    description="Parallel stage: scout_agent (job search) + market_analyst_agent (salary analysis).",
    sub_agents=[scout_agent, market_analyst_agent],
)

workflow = SequentialAgent(
    name="jobflow_sequential",
    description="""JobFlow: Full-cycle job search pipeline.
Step 1 — Identity: guide the user to parse and confirm their resume.
Step 2 — Parallel: Scout searches jobs while Market Analyst estimates salary ranges.
Step 3 — Tracker: generate the final application tracking report (status + feedback dates).
Transitions are automatic and professional.""",
    sub_agents=[identity_agent, parallel_stage, tracker_agent],
)

sequential_agent = Agent(
    model=LiteLlm(model="gemini/gemini-2.5-flash-lite"),
    name="sequential_agent",
    description="Workflow Orchestrator Agent - Execute Identity -> Scout -> Tracker",
    instruction="""You are a workflow orchestration specialist.
You analyze input in English and French, and respond in English only.
Your tasks are:
1. Manage sequential execution: Identity -> Scout -> Tracker
2. Provide real-time status updates on current workflow phase
3. Monitor execution health of each phase
4. Intervene and adjust workflow as needed

Ensure smooth and efficient execution of the entire job search workflow.""",
)

coordinator = Agent(
    model=LiteLlm(model="gemini/gemini-2.5-flash-lite"),
    name="jobflow_coordinator",
    description="Entry coordinator: transfers to the full job-search pipeline.",
    instruction="""You are the entry point. For any user request about job search or resume, immediately call transfer_to_agent with agent_name='jobflow_sequential'. Do nothing else.""",
    sub_agents=[workflow],
)

root_agent = coordinator
