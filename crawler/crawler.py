import asyncio
import aiohttp
import time
import logging
import sqlite3
import threading
from typing import List, Dict, Set, Optional, Tuple, Any, Generic, TypeVar
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import os
from collections import deque
import json

from config.settings import CRAWLER_CONFIG, FINANCIAL_SEED_URLS
from utils.text_processor import TextProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')

class SmartQueue(Generic[T]):
    """
    智能队列类，可以将数据自动卸载到数据库，需要时再读取出来
    内存中的队列元素适中保持在合适数量，不至于内存溢出
    使用先进先出（FIFO）顺序
    """
    
    def __init__(self, max_memory_size: int = 300, db_path: str = "data/crawler/smart_queue.db"):
        """
        初始化智能队列
        
        Args:
            max_memory_size: 内存中最大元素数量
            db_path: 数据库文件路径
        """
        self.max_memory_size = max_memory_size
        self.db_path = db_path
        self.memory_queue: deque = deque()
        self.offload_size = max_memory_size // 2
        self.offload_queue: deque = deque()
        self.lock = threading.Lock()
        
        # 创建数据目录和数据库
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
        
        logger.info(f"SmartQueue initialized with max_memory_size={max_memory_size}")
    
    def _init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建队列数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS smart_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 初始化时清空数据库
        cursor.execute('DELETE FROM smart_queue')
        
        conn.commit()
        conn.close()
        logger.info("SmartQueue database initialized")
    
    def put(self, item: T) -> None:
        """
        将元素添加到队列
        
        Args:
            item: 要添加的元素
        """
        with self.lock:
            # 如果内存队列已满，将数据存入offload_queue
            if len(self.memory_queue) >= self.max_memory_size:
                # 如果offload_queue未满，将数据存入offload_queue
                if len(self.offload_queue) > self.offload_size:
                    self._move_to_database()
                    print('offload to database')
                self.offload_queue.append((item, time.time()))
                logger.debug(f"Added item to offload queue, current size: {len(self.offload_queue)}")
            else:
                # 将新元素添加到内存队列
                self.memory_queue.append((item, time.time()))
                logger.debug(f"Added item to memory queue, current size: {len(self.memory_queue)}")
    
    def get(self) -> Optional[T]:
        """
        从队列中获取元素（先进先出）
        
        Returns:
            队列中的元素，如果队列为空则返回None
        """
        with self.lock:
            # 首先从内存队列中获取（FIFO）
            if self.memory_queue:
                item, timestamp = self.memory_queue.popleft()
                logger.debug(f"Retrieved item from memory queue, remaining: {len(self.memory_queue)}")
                return item
            
            # 如果内存队列为空，从数据库加载
            items = self._load_from_database()
            logger.info('loaded {} items from database'.format(len(items)))
            if items:
                logger.debug("Retrieved items from database")
                self.memory_queue.extend(items)
                logger.info('after extend, memory queue size: {}'.format(len(self.memory_queue)))
                item, timestamp = self.memory_queue.popleft()
                return item
            return None
    
    def peek(self) -> Optional[T]:
        """
        查看队列头部的元素，但不移除
        
        Returns:
            队列头部的元素，如果队列为空则返回None
        """
        with self.lock:
            # 首先查看内存队列
            if self.memory_queue:
                item, timestamp = self.memory_queue[0]
                return item
            
            # 如果内存队列为空，从数据库查看
            return self._peek_from_database()
    
    def size(self) -> int:
        """
        获取队列总大小（内存 + 数据库）
        
        Returns:
            队列中的总元素数量
        """
        with self.lock:
            memory_size = len(self.memory_queue)
            db_size = self._get_database_size()
            return memory_size + db_size
    
    def memory_size(self) -> int:
        """
        获取内存中队列的大小
        
        Returns:
            内存中队列的元素数量
        """
        with self.lock:
            return len(self.memory_queue)
    
    def clear(self) -> None:
        """清空队列（内存和数据库）"""
        with self.lock:
            self.memory_queue.clear()
            self._clear_database()
            logger.info("SmartQueue cleared")
    
    def _move_to_database(self) -> None:
        """将内存队列中最旧的数据移动到数据库"""
        if not self.offload_queue:
            return
        
        # 将offload_queue中的数据移动到内存队列
        to_offload = []
        while self.offload_queue:
            oldest_item, timestamp = self.offload_queue.popleft()
            to_offload.append((oldest_item, timestamp))
        
        # 保存到数据库
        self._save_to_database(to_offload)
        logger.info("Moved {} items from memory to database".format(len(to_offload)))    
    
    def _save_to_database(self, items: List[Tuple[T, float]]) -> None:
        """将元素保存到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            data_jsons = []
            # 将对象序列化为JSON字符串
            for item, timestamp in items:
                if isinstance(item, (dict, list, str, int, float, bool)):
                    data_json = json.dumps(item, ensure_ascii=False)
                    data_jsons.append((data_json, timestamp))

            #批量插入
            cursor.executemany('''
                INSERT INTO smart_queue (data, created_at)
                VALUES (?, ?)
            ''', [(data_json, timestamp) for data_json, timestamp in data_jsons])
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving item to database: {e}")
    
    #批量加载数据库中的元素
    def _load_from_database(self) -> Optional[List[Tuple[T, float]]]:
        """从数据库加载元素（FIFO）"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 按创建时间排序获取最早的元素
            cursor.execute('''
                SELECT data, id FROM smart_queue 
                ORDER BY created_at ASC 
                LIMIT ?
            ''', (self.offload_size,))
            
            results = cursor.fetchall()
            if results:
                res_with_timestamp = [(result[0], result[1]) for result in results]
                
                # 删除已读取的元素
                cursor.executemany('DELETE FROM smart_queue WHERE id = ?', [(result[1],) for result in results])
                conn.commit()
                
                # 反序列化数据
                try:
                    items = [(json.loads(data_json), timestamp) for data_json, timestamp in res_with_timestamp]
                    conn.close()
                    return items
                except json.JSONDecodeError:
                    logger.error(f"Error deserializing items from database: {res_with_timestamp}")
                    conn.close()
                    return None
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Error loading item from database: {e}")
            return None
    
    def _peek_from_database(self) -> Optional[T]:
        """从数据库查看元素但不删除（FIFO）"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT data FROM smart_queue 
                ORDER BY created_at ASC 
                LIMIT 1
            ''')
            
            result = cursor.fetchone()
            if result:
                data_json = result[0]
                try:
                    item = json.loads(data_json)
                    conn.close()
                    return item
                except json.JSONDecodeError:
                    logger.error(f"Error deserializing item from database: {data_json}")
                    conn.close()
                    return None
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Error peeking item from database: {e}")
            return None
    
    def _get_database_size(self) -> int:
        """获取数据库中的元素数量"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM smart_queue')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error getting database size: {e}")
            return 0
    
    def _clear_database(self) -> None:
        """清空数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM smart_queue')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取队列统计信息
        
        Returns:
            包含队列统计信息的字典
        """
        with self.lock:
            memory_size = len(self.memory_queue)
            db_size = self._get_database_size()
            
            return {
                'memory_size': memory_size,
                'database_size': db_size,
                'total_size': memory_size + db_size,
                'max_memory_size': self.max_memory_size,
                'memory_usage_percent': (memory_size / self.max_memory_size) * 100 if self.max_memory_size > 0 else 0
            }
    
    def __len__(self) -> int:
        """返回队列的总大小"""
        return self.size()
    
    def __bool__(self) -> bool:
        """检查队列是否为空"""
        return self.size() > 0


class BatchCrawler:
    """批量处理爬虫"""
    
    def __init__(self, batch_size: int = 8):
        self.config = CRAWLER_CONFIG
        self.text_processor = TextProcessor()
        self.batch_size = batch_size
        self.visited_urls: Set[str] = set()
        # 使用SmartQueue替代原来的asyncio.Queue
        self.url_queue: SmartQueue[str] = SmartQueue(max_memory_size=300, db_path="data/crawler/url_queue.db")
        self.db_path = "data/crawler/crawler.db"
        
        # 创建数据目录和数据库
        os.makedirs('data/crawler', exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """初始化SQLite数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 清空pages表
        cursor.execute('DELETE FROM pages')
        conn.commit()

        # 清空url_queue表
        cursor.execute('DELETE FROM url_queue')
        conn.commit()
        
        # 创建页面数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                content TEXT,
                keywords TEXT,
                domain TEXT,
                crawl_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 清空页面表
        cursor.execute('DELETE FROM pages')

        # 创建失败URL表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS failed_urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    async def start(self, max_pages: int = 1000):
        """启动爬虫"""
        logger.info(f"Starting batch crawler with batch_size={self.batch_size}")
        
        # 初始化URL队列
        for url in FINANCIAL_SEED_URLS:
            self.url_queue.put(url)
        
        # 加载已访问的URL
        self._load_visited_urls()
        
        # 开始batch处理
        processed_pages = 0
        while processed_pages < max_pages:
            # 获取一个batch的URL
            batch_urls = await self._get_batch_urls()
            logger.info('get batch urls: {}'.format(batch_urls))
            if not batch_urls:
                logger.info("No more URLs to process")
                break
            
            # 并发爬取batch中的URL
            batch_results = await self._crawl_batch(batch_urls)
            
            # 串行处理结果
            await self._process_batch_results(batch_results)
            
            processed_pages += len([r for r in batch_results if r is not None])
            logger.info(f"Processed {processed_pages}/{max_pages} pages")
            
            # 添加延迟
            await asyncio.sleep(self.config['request_delay'])
        
        logger.info(f"Crawler finished. Processed {processed_pages} pages.")
    
    def _load_visited_urls(self):
        """从数据库加载已访问的URL"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT url FROM pages")
        urls = cursor.fetchall()
        self.visited_urls = set(url[0] for url in urls)
        conn.close()
        logger.info(f"Loaded {len(self.visited_urls)} visited URLs")
    
    async def _get_batch_urls(self) -> List[str]:
        """获取一个batch的URL"""
        urls = []
        while len(urls) < self.batch_size:
            url = self.url_queue.get()
            if url is None:
                break
            if url not in self.visited_urls:
                urls.append(url)
        return urls
    
    async def _crawl_batch(self, urls: List[str]) -> List[Optional[Dict]]:
        """并发爬取一个batch的URL"""
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config['timeout']),
            headers={'User-Agent': self.config['user_agent']}
        ) as session:
            # 创建并发任务
            tasks = []
            for url in urls:
                task = asyncio.create_task(self._crawl_single_page(session, url))
                tasks.append(task)
            
            # 等待所有任务完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理异常
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error crawling {urls[i]}: {result}")
                    processed_results.append(None)
                else:
                    processed_results.append(result)
            
            return processed_results
    
    # 将爬取失败的url记录到数据库
    def _record_failed_url(self, url: str):
        """将爬取失败的url记录到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO failed_urls (url) VALUES (?)', (url,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error recording failed url: {e}")

    async def _crawl_single_page(self, session: aiohttp.ClientSession, url: str) -> Optional[Dict]:
        """爬取单个页面"""
        try:
            # logger.info(f"Crawling: {url}")
            
            async with session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to crawl {url}: status {response.status}")
                    self._record_failed_url(url)
                    return None
                
                content = await response.text()
                
                # 解析页面
                page_data = await self._parse_page(url, content)
                
                if page_data:
                    # 提取新链接
                    new_urls = self._extract_links(content, url)
                    page_data['new_urls'] = new_urls
                
                return page_data
                
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return None
    
    async def _process_batch_results(self, batch_results: List[Optional[Dict]]):
        """串行处理batch结果"""
        for result in batch_results:
            if result is None:
                continue
            
            # 保存到数据库
            self._save_to_database(result)
            
            # 更新已访问URL集合
            self.visited_urls.add(result['url'])
            
            # 添加新URL到队列
            new_urls = result.get('new_urls', [])
            for new_url in new_urls:
                if new_url not in self.visited_urls:
                    self.url_queue.put(new_url)
            
            # 打印队列统计信息
            stats = self.url_queue.get_stats()
            logger.error(f"Queue stats: memory={stats['memory_size']}, db={stats['database_size']}, total={stats['total_size']}")
    
    def _save_to_database(self, page_data: Dict):
        """保存页面数据到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 将关键词列表转换为字符串
            keywords_str = ','.join(page_data.get('keywords', []))
            
            cursor.execute('''
                INSERT OR REPLACE INTO pages 
                (url, title, content, keywords, domain, crawl_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                page_data['url'],
                page_data['title'],
                page_data['content'],
                keywords_str,
                page_data['domain'],
                page_data['crawl_time']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
    
    async def _parse_page(self, url: str, html_content: str) -> Optional[Dict]:
        """解析页面内容"""
        try:
            # 提取标题和内容
            title = self.text_processor.extract_title(html_content)
            content = self.text_processor.extract_content(html_content)
            
            # 过滤非金融相关内容
            if not self._is_financial_content(title, content):
                return None
            
            # 提取关键词
            keywords = self.text_processor.extract_keywords(content, top_k=10)
            
            # 构建页面数据
            page_data = {
                'url': url,
                'title': title,
                'content': content,
                'keywords': keywords,
                'crawl_time': time.time(),
                'domain': urlparse(url).netloc
            }
            
            return page_data
            
        except Exception as e:
            logger.error(f"Error parsing page {url}: {e}")
            return None
    
    def _is_financial_content(self, title: str, content: str) -> bool:
        """判断是否为金融相关内容"""
        financial_keywords = [
            # 中文金融术语
            '股票', '债券', '基金', '期货', '期权', '外汇', '黄金', '原油',
            '投资', '理财', '保险', '银行', '证券', '信托', '私募', '公募',
            'IPO', '并购', '重组', '上市', '退市', '分红', '配股', '增发',
            '牛市', '熊市', '震荡', '上涨', '下跌', '涨停', '跌停', '停牌',
            '市盈率', '市净率', 'ROE', 'ROA', 'EPS', 'PEG', '股息率',
            '美联储', '央行', '利率', '通胀', 'GDP', 'CPI', 'PPI', 'PMI',
            '纳斯达克', '道琼斯', '标普500', '恒生指数', '上证指数', '深证成指',

            # 中概股互联网
            '阿里巴巴', '腾讯', '百度', '京东', '美团', '拼多多', '网易', '小米',
            '中概股', '互联网', '科技', '科技股', '科技公司', '科技行业', '科技市场', '科技趋势',
            '科技发展', '科技进步', '科技革命', '科技突破', '科技创新', '科技领先', '科技领先公司', '科技领先行业',
           
            # 中文科技术语
            '人工智能', '机器学习', '深度学习', '自然语言处理', '计算机视觉', '语音识别', '自动驾驶', '物联网',
            '云计算', '大数据', '区块链', '量子计算', '5G', '6G', '7G', '8G', '9G', '10G',
            '16G', '32G', '64G', '128G', '256G', '512G', '1024G', '2048G', '4096G', '8192G', '1TB',

            # 中文汽车术语
            '汽车', '汽车市场', '汽车行业', '汽车销售', '汽车制造', '汽车设计', '汽车技术', '汽车安全',
            '汽车环保', '汽车能源', '汽车电子', '汽车零部件', '汽车配件', '汽车维修', '汽车保养', '汽车改装',
            
            # 英文金融术语
            'stock', 'bond', 'fund', 'futures', 'options', 'forex', 'gold', 'oil',
            'investment', 'finance', 'insurance', 'bank', 'securities', 'trust',
            'market', 'trading', 'economy', 'economic', 'financial', 'money',
            'currency', 'exchange', 'rate', 'interest', 'inflation', 'GDP',
            
            # 加密货币和区块链
            'bitcoin', 'ethereum', 'crypto', 'cryptocurrency', 'blockchain',
            'defi', 'nft', 'token', 'wallet', 'mining', 'altcoin',
            
            # 金融科技
            'fintech', 'digital banking', 'mobile payment', 'robo-advisor',
            'insurtech', 'regtech', 'wealthtech', 'lending', 'crowdfunding',
            
            # 可持续金融
            'esg', 'sustainable', 'green finance', 'climate finance',
            'impact investing', 'social responsibility', 'environmental',
            
            # 新兴市场
            'emerging markets', 'frontier markets', 'developing countries',
            'global south', 'brics', 'africa', 'latin america', 'asia',
            
            # 专业金融术语
            'hedge fund', 'private equity', 'venture capital', 'derivatives',
            'commodities', 'real estate', 'mortgage', 'credit', 'debt',
            'equity', 'dividend', 'earnings', 'revenue', 'profit', 'loss',
            'balance sheet', 'income statement', 'cash flow', 'valuation',
            'portfolio', 'asset allocation', 'risk management', 'compliance',
            
            # 宏观经济
            'monetary policy', 'fiscal policy', 'central bank', 'federal reserve',
            'european central bank', 'bank of england', 'bank of japan',
            'recession', 'depression', 'recovery', 'growth', 'unemployment',
            'consumer price index', 'producer price index', 'purchasing managers',
            
            # 行业术语
            'banking', 'insurance', 'asset management', 'investment banking',
            'retail banking', 'commercial banking', 'wealth management',
            'pension', 'annuity', 'mutual fund', 'etf', 'index fund'
        ]
        
        text = (title + ' ' + content).lower()
        return any(keyword.lower() in text for keyword in financial_keywords)
    
    def _extract_links(self, html_content: str, base_url: str) -> List[str]:
        """提取页面中的链接"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)
                
                # 过滤链接
                if self._is_valid_url(full_url):
                    links.append(full_url)

            return links[:50]  # 限制链接数量
            
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []
    
    def _is_valid_url(self, url: str) -> bool:
        """判断是否为有效URL"""
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in ['http', 'https'] and
                parsed.netloc and
                not url.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.gif'))
            )
        except:
            return False
    
    def get_crawled_data(self) -> List[Dict]:
        """从数据库获取爬取的数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT url, title, content, keywords, domain, crawl_time
            FROM pages
            ORDER BY crawl_time DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            url, title, content, keywords_str, domain, crawl_time = row
            keywords = keywords_str.split(',') if keywords_str else []
            
            results.append({
                'url': url,
                'title': title,
                'content': content,
                'keywords': keywords,
                'domain': domain,
                'crawl_time': crawl_time
            })
        
        return results 