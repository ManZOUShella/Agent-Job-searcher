"""
Smoke Test - 测试 Agent 的对话能力
"""

from my_agent.agent import root_agent

def test_smoke():
    # 测试用例 1：输入"hello"
    print("=" * 50)
    print("测试 1：输入 'hello'")
    print("=" * 50)
    response = root_agent.generate_response("hello")
    print(f"Agent 回复：{response}")
    print()
    
    # 测试用例 2：输入"你好"
    print("=" * 50)
    print("测试 2：输入 '你好'")
    print("=" * 50)
    response = root_agent.generate_response("你好")
    print(f"Agent 回复：{response}")
    print()
    
    # 测试用例 3：其他输入
    print("=" * 50)
    print("测试 3：输入 '你好吗？'")
    print("=" * 50)
    response = root_agent.generate_response("你好吗？")
    print(f"Agent 回复：{response}")
    print()

if __name__ == "__main__":
    print("\n🚀 开始 Smoke Test...\n")
    test_smoke()
    print("\n✅ 测试完成！\n")
