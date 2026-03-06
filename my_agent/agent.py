"""
JobFlow-ADK Agent Entry Point
全自动求职流水线：Identity → (Scout ∥ MarketAnalyst) → Tracker。
ADK 框架启动时会查找 root_agent。
"""

from google.adk.agents import ParallelAgent, SequentialAgent

from .agents import identity_agent, market_analyst_agent, scout_agent, tracker_agent

# === SequentialAgent：三步求职流水线 ===
# 第一步：identity_agent 解析并确认简历
# 第二步（并行）：scout_agent 职位搜索；market_analyst_agent 分析市场薪资范围
# 第三步：tracker_agent 投递反馈追踪表
# 执行顺序由 sub_agents 列表顺序决定；state 在步骤间自动传递。
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

# ADK 启动时查找 root_agent
root_agent = workflow
