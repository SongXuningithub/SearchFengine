#!/usr/bin/env python3
"""
搜索引擎演示脚本
展示完整的搜索工作流程
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indexer.inverted_index import InvertedIndexBuilder
from engine.search_engine import SearchEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demo_search_workflow():
    """演示搜索引擎的完整工作流程"""
    
    print("=" * 60)
    print("搜索引擎演示")
    print("=" * 60)
    
    # 检查必要文件
    db_path = "data/crawler/crawler.db"
    index_path = "data/indexer"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        print("请先运行爬虫收集数据")
        return
    
    if not os.path.exists(index_path):
        print(f"❌ 索引目录不存在: {index_path}")
        print("请先构建倒排索引")
        return
    
    print("✅ 检查文件完成")
    
    try:
        # 1. 加载倒排索引
        print("\n1. 加载倒排索引...")
        index_builder = InvertedIndexBuilder(
            db_path=db_path,
            index_path=index_path,
            num_shards=16
        )
        print("✅ 倒排索引加载完成")
        
        # 2. 初始化搜索引擎
        print("\n2. 初始化搜索引擎...")
        search_engine = SearchEngine(index_builder, db_path)
        
        # 显示统计信息
        stats = search_engine.get_search_stats()
        print(f"✅ 搜索引擎初始化完成")
        print(f"   - 总文档数: {stats['total_docs']}")
        print(f"   - 平均文档长度: {stats['avg_doc_length']:.2f}")
        print(f"   - BM25参数: k1={stats['bm25_k1']}, b={stats['bm25_b']}")
        
        # 3. 演示搜索功能
        print("\n3. 演示搜索功能...")
        
        # 测试查询
        test_queries = [
            "股票",
            "投资理财",
            "人工智能",
            "区块链技术",
            "金融科技"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- 测试查询 {i}: '{query}' ---")
            
            # 分词演示
            tokens = search_engine.tokenize_query(query)
            print(f"分词结果: {tokens}")
            
            # 执行搜索
            results = search_engine.search(query, max_results=3)
            
            if results:
                print(f"找到 {len(results)} 个结果:")
                for j, result in enumerate(results, 1):
                    print(f"  {j}. {result['title']}")
                    print(f"     分数: {result['score']:.3f}")
                    print(f"     URL: {result['url']}")
                    print(f"     预览: {result['content_preview'][:80]}...")
            else:
                print("未找到结果，尝试OR搜索...")
                or_results = search_engine.search_with_fallback(query, max_results=2)
                if or_results:
                    print(f"OR搜索找到 {len(or_results)} 个结果:")
                    for j, result in enumerate(or_results, 1):
                        print(f"  {j}. {result['title']}")
                        print(f"     分数: {result['score']:.3f}")
                else:
                    print("仍然没有找到结果")
        
        print("\n" + "=" * 60)
        print("演示完成！")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

def demo_interactive_search():
    """交互式搜索演示"""
    
    print("=" * 60)
    print("交互式搜索演示")
    print("输入查询词进行搜索，输入 'quit' 退出")
    print("=" * 60)
    
    # 检查必要文件
    db_path = "data/crawler/crawler.db"
    index_path = "data/indexer"
    
    if not os.path.exists(db_path) or not os.path.exists(index_path):
        print("❌ 缺少必要文件，请先运行爬虫和索引构建")
        return
    
    try:
        # 初始化搜索引擎
        print("正在初始化搜索引擎...")
        index_builder = InvertedIndexBuilder(
            db_path=db_path,
            index_path=index_path,
            num_shards=16
        )
        search_engine = SearchEngine(index_builder, db_path)
        print("✅ 搜索引擎初始化完成")
        
        # 交互式搜索
        while True:
            try:
                query = input("\n请输入搜索查询: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("再见！")
                    break
                
                if not query:
                    print("请输入有效的查询词")
                    continue
                
                print(f"\n正在搜索: '{query}'")
                
                # 执行搜索
                results = search_engine.search(query, max_results=5)
                
                if results:
                    print(f"\n找到 {len(results)} 个结果:")
                    for i, result in enumerate(results, 1):
                        print(f"\n{i}. {result['title']}")
                        print(f"   分数: {result['score']:.3f}")
                        print(f"   URL: {result['url']}")
                        print(f"   预览: {result['content_preview'][:120]}...")
                else:
                    print("未找到结果，尝试OR搜索...")
                    or_results = search_engine.search_with_fallback(query, max_results=3)
                    if or_results:
                        print(f"OR搜索找到 {len(or_results)} 个结果:")
                        for i, result in enumerate(or_results, 1):
                            print(f"\n{i}. {result['title']}")
                            print(f"   分数: {result['score']:.3f}")
                            print(f"   URL: {result['url']}")
                    else:
                        print("没有找到相关结果")
                        
            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                print(f"搜索过程中出现错误: {e}")
        
    except Exception as e:
        logger.error(f"初始化搜索引擎时出现错误: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="搜索引擎演示")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="运行交互式搜索模式")
    
    args = parser.parse_args()
    
    if args.interactive:
        demo_interactive_search()
    else:
        demo_search_workflow()
