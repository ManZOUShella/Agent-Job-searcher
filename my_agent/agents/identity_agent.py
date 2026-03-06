"""
IdentityAgent - 身份解析专家
职责：核心数据提取（简历解析）
工作逻辑：
  1. 读取用户本地简历文件
  2. 提取关键维度：目标职位类型、地点、合同类型、工作年限、薪资预期、核心技能
  3. 生成信息总结并向用户提问："这是我提取的信息，是否准确？需要修改吗？"
  4. 获得用户确认后完成任务
  5. 通过 output_key "confirmed_resume_profile" 传递结构化数据给 ScoutAgent
"""

import os
import json
import asyncio
from pathlib import Path
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm


# === 异步工具函数 ===

async def read_resume_file(file_path: str) -> dict:
    """
    异步读取用户的本地简历文件 (支持 .txt, .md, .json 格式)
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return {
                "status": "error",
                "message": f"Resume file not found: {file_path}"
            }
        
        # 使用线程池避免阻塞异步事件循环
        loop = asyncio.get_event_loop()
        
        if path.suffix == '.json':
            content = await loop.run_in_executor(None, lambda: json.load(open(path, 'r', encoding='utf-8')))
            return {
                "status": "success",
                "content": json.dumps(content, ensure_ascii=False),
                "format": "json"
            }
        else:  # .txt, .md
            content = await loop.run_in_executor(None, lambda: open(path, 'r', encoding='utf-8').read())
            return {
                "status": "success",
                "content": content,
                "format": path.suffix
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading resume: {str(e)}"
        }


async def extract_resume_dimensions(resume_content: str) -> dict:
    """
    从简历内容中提取关键维度 (异步版本)
    关键维度：目标职位、地点、合同类型、工作年限、薪资预期、核心技能
    """
    dimensions = {
        "target_position": "Not extracted",
        "location": "Not extracted",
        "contract_type": "Not extracted",
        "years_of_experience": "Not extracted",
        "salary_expectations": "Not extracted",
        "core_skills": "Not extracted"
    }
    
    return {
        "status": "pending_confirmation",
        "extracted_dimensions": dimensions,
        "prompt": "This is the extracted information. Is it accurate? Do you need any modifications?"
    }


async def save_resume_profile(profile_data: dict, output_path: str = "my_agent/tests/my_tests.test.json") -> dict:
    """
    异步保存提取的简历信息到本地
    通过 output_key "confirmed_resume_profile" 为下游 Agent (ScoutAgent) 提供数据
    """
    try:
        # 确保目录存在
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: Path(output_path).parent.mkdir(parents=True, exist_ok=True))
        
        # 异步写入文件
        def write_file():
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
        
        await loop.run_in_executor(None, write_file)
        
        return {
            "status": "success",
            "message": f"Profile saved to {output_path}",
            "output_key": "confirmed_resume_profile",  # 明确的数据传递键
            "data": profile_data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error saving profile: {str(e)}"
        }


# === IdentityAgent 定义 ===
# 使用 mistral 模型以提高简历解析的逻辑准确度（异构模型策略）

identity_agent = Agent(
    model=LiteLlm(model='ollama/mistral'),  # 升级到 mistral 以提高准确度
    name='identity_agent',
    description="Resume Parser Agent - Extract Key Information from User Resume",
    instruction="""You are a professional resume parsing specialist.
You analyze input in English and French, and respond in English only.

Your workflow:
1. When user provides a resume file path, use read_resume_file() to retrieve the content
2. Use extract_resume_dimensions() to identify key information:
   - Target position type
   - Location
   - Contract type (permanent, contract, freelance, etc.)
   - Years of experience
   - Salary expectations
   - Core technical and professional skills
3. Generate a clear summary of extracted information
4. Ask user for confirmation: "This is the extracted information. Is it accurate? Do you need any modifications?"
5. After user confirms, save the profile using save_resume_profile()
6. The output key "confirmed_resume_profile" will be automatically passed to downstream agents (ScoutAgent, TrackerAgent)

Maintain high accuracy and professionalism in all data extractions.
Always verify information with the user before proceeding.""",
    tools=[read_resume_file, extract_resume_dimensions, save_resume_profile]
)

# === 设置 Agent 的接力键（用于下游 Agent 数据获取）===
identity_agent.output_key = "confirmed_resume_profile"

