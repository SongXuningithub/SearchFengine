#!/usr/bin/env python3
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import FINANCIAL_SEED_URLS

def test_urls():
    print("Financial Seed URLs:")
    print("=" * 50)
    
    categories = {}
    for url in FINANCIAL_SEED_URLS:
        domain = url.split('/')[2]  # 提取域名
        if 'cnbc.com' in domain:
            category = 'CNBC'
        elif 'bloomberg.com' in domain:
            category = 'Bloomberg'
        elif 'reuters.com' in domain:
            category = 'Reuters'
        elif 'ft.com' in domain:
            category = 'Financial Times'
        elif 'wsj.com' in domain:
            category = 'Wall Street Journal'
        elif 'economist.com' in domain:
            category = 'The Economist'
        elif 'bbc.com' in domain:
            category = 'BBC'
        elif 'yahoo.com' in domain:
            category = 'Yahoo Finance'
        elif 'marketwatch.com' in domain:
            category = 'MarketWatch'
        elif 'forbes.com' in domain:
            category = 'Forbes'
        elif 'businessinsider.com' in domain:
            category = 'Business Insider'
        elif 'investing.com' in domain:
            category = 'Investing.com'
        elif 'fxstreet.com' in domain:
            category = 'FXStreet'
        elif 'forexfactory.com' in domain:
            category = 'Forex Factory'
        elif 'tradingview.com' in domain:
            category = 'TradingView'
        elif 'seekingalpha.com' in domain:
            category = 'Seeking Alpha'
        elif 'fool.com' in domain:
            category = 'The Motley Fool'
        elif 'morningstar.com' in domain:
            category = 'Morningstar'
        elif 'zacks.com' in domain:
            category = 'Zacks'
        elif 'cointelegraph.com' in domain:
            category = 'Cointelegraph'
        elif 'coindesk.com' in domain:
            category = 'CoinDesk'
        elif 'coingecko.com' in domain:
            category = 'CoinGecko'
        elif 'cryptonews.com' in domain:
            category = 'CryptoNews'
        elif 'scmp.com' in domain:
            category = 'South China Morning Post'
        elif 'straitstimes.com' in domain:
            category = 'The Straits Times'
        elif 'channelnewsasia.com' in domain:
            category = 'Channel News Asia'
        elif 'todayonline.com' in domain:
            category = 'Today Online'
        elif 'handelsblatt.com' in domain:
            category = 'Handelsblatt'
        elif 'lesechos.fr' in domain:
            category = 'Les Echos'
        elif 'expansion.com' in domain:
            category = 'Expansion'
        elif 'ilsole24ore.com' in domain:
            category = 'Il Sole 24 Ore'
        elif 'barrons.com' in domain:
            category = 'Barron\'s'
        elif 'investors.com' in domain:
            category = 'Investor\'s Business Daily'
        elif 'money.cnn.com' in domain:
            category = 'CNN Money'
        elif 'usatoday.com' in domain:
            category = 'USA Today Money'
        elif 'nbcnews.com' in domain:
            category = 'NBC News Business'
        elif 'cbsnews.com' in domain:
            category = 'CBS MoneyWatch'
        elif 'fintechfutures.com' in domain:
            category = 'FinTech Futures'
        elif 'finextra.com' in domain:
            category = 'Finextra'
        elif 'bankingtech.com' in domain:
            category = 'Banking Technology'
        elif 'imf.org' in domain:
            category = 'IMF'
        elif 'worldbank.org' in domain:
            category = 'World Bank'
        elif 'oecd.org' in domain:
            category = 'OECD'
        elif 'bis.org' in domain:
            category = 'BIS'
        elif 'spglobal.com' in domain:
            category = 'S&P Global'
        elif 'refinitiv.com' in domain:
            category = 'Refinitiv'
        elif 'factset.com' in domain:
            category = 'FactSet'
        elif 'moodys.com' in domain:
            category = 'Moody\'s'
        elif 'fitchratings.com' in domain:
            category = 'Fitch Ratings'
        elif 'insurancejournal.com' in domain:
            category = 'Insurance Journal'
        elif 'thinkadvisor.com' in domain:
            category = 'ThinkAdvisor'
        elif 'investmentnews.com' in domain:
            category = 'InvestmentNews'
        elif 'wealthmanagement.com' in domain:
            category = 'Wealth Management'
        elif 'fa-mag.com' in domain:
            category = 'Financial Advisor'
        elif 'emergingmarkets.com' in domain:
            category = 'Emerging Markets'
        elif 'frontiermarkets.com' in domain:
            category = 'Frontier Markets'
        elif 'africanbusiness.com' in domain:
            category = 'African Business'
        elif 'latinfinance.com' in domain:
            category = 'Latin Finance'
        elif 'environmental-finance.com' in domain:
            category = 'Environmental Finance'
        elif 'responsible-investor.com' in domain:
            category = 'Responsible Investor'
        elif 'greenbiz.com' in domain:
            category = 'GreenBiz'
        elif 'esginvestor.net' in domain:
            category = 'ESG Investor'
        else:
            category = 'Other'
        
        if category not in categories:
            categories[category] = []
        categories[category].append(url)
    
    # 按分类显示URL
    for category, urls in sorted(categories.items()):
        print(f"\n{category} ({len(urls)} URLs):")
        print("-" * 30)
        for url in urls:
            print(f"  {url}")
    
    print(f"\nTotal URLs: {len(FINANCIAL_SEED_URLS)}")

if __name__ == "__main__":
    test_urls()
