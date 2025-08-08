#!/usr/bin/env python3
"""
索引构建命令行工具
"""

import argparse
import sys
import os
import logging
import time
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indexer.index_manager import IndexManager
from config.settings import INDEXER_CONFIG

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_status(manager: IndexManager):
    """打印系统状态"""
    print("\n" + "="*50)
    print("系统状态")
    print("="*50)
    
    # 数据库状态
    db_status = manager.check_database()
    print("\n数据库状态:")
    for key, value in db_status.items():
        if key == 'error':
            print(f"  ❌ 错误: {value}")
        else:
            print(f"  📊 {key}: {value}")
    
    # 索引状态
    index_status = manager.get_index_status()
    print("\n索引状态:")
    for index_type, status in index_status.items():
        if status['built']:
            print(f"  ✅ {index_type}: 已构建")
            if status['last_updated']:
                print(f"    最后更新: {time.ctime(status['last_updated'])}")
        else:
            print(f"  ❌ {index_type}: 未构建")

def build_indexes(manager: IndexManager, args: argparse.Namespace):
    """构建索引"""
    print("\n" + "="*50)
    print("开始构建索引")
    print("="*50)
    
    # 设置参数
    num_shards = args.shards if args.shards else 16
    batch_size = args.batch_size if args.batch_size else 1000
    max_memory = args.max_memory if args.max_memory else 10000
    
    print(f"配置参数:")
    print(f"  分片数量: {num_shards}")
    print(f"  批处理大小: {batch_size}")
    print(f"  最大内存大小: {max_memory}")
    
    # 构建索引
    start_time = time.time()
    
    if args.index_type == "all":
        results = manager.build_all_indexes(
            num_shards=num_shards,
            batch_size=batch_size,
            max_memory_size=max_memory
        )
    elif args.index_type == "basic":
        results = {'basic_index': manager.build_basic_index(
            num_shards=num_shards,
            batch_size=batch_size,
            max_memory_size=max_memory
        )}
    elif args.index_type == "bm25":
        results = {'bm25_index': manager.build_bm25_index(
            num_shards=num_shards,
            batch_size=batch_size,
            max_memory_size=max_memory
        )}
    else:
        print(f"❌ 未知的索引类型: {args.index_type}")
        return
    
    # 显示结果
    total_time = time.time() - start_time
    print(f"\n构建完成 (耗时: {total_time:.2f}秒)")
    
    for index_type, success in results.items():
        if success:
            print(f"  ✅ {index_type}: 构建成功")
        else:
            print(f"  ❌ {index_type}: 构建失败")

def test_search(manager: IndexManager, args: argparse.Namespace):
    """测试搜索功能"""
    print("\n" + "="*50)
    print("测试搜索功能")
    print("="*50)
    
    if not args.query:
        print("❌ 请提供查询字符串")
        return
    
    print(f"查询: '{args.query}'")
    print(f"索引类型: {args.index_type}")
    print(f"最大结果数: {args.max_results}")
    
    # 执行搜索
    results = manager.search(
        query=args.query,
        index_type=args.index_type,
        max_results=args.max_results
    )
    
    if results:
        print(f"\n找到 {len(results)} 个结果:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. 文档 {result['doc_id']}: {result['score']:.4f}")
    else:
        print("\n❌ 没有找到相关结果")

def show_stats(manager: IndexManager, args: argparse.Namespace):
    """显示统计信息"""
    print("\n" + "="*50)
    print("索引统计信息")
    print("="*50)
    
    stats = manager.get_index_stats(args.index_type)
    if stats:
        print(f"\n{args.index_type.upper()} 索引统计:")
        for key, value in stats.items():
            if key != 'doc_lengths':  # 跳过大的字典
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")
    else:
        print(f"❌ 无法获取 {args.index_type} 索引的统计信息")

def show_shard_info(manager: IndexManager, args: argparse.Namespace):
    """显示分片信息"""
    print("\n" + "="*50)
    print("分片信息")
    print("="*50)
    
    shard_info = manager.get_shard_info(args.index_type)
    if shard_info:
        print(f"\n{args.index_type.upper()} 索引分片信息:")
        for shard_id, info in shard_info.items():
            print(f"  分片 {shard_id}:")
            print(f"    内存大小: {info['memory_size']}")
            print(f"    词条数量: {info['term_count']}")
            if 'metadata' in info:
                metadata = info['metadata']
                print(f"    元数据: {metadata}")
    else:
        print(f"❌ 无法获取 {args.index_type} 索引的分片信息")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="搜索引擎索引构建工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 查看系统状态
  python run_indexer.py status
  
  # 构建所有索引
  python run_indexer.py build --type all
  
  # 构建BM25索引
  python run_indexer.py build --type bm25 --shards 32 --batch-size 500
  
  # 测试搜索
  python run_indexer.py search --query "股票投资" --type bm25
  
  # 显示统计信息
  python run_indexer.py stats --type bm25
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 状态命令
    status_parser = subparsers.add_parser('status', help='显示系统状态')
    
    # 构建命令
    build_parser = subparsers.add_parser('build', help='构建索引')
    build_parser.add_argument('--type', choices=['all', 'basic', 'bm25'], 
                            default='all', help='索引类型')
    build_parser.add_argument('--shards', type=int, help='分片数量')
    build_parser.add_argument('--batch-size', type=int, help='批处理大小')
    build_parser.add_argument('--max-memory', type=int, help='最大内存大小')
    
    # 搜索命令
    search_parser = subparsers.add_parser('search', help='测试搜索')
    search_parser.add_argument('--query', required=True, help='查询字符串')
    search_parser.add_argument('--type', choices=['basic', 'bm25'], 
                             default='bm25', help='索引类型')
    search_parser.add_argument('--max-results', type=int, default=10, help='最大结果数')
    
    # 统计命令
    stats_parser = subparsers.add_parser('stats', help='显示统计信息')
    stats_parser.add_argument('--type', choices=['basic', 'bm25'], 
                            default='bm25', help='索引类型')
    
    # 分片信息命令
    shard_parser = subparsers.add_parser('shards', help='显示分片信息')
    shard_parser.add_argument('--type', choices=['basic', 'bm25'], 
                            default='bm25', help='索引类型')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建索引管理器
    try:
        manager = IndexManager(
            db_path="data/crawler/crawler.db",
            index_path="data/indexer"
        )
    except Exception as e:
        print(f"❌ 初始化索引管理器失败: {e}")
        return
    
    # 执行命令
    try:
        if args.command == 'status':
            print_status(manager)
        elif args.command == 'build':
            build_indexes(manager, args)
        elif args.command == 'search':
            test_search(manager, args)
        elif args.command == 'stats':
            show_stats(manager, args)
        elif args.command == 'shards':
            show_shard_info(manager, args)
        else:
            print(f"❌ 未知命令: {args.command}")
            
    except KeyboardInterrupt:
        print("\n⚠️  操作被用户中断")
    except Exception as e:
        print(f"❌ 执行命令时发生错误: {e}")
        logger.exception("Command execution error")

if __name__ == "__main__":
    main()
