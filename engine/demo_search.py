#!/usr/bin/env python3
"""
搜索引擎演示脚本
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.search_engine import BM25SearchEngine

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_result(result, index):
    """打印搜索结果"""
    print(f"\n{index}. {result.get('title', 'N/A')}")
    print(f"   分数: {result.get('score', 0):.4f}")
    print(f"   URL: {result.get('url', 'N/A')}")
    print(f"   域名: {result.get('domain', 'N/A')}")
    
    # 显示高亮片段
    highlights = result.get('highlights', [])
    if highlights:
        print("   高亮片段:")
        for highlight in highlights[:2]:  # 只显示前2个片段
            print(f"     {highlight}")

def demo_basic_search():
    """演示基础搜索功能"""
    print_header("基础搜索功能演示")
    
    engine = BM25SearchEngine()
    
    # 测试查询
    queries = [
        "股票投资",
        "基金理财", 
        "比特币",
        "人工智能",
        "金融科技"
    ]
    
    for query in queries:
        print(f"\n🔍 搜索: '{query}'")
        
        start_time = time.time()
        results = engine.search(query, max_results=3)
        search_time = time.time() - start_time
        
        if results:
            print(f"✅ 找到 {len(results)} 个结果 (耗时: {search_time:.3f}秒)")
            for i, result in enumerate(results, 1):
                print_result(result, i)
        else:
            print("❌ 无结果")

def demo_domain_search():
    """演示按域名搜索"""
    print_header("按域名搜索演示")
    
    engine = BM25SearchEngine()
    
    # 测试域名
    domains = [
        "cnbc.com",
        "bloomberg.com", 
        "reuters.com",
        "ft.com"
    ]
    
    for domain in domains:
        print(f"\n🌐 搜索域名: '{domain}'")
        
        results = engine.search_by_domain(domain, max_results=2)
        
        if results:
            print(f"✅ 找到 {len(results)} 个结果")
            for i, result in enumerate(results, 1):
                print_result(result, i)
        else:
            print("❌ 无结果")

def demo_keyword_search():
    """演示按关键词搜索"""
    print_header("按关键词搜索演示")
    
    engine = BM25SearchEngine()
    
    # 测试关键词组合
    keyword_groups = [
        ["股票", "投资"],
        ["基金", "理财"],
        ["比特币", "加密货币"],
        ["人工智能", "机器学习"]
    ]
    
    for keywords in keyword_groups:
        print(f"\n🏷️  搜索关键词: {keywords}")
        
        results = engine.search_by_keywords(keywords, max_results=2)
        
        if results:
            print(f"✅ 找到 {len(results)} 个结果")
            for i, result in enumerate(results, 1):
                print_result(result, i)
                print(f"   关键词匹配数: {result.get('keyword_matches', 0)}")
        else:
            print("❌ 无结果")

def demo_query_suggestions():
    """演示查询建议"""
    print_header("查询建议演示")
    
    engine = BM25SearchEngine()
    
    # 测试部分查询
    partial_queries = [
        "股票",
        "投资",
        "基金",
        "比特",
        "人工"
    ]
    
    for partial in partial_queries:
        print(f"\n💡 部分查询: '{partial}'")
        
        suggestions = engine.suggest_queries(partial, max_suggestions=3)
        
        if suggestions:
            print("✅ 建议:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"   {i}. {suggestion}")
        else:
            print("❌ 无建议")

def demo_popular_keywords():
    """演示热门关键词"""
    print_header("热门关键词演示")
    
    engine = BM25SearchEngine()
    
    print("\n📊 获取热门关键词...")
    
    popular_keywords = engine.get_popular_keywords(top_k=15)
    
    if popular_keywords:
        print("✅ 热门关键词 (前15个):")
        for i, (keyword, freq) in enumerate(popular_keywords, 1):
            print(f"   {i:2d}. {keyword:<15} ({freq} 次)")
    else:
        print("❌ 无热门关键词")

def demo_search_stats():
    """演示搜索统计"""
    print_header("搜索统计演示")
    
    engine = BM25SearchEngine()
    
    print("\n📈 获取搜索统计信息...")
    
    stats = engine.get_search_stats()
    
    print("✅ 搜索统计:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")

def demo_index_status():
    """演示索引状态"""
    print_header("索引状态演示")
    
    engine = BM25SearchEngine()
    
    print("\n🔍 获取索引状态...")
    
    index_status = engine.get_index_status()
    
    print("✅ 索引状态:")
    for index_type, status in index_status.items():
        if status['built']:
            print(f"   {index_type}: ✅ 已构建")
            if status['last_updated']:
                print(f"     最后更新: {time.ctime(status['last_updated'])}")
        else:
            print(f"   {index_type}: ❌ 未构建")
    
    # 获取分片信息
    shard_info = engine.get_shard_info()
    if shard_info:
        print(f"\n📊 分片信息 (共 {len(shard_info)} 个分片):")
        for shard_id, info in list(shard_info.items())[:10]:  # 只显示前10个分片
            print(f"   分片 {shard_id:2d}: {info['term_count']:4d} 词条")

def demo_performance_test():
    """演示性能测试"""
    print_header("性能测试演示")
    
    engine = BM25SearchEngine()
    
    print("\n⚡ 运行性能测试...")
    
    # 测试查询
    test_queries = [
        "股票投资",
        "基金理财",
        "比特币",
        "金融科技",
        "人工智能",
        "机器学习",
        "区块链",
        "加密货币"
    ]
    
    total_time = 0
    total_results = 0
    
    print("\n查询结果:")
    for query in test_queries:
        start_time = time.time()
        results = engine.search(query, max_results=5)
        search_time = time.time() - start_time
        
        total_time += search_time
        total_results += len(results)
        
        print(f"   '{query}': {len(results):2d} 结果, {search_time:.3f}秒")
    
    avg_time = total_time / len(test_queries)
    avg_results = total_results / len(test_queries)
    
    print(f"\n📊 性能统计:")
    print(f"   平均查询时间: {avg_time:.3f}秒")
    print(f"   平均结果数: {avg_results:.1f}")
    print(f"   总查询时间: {total_time:.3f}秒")

def main():
    """主函数"""
    print("🚀 搜索引擎功能演示")
    print("="*60)
    
    try:
        # 初始化搜索引擎
        print("🔧 初始化搜索引擎...")
        engine = BM25SearchEngine()
        
        # 检查索引状态
        stats = engine.get_search_stats()
        if not stats.get('index_available', False):
            print("❌ BM25索引不可用，请先运行索引构建器")
            print("   运行命令: python indexer/run_indexer.py build --type bm25")
            return
        
        print(f"✅ 搜索引擎初始化成功")
        print(f"   总文档数: {stats.get('total_documents', 0)}")
        print(f"   索引可用: {stats.get('index_available', False)}")
        
        # 运行演示
        demos = [
            ("基础搜索功能", demo_basic_search),
            ("按域名搜索", demo_domain_search),
            ("按关键词搜索", demo_keyword_search),
            ("查询建议", demo_query_suggestions),
            ("热门关键词", demo_popular_keywords),
            ("搜索统计", demo_search_stats),
            ("索引状态", demo_index_status),
            ("性能测试", demo_performance_test),
        ]
        
        for demo_name, demo_func in demos:
            try:
                demo_func()
            except Exception as e:
                print(f"❌ {demo_name} 演示失败: {e}")
        
        print("\n" + "="*60)
        print("🎉 演示完成！")
        print("="*60)
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")

if __name__ == "__main__":
    main()
