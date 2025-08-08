#!/usr/bin/env python3
"""
搜索引擎测试脚本
演示如何使用SearchEngine类进行搜索
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.index_adapter import AdaptedInvertedIndexBuilder
from engine.search_engine import SearchEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_search_engine():
    """测试搜索引擎"""
    
    # 检查索引是否存在
    index_path = "data/indexer"
    if not os.path.exists(index_path):
        logger.error(f"Index path {index_path} does not exist. Please build the index first.")
        return
    
    # 检查数据库是否存在
    db_path = "data/crawler/crawler.db"
    if not os.path.exists(db_path):
        logger.error(f"Database {db_path} does not exist. Please run crawler first.")
        return
    
    try:
        # 创建适配后的索引构建器
        logger.info("Loading inverted index...")
        index_builder = AdaptedInvertedIndexBuilder(
            index_path=index_path,
            num_shards=64
        )

        postings = index_builder.get_posting("中国")
        print(f"找到 {len(postings)} 个posting")
        for posting in postings[:3]:
            print(f"  doc_id: {posting.doc_id}, tf: {posting.tf}")
        return
    
        # 创建搜索引擎
        logger.info("Initializing search engine...")
        search_engine = SearchEngine(index_builder, db_path)
        
        # 打印搜索统计信息
        stats = search_engine.get_search_stats()
        logger.info(f"Search engine stats: {stats}")
        
        # 测试查询
        test_queries = [
            "股票",
            "投资",
            "基金",
            "比特币",
            "人工智能",
            "区块链",
            "金融科技",
            "市场分析",
            "经济政策",
            "科技股"
        ]
        
        logger.info("Starting search tests...")
        
        for query in test_queries:
            logger.info(f"\n{'='*50}")
            logger.info(f"Testing query: '{query}'")
            
            # 执行搜索
            results = search_engine.search(query, max_results=5)
            
            if results:
                logger.info(f"Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    logger.info(f"{i}. {result['title']} (Score: {result['score']:.3f})")
                    logger.info(f"   URL: {result['url']}")
                    logger.info(f"   Preview: {result['content_preview'][:100]}...")
            else:
                logger.info("No results found")
                
                # 尝试OR搜索
                logger.info("Trying OR search...")
                or_results = search_engine.search_with_fallback(query, max_results=3)
                if or_results:
                    logger.info(f"OR search found {len(or_results)} results:")
                    for i, result in enumerate(or_results, 1):
                        logger.info(f"{i}. {result['title']} (Score: {result['score']:.3f})")
                else:
                    logger.info("No results found even with OR search")
        
        logger.info(f"\n{'='*50}")
        logger.info("Search engine test completed!")
        
    except Exception as e:
        logger.error(f"Error testing search engine: {e}")
        import traceback
        traceback.print_exc()

def interactive_search():
    """交互式搜索"""
    
    # 检查索引是否存在
    index_path = "data/indexer"
    if not os.path.exists(index_path):
        logger.error(f"Index path {index_path} does not exist. Please build the index first.")
        return
    
    # 检查数据库是否存在
    db_path = "data/crawler/crawler.db"
    if not os.path.exists(db_path):
        logger.error(f"Database {db_path} does not exist. Please run crawler first.")
        return
    
    try:
        # 创建索引构建器
        logger.info("Loading inverted index...")
        index_builder = InvertedIndexBuilder(
            db_path=db_path,
            index_path=index_path,
            num_shards=16,
            batch_size=1000,
            max_memory_size=10000
        )
        
        # 创建搜索引擎
        logger.info("Initializing search engine...")
        search_engine = SearchEngine(index_builder, db_path)
        
        logger.info("Interactive search mode. Type 'quit' to exit.")
        
        while True:
            try:
                query = input("\nEnter search query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not query:
                    continue
                
                # 执行搜索
                results = search_engine.search(query, max_results=10)
                
                if results:
                    print(f"\nFound {len(results)} results:")
                    for i, result in enumerate(results, 1):
                        print(f"\n{i}. {result['title']}")
                        print(f"   Score: {result['score']:.3f}")
                        print(f"   URL: {result['url']}")
                        print(f"   Preview: {result['content_preview'][:150]}...")
                else:
                    print("No results found.")
                    
                    # 尝试OR搜索
                    print("Trying OR search...")
                    or_results = search_engine.search_with_fallback(query, max_results=5)
                    if or_results:
                        print(f"OR search found {len(or_results)} results:")
                        for i, result in enumerate(or_results, 1):
                            print(f"\n{i}. {result['title']}")
                            print(f"   Score: {result['score']:.3f}")
                            print(f"   URL: {result['url']}")
                    else:
                        print("No results found even with OR search.")
                        
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                logger.error(f"Error during search: {e}")
        
    except Exception as e:
        logger.error(f"Error initializing search engine: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Search Engine Test")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_search()
    else:
        test_search_engine()
