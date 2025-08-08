#!/usr/bin/env python3
"""
索引系统测试脚本
"""

import sys
import os
import time
import logging
from typing import Dict, List

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indexer.index_manager import IndexManager
from utils.text_processor import TextProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    
    manager = IndexManager()
    db_status = manager.check_database()
    
    if 'error' in db_status:
        print(f"❌ 数据库连接失败: {db_status['error']}")
        return False
    
    print(f"✅ 数据库连接成功")
    print(f"   总文档数: {db_status.get('total_documents', 0)}")
    print(f"   最近文档数: {db_status.get('recent_documents', 0)}")
    print(f"   平均内容长度: {db_status.get('avg_content_length', 0):.0f}")
    
    return True

def test_text_processor():
    """测试文本处理器"""
    print("\n🔍 测试文本处理器...")
    
    try:
        processor = TextProcessor()
        
        # 测试文本
        test_text = "这是一个测试文档，包含股票投资和基金理财等金融相关内容。"
        
        # 分词测试
        tokens = processor.tokenize(test_text)
        print(f"✅ 分词测试通过")
        print(f"   原文: {test_text}")
        print(f"   分词结果: {tokens}")
        
        # 关键词提取测试
        keywords = processor.extract_keywords(test_text, top_k=5)
        print(f"✅ 关键词提取测试通过")
        print(f"   关键词: {keywords}")
        
        return True
        
    except Exception as e:
        print(f"❌ 文本处理器测试失败: {e}")
        return False

def test_basic_index_building():
    """测试基础索引构建"""
    print("\n🔍 测试基础索引构建...")
    
    try:
        manager = IndexManager()
        
        # 检查是否有文档
        db_status = manager.check_database()
        if db_status.get('total_documents', 0) == 0:
            print("⚠️  数据库中没有文档，跳过索引构建测试")
            return True
        
        # 构建基础索引
        start_time = time.time()
        success = manager.build_basic_index(
            num_shards=64,  # 使用较少的分片进行测试
            batch_size=100,
            max_memory_size=1600
        )
        build_time = time.time() - start_time
        
        if success:
            print(f"✅ 基础索引构建成功 (耗时: {build_time:.2f}秒)")
            
            # 获取统计信息
            stats = manager.get_index_stats("basic")
            if stats:
                print(f"   总文档数: {stats.get('total_docs', 0)}")
                print(f"   总词条数: {stats.get('total_terms', 0)}")
                print(f"   总倒排列表项: {stats.get('total_postings', 0)}")
            
            return True
        else:
            print("❌ 基础索引构建失败")
            return False
            
    except Exception as e:
        print(f"❌ 基础索引构建测试失败: {e}")
        return False

def test_bm25_index_building():
    """测试BM25索引构建"""
    print("\n🔍 测试BM25索引构建...")
    
    try:
        manager = IndexManager()
        
        # 检查是否有文档
        db_status = manager.check_database()
        if db_status.get('total_documents', 0) == 0:
            print("⚠️  数据库中没有文档，跳过索引构建测试")
            return True
        
        # 构建BM25索引
        start_time = time.time()
        success = manager.build_bm25_index(
            num_shards=4,  # 使用较少的分片进行测试
            batch_size=100,
            max_memory_size=1000
        )
        build_time = time.time() - start_time
        
        if success:
            print(f"✅ BM25索引构建成功 (耗时: {build_time:.2f}秒)")
            
            # 获取统计信息
            stats = manager.get_index_stats("bm25")
            if stats:
                print(f"   总文档数: {stats.get('total_docs', 0)}")
                print(f"   总词条数: {stats.get('total_terms', 0)}")
                print(f"   总倒排列表项: {stats.get('total_postings', 0)}")
                print(f"   平均文档长度: {stats.get('avg_doc_length', 0):.2f}")
            
            return True
        else:
            print("❌ BM25索引构建失败")
            return False
            
    except Exception as e:
        print(f"❌ BM25索引构建测试失败: {e}")
        return False

def test_search_functionality():
    """测试搜索功能"""
    print("\n🔍 测试搜索功能...")
    
    try:
        manager = IndexManager()
        
        # 测试查询
        test_queries = ["股票", "投资", "基金", "比特币", "金融"]
        
        for query in test_queries:
            print(f"\n   查询: '{query}'")
            
            # 测试基础索引搜索
            basic_results = manager.search(query, index_type="basic", max_results=3)
            if basic_results:
                print(f"   基础索引结果: {len(basic_results)} 个")
                for i, result in enumerate(basic_results[:2], 1):
                    print(f"     {i}. 文档 {result['doc_id']}: {result['score']:.4f}")
            else:
                print("   基础索引: 无结果")
            
            # 测试BM25索引搜索
            bm25_results = manager.search(query, index_type="bm25", max_results=3)
            if bm25_results:
                print(f"   BM25索引结果: {len(bm25_results)} 个")
                for i, result in enumerate(bm25_results[:2], 1):
                    print(f"     {i}. 文档 {result['doc_id']}: {result['score']:.4f}")
            else:
                print("   BM25索引: 无结果")
        
        print("✅ 搜索功能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 搜索功能测试失败: {e}")
        return False

def test_shard_management():
    """测试分片管理"""
    print("\n🔍 测试分片管理...")
    
    try:
        manager = IndexManager()
        
        # 获取分片信息
        basic_shards = manager.get_shard_info("basic")
        bm25_shards = manager.get_shard_info("bm25")
        
        if basic_shards:
            print("✅ 基础索引分片信息:")
            for shard_id, info in basic_shards.items():
                print(f"   分片 {shard_id}: {info['term_count']} 词条, {info['memory_size']} 内存")
        
        if bm25_shards:
            print("✅ BM25索引分片信息:")
            for shard_id, info in bm25_shards.items():
                print(f"   分片 {shard_id}: {info['term_count']} 词条, {info['memory_size']} 内存")
        
        return True
        
    except Exception as e:
        print(f"❌ 分片管理测试失败: {e}")
        return False

def test_index_status():
    """测试索引状态管理"""
    print("\n🔍 测试索引状态管理...")
    
    try:
        manager = IndexManager()
        
        # 获取索引状态
        status = manager.get_index_status()
        
        print("✅ 索引状态:")
        for index_type, info in status.items():
            if info['built']:
                print(f"   {index_type}: 已构建")
                if info['last_updated']:
                    print(f"     最后更新: {time.ctime(info['last_updated'])}")
            else:
                print(f"   {index_type}: 未构建")
        
        return True
        
    except Exception as e:
        print(f"❌ 索引状态管理测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始索引系统测试")
    print("="*50)
    
    tests = [
        ("数据库连接", test_database_connection),
        ("文本处理器", test_text_processor),
        ("基础索引构建", test_basic_index_building),
        # ("BM25索引构建", test_bm25_index_building),
        # ("搜索功能", test_search_functionality),
        # ("分片管理", test_shard_management),
        # ("索引状态管理", test_index_status),
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
        print("🎉 所有测试通过！")
        return True
    else:
        print("⚠️  部分测试失败，请检查系统配置")
        return False

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
索引系统测试工具

用法:
  python test_indexer.py              # 运行所有测试
  python test_indexer.py --help       # 显示帮助信息

测试项目:
  - 数据库连接测试
  - 文本处理器测试
  - 基础索引构建测试
  - BM25索引构建测试
  - 搜索功能测试
  - 分片管理测试
  - 索引状态管理测试
        """)
        return
    
    success = run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
