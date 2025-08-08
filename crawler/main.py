import asyncio
import argparse
import logging
from crawler.crawler import BatchCrawler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    parser = argparse.ArgumentParser(description='Financial Information Batch Crawler')
    parser.add_argument('--max-pages', type=int, default=10000, 
                       help='Maximum number of pages to crawl')
    parser.add_argument('--batch-size', type=int, default=8,
                       help='Batch size for concurrent crawling')
    
    args = parser.parse_args()
    
    # 创建批量爬虫实例
    crawler = BatchCrawler(batch_size=args.batch_size)
    
    try:
        # 启动爬虫
        await crawler.start(max_pages=args.max_pages)
    except KeyboardInterrupt:
        logging.info("Crawler interrupted by user")
    except Exception as e:
        logging.error(f"Crawler error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 