#!/usr/bin/env python3
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.crawler import BatchCrawler

async def test_crawler():
    print("Testing Batch Crawler...")
    
    # 创建爬虫实例，batch_size=4
    crawler = BatchCrawler(batch_size=4)
    
    try:
        # 爬取少量页面进行测试
        await crawler.start(max_pages=10)
        
        # 获取爬取的数据
        data = crawler.get_crawled_data()
        print(f"Successfully crawled {len(data)} pages")
        
        # 显示前几个结果
        for i, page in enumerate(data[:3]):
            print(f"\nPage {i+1}:")
            print(f"  URL: {page['url']}")
            print(f"  Title: {page['title'][:50]}...")
            print(f"  Keywords: {page['keywords'][:5]}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_crawler())
