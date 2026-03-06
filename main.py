"""
Programmatic Runner: Runner + InMemorySessionService. Run: python main.py
"""

import asyncio
from pathlib import Path

_env = Path(__file__).resolve().parent / "my_agent" / ".env"
if _env.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env)
    except ImportError:
        pass

from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from my_agent.agent import root_agent


def create_runner_and_session_service():
    """Create InMemorySessionService and Runner."""
    session_service = InMemorySessionService()
    app = App(name="my_agent", root_agent=root_agent)
    runner = Runner(app=app, session_service=session_service)
    return runner, session_service


async def run_once():
    """Create session, send one sample message and stream events."""
    runner, session_service = create_runner_and_session_service()
    app_name = "my_agent"
    user_id = "main.py-user"
    session = await session_service.create_session(app_name=app_name, user_id=user_id)
    content = types.Content(role="user", parts=[types.Part(text="Hello, I want to start the job search pipeline.")])
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
    print()


if __name__ == "__main__":
    runner, session_service = create_runner_and_session_service()
    print("Runner and InMemorySessionService ready.")
    print("Running one round with a sample message...")
    asyncio.run(run_once())
