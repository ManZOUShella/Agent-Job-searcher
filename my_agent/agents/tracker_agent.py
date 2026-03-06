"""
TrackerAgent - Application tracker. Reads job list from {job_search_results}, calls fetch_tracking_updates for status/feedback,
outputs full-cycle tracking table (position, company, status, feedback date).
"""

import random
from datetime import datetime, timedelta
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm


async def fetch_tracking_updates(jobs: list[dict]) -> dict:
    """
    Fetch updates for a list of job applications (status and feedback date).

    Args:
        jobs: A list of dictionaries. Each dict must contain at least 'title' and 'company';
              it may also contain 'url', 'location', etc. Example:
              [{"title": "Python Developer", "company": "TechCorp", "url": "https://..."}]

    Returns:
        A dict with "status" ("success"), "jobs" (each item enriched with "status" and "feedback_date"),
        and "updated_at".
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
        days_ago = random.randint(1, 14)
        item["feedback_date"] = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        enriched.append(item)
    
    return {
        "status": "success",
        "jobs": enriched,
        "updated_at": datetime.now().isoformat()
    }


def _tracker_after_tool(tool, args, tool_context, tool_response):
    """After fetch_tracking_updates: log audit. Return None to keep default behavior."""
    tool_name = getattr(tool, "__name__", None) or str(tool)
    if tool_name == "fetch_tracking_updates":
        jobs_count = 0
        if isinstance(tool_response, dict) and "jobs" in tool_response:
            jobs_count = len(tool_response.get("jobs", []))
        print(f"[TrackerAgent after_tool] Tracking table generated, {jobs_count} records — pipeline end audit.")
    return None


tracker_agent = Agent(
    model=LiteLlm(model="gemini/gemini-2.5-flash-lite"),
    name='tracker_agent',
    description="Application Tracker Agent - Track Feedback and Build Application Report",
    instruction="""You are a job application tracking specialist. You maintain the user's application tracking table.
You analyze input in English and French, and respond in English only.
Do NOT call any tool named "Identity Check" or similar; your only allowed tool is fetch_tracking_updates. Input comes from {job_search_results} (from ScoutAgent).

Your workflow:
1. Read the job list from {job_search_results} (stored by ScoutAgent upstream). Extract the "jobs" array.

2. Call fetch_tracking_updates(jobs) to get application status and feedback date (mock email/DB).

3. Generate the full-cycle application tracking table: Position, Company, Status, Feedback Date. Output a clear Markdown table with these columns and one row per job.""",
    tools=[fetch_tracking_updates],
    after_tool_callback=_tracker_after_tool,
)

tracker_agent.output_key = "final_application_report"
