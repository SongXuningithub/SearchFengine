#!/usr/bin/env python3
"""
SmartQueue在爬虫中的使用示例（FIFO）
"""

import asyncio
import time
import logging
from crawler import SmartQueue

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def example_crawler_with_smart_queue():
    """使用SmartQueue的爬虫示例"""
    print("=== SmartQueue爬虫示例 ===")
    
    # 创建一个智能队列，最大内存大小为10
    url_queue = SmartQueue(max_memory_size=10, db_path="data/crawler/example_queue.db")
    
    # 模拟一些URL数据
    urls = [
        {"url": "https://example1.com", "domain": "example1.com"},
        {"url": "https://example2.com", "domain": "example2.com"},
        {"url": "https://example3.com", "domain": "example3.com"},
        {"url": "https://example4.com", "domain": "example4.com"},
        {"url": "https://example5.com", "domain": "example5.com"},
        {"url": "https://example6.com", "domain": "example6.com"},
        {"url": "https://example7.com", "domain": "example7.com"},
        {"url": "https://example8.com", "domain": "example8.com"},
        {"url": "https://example9.com", "domain": "example9.com"},
        {"url": "https://example10.com", "domain": "example10.com"},
        {"url": "https://example11.com", "domain": "example11.com"},
        {"url": "https://example12.com", "domain": "example12.com"},
    ]
    
    print(f"添加 {len(urls)} 个URL到队列...")
    for url_data in urls:
        url_queue.put(url_data)
        print(f"添加URL: {url_data['url']}")
    
    # 显示队列统计信息
    stats = url_queue.get_stats()
    print(f"\n队列统计信息:")
    print(f"  内存中URL数量: {stats['memory_size']}")
    print(f"  数据库中URL数量: {stats['database_size']}")
    print(f"  总URL数量: {stats['total_size']}")
    print(f"  内存使用率: {stats['memory_usage_percent']:.1f}%")
    
    # 模拟爬虫处理
    print(f"\n开始模拟爬虫处理...")
    processed_count = 0
    
    while url_queue:
        # 获取下一个URL
        url_data = url_queue.get()
        if url_data:
            processed_count += 1
            print(f"处理URL {processed_count}: {url_data['url']}")
            
            # 模拟爬虫处理时间
            await asyncio.sleep(0.1)
            
            # 模拟发现新URL
            if processed_count % 3 == 0:
                new_url = {
                    "url": f"https://new{processed_count}.com",
                    "domain": f"new{processed_count}.com"
                }
                url_queue.put(new_url)
                print(f"  发现新URL: {new_url['url']}")
            
            # 每处理5个URL显示一次统计信息
            if processed_count % 5 == 0:
                stats = url_queue.get_stats()
                print(f"  当前队列状态: 内存={stats['memory_size']}, 数据库={stats['database_size']}, 总计={stats['total_size']}")
        else:
            break
    
    print(f"\n爬虫处理完成，共处理了 {processed_count} 个URL")

def example_memory_management():
    """内存管理示例"""
    print("\n=== 内存管理示例 ===")
    
    # 创建一个很小的队列来演示内存管理
    queue = SmartQueue(max_memory_size=3, db_path="data/crawler/memory_example.db")
    
    print("添加大量数据到队列，观察内存管理...")
    
    for i in range(10):
        data = {"id": i, "content": f"data_{i}", "timestamp": time.time()}
        queue.put(data)
        print(f"添加数据 {i}")
        
        # 显示当前状态
        stats = queue.get_stats()
        print(f"  内存: {stats['memory_size']}, 数据库: {stats['database_size']}, 总计: {stats['total_size']}")
    
    print("\n从队列中获取数据...")
    retrieved_count = 0
    while queue:
        item = queue.get()
        if item:
            retrieved_count += 1
            print(f"获取数据 {retrieved_count}: ID {item['id']}")
        else:
            break
    
    print(f"共获取了 {retrieved_count} 个数据")

def example_fifo_handling():
    """FIFO处理示例"""
    print("\n=== FIFO处理示例 ===")
    
    queue = SmartQueue(max_memory_size=5, db_path="data/crawler/fifo_example.db")
    
    # 添加数据
    test_data = [
        {"task": "第一个任务", "id": 1},
        {"task": "第二个任务", "id": 2},
        {"task": "第三个任务", "id": 3},
        {"task": "第四个任务", "id": 4},
        {"task": "第五个任务", "id": 5},
    ]
    
    print("按顺序添加任务...")
    for data in test_data:
        queue.put(data)
        print(f"添加任务: {data['task']}")
    
    print("\n按FIFO顺序获取任务...")
    task_count = 0
    while queue:
        task = queue.get()
        if task:
            task_count += 1
            print(f"处理任务 {task_count}: {task['task']}")
        else:
            break

if __name__ == "__main__":
    # 运行示例
    asyncio.run(example_crawler_with_smart_queue())
    example_memory_management()
    example_fifo_handling()
    
    print("\n=== 所有示例完成 ===")
