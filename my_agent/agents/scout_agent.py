"""
ScoutAgent - 情报搜寻员
职责：全网职位抓取与匹配
工作逻辑：
  1. 从 {confirmed_resume_profile} 中读取用户目标职位和地点
  2. 在 LinkedIn、Indeed、Welcome to the Jungle 等平台搜寻职位
  3. 根据简历匹配度进行评分（1-5星）
  4. 生成结构化表格（职位名、公司、匹配分、投递链接）
"""

import asyncio
import json
from datetime import datetime
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm


# === 异步工具函数 ===

async def search_jobs_on_web(query: str, location: str) -> dict:
    """
    异步搜索职位 - 从多个平台聚合职位信息
    目前返回 Mock 数据（模拟 LinkedIn、Indeed、Welcome to the Jungle 的搜索结果）
    
    参数：
        query: 职位关键词 (e.g., "Senior Python Developer")
        location: 地点 (e.g., "Paris, France")
    
    返回：
        包含 Mock 职位列表的字典
    """
    
    # 模拟不同平台的搜索结果
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
    
    # 合并所有结果
    all_jobs = []
    for platform, jobs in mock_jobs.items():
        for job in jobs:
            job["source"] = platform.upper()
            all_jobs.append(job)
    
    # 按匹配度排序
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
    异步格式化职位数据为 Markdown 表格
    用于在 Web UI 中展示给用户
    """
    try:
        jobs = jobs_data.get("jobs", [])
        
        if not jobs:
            return {
                "status": "success",
                "markdown_table": "No jobs found matching your criteria."
            }
        
        # 构建 Markdown 表格
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


# === ScoutAgent 定义 ===
# 使用 mistral 模型以提高职位匹配的逻辑准确度（异构模型策略）

scout_agent = Agent(
    model=LiteLlm(model='ollama/mistral'),  # 使用 mistral 进行高级逻辑推理
    name='scout_agent',
    description="Job Scout Agent - Job Discovery and Matching",
    instruction="""You are a professional job discovery specialist and recruiter.
You analyze input in English and French, and respond in English only.

You have only two tools: search_jobs_on_web and format_jobs_as_table. Call only these two; do not call any other function (e.g. there is no ask_user_for_job_selection or similar).

If the data from {confirmed_resume_profile} is missing or empty, do not call any tools. Reply briefly: "Please confirm your resume information first. Reply 'yes' or 'I confirm' to the previous message so we can save your profile and start job search." Then stop.

Your workflow (only when {confirmed_resume_profile} has data):
1. You will receive resume profile data via {confirmed_resume_profile} containing:
   - target_position: The desired job title/role
   - location: Preferred work location
   - core_skills: Key technical skills
   
2. Use the search_jobs_on_web(query, location) tool to find matching positions based on the target position and location.

3. Once you have job results, use format_jobs_as_table(jobs_data) to generate a professional Markdown table showing:
   - Job Title
   - Company Name
   - Location
   - Match Score (1-5 stars)
   - Salary Range
   - Source Platform (LinkedIn, Indeed, Welcome to the Jungle)
   - Direct Application Link

4. Provide intelligent commentary on the best matches and explain why they align with the user's profile.

5. In your reply message, ask the user which positions they would like to apply to and prepare for the next phase (application tracking). Do not call a tool for this — just write the question in your response.

Maintain professionalism and accuracy. Always prioritize quality matches over quantity.
Focus on jobs that match the user's skills and location preferences.""",
    tools=[search_jobs_on_web, format_jobs_as_table]
)

# === 设置 Agent 的输出键（ADK LlmAgent 仅支持 output_key，无 input_key）===
# 上游 IdentityAgent 的 output_key="confirmed_resume_profile" 会通过 state 传入，instruction 中已引用 {confirmed_resume_profile}
scout_agent.output_key = "job_search_results"  # 输出给 TrackerAgent
