#!/usr/bin/env python3
"""
金融搜索引擎演示脚本
展示新的batch爬虫和扩充的URL列表
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import FINANCIAL_SEED_URLS
from crawler.crawler import BatchCrawler

async def demo():
    print("🚀 金融搜索引擎演示")
    print("=" * 50)
    
    print(f"📊 种子URL数量: {len(FINANCIAL_SEED_URLS)}")
    print(f"🌍 覆盖网站类型:")
    
    # 统计网站类型
    categories = {
        '国际主流财经媒体': ['cnbc.com', 'bloomberg.com', 'reuters.com', 'ft.com', 'wsj.com'],
        '专业金融网站': ['investing.com', 'tradingview.com', 'seekingalpha.com'],
        '加密货币': ['cointelegraph.com', 'coindesk.com', 'coingecko.com'],
        '亚洲财经媒体': ['scmp.com', 'straitstimes.com', 'channelnewsasia.com'],
        '欧洲财经媒体': ['handelsblatt.com', 'lesechos.fr', 'expansion.com'],
        '金融科技': ['fintechfutures.com', 'finextra.com', 'bankingtech.com'],
        '宏观经济': ['imf.org', 'worldbank.org', 'oecd.org', 'bis.org'],
        '可持续金融': ['environmental-finance.com', 'responsible-investor.com', 'greenbiz.com']
    }
    
    for category, domains in categories.items():
        count = sum(1 for url in FINANCIAL_SEED_URLS 
                   if any(domain in url for domain in domains))
        if count > 0:
            print(f"   • {category}: {count} 个网站")
    
    print("\n🔧 技术特性:")
    print("   • Batch处理模式 (默认8个URL并发)")
    print("   • SQLite数据库存储")
    print("   • 智能金融内容识别")
    print("   • 支持中英文混合内容")
    
    print("\n📈 支持的金融领域:")
    print("   • 股票、债券、基金、期货、期权")
    print("   • 外汇、黄金、原油、大宗商品")
    print("   • 加密货币、区块链、DeFi")
    print("   • 金融科技、数字银行")
    print("   • ESG、可持续金融")
    print("   • 新兴市场、宏观经济")
    
    print("\n🎯 使用示例:")
    print("   # 启动爬虫 (batch_size=8)")
    print("   python -m crawler.main --max-pages 100 --batch-size 8")
    print("   ")
    print("   # 启动索引器")
    print("   python -m indexer.main")
    print("   ")
    print("   # 启动搜索引擎")
    print("   python -m engine.main")
    print("   ")
    print("   # 启动前端")
    print("   python -m frontend.app")
    
    print("\n✨ 一键启动:")
    print("   ./start.sh")
    
    print("\n" + "=" * 50)
    print("🎉 演示完成！")

if __name__ == "__main__":
    asyncio.run(demo())
