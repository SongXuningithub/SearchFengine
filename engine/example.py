#!/usr/bin/env python3
"""
搜索引擎使用示例
展示如何快速使用SearchEngine类
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indexer.inverted_index import InvertedIndexBuilder
from engine.search_engine import SearchEngine

def quick_search_example():
    """快速搜索示例"""
    
    # 检查必要文件
    db_path = "data/crawler/crawler.db"
    index_path = "data/indexer"
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在，请先运行爬虫")
        return
    
    if not os.path.exists(index_path):
        print("❌ 索引目录不存在，请先构建索引")
        return
    
    try:
        # 1. 创建索引构建器
        print("正在加载倒排索引...")
        index_builder = InvertedIndexBuilder(
            db_path=db_path,
            index_path=index_path,
            num_shards=16
        )
        
        # 2. 创建搜索引擎
        print("正在初始化搜索引擎...")
        search_engine = SearchEngine(index_builder, db_path)
        
        # 3. 执行搜索
        query = "股票投资"
        print(f"\n搜索查询: '{query}'")
        
        results = search_engine.search(query, max_results=5)
        
        if results:
            print(f"\n找到 {len(results)} 个结果:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['title']}")
                print(f"   分数: {result['score']:.3f}")
                print(f"   URL: {result['url']}")
                print(f"   预览: {result['content_preview'][:100]}...")
        else:
            print("未找到结果")
            
    except Exception as e:
        print(f"错误: {e}")

def advanced_search_example():
    """高级搜索示例"""
    
    db_path = "data/crawler/crawler.db"
    index_path = "data/indexer"
    
    if not os.path.exists(db_path) or not os.path.exists(index_path):
        print("❌ 缺少必要文件")
        return
    
    try:
        # 初始化搜索引擎
        index_builder = InvertedIndexBuilder(db_path=db_path, index_path=index_path)
        search_engine = SearchEngine(index_builder, db_path)
        
        # 演示不同的搜索功能
        queries = [
            "人工智能",
            "区块链",
            "金融科技",
            "投资理财"
        ]
        
        print("高级搜索示例")
        print("=" * 50)
        
        for query in queries:
            print(f"\n查询: '{query}'")
            
            # 分词演示
            tokens = search_engine.tokenize_query(query)
            print(f"分词: {tokens}")
            
            # 执行搜索
            results = search_engine.search(query, max_results=3)
            
            if results:
                print(f"结果数量: {len(results)}")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['title']} (分数: {result['score']:.3f})")
            else:
                print("无结果，尝试OR搜索...")
                or_results = search_engine.search_with_fallback(query, max_results=2)
                if or_results:
                    print(f"OR搜索找到 {len(or_results)} 个结果")
                else:
                    print("仍然无结果")
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    print("搜索引擎使用示例")
    print("=" * 50)
    
    print("\n1. 快速搜索示例:")
    quick_search_example()
    
    print("\n" + "=" * 50)
    print("\n2. 高级搜索示例:")
    advanced_search_example()
