# JobFlow-ADK: 自动化求职情报与追踪系统

## 本项目是一个基于 Google ADK (Agent Development Kit) 和 Ollama (本地 LLM) 的多智能体协作系统，旨在实现从简历解析、职位发现到投递追踪的全流程自动化。

## 核心智能体架构 (Multi-Agent Workflow)：本项目采用 SequentialFlow（顺序工作流）逻辑，由四个各司其职的智能体协作完成：

### 1. IdentityAgent (身份解析专家)

* 职责：核心数据提取。

* 工作逻辑：

** 读取用户本地简历文件。

** 提取关键维度：目标职位类型、地点、合同类型、工作年限、薪资预期、核心技能。

* 交互逻辑：生成信息总结并向用户提问：“这是我提取的信息，是否准确？需要修改吗？”。

* 结束条件：获得用户确认。

### 2. ScoutAgent (情报搜寻员)

职责：全网职位抓取与匹配。

工作逻辑：

基于 IdentityAgent 确定的关键词，在 LinkedIn、Indeed、Welcome to the Jungle 三大平台进行定向搜集。

智能排序：根据简历匹配度进行 Ranking (1-5)。

产出：生成结构化表格，包含：职位名、公司、匹配分、投递链接。

### 3. TrackerAgent (求职秘书)

职责：闭环追踪与反馈分析。

工作逻辑：

扫描关联邮箱，识别投递反馈邮件（拒信/面试/待定）。

Action Plan：生成本周投递总结。

数据模型：承接 ScoutAgent 的表结构，补充 投递时间、反馈时间、最终结果。

### 4. SequentialAgent (调度指挥官)

职责：流程编排与状态监控。

逻辑：确保 Identity -> Scout -> Tracker 按序执行，并实时反馈当前系统处于哪一个阶段。

🛠️ 技术栈与环境 (Current Tech Stack)

框架: Google ADK 1.26.0

推理引擎: Ollama (本地运行)

默认模型: gemma3:1b (已通过连通性压力测试)

通信协议: LiteLLM / Agent-based Tool Calling

开发环境: Python 3.11 + VS Code

异构模型支持: 系统支持多个异构模型协作（不同 Agent 可使用不同的 LLM 模型），通过 LiteLlm 动态加载和切换

## 项目进度 (Implementation Status)

[x] Phase 1: 环境打通 (Connectivity)

解决了 google-adk 命名空间导入问题。

解决了 Pydantic ValidationError (参数名锁定为 instruction)。

成功实现 root_agent 与本地 Ollama 的 Tool Calling 闭环。

[ ] Phase 2: 核心工具开发 (Current Focus)

编写 IdentityAgent 的简历解析工具。

开发基于 BeautifulSoup 的三站聚合抓取脚本。

[ ] Phase 3: 状态持久化

实现 Agent 间的信息共享与状态转换。

## 如何运行

启动本地大脑：确保 Ollama 运行中 (ollama run gemma3:1b)。

激活环境：source .venv/bin/activate。

运行项目：

# 清理缓存并启动 Web UI
find . -name "__pycache__" -type d -exec rm -rf {} +
adk web


## Copilot 编程提示

如果你正在使用 Copilot 辅助编写代码，请参考 my_agent/agent.py 中的 Agent 类定义。请注意，本版本 ADK 的初始化参数为 instruction (单数)，且必须通过 LiteLlm 显式包装模型路径。

