import requests
from bs4 import BeautifulSoup
import time
import random

# 测试目标 URL
targets = {
    "LinkedIn": "https://www.linkedin.com/jobs/search?keywords=Python",
    "Indeed": "https://fr.indeed.com/jobs?q=python",
    "WelcomeToThe Jungle": "https://www.welcometothejungle.com/fr/jobs?query=python"
}

# 模拟真实的浏览器请求头 (非常重要)
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
}

def test_site(name, url):
    print(f"--- 正在测试 {name} ---")
    try:
        # 增加随机延迟，模拟人类行为
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ 成功连接 {name} (状态码: 200)")
            # 检查是否拿到了真实内容，还是拿到了验证码页面
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "No Title"
            print(f"📄 页面标题: {title}")
            
            # 简单判断是否被拦截 (根据标题关键词)
            if "Security Check" in title or "Captcha" in title or "Forbidden" in title:
                print(f"⚠️ 警告: 虽然连接成功，但似乎触发了验证码或安全检查。")
            else:
                print(f"🎉 看起来可以抓取基础 HTML。")
                
        elif response.status_code == 429:
            print(f"❌ 失败: {name} 返回了 429 (Too Many Requests)。你被限流了。")
        elif response.status_code == 403:
            print(f"❌ 失败: {name} 返回了 403 (Forbidden)。你的 IP 或请求头被封锁了。")
        else:
            print(f"❓ 异常: {name} 返回了状态码 {response.status_code}")
            
    except Exception as e:
        print(f"🚨 错误: 连接 {name} 时发生崩溃: {e}")
    print("\n")

if __name__ == "__main__":
    print("开始抓取可行性初步评估...\n")
    for name, url in targets.items():
        test_site(name, url)