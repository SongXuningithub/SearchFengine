#!/usr/bin/env python3
"""
SmartQueue测试文件
演示智能队列的使用方法（FIFO）
"""

import asyncio
import time
import logging
from crawler import SmartQueue

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_smart_queue_basic():
    """测试SmartQueue的基本功能"""
    print("=== 测试SmartQueue基本功能 ===")
    
    # 创建一个最大内存大小为5的队列
    queue = SmartQueue(max_memory_size=5, db_path="data/crawler/test_smart_queue.db")
    
    # 添加一些测试数据
    test_data = [
        {"id": 1, "name": "Alice", "age": 25},
        {"id": 2, "name": "Bob", "age": 30},
        {"id": 3, "name": "Charlie", "age": 35},
        {"id": 4, "name": "David", "age": 40},
        {"id": 5, "name": "Eve", "age": 45},
        {"id": 6, "name": "Frank", "age": 50},
        {"id": 7, "name": "Grace", "age": 55},
        {"id": 8, "name": "Henry", "age": 60},
    ]
    
    print(f"添加 {len(test_data)} 个元素到队列...")
    for i, data in enumerate(test_data):
        queue.put(data)
        print(f"添加元素 {i+1}: {data['name']}")
    
    # 显示队列统计信息
    stats = queue.get_stats()
    print(f"\n队列统计信息:")
    print(f"  内存中元素数量: {stats['memory_size']}")
    print(f"  数据库中元素数量: {stats['database_size']}")
    print(f"  总元素数量: {stats['total_size']}")
    print(f"  内存使用率: {stats['memory_usage_percent']:.1f}%")
    
    # 从队列中获取元素（FIFO）
    print(f"\n从队列中获取元素（FIFO）:")
    for i in range(len(test_data)):
        item = queue.get()
        if item:
            print(f"获取元素 {i+1}: {item['name']}")
        else:
            print(f"队列为空，无法获取元素 {i+1}")
    
    # 再次显示统计信息
    stats = queue.get_stats()
    print(f"\n获取后的队列统计信息:")
    print(f"  内存中元素数量: {stats['memory_size']}")
    print(f"  数据库中元素数量: {stats['database_size']}")
    print(f"  总元素数量: {stats['total_size']}")

def test_smart_queue_fifo():
    """测试SmartQueue的FIFO功能"""
    print("\n=== 测试SmartQueue FIFO功能 ===")
    
    queue = SmartQueue(max_memory_size=10, db_path="data/crawler/test_fifo_queue.db")
    
    # 添加数据
    test_data = [{"id": i, "name": f"item_{i}"} for i in range(100)]
    
    print("按顺序添加数据...")
    for data in test_data:
        queue.put(data)
        print(f"添加: {data['name']}")
    
    # 按FIFO顺序获取元素
    print("\n按FIFO顺序获取元素:")
    for i in range(len(test_data)):
        item = queue.get()
        if item:
            print(f"获取元素 {i+1}: {item['name']}")
        else:
            print(f"队列为空，无法获取元素 {i+1}")

def test_smart_queue_performance():
    """测试SmartQueue的性能"""
    print("\n=== 测试SmartQueue性能 ===")
    
    queue = SmartQueue(max_memory_size=100, db_path="data/crawler/test_performance_queue.db")
    
    # 测试大量数据的添加和获取
    num_items = 1000
    print(f"测试 {num_items} 个元素的添加和获取性能...")
    
    # 添加数据
    start_time = time.time()
    for i in range(num_items):
        queue.put({"id": i, "data": f"item_{i}"})
    
    add_time = time.time() - start_time
    print(f"添加 {num_items} 个元素耗时: {add_time:.3f} 秒")
    
    # 获取数据
    start_time = time.time()
    retrieved_count = 0
    for i in range(num_items):
        item = queue.get()
        if item:
            retrieved_count += 1
    
    get_time = time.time() - start_time
    print(f"获取 {retrieved_count} 个元素耗时: {get_time:.3f} 秒")
    
    # 显示统计信息
    stats = queue.get_stats()
    print(f"最终队列统计: 内存={stats['memory_size']}, 数据库={stats['database_size']}, 总计={stats['total_size']}")

def test_smart_queue_edge_cases():
    """测试SmartQueue的边界情况"""
    print("\n=== 测试SmartQueue边界情况 ===")
    
    queue = SmartQueue(max_memory_size=2, db_path="data/crawler/test_edge_cases_queue.db")
    
    # 测试空队列
    print("测试空队列:")
    item = queue.get()
    print(f"从空队列获取: {item}")
    
    # 测试peek功能
    print("\n测试peek功能:")
    queue.put({"test": "peek1"})
    queue.put({"test": "peek2"})
    
    peek_item = queue.peek()
    print(f"Peek结果: {peek_item}")
    
    # 验证peek没有移除元素
    stats = queue.get_stats()
    print(f"Peek后队列大小: {stats['total_size']}")
    
    # 测试clear功能
    print("\n测试clear功能:")
    queue.clear()
    stats = queue.get_stats()
    print(f"Clear后队列大小: {stats['total_size']}")

if __name__ == "__main__":
    # 运行所有测试
    # test_smart_queue_basic()
    # test_smart_queue_fifo()
    test_smart_queue_performance()
    # test_smart_queue_edge_cases()
    
    print("\n=== 所有测试完成 ===")
