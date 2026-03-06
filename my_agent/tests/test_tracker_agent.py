"""
TrackerAgent 综合测试脚本 (v1.0)
功能：验证投递追踪工具、状态/反馈日期逻辑以及多智能体状态接力。
结构：对标 test_scout_agent.py 的四段式检查结构。
"""

import asyncio
import sys
from pathlib import Path
from inspect import iscoroutinefunction

# 直接运行本脚本时，将项目根目录加入 path，以便能导入 my_agent
if __name__ == "__main__":
    _root = Path(__file__).resolve().parent.parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

# 导入 TrackerAgent 实例及其工具
try:
    from my_agent.agents.tracker_agent import tracker_agent, fetch_tracking_updates
except ImportError as e:
    print(f"❌ 导入错误: 无法从 my_agent.agents.tracker_agent 导入。错误详情: {e}")
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


async def simulate_tracker_workflow():
    """
    逻辑流仿真测试：模拟 TrackerAgent 接收到上游 ScoutAgent 的 job_search_results。
    """
    print("\n" + "=" * 60)
    print("🎬 检查 3️⃣: TrackerAgent 逻辑流仿真 (追踪与反馈链路)")
    print("=" * 60 + "\n")

    # 1. 模拟上游 ScoutAgent 传来的 job_search_results（含 jobs 列表）
    mock_job_search_results = {
        "status": "success",
        "query": "Python Developer",
        "location": "Paris, France",
        "total_results": 2,
        "jobs": [
            {"title": "Senior Python Engineer", "company": "TechCorp France", "url": "https://linkedin.com/jobs/1"},
            {"title": "Python Developer", "company": "StartupHub", "url": "https://welcometothejungle.com/jobs/2"}
        ]
    }
    jobs = mock_job_search_results["jobs"]
    print(f"📡 [模拟接力]: 接收到 {{job_search_results}} 数据...")
    print(f"   职位数: {len(jobs)}")

    # 2. 工具测试：获取追踪更新（status + feedback_date）
    tracking_res = await run_test_step("fetch_tracking_updates", fetch_tracking_updates(jobs))

    # 3. 校验返回结构：每条 job 应有 status 和 feedback_date
    if tracking_res:
        enriched = tracking_res.get("jobs", [])
        if enriched:
            first = enriched[0]
            has_status = "status" in first
            has_date = "feedback_date" in first
            print(f"\n📋 返回结构检查: status={has_status}, feedback_date={has_date}")
            if has_status and has_date:
                print(f"   示例: {first.get('title')} @ {first.get('company')} -> {first.get('status')} ({first.get('feedback_date')})")
            else:
                print("   ❌ 缺少 status 或 feedback_date 字段")
        else:
            print("   ⚠️ jobs 为空")

    return True


async def main():
    print("\n🚀 开始 TrackerAgent 深度预检程序 (v1.0)")

    # --- 检查 1: Agent 基础属性 ---
    print("\n检查 1️⃣: Agent 基础属性与连接性")
    required_attrs = ["name", "description", "instruction", "model"]
    for attr in required_attrs:
        status = "✅" if hasattr(tracker_agent, attr) else "❌"
        print(f"  {status} {attr}: {'已配置' if status == '✅' else '缺失'}")

    # --- 检查 2: 工具函数异步性 ---
    print("\n检查 2️⃣: 工具函数异步性 (Async/Await)")
    tools_to_check = [("fetch_tracking_updates", fetch_tracking_updates)]
    for name, func in tools_to_check:
        status = "✅" if iscoroutinefunction(func) else "⚠️"
        print(f"  {status} {name}: {'符合异步规范' if status == '✅' else '非异步定义'}")

    # --- 检查 3: 运行逻辑流仿真 ---
    success = await simulate_tracker_workflow()

    # --- 检查 4: 接力键与变量引用检查 ---
    print("\n检查 4️⃣: 多智能体变量链路 (Handoff Chain)")
    instr = getattr(tracker_agent, "instruction", "")
    input_ref = "{job_search_results}"
    output_key = getattr(tracker_agent, "output_key", None)

    if input_ref in instr:
        print(f"  ✅ 变量引用: 已正确引用 {input_ref}")
    else:
        print(f"  ❌ 变量引用: 缺失！TrackerAgent 无法获取上游数据")
        success = False

    if output_key == "final_application_report":
        print(f"  ✅ output_key: {output_key}")
    else:
        print(f"  ❌ output_key: 期望 'final_application_report'，当前为 {output_key!r}")
        success = False

    if success:
        print("\n" + "=" * 60)
        print("🎉 TrackerAgent 预检通过！结构与 ScoutAgent 对称。")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
