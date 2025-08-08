#!/usr/bin/env python3
"""
搜索引擎测试脚本
"""

import sys
import os
import time
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.search_engine import BM25SearchEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_search_engine_initialization():
    """测试搜索引擎初始化"""
    print("🔍 测试搜索引擎初始化...")
    
    try:
        engine = BM25SearchEngine()
        
        # 获取搜索统计信息
        stats = engine.get_search_stats()
        
        print("✅ 搜索引擎初始化成功")
        print(f"   总文档数: {stats.get('total_documents', 0)}")
        print(f"   平均文档长度: {stats.get('avg_doc_length', 0):.0f}")
        print(f"   索引可用: {stats.get('index_available', False)}")
        
        if stats.get('index_available'):
            print(f"   总词条数: {stats.get('total_terms', 0)}")
            print(f"   总倒排列表项: {stats.get('total_postings', 0)}")
            print(f"   索引构建时间: {stats.get('processing_time', 0):.2f}秒")
        
        return True
        
    except Exception as e:
        print(f"❌ 搜索引擎初始化失败: {e}")
        return False

def test_basic_search():
    """测试基础搜索功能"""
    print("\n🔍 测试基础搜索功能...")
    
    try:
        engine = BM25SearchEngine()
        
        # 测试查询
        test_queries = ["股票", "投资", "基金", "比特币", "金融"]
        
        for query in test_queries:
            print(f"\n   查询: '{query}'")
            
            start_time = time.time()
            results = engine.search(query, max_results=5)
            search_time = time.time() - start_time
            
            if results:
                print(f"   找到 {len(results)} 个结果 (耗时: {search_time:.3f}秒)")
                for i, result in enumerate(results[:3], 1):
                    print(f"     {i}. {result.get('title', 'N/A')}")
                    print(f"        分数: {result.get('score', 0):.4f}")
                    print(f"        域名: {result.get('domain', 'N/A')}")
            else:
                print("   无结果")
        
        print("✅ 基础搜索功能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 基础搜索功能测试失败: {e}")
        return False

def test_domain_search():
    """测试按域名搜索"""
    print("\n🔍 测试按域名搜索...")
    
    try:
        engine = BM25SearchEngine()
        
        # 测试域名
        test_domains = ["cnbc.com", "bloomberg.com", "reuters.com"]
        
        for domain in test_domains:
            print(f"\n   域名: '{domain}'")
            
            results = engine.search_by_domain(domain, max_results=3)
            
            if results:
                print(f"   找到 {len(results)} 个结果")
                for i, result in enumerate(results[:2], 1):
                    print(f"     {i}. {result.get('title', 'N/A')}")
                    print(f"        URL: {result.get('url', 'N/A')}")
            else:
                print("   无结果")
        
        print("✅ 按域名搜索测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 按域名搜索测试失败: {e}")
        return False

def test_keyword_search():
    """测试按关键词搜索"""
    print("\n🔍 测试按关键词搜索...")
    
    try:
        engine = BM25SearchEngine()
        
        # 测试关键词
        test_keywords = [["股票", "投资"], ["基金", "理财"], ["比特币", "加密货币"]]
        
        for keywords in test_keywords:
            print(f"\n   关键词: {keywords}")
            
            results = engine.search_by_keywords(keywords, max_results=3)
            
            if results:
                print(f"   找到 {len(results)} 个结果")
                for i, result in enumerate(results[:2], 1):
                    print(f"     {i}. {result.get('title', 'N/A')}")
                    print(f"        匹配数: {result.get('keyword_matches', 0)}")
            else:
                print("   无结果")
        
        print("✅ 按关键词搜索测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 按关键词搜索测试失败: {e}")
        return False

def test_query_suggestions():
    """测试查询建议"""
    print("\n🔍 测试查询建议...")
    
    try:
        engine = BM25SearchEngine()
        
        # 测试部分查询
        test_partials = ["股票", "投资", "基金", "比特"]
        
        for partial in test_partials:
            print(f"\n   部分查询: '{partial}'")
            
            suggestions = engine.suggest_queries(partial, max_suggestions=3)
            
            if suggestions:
                print(f"   建议: {suggestions}")
            else:
                print("   无建议")
        
        print("✅ 查询建议测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 查询建议测试失败: {e}")
        return False

def test_popular_keywords():
    """测试热门关键词"""
    print("\n🔍 测试热门关键词...")
    
    try:
        engine = BM25SearchEngine()
        
        # 获取热门关键词
        popular_keywords = engine.get_popular_keywords(top_k=10)
        
        if popular_keywords:
            print("✅ 热门关键词:")
            for i, (keyword, freq) in enumerate(popular_keywords[:5], 1):
                print(f"   {i}. {keyword}: {freq} 次")
        else:
            print("   无热门关键词")
        
        print("✅ 热门关键词测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 热门关键词测试失败: {e}")
        return False

def test_index_status():
    """测试索引状态"""
    print("\n🔍 测试索引状态...")
    
    try:
        engine = BM25SearchEngine()
        
        # 获取索引状态
        index_status = engine.get_index_status()
        
        print("✅ 索引状态:")
        for index_type, status in index_status.items():
            if status['built']:
                print(f"   {index_type}: 已构建")
                if status['last_updated']:
                    print(f"     最后更新: {time.ctime(status['last_updated'])}")
            else:
                print(f"   {index_type}: 未构建")
        
        # 获取分片信息
        shard_info = engine.get_shard_info()
        if shard_info:
            print("\n   分片信息:")
            for shard_id, info in list(shard_info.items())[:5]:  # 只显示前5个分片
                print(f"     分片 {shard_id}: {info['term_count']} 词条")
        
        print("✅ 索引状态测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 索引状态测试失败: {e}")
        return False

def run_performance_test():
    """运行性能测试"""
    print("\n🔍 运行性能测试...")
    
    try:
        engine = BM25SearchEngine()
        
        # 测试查询
        test_queries = ["股票投资", "基金理财", "比特币", "金融科技", "人工智能"]
        
        total_time = 0
        total_results = 0
        
        for query in test_queries:
            start_time = time.time()
            results = engine.search(query, max_results=10)
            search_time = time.time() - start_time
            
            total_time += search_time
            total_results += len(results)
            
            print(f"   查询 '{query}': {len(results)} 结果, {search_time:.3f}秒")
        
        avg_time = total_time / len(test_queries)
        avg_results = total_results / len(test_queries)
        
        print(f"\n   平均查询时间: {avg_time:.3f}秒")
        print(f"   平均结果数: {avg_results:.1f}")
        
        print("✅ 性能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始搜索引擎测试")
    print("="*50)
    
    tests = [
        ("搜索引擎初始化", test_search_engine_initialization),
        ("基础搜索功能", test_basic_search),
        ("按域名搜索", test_domain_search),
        ("按关键词搜索", test_keyword_search),
        ("查询建议", test_query_suggestions),
        ("热门关键词", test_popular_keywords),
        ("索引状态", test_index_status),
        ("性能测试", run_performance_test),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n" + "="*50)
    print("测试结果汇总")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        if success:
            print(f"✅ {test_name}: 通过")
            passed += 1
        else:
            print(f"❌ {test_name}: 失败")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！搜索引擎工作正常")
        return True
    else:
        print("⚠️  部分测试失败，请检查系统配置")
        return False

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
搜索引擎测试工具

用法:
  python test_search_engine.py              # 运行所有测试
  python test_search_engine.py --help       # 显示帮助信息

测试项目:
  - 搜索引擎初始化测试
  - 基础搜索功能测试
  - 按域名搜索测试
  - 按关键词搜索测试
  - 查询建议测试
  - 热门关键词测试
  - 索引状态测试
  - 性能测试
        """)
        return
    
    success = run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
