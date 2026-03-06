"""
Google ADK Package Initializer
此文件负责将 agent.py 中定义的 root_agent 暴露给 ADK 框架。
"""

# 从当前目录下的 agent.py 文件中导入 root_agent
# 这样当运行 'adk web' 时，框架可以直接通过 my_agent 包访问到它
from .agent import root_agent
