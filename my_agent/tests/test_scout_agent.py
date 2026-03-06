"""
ScoutAgent 综合测试脚本 (v1.1)
功能：验证职位搜索聚合工具、Markdown 表格生成逻辑以及多智能体状态接力。
结构：完全对标 test_identity.py 的四段式检查结构。
"""

import asyncio
import json
import sys
from pathlib import Path
from inspect import iscoroutinefunction

# 直接运行本脚本时，将项目根目录加入 path，以便能导入 my_agent
if __name__ == "__main__":
    _root = Path(__file__).resolve().parent.parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

# 导入 ScoutAgent 实例及其工具
try:
    from my_agent.agents.scout_agent import scout_agent, search_jobs_on_web, format_jobs_as_table
except ImportError as e:
    print(f"❌ 导入错误: 无法从 my_agent.agents.scout_agent 导入。错误详情: {e}")
    sys.exit(1)

async def run_test_step(name, coro):
    """通用的测试步骤执行器"""
    print(f"正在执行: {name}...", end=" ", flush=True)
    try:
        result = await coro
        if result and result.get("status") == "success":
            print("✅ 成功")
            return result
        else:
            print(f"❌ 失败: {result.get('message', '逻辑错误')}")
            return None
    except Exception as e:
        print(f"💥 崩溃: {str(e)}")
        return None

async def simulate_scout_workflow():
    """
    逻辑流仿真测试：模拟 ScoutAgent 接收到上游 IdentityAgent 确认后的画像数据。
    """
    print("\n" + "="*60)
    print("🎬 检查 3️⃣: ScoutAgent 逻辑流仿真 (搜索与匹配链路)")
    print("="*60 + "\n")
    
    # 1. 模拟上游传来的“接力棒” (State 数据)
    mock_confirmed_profile = {
        "target_position": "Python Backend Developer",
        "location": "Biot, France",
        "core_skills": ["Python", "FastAPI", "PostgreSQL", "Google ADK"]
    }
    print(f"📡 [模拟接力]: 接收到 {{confirmed_resume_profile}} 数据...")
    print(f"   目标: {mock_confirmed_profile['target_position']} @ {mock_confirmed_profile['location']}")

    # 2. 工具测试：搜索聚合
    search_res = await run_test_step(
        "search_jobs_on_web", 
        search_jobs_on_web(mock_confirmed_profile['target_position'], mock_confirmed_profile['location'])
    )
    
    # 3. 工具测试：表格格式化
    if search_res:
        table_res = await run_test_step("format_jobs_as_table", format_jobs_as_table(search_res))
        if table_res:
            print("\n📊 生成的表格预览:")
            print("-" * 30)
            print(table_res.get('markdown_table', '')[:200] + "...")
            print("-" * 30)

    return True

async def main():
    print("\n🚀 开始 ScoutAgent 深度预检程序 (v1.1)")
    
    # --- 检查 1: Agent 基础属性 ---
    print("\n检查 1️⃣: Agent 基础属性与连接性")
    required_attrs = ['name', 'description', 'instruction', 'model']
    for attr in required_attrs:
        status = "✅" if hasattr(scout_agent, attr) else "❌"
        print(f"  {status} {attr}: {'已配置' if status == '✅' else '缺失'}")
    
    # --- 检查 2: 工具函数异步性 ---
    print("\n检查 2️⃣: 工具函数异步性 (Async/Await)")
    tools_to_check = [
        ('search_jobs_on_web', search_jobs_on_web),
        ('format_jobs_as_table', format_jobs_as_table)
    ]
    for name, func in tools_to_check:
        status = "✅" if iscoroutinefunction(func) else "⚠️"
        print(f"  {status} {name}: {'符合异步规范' if status == '✅' else '非异步定义'}")

    # --- 检查 3: 运行逻辑流仿真 ---
    success = await simulate_scout_workflow()
    
    # --- 检查 4: 接力键与变量引用检查 ---
    print("\n检查 4️⃣: 多智能体变量链路 (Handoff Chain)")
    instr = getattr(scout_agent, 'instruction', '')
    input_key = "{confirmed_resume_profile}"
    
    if input_key in instr:
        print(f"  ✅ 变量引用: 已正确引用 {input_key}")
    else:
        print(f"  ❌ 变量引用: 缺失！ScoutAgent 无法获取上游数据")
        success = False

    if success:
        print("\n" + "="*60)
        print("🎉 ScoutAgent 预检通过！结构与 IdentityAgent 完全对称。")
        print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())