#!/usr/bin/env python3
"""
搜索引擎测试脚本
"""

import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.search_engine import SearchEngine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_search_engine():
    """测试搜索引擎功能"""
    print("=== 搜索引擎测试 ===")
    
    try:
        # 初始化搜索引擎
        print("1. 初始化搜索引擎...")
        search_engine = SearchEngine()
        
        # 获取搜索统计信息
        stats = search_engine.get_search_stats()
        print(f"文档总数: {stats['total_documents']}")
        print(f"平均文档长度: {stats['avg_document_length']:.2f}")
        print(f"BM25参数 - k1: {stats['bm25_k1']}, b: {stats['bm25_b']}")
        print(f"最大结果数: {stats['max_results']}")
        
        # 测试查询
        test_queries = [
            "股票",
            "投资",
            "基金",
            "科技",
            "汽车",
            "人工智能",
            "区块链",
            "比特币",
            "特斯拉",
            "苹果公司"
        ]
        
        print("\n2. 执行搜索测试...")
        for query in test_queries:
            print(f"\n--- 查询: '{query}' ---")
            
            # 分词测试
            terms = search_engine.tokenize_query(query)
            print(f"分词结果: {terms}")
            
            # 搜索测试
            results = search_engine.search(query)
            print(f"搜索结果数量: {len(results)}")
            
            if results:
                print("前3个结果:")
                for i, result in enumerate(results[:3]):
                    print(f"  {i+1}. 文档ID: {result['doc_id']}")
                    print(f"     标题: {result['title']}")
                    print(f"     内容: {result['content'][:100]}...")
                    print(f"     分数: {result['score']:.4f}")
                    print(f"     长度: {result['length']}")
            else:
                print("  无搜索结果")
        
        # 测试高亮搜索
        print("\n3. 测试高亮搜索...")
        highlight_query = "股票投资"
        highlight_results = search_engine.search_with_highlight(highlight_query)
        print(f"高亮搜索结果数量: {len(highlight_results)}")
        
        if highlight_results:
            print("前2个高亮结果:")
            for i, result in enumerate(highlight_results[:2]):
                print(f"  {i+1}. 文档ID: {result['doc_id']}")
                print(f"     高亮标题: {result['highlighted_title']}")
                print(f"     高亮内容: {result['highlighted_content'][:150]}...")
                print(f"     分数: {result['score']:.4f}")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

def test_posting_intersection():
    """测试倒排列表求交功能"""
    print("\n=== 倒排列表求交测试 ===")
    
    try:
        search_engine = SearchEngine()
        
        # 测试查询
        test_query = "广州的天气"
        terms = search_engine.tokenize_query(test_query)
        print(f"查询词: {terms}")
        
        # 获取倒排列表
        postings_list = []
        for term in terms:
            postings = search_engine.get_postings(term)
            if postings:
                postings_list.append(postings)
                print(f"词 '{term}' 的倒排列表长度: {len(postings)}")
                print(f"  前3个文档ID: {[p.doc_id for p in postings[:3]]}")
            else:
                print(f"词 '{term}' 没有倒排列表")
        
        # 求交
        if postings_list:
            intersection = search_engine.intersect_postings(postings_list)
            print(f"求交结果: {len(intersection)} 个文档")
            if intersection:
                print(f"前5个文档ID: {intersection[:5]}")
        else:
            print("没有可求交的倒排列表")
        
    except Exception as e:
        print(f"求交测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # test_search_engine()
    test_posting_intersection()
