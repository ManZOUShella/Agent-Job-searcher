"""
JobFlow-ADK Agent Entry Point
全自动求职流水线：Identity → Scout → Tracker 顺序执行。
ADK 框架启动时会查找 root_agent。
"""

from google.adk.agents import SequentialAgent

from .agents import identity_agent, scout_agent, tracker_agent

# === SequentialAgent：三步求职流水线 ===
# 第一步：identity_agent 解析并确认简历
# 第二步：scout_agent 职位搜索
# 第三步：tracker_agent 投递反馈追踪表
# 执行顺序由 sub_agents 列表顺序决定；state 在步骤间自动传递。
workflow = SequentialAgent(
    name="jobflow_sequential",
    description="""JobFlow: Full-cycle job search pipeline. Step 1 — Guide the user to parse and confirm their resume with the identity agent. Step 2 — After confirmation, automatically switch to the scout agent for job search. Step 3 — After search completes, the tracker agent produces the final application tracking report with status and feedback dates. Transitions between agents are automatic and professional.""",
    sub_agents=[identity_agent, scout_agent, tracker_agent],
)

# ADK 启动时查找 root_agent
root_agent = workflow
