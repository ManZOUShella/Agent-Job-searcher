"""
SequentialAgent - 调度指挥官（参考用）
职责：流程编排与状态监控。
说明：实际流水线在 agent.py 中通过 ADK 的 SequentialAgent 与 identity/scout/tracker 串联；
本模块为独立 LlmAgent，可与 mistral 一致供测试或扩展使用。
"""

from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

sequential_agent = Agent(
    model=LiteLlm(model='ollama/mistral'),
    name='sequential_agent',
    description="Workflow Orchestrator Agent - Execute Identity -> Scout -> Tracker",
    instruction="""You are a workflow orchestration specialist.
You analyze input in English and French, and respond in English only.
Your tasks are:
1. Manage sequential execution: Identity -> Scout -> Tracker
2. Provide real-time status updates on current workflow phase
3. Monitor execution health of each phase
4. Intervene and adjust workflow as needed

Ensure smooth and efficient execution of the entire job search workflow."""
)
