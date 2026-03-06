import os
import sys
import subprocess
import importlib.util

def check_step(name, condition, error_msg):
    if condition:
        print(f"✅ {name}: 成功")
        return True
    else:
        print(f"❌ {name}: 失败 - {error_msg}")
        return False

print("🔍 开始项目环境预检...\n")

# 1. 检查 Python 版本
check_step("Python 版本", sys.version_info >= (3, 10), "需要 Python 3.10 或更高版本")

# 2. 检查 ADK 安装
adk_installed = importlib.util.find_spec("adk") is not None
check_step("Google ADK 安装", adk_installed, "请运行 'pip install google-adk'")

# 3. 检查文件结构 (2.5 节要求)
required_files = [
    "my_agent/__init__.py",
    "my_agent/agent.py",
    "my_agent/.env",
    "my_agent/tools/my_tools.py"
]
for f in required_files:
    check_step(f"文件存在: {f}", os.path.exists(f), "请检查文件路径是否正确")

# 4. 检查 .env 内容
env_path = "my_agent/.env"
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        content = f.read()
        check_step(".env 配置", "ADK_MODEL_NAME" in content, ".env 缺少模型配置")

# 5. 检查 Ollama 服务
try:
    # 尝试连接本地 Ollama 默认端口
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    s.connect(("127.0.0.1", 11434))
    check_step("Ollama 服务", True, "")
    s.close()
except:
    check_step("Ollama 服务", False, "请确保 Ollama 正在后台运行")

print("\n🚀 如果以上全部为 ✅，请运行 'adk web' 进行最后的集成测试。")