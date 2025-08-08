#!/usr/bin/env python3
"""
搜索引擎演示脚本
"""

import sys
import os
import time
import requests
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def demo_search_engine():
    """演示搜索引擎功能"""
    print("搜索引擎演示")
    print("=" * 50)
    
    # 检查API服务器是否运行
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✓ API服务器正在运行")
        else:
            print("✗ API服务器响应异常")
            return
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到API服务器")
        print("请先启动API服务器: python engine/run_engine.py")
        return
    
    # 演示搜索功能
    print("\n1. 搜索功能演示")
    print("-" * 30)
    
    test_queries = [
        "股票投资",
        "基金理财", 
        "市场分析",
        "金融科技",
        "区块链"
    ]
    
    for query in test_queries:
        print(f"\n查询: '{query}'")
        try:
            response = requests.get(
                "http://localhost:5000/api/search",
                params={'q': query, 'max_results': 3},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"  找到 {data['total_results']} 个结果")
                    print(f"  搜索耗时: {data['search_time']} 秒")
                    
                    for i, result in enumerate(data['results'][:2], 1):
                        print(f"  {i}. {result['title']}")
                        print(f"     评分: {result['score']}")
                        print(f"     摘要: {result['summary'][:100]}...")
                else:
                    print(f"  搜索失败: {data.get('error', '未知错误')}")
            else:
                print(f"  HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"  请求失败: {e}")
    
    # 演示系统统计
    print("\n2. 系统统计演示")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:5000/api/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"文档总数: {data['total_documents']}")
                print(f"平均文档长度: {data['avg_document_length']}")
                print(f"分片数量: {data['num_shards']}")
                print(f"BM25参数 k1: {data['bm25_k1']}")
                print(f"BM25参数 b: {data['bm25_b']}")
            else:
                print(f"获取统计失败: {data.get('error', '未知错误')}")
        else:
            print(f"HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 演示查询建议
    print("\n3. 查询建议演示")
    print("-" * 30)
    
    suggestions = ["股票", "基金", "投资"]
    for suggestion in suggestions:
        try:
            response = requests.get(
                "http://localhost:5000/api/suggest",
                params={'q': suggestion, 'max': 3},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"'{suggestion}' 的建议: {data['suggestions']}")
                else:
                    print(f"获取建议失败: {data.get('error', '未知错误')}")
            else:
                print(f"HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"请求失败: {e}")
    
    # 演示热门关键词
    print("\n4. 热门关键词演示")
    print("-" * 30)
    
    try:
        response = requests.get(
            "http://localhost:5000/api/keywords",
            params={'top': 5},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("热门关键词:")
                for keyword, freq in data['keywords']:
                    print(f"  {keyword}: {freq}")
            else:
                print(f"获取关键词失败: {data.get('error', '未知错误')}")
        else:
            print(f"HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n演示完成!")

def demo_api_endpoints():
    """演示API端点"""
    print("\nAPI端点演示")
    print("=" * 50)
    
    endpoints = [
        ("健康检查", "/api/health"),
        ("系统信息", "/api/info"),
        ("系统统计", "/api/stats"),
        ("搜索", "/api/search?q=股票&max_results=2"),
        ("建议", "/api/suggest?q=股票&max=3"),
        ("关键词", "/api/keywords?top=3")
    ]
    
    for name, endpoint in endpoints:
        print(f"\n{name}: GET {endpoint}")
        try:
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=5)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✓ 成功")
                else:
                    print(f"✗ 失败: {data.get('error', '未知错误')}")
            else:
                print(f"✗ HTTP错误")
        except Exception as e:
            print(f"✗ 连接失败: {e}")

if __name__ == '__main__':
    print("搜索引擎演示工具")
    print("请确保API服务器正在运行: python engine/run_engine.py")
    print()
    
    # 演示搜索引擎功能
    demo_search_engine()
    
    # 演示API端点
    demo_api_endpoints() 