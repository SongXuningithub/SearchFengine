#!/usr/bin/env python3
"""
搜索引擎测试脚本
"""

import sys
import os
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from search_engine import SearchEngine

def test_search_engine():
    """测试搜索引擎"""
    print("开始测试搜索引擎...")
    
    try:
        # 初始化搜索引擎
        print("初始化搜索引擎...")
        engine = SearchEngine(
            index_path="data/indexer",
            db_path="data/crawler/crawler.db",
            num_shards=64
        )
        
        # 测试统计信息
        print("\n获取统计信息...")
        stats = engine.get_stats()
        print(f"文档总数: {stats['total_documents']}")
        print(f"平均文档长度: {stats['avg_document_length']}")
        print(f"分片数量: {stats['num_shards']}")
        
        # 测试搜索
        test_queries = [
            "股票",
            "投资",
            "基金",
            "市场",
            "金融"
        ]
        
        print("\n测试搜索功能...")
        for query in test_queries:
            print(f"\n查询: '{query}'")
            start_time = time.time()
            results = engine.search(query, max_results=5)
            search_time = time.time() - start_time
            
            print(f"搜索耗时: {search_time:.3f}秒")
            print(f"找到 {len(results)} 个结果")
            
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. {result['title']} (评分: {result['score']})")
                print(f"     {result['summary'][:100]}...")
        
        # 测试建议功能
        print("\n测试查询建议...")
        suggestions = engine.suggest("股票", max_suggestions=3)
        print(f"建议: {suggestions}")
        
        # 测试热门关键词
        print("\n测试热门关键词...")
        keywords = engine.get_popular_keywords(top_k=5)
        print(f"热门关键词: {keywords}")
        
        print("\n搜索引擎测试完成!")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_api_endpoints():
    """测试API端点"""
    print("\n开始测试API端点...")
    
    try:
        import requests
        
        base_url = "http://localhost:5000/api"
        
        # 测试健康检查
        print("测试健康检查...")
        response = requests.get(f"{base_url}/health")
        print(f"健康检查: {response.status_code} - {response.json()}")
        
        # 测试系统信息
        print("测试系统信息...")
        response = requests.get(f"{base_url}/info")
        print(f"系统信息: {response.status_code} - {response.json()}")
        
        # 测试统计信息
        print("测试统计信息...")
        response = requests.get(f"{base_url}/stats")
        print(f"统计信息: {response.status_code} - {response.json()}")
        
        # 测试搜索
        print("测试搜索...")
        response = requests.get(f"{base_url}/search", params={'q': '股票', 'max_results': 3})
        print(f"搜索: {response.status_code} - {response.json()}")
        
        # 测试建议
        print("测试建议...")
        response = requests.get(f"{base_url}/suggest", params={'q': '股票', 'max': 3})
        print(f"建议: {response.status_code} - {response.json()}")
        
        # 测试热门关键词
        print("测试热门关键词...")
        response = requests.get(f"{base_url}/keywords", params={'top': 5})
        print(f"热门关键词: {response.status_code} - {response.json()}")
        
        print("\nAPI端点测试完成!")
        
    except requests.exceptions.ConnectionError:
        print("无法连接到API服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"API测试失败: {e}")

if __name__ == '__main__':
    print("搜索引擎测试工具")
    print("=" * 50)
    
    # 测试搜索引擎核心功能
    test_search_engine()
    
    # 测试API端点
    test_api_endpoints() 