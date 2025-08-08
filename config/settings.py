import os
from dotenv import load_dotenv

load_dotenv()

# 数据库配置
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DB = os.getenv('MONGO_DB', 'financial_search')
REDIS_URI = os.getenv('REDIS_URI', 'redis://localhost:6379/0')

# 爬虫配置
CRAWLER_CONFIG = {
    'max_concurrent': 10,  # 最大并发数
    'request_delay': 1,    # 请求间隔(秒)
    'timeout': 30,         # 请求超时时间
    'max_retries': 3,      # 最大重试次数
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 金融网站种子URL
FINANCIAL_SEED_URLS = [
    # 国际主流财经媒体
    'https://www.cnbc.com/',
    'https://www.bloomberg.com/',
    'https://www.reuters.com/business/',
    'https://www.ft.com/',
    'https://www.wsj.com/',
    'https://www.economist.com/',
    'https://www.bbc.com/news/business',
    'https://www.marketwatch.com/',
    'https://www.forbes.com/business/',
    'https://www.businessinsider.com/',
    'https://www.cnbc.com/markets/',
    'https://www.cnbc.com/investing/',
    'https://www.cnbc.com/economy/',

    # 国内主流财经媒体
    'https://www.cctv.com',
    'https://www.people.com.cn',
    'https://www.163.com',
    'https://www.sina.com.cn',
    'https://finance.cctv.com/index.shtml?spm=C96370.PPDB2vhvSivD.E59hodVIdh2C.6',

    # 国内科技媒体
    'https://www.techweb.com/',
    'https://www.ithome.com/',
    'https://www.ithome.com/',
    
    # 专业金融网站
    'https://www.investing.com/',
    'https://www.fxstreet.com/',
    'https://www.forexfactory.com/',
    'https://www.tradingview.com/',
    'https://www.seekingalpha.com/',
    'https://www.fool.com/',
    'https://www.morningstar.com/',
    'https://www.zacks.com/',

    # 国内新闻
    'https://www.xinhuanet.com/',
    'https://www.cctv.com/',
    'https://www.people.com.cn/',
    'https://www.163.com/',
    'https://www.sina.com.cn/',
    'https://www.sohu.com/',

    # 汽车媒体
    'https://www.autoblog.com/',
    'https://www.caranddriver.com/',
    'https://www.carscoops.com/',
    'https://www.carwow.co.uk/',
    'https://www.caradvice.com.au/',
    'https://www.carscoops.com/',
    
    # 加密货币和区块链
    'https://cointelegraph.com/',
    'https://coindesk.com/',
    'https://www.coingecko.com/',
    'https://cryptonews.com/',
    
    # 亚洲财经媒体
    'https://www.scmp.com/business',
    'https://www.straitstimes.com/business',
    'https://www.channelnewsasia.com/business',
    'https://www.todayonline.com/business',
    
    # 欧洲财经媒体
    'https://www.handelsblatt.com/english/',
    'https://www.lesechos.fr/',
    'https://www.expansion.com/',
    'https://www.ilsole24ore.com/',
    
    # 专业投资网站
    'https://www.barrons.com/',
    'https://www.investors.com/',
    'https://www.money.cnn.com/',
    'https://www.usatoday.com/money/',
    'https://www.nbcnews.com/business',
    'https://www.cbsnews.com/moneywatch/',
    
    # 金融科技
    'https://www.fintechfutures.com/',
    'https://www.finextra.com/',
    'https://www.bankingtech.com/',
    
    # 宏观经济和政策
    'https://www.imf.org/en/news',
    'https://www.worldbank.org/en/news',
    'https://www.oecd.org/newsroom/',
    'https://www.bis.org/',
    
    # 专业金融数据和分析
    'https://www.spglobal.com/platts/',
    'https://www.refinitiv.com/en/news',
    'https://www.factset.com/insights',
    'https://www.moodys.com/research',
    'https://www.fitchratings.com/',
    'https://www.spglobal.com/ratings/en/',
    
    # 行业专业网站
    'https://www.insurancejournal.com/',
    'https://www.thinkadvisor.com/',
    'https://www.investmentnews.com/',
    'https://www.wealthmanagement.com/',
    'https://www.fa-mag.com/',
    
    # 新兴市场
    'https://www.emergingmarkets.com/',
    'https://www.frontiermarkets.com/',
    'https://www.africanbusiness.com/',
    'https://www.latinfinance.com/',
    
    # 可持续金融
    'https://www.environmental-finance.com/',
    'https://www.responsible-investor.com/',
    'https://www.greenbiz.com/',
    'https://www.esginvestor.net/'

    # 世界新闻
    'https://www.bbc.com/news/business',
    'https://www.reuters.com/business/',
    'https://www.ft.com/',
    'https://www.wsj.com/',
    'https://www.economist.com/',
    'https://www.bbc.com/news/business',
    'https://www.marketwatch.com/',
]

# 索引器配置
INDEXER_CONFIG = {
    'batch_size': 1000,    # 批处理大小
    'flush_interval': 300, # 刷新间隔(秒)
    'max_memory_mb': 512   # 最大内存使用量(MB)
}

# 搜索引擎配置
SEARCH_CONFIG = {
    'bm25_k1': 1.5,        # BM25参数k1
    'bm25_b': 0.75,        # BM25参数b
    'max_results': 20      # 最大结果数
}

# 前端配置
FRONTEND_CONFIG = {
    'host': '0.0.0.0',
    'port': 8090,
    'debug': True
} 