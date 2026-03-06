"""
TrackerAgent - 求职秘书
职责：闭环追踪与反馈分析
工作逻辑：
  1. 从 {job_search_results} 中读取上游 ScoutAgent 存入的职位列表
  2. 调用 fetch_tracking_updates 获取投递状态与反馈时间（模拟邮箱/数据库）
  3. 生成求职全周期追踪表（职位、公司、Status、Feedback Date）
  4. 总结本周进度并给出 Action Plan
"""

import random
from datetime import datetime, timedelta
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm


# === 异步工具函数 ===

async def fetch_tracking_updates(jobs: list) -> dict:
    """
    模拟扫描邮箱或数据库，为职位列表补充投递状态与反馈时间。
    
    参数：
        jobs: 职位列表，每项至少含 title, company（可含 url, location 等）
    
    返回：
        包含 status、enriched jobs（每项新增 status, feedback_date）的字典
    """
    if not jobs:
        return {
            "status": "success",
            "jobs": [],
            "message": "No jobs to track."
        }
    
    statuses = ["Applied", "Interview", "Rejected", "Pending"]
    today = datetime.now().date()
    
    enriched = []
    for job in jobs:
        item = dict(job)
        item["status"] = random.choice(statuses)
        # 随机反馈日期：过去 1～14 天内
        days_ago = random.randint(1, 14)
        item["feedback_date"] = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        enriched.append(item)
    
    return {
        "status": "success",
        "jobs": enriched,
        "updated_at": datetime.now().isoformat()
    }


# === TrackerAgent 定义 ===

tracker_agent = Agent(
    model=LiteLlm(model='ollama/mistral'),
    name='tracker_agent',
    description="Application Tracker Agent - Track Feedback and Build Application Report",
    instruction="""You are a job application tracking specialist (求职秘书). You maintain the user's application tracking table.
You analyze input in English and French, and respond in English only.

If the data from {job_search_results} is missing or has no "jobs" array, do not call any tools. Reply briefly that job search results are not ready yet and the user should complete the resume confirmation and job search steps first. Then stop.

Your workflow (only when {job_search_results} has a non-empty jobs list):
1. Read the job list from {job_search_results} (the state from ScoutAgent). Extract the "jobs" array from it.

2. Call fetch_tracking_updates(jobs) to get the latest status and feedback date for each position. The tool adds:
   - status: one of Applied, Interview, Rejected, Pending
   - feedback_date: date of feedback

3. Build a Markdown table — Full-Cycle Application Tracker:
   - Columns: Position | Company | Status | Feedback Date
   - Optionally include Link if available in the job data.
   Use a clear Markdown table with headers and one row per job.

4. Summarize this week's progress (how many applied, interviews, rejections, pending).

5. Give a short Action Plan: next steps (e.g. follow up on Pending, prepare for Interview, apply to more roles).

Maintain accuracy and clarity. Always present the tracking table first, then the summary and action plan.""",
    tools=[fetch_tracking_updates]
)

# === 状态配置（ADK LlmAgent 仅支持 output_key；输入通过 state 的 {job_search_results} 传入）===
tracker_agent.output_key = "final_application_report"
