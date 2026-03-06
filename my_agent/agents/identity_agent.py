"""
IdentityAgent - Resume parser. Extracts key dimensions (target role, location, contract, experience, salary, skills),
presents a summary for user confirmation, then passes structured data to ScoutAgent via output_key "confirmed_resume_profile".
"""

import json
import asyncio
from pathlib import Path
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm


async def read_resume_file(file_path: str) -> dict:
    """
    Read user's local resume file (.txt, .md, .json).
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return {
                "status": "error",
                "message": f"Resume file not found: {file_path}"
            }
        
        loop = asyncio.get_event_loop()
        
        if path.suffix == '.json':
            content = await loop.run_in_executor(None, lambda: json.load(open(path, 'r', encoding='utf-8')))
            return {
                "status": "success",
                "content": json.dumps(content, ensure_ascii=False),
                "format": "json"
            }
        else:
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


async def save_resume_profile(profile_data: dict, output_path: str = "my_agent/tests/my_tests.test.json") -> dict:
    """
    Save extracted resume profile to disk. Feeds downstream ScoutAgent via output_key "confirmed_resume_profile".
    """
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: Path(output_path).parent.mkdir(parents=True, exist_ok=True))
        
        def write_file():
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
        
        await loop.run_in_executor(None, write_file)
        
        return {
            "status": "success",
            "message": f"Profile saved to {output_path}",
            "output_key": "confirmed_resume_profile",
            "data": profile_data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error saving profile: {str(e)}"
        }


def _identity_before_tool(tool, args, tool_context):
    """Before read_resume_file: log for audit. Return None to keep default behavior."""
    tool_name = getattr(tool, "__name__", None) or str(tool)
    if tool_name == "read_resume_file":
        file_path = args.get("file_path", "(unknown)") if isinstance(args, dict) else "(unknown)"
        print(f"[IdentityAgent before_tool] About to read resume file_path={file_path}")
    return None


identity_agent = Agent(
    model=LiteLlm(model="gemini/gemini-2.5-flash-lite"),
    name='identity_agent',
    description="Resume Parser Agent - Extract Key Information from User Resume",
    instruction="""You are a professional resume parsing specialist. You analyze input in English and French, and respond in English only.

ALLOWED TOOLS (use only these exact names; do not invent any other tool name):
- read_resume_file
- save_resume_profile

Workflow:

Step 1 (ONCE per file): When the user provides a resume file path, use read_resume_file to get the content. Call it exactly once for that path.

Step 2: From the content, extract: target position type, location, contract type, years of experience, salary expectations, core technical and professional skills. You MUST present the summary to the user in the following Markdown breakdown format (use exactly these section headers and bullet style so the reply is clear and readable):

## Resume summary

| Field | Value |
|-------|-------|
| **Target position** | ... |
| **Location** | ... |
| **Contract type** | permanent / contract / freelance |
| **Years of experience** | ... |
| **Salary expectations** | ... |
| **Core skills** | ... (comma-separated or short list) |

Then on a new line ask: **"Do you need any modifications?"**

CONFIRMATION LOOP (state lock — do not break this):
- You may call save_resume_profile ONLY when the user explicitly confirms (e.g. says "No", "No modifications", "Confirm", "It's correct", "Looks good"). Until then, do NOT call save_resume_profile.
- If the user says they need modifications (e.g. "Yes", "I need to change...", "Modify..."): do NOT call save_resume_profile. Update the extracted information according to their feedback, present the updated summary again in the same Markdown table format above, and ask again: "Do you need any modifications?" Repeat until the user explicitly confirms.
- When the user confirms (No / Confirm): call save_resume_profile exactly once with the final profile dict (at least target_position, location, and any other fields you extracted). Then you may reply with a brief confirmation and the same Markdown table for reference, and end the task.

Summary: Never call save_resume_profile until the user clearly indicates no modifications or confirmation. If they ask for changes, re-extract or modify and ask again; only after explicit confirmation do you save and finish. Always use the Markdown table format when showing the resume summary to the user.""",
    tools=[read_resume_file, save_resume_profile],
    before_tool_callback=_identity_before_tool,
)

identity_agent.output_key = "confirmed_resume_profile"

