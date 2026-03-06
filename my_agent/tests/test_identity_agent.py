"""
IdentityAgent 综合测试脚本 (v2.5)
功能：验证异步工具逻辑、Agent 属性、以及状态接力配置。
适配：Mistral 强逻辑模式（由 LLM 负责提取，工具负责读写）。
"""

import asyncio
import json
from pathlib import Path
from inspect import iscoroutinefunction
from my_agent.agents.identity_agent import identity_agent

# 尝试导入核心工具 (假设我们让 LLM 直接提取，不再需要专门的提取函数)
try:
    from my_agent.agents.identity_agent import read_resume_file, save_resume_profile
except ImportError as e:
    print(f"❌ 导入错误: 请检查 identity_agent.py。错误详情: {e}")

async def run_test_step(name, coro):
    """通用的测试步骤执行器"""
    print(f"执行: {name}...", end=" ", flush=True)
    try:
        result = await coro
        if result and result.get("status") == "success":
            print("✅")
            return result
        else:
            print(f"❌ ({result.get('message', '逻辑错误')})")
            return None
    except Exception as e:
        print(f"💥 异常: {e}")
        return None

async def simulate_logic_workflow():
    """仿真测试：模拟从文件读取到生成接力数据的全过程"""
    print("\n" + "="*50)
    print("🎬 IdentityAgent 逻辑流仿真 (接力链路测试)")
    print("="*50)
    
    current_dir = Path(__file__).parent
    json_path = current_dir / "sample_resume.json"
    
    # 1. 模拟 LLM 调用工具读取
    read_res = await run_test_step("1. 模拟读取工具", read_resume_file(str(json_path)))
    if not read_res: return False
    
    # 2. 模拟 Mistral 提取并确认后的数据 (这是我们假设 Mistral 思考后的结果)
    mock_confirmed_data = {
        "target_position": "Python Developer",
        "location": "Biot, France",
        "skills": ["Python", "ADK", "Mistral"]
    }
    
    # 3. 模拟调用保存工具并检查 output_key
    save_res = await run_test_step("2. 模拟保存工具 (存入 State)", save_resume_profile(mock_confirmed_data))
    
    # 4. 核心检查：Agent 的接力键设置
    print("\n🔑 链路检查:")
    actual_key = getattr(identity_agent, 'output_key', None)
    expected_key = "confirmed_resume_profile"
    
    if actual_key == expected_key:
        print(f"   ✅ [接力键对齐]: '{actual_key}' 已就绪。")
        print(f"   💡 下游 ScoutAgent 可通过 {{{actual_key}}} 获取数据。")
    else:
        print(f"   ❌ [接力键错误]: 期望 '{expected_key}', 实际为 '{actual_key}'。")
        return False

    return True

async def main():
    print("\n🚀 开始 IdentityAgent 深度预检 (v2.5)")
    
    # --- 1. Agent 基础配置检查 ---
    print(f"\n🤖 Agent 名称: {identity_agent.name}")
    print(f"🧠 模型大脑: {identity_agent.model.model if hasattr(identity_agent.model, 'model') else 'Unknown'}")
    
    # --- 2. 运行仿真测试 ---
    success = await simulate_logic_workflow()
    
    if success:
        print("\n" + "="*50)
        print("🎉 预检通过！你的 IdentityAgent 已经具备‘接力’能力。")
        print("现在可以启动 'adk web' 进行真实对话测试了。")
        print("="*50 + "\n")
    else:
        print("\n❌ 预检未通过，请检查上述错误。")

if __name__ == "__main__":
    asyncio.run(main())