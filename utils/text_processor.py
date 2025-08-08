import re
import jieba
from typing import List, Set

class TextProcessor:
    """文本处理工具类"""
    
    def __init__(self):
        # 加载金融相关词汇
        self._load_financial_terms()
    
    def _load_financial_terms(self):
        """加载金融专业词汇"""
        financial_terms = [
            # 中文金融术语
            '股票', '债券', '基金', '期货', '期权', '外汇', '黄金', '原油',
            '投资', '理财', '保险', '银行', '证券', '信托', '私募', '公募',
            'IPO', '并购', '重组', '上市', '退市', '分红', '配股', '增发',
            '牛市', '熊市', '震荡', '上涨', '下跌', '涨停', '跌停', '停牌',
            '市盈率', '市净率', 'ROE', 'ROA', 'EPS', 'PEG', '股息率',
            '美联储', '央行', '利率', '通胀', 'GDP', 'CPI', 'PPI', 'PMI',
            '纳斯达克', '道琼斯', '标普500', '恒生指数', '上证指数', '深证成指',
            
            # 英文金融术语（用于混合语言内容）
            'Bitcoin', 'Ethereum', 'Cryptocurrency', 'Blockchain', 'DeFi', 'NFT',
            'Fintech', 'ESG', 'Hedge Fund', 'Private Equity', 'Venture Capital',
            'Derivatives', 'Commodities', 'Real Estate', 'Mortgage', 'Credit',
            'Equity', 'Dividend', 'Earnings', 'Revenue', 'Profit', 'Loss',
            'Portfolio', 'Asset Allocation', 'Risk Management', 'Compliance',
            'Monetary Policy', 'Fiscal Policy', 'Central Bank', 'Federal Reserve',
            'Recession', 'Depression', 'Recovery', 'Growth', 'Unemployment',
            'Banking', 'Insurance', 'Asset Management', 'Investment Banking',
            'Wealth Management', 'Pension', 'Annuity', 'Mutual Fund', 'ETF'
        ]
        
        for term in financial_terms:
            jieba.add_word(term)
    
    def clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符，保留中文、英文、数字和基本标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s.,!?;:()\[\]{}"\'-]', '', text)
        
        return text.strip()
    
    def extract_title(self, html_content: str) -> str:
        """从HTML中提取标题"""
        title_pattern = r'<title[^>]*>(.*?)</title>'
        title_match = re.search(title_pattern, html_content, re.IGNORECASE | re.DOTALL)
        
        if title_match:
            return self.clean_text(title_match.group(1))
        
        # 尝试从h1标签提取
        h1_pattern = r'<h1[^>]*>(.*?)</h1>'
        h1_match = re.search(h1_pattern, html_content, re.IGNORECASE | re.DOTALL)
        
        if h1_match:
            return self.clean_text(h1_match.group(1))
        
        return ""
    
    def extract_content(self, html_content: str) -> str:
        """从HTML中提取主要内容"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 移除script和style标签
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 尝试找到主要内容区域
        content_selectors = [
            'article', 'main', '.content', '.article-content', 
            '.post-content', '.entry-content', '.story-body'
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = elements[0].get_text()
                break
        
        # 如果没有找到特定内容区域，使用body
        if not content:
            content = soup.get_text()
        
        return self.clean_text(content)
    
    def tokenize(self, text: str) -> List[str]:
        """分词"""
        if not text:
            return []
        
        # 使用jieba分词
        tokens = jieba.lcut(text)
        
        # 过滤停用词和短词
        filtered_tokens = []
        for token in tokens:
            token = token.strip()
            if len(token) > 1 and not self._is_stopword(token):
                filtered_tokens.append(token)
        
        return filtered_tokens
    
    def _is_stopword(self, word: str) -> bool:
        """判断是否为停用词"""
        stopwords = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            '自己', '这', '那', '他', '她', '它', '们', '我们', '你们', '他们', '她们', '它们',
            '这个', '那个', '这些', '那些', '什么', '怎么', '为什么', '哪里', '何时', '如何',
            '可以', '应该', '必须', '需要', '想要', '希望', '觉得', '认为', '知道', '看到',
            '听到', '感到', '觉得', '认为', '知道', '看到', '听到', '感到'
        }
        return word in stopwords
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键词"""
        tokens = self.tokenize(text)
        
        # 简单的词频统计
        word_freq = {}
        for token in tokens:
            word_freq[token] = word_freq.get(token, 0) + 1
        
        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_words[:top_k]] 