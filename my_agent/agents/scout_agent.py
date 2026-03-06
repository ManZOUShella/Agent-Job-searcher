"""
ScoutAgent - Job discovery. Reads target role/location from {confirmed_resume_profile}, searches jobs (LinkedIn, Indeed, Welcome to the Jungle),
scores by match (1-5), outputs structured table (position, company, match, link).
"""

import asyncio
import json
from datetime import datetime
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm


async def search_jobs_on_web(query: str, location: str) -> dict:
    """
    Search jobs across platforms. Returns mock data (LinkedIn, Indeed, Welcome to the Jungle).
    Args: query (e.g. "Senior Python Developer"), location (e.g. "Paris, France").
    Returns: dict with mock job list.
    """
    mock_jobs = {
        "linkedin": [
            {
                "title": f"Senior {query.split()[-1]} Engineer",
                "company": "TechCorp France",
                "location": location,
                "salary": "€60,000 - €80,000",
                "match_score": 5,
                "url": "https://linkedin.com/jobs/view/1234567890",
                "posted_date": "2 days ago"
            },
            {
                "title": f"{query} Specialist",
                "company": "CloudTech Solutions",
                "location": location,
                "salary": "€50,000 - €70,000",
                "match_score": 4,
                "url": "https://linkedin.com/jobs/view/1234567891",
                "posted_date": "1 week ago"
            }
        ],
        "indeed": [
            {
                "title": f"Lead {query.split()[-1]} Developer",
                "company": "InnovateLabs",
                "location": location,
                "salary": "€55,000 - €75,000",
                "match_score": 4,
                "url": "https://indeed.com/jobs/view/987654321",
                "posted_date": "3 days ago"
            }
        ],
        "welcome_to_jungle": [
            {
                "title": f"{query} (Remote Option)",
                "company": "StartupHub",
                "location": f"{location} (Remote)",
                "salary": "€45,000 - €65,000",
                "match_score": 3,
                "url": "https://welcometothejungle.com/jobs/987654",
                "posted_date": "5 days ago"
            }
        ]
    }
    all_jobs = []
    for platform, jobs in mock_jobs.items():
        for job in jobs:
            job["source"] = platform.upper()
            all_jobs.append(job)
    all_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {
        "status": "success",
        "query": query,
        "location": location,
        "total_results": len(all_jobs),
        "jobs": all_jobs,
        "timestamp": datetime.now().isoformat()
    }


async def format_jobs_as_table(jobs_data: dict) -> dict:
    """
    Format job data as Markdown table for Web UI display.
    """
    try:
        jobs = jobs_data.get("jobs", [])
        
        if not jobs:
            return {
                "status": "success",
                "markdown_table":                 "No jobs found matching your criteria."
            }
        markdown_lines = [
            f"## Job Search Results for **{jobs_data.get('query')}** in **{jobs_data.get('location')}**\n",
            f"Found **{jobs_data.get('total_results')}** matching positions:\n",
            "| Rank | Position | Company | Location | Match Score | Salary | Source | Link |",
            "|------|----------|---------|----------|-------------|--------|--------|------|"
        ]
        
        for idx, job in enumerate(jobs, 1):
            match_stars = "⭐" * job.get("match_score", 0)
            row = f"| {idx} | {job.get('title', 'N/A')} | {job.get('company', 'N/A')} | {job.get('location', 'N/A')} | {match_stars} {job.get('match_score', 0)}/5 | {job.get('salary', 'Competitive')} | {job.get('source', 'Unknown')} | [View Job]({job.get('url', '#')}) |"
            markdown_lines.append(row)
        
        markdown_table = "\n".join(markdown_lines)
        
        return {
            "status": "success",
            "markdown_table": markdown_table,
            "job_count": len(jobs)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error formatting jobs: {str(e)}"
        }


scout_agent = Agent(
    model=LiteLlm(model="gemini/gemini-2.5-flash-lite"),
    name='scout_agent',
    description="Job Scout Agent - Job Discovery and Matching",
    instruction="""You are a professional job discovery specialist and recruiter.
You analyze input in English and French, and respond in English only.

TOOLS: You may ONLY use these two tools, with exact names (no variation): search_jobs_on_web, format_jobs_as_table.
Do NOT use format_job_list, "Identity Check", or any other tool name; to format results you must call format_jobs_as_table only.
Input: You receive {confirmed_resume_profile} from the previous step (IdentityAgent). Use it as-is; do not call any identity or confirmation tool.

Your workflow:
1. Read the user's target position and location from {confirmed_resume_profile}.

2. Search for jobs on LinkedIn, Indeed, Welcome to the Jungle and similar platforms by calling search_jobs_on_web(query, location).

3. Score each result by resume match (1–5 stars). Use the job results and match scores when building the table.

4. Generate a structured table with: job title, company, salary, match score (1–5 stars), and application link. Call format_jobs_as_table(jobs_data) to produce this Markdown table.""",
    tools=[search_jobs_on_web, format_jobs_as_table]
)

scout_agent.output_key = "job_search_results"
