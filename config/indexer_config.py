"""
索引器配置文件
"""

# 索引器基本配置
INDEXER_CONFIG = {
    # 索引存储目录
    'index_dir': 'data/indexer',
    
    # 分片配置
    'num_shards': 16,  # 分片数量，建议为2的幂次
    'shard_hash_method': 'md5',  # 分片哈希方法
    
    # 批处理配置
    'batch_size': 100,  # 批处理大小
    'max_memory_docs': 5000,  # 内存中最大文档数量
    
    # 合并配置
    'merge_threshold': 1000,  # 触发合并的阈值
    'merge_interval': 300,  # 定期合并间隔（秒）
    'force_merge_on_shutdown': True,  # 关闭时是否强制合并
    
    # 搜索配置
    'default_top_k': 10,  # 默认返回结果数量
    'search_timeout': 30,  # 搜索超时时间（秒）
    
    # 文本处理配置
    'min_term_length': 2,  # 最小词长度
    'max_term_length': 20,  # 最大词长度
    'enable_stopwords': True,  # 是否启用停用词过滤
    
    # 数据库配置
    'db_connection_timeout': 30,  # 数据库连接超时
    'db_max_connections': 10,  # 最大数据库连接数
}

# 停用词列表
STOPWORDS = {
    # 中文停用词
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这',
    '那', '他', '她', '它', '我们', '你们', '他们', '她们', '它们', '这个', '那个', '这些', '那些', '什么', '怎么', '为什么', '哪里', '哪个', '多少', '几个', '一些', '很多', '全部', '部分',
    '可以', '应该', '必须', '需要', '想要', '希望', '觉得', '认为', '知道', '了解', '明白', '清楚', '记得', '忘记', '想起', '想到', '想到', '想到', '想到', '想到', '想到', '想到',
    '因为', '所以', '但是', '然而', '不过', '只是', '而且', '或者', '如果', '虽然', '尽管', '无论', '不管', '除了', '除了', '除了', '除了', '除了', '除了', '除了', '除了',
    '时候', '时间', '现在', '以前', '以后', '今天', '昨天', '明天', '今年', '去年', '明年', '上午', '下午', '晚上', '早上', '中午', '深夜', '凌晨',
    '地方', '位置', '地点', '区域', '地区', '城市', '国家', '世界', '地球', '宇宙', '天空', '地面', '地下', '水里', '空中', '外面', '里面', '前面', '后面', '左边', '右边',
    '东西', '物品', '物体', '事物', '事情', '事件', '情况', '状态', '条件', '环境', '背景', '原因', '结果', '影响', '作用', '效果', '功能', '作用', '意义', '价值', '重要性',
    '方式', '方法', '手段', '工具', '技术', '技能', '能力', '水平', '程度', '范围', '规模', '大小', '数量', '质量', '性质', '特点', '特征', '属性', '性质', '本质', '核心',
    '问题', '困难', '挑战', '风险', '危险', '威胁', '机会', '机遇', '优势', '劣势', '优点', '缺点', '好处', '坏处', '利益', '损失', '收益', '成本', '费用', '价格', '价值',
    
    # 英文停用词
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs', 'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'yourselves', 'themselves',
    'who', 'whom', 'whose', 'which', 'what', 'where', 'when', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
    'also', 'just', 'now', 'then', 'here', 'there', 'where', 'when', 'why', 'how', 'again', 'ever', 'far', 'late', 'long', 'once', 'soon', 'still', 'today', 'tomorrow', 'yesterday',
    'about', 'above', 'across', 'after', 'against', 'along', 'among', 'around', 'before', 'behind', 'below', 'beneath', 'beside', 'between', 'beyond', 'during', 'except', 'inside', 'near', 'off', 'over', 'since', 'through', 'toward', 'under', 'within',
    'first', 'second', 'third', 'last', 'next', 'previous', 'current', 'new', 'old', 'young', 'big', 'small', 'large', 'little', 'high', 'low', 'good', 'bad', 'better', 'worse', 'best', 'worst',
    'many', 'much', 'few', 'little', 'more', 'less', 'most', 'least', 'some', 'any', 'none', 'all', 'both', 'either', 'neither', 'each', 'every', 'several', 'various', 'different', 'same', 'similar', 'other', 'another',
    'time', 'year', 'month', 'week', 'day', 'hour', 'minute', 'second', 'morning', 'afternoon', 'evening', 'night', 'today', 'yesterday', 'tomorrow', 'now', 'then', 'ago', 'before', 'after', 'during', 'while', 'since', 'until',
    'place', 'location', 'position', 'area', 'region', 'country', 'city', 'town', 'village', 'street', 'road', 'house', 'home', 'room', 'building', 'office', 'school', 'hospital', 'store', 'shop', 'market', 'park', 'garden',
    'thing', 'object', 'item', 'stuff', 'material', 'substance', 'matter', 'element', 'part', 'piece', 'bit', 'section', 'portion', 'fraction', 'half', 'quarter', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth',
    'way', 'method', 'means', 'approach', 'technique', 'procedure', 'process', 'system', 'plan', 'strategy', 'tactic', 'methodology', 'framework', 'model', 'pattern', 'structure', 'organization', 'arrangement', 'setup', 'configuration',
    'work', 'job', 'task', 'duty', 'responsibility', 'obligation', 'requirement', 'need', 'demand', 'request', 'order', 'command', 'instruction', 'direction', 'guidance', 'advice', 'suggestion', 'recommendation', 'proposal', 'offer',
    'people', 'person', 'man', 'woman', 'boy', 'girl', 'child', 'baby', 'kid', 'guy', 'lady', 'gentleman', 'sir', 'madam', 'miss', 'mister', 'doctor', 'professor', 'teacher', 'student', 'worker', 'employee', 'manager', 'boss', 'leader',
    'group', 'team', 'company', 'organization', 'institution', 'association', 'society', 'club', 'community', 'family', 'class', 'grade', 'level', 'category', 'type', 'kind', 'sort', 'variety', 'class', 'species', 'breed', 'race', 'ethnicity',
    'information', 'data', 'fact', 'detail', 'point', 'aspect', 'feature', 'characteristic', 'property', 'attribute', 'quality', 'trait', 'nature', 'essence', 'core', 'heart', 'center', 'middle', 'focus', 'emphasis', 'priority', 'importance',
    'problem', 'issue', 'matter', 'concern', 'worry', 'anxiety', 'fear', 'doubt', 'uncertainty', 'confusion', 'misunderstanding', 'disagreement', 'conflict', 'dispute', 'argument', 'debate', 'discussion', 'conversation', 'talk', 'speech', 'presentation',
    'result', 'outcome', 'consequence', 'effect', 'impact', 'influence', 'change', 'difference', 'improvement', 'progress', 'development', 'growth', 'increase', 'decrease', 'rise', 'fall', 'gain', 'loss', 'profit', 'benefit', 'advantage', 'disadvantage',
    'money', 'cash', 'currency', 'dollar', 'cent', 'penny', 'nickel', 'dime', 'quarter', 'bill', 'note', 'coin', 'payment', 'price', 'cost', 'expense', 'fee', 'charge', 'rate', 'tax', 'interest', 'loan', 'debt', 'credit', 'saving', 'investment',
}

# 金融专业词汇（用于分词优化）
FINANCIAL_TERMS = [
    # 中文金融术语
    '股票', '债券', '基金', '期货', '期权', '外汇', '黄金', '原油',
    '投资', '理财', '保险', '银行', '证券', '信托', '私募', '公募',
    'IPO', '并购', '重组', '上市', '退市', '分红', '配股', '增发',
    '牛市', '熊市', '震荡', '上涨', '下跌', '涨停', '跌停', '停牌',
    '市盈率', '市净率', 'ROE', 'ROA', 'EPS', 'PEG', '股息率',
    '美联储', '央行', '利率', '通胀', 'GDP', 'CPI', 'PPI', 'PMI',
    '纳斯达克', '道琼斯', '标普500', '恒生指数', '上证指数', '深证成指',
    
    # 英文金融术语
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

# 搜索评分权重配置
SEARCH_WEIGHTS = {
    'title_weight': 3.0,      # 标题权重
    'content_weight': 1.0,    # 内容权重
    'keyword_weight': 2.0,    # 关键词权重
    'tf_weight': 1.0,         # 词频权重
    'recency_weight': 0.1,    # 时效性权重
}

# 索引优化配置
INDEX_OPTIMIZATION = {
    'enable_compression': True,        # 启用压缩
    'compression_level': 6,           # 压缩级别
    'enable_caching': True,           # 启用缓存
    'cache_size': 1000,              # 缓存大小
    'enable_background_merge': True,  # 启用后台合并
    'merge_thread_count': 2,          # 合并线程数
}
