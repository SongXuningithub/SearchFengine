#!/usr/bin/env python3
"""
前端功能测试脚本
"""

import requests
import time
import webbrowser
from urllib.parse import quote

def test_frontend():
    """测试前端功能"""
    base_url = "http://localhost:5000"
    
    print("前端功能测试")
    print("=" * 50)
    
    # 测试主页
    print("1. 测试主页...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✓ 主页加载成功")
        else:
            print(f"✗ 主页加载失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 主页测试失败: {e}")
    
    # 测试搜索页面
    print("\n2. 测试搜索页面...")
    try:
        query = "股票"
        encoded_query = quote(query)
        response = requests.get(f"{base_url}/search?q={encoded_query}")
        if response.status_code == 200:
            print("✓ 搜索页面加载成功")
        else:
            print(f"✗ 搜索页面加载失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 搜索页面测试失败: {e}")
    
    # 测试API端点
    print("\n3. 测试API端点...")
    endpoints = [
        ("健康检查", "/api/health"),
        ("系统信息", "/api/info"),
        ("系统统计", "/api/stats"),
        ("搜索", f"/api/search?q={quote('股票')}&max_results=3"),
        ("建议", f"/api/suggest?q={quote('股票')}&max=3"),
        ("关键词", "/api/keywords?top=5")
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✓ {name} API正常")
                else:
                    print(f"✗ {name} API返回错误: {data.get('error', '未知错误')}")
            else:
                print(f"✗ {name} API失败: {response.status_code}")
        except Exception as e:
            print(f"✗ {name} API测试失败: {e}")
    
    print("\n4. 打开浏览器测试...")
    print("正在打开浏览器...")
    
    # 打开主页
    webbrowser.open(f"{base_url}/")
    time.sleep(2)
    
    # 打开搜索页面
    webbrowser.open(f"{base_url}/search?q={quote('股票')}")
    
    print("\n测试完成!")
    print("请在浏览器中查看前端页面是否正常工作")

if __name__ == '__main__':
    test_frontend() 