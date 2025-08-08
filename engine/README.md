# 搜索引擎系统

这是一个基于BM25算法的高性能搜索引擎，使用分片索引技术，支持大规模文档的快速搜索。

## 功能特性

### 🔍 核心搜索功能
- **BM25算法**: 使用BM25评分算法，提供更准确的搜索结果
- **分片索引**: 支持64个分片的哈希索引，提高并行性能
- **文档缓存**: 智能文档缓存机制，减少数据库查询
- **高亮显示**: 自动生成搜索结果的高亮片段

### 📊 搜索类型
- **基础搜索**: 支持关键词搜索，返回相关度排序的结果
- **域名搜索**: 按网站域名过滤搜索结果
- **关键词搜索**: 按文档关键词进行精确匹配搜索
- **查询建议**: 智能查询建议功能
- **热门关键词**: 获取文档中的热门关键词统计

### ⚡ 性能优化
- **内存管理**: 智能内存管理，支持大规模文档索引
- **缓存机制**: 文档缓存减少重复数据库查询
- **分片技术**: 哈希分片提高并行处理能力
- **批量处理**: 支持大批量文档的索引构建

## 系统架构

```
engine/
├── search_engine.py      # 主搜索引擎类
├── test_search_engine.py # 测试脚本
├── demo_search.py        # 演示脚本
└── README.md           # 说明文档
```

## 快速开始

### 1. 初始化搜索引擎

```python
from engine.search_engine import BM25SearchEngine

# 创建搜索引擎实例
engine = BM25SearchEngine()

# 检查索引状态
stats = engine.get_search_stats()
print(f"总文档数: {stats['total_documents']}")
print(f"索引可用: {stats['index_available']}")
```

### 2. 基础搜索

```python
# 执行搜索
results = engine.search("股票投资", max_results=10)

# 处理搜索结果
for result in results:
    print(f"标题: {result['title']}")
    print(f"分数: {result['score']:.4f}")
    print(f"URL: {result['url']}")
    print(f"域名: {result['domain']}")
    
    # 显示高亮片段
    for highlight in result['highlights']:
        print(f"高亮: {highlight}")
```

### 3. 按域名搜索

```python
# 搜索特定域名的文档
results = engine.search_by_domain("cnbc.com", max_results=5)

for result in results:
    print(f"标题: {result['title']}")
    print(f"URL: {result['url']}")
```

### 4. 按关键词搜索

```python
# 按关键词组合搜索
keywords = ["股票", "投资"]
results = engine.search_by_keywords(keywords, max_results=5)

for result in results:
    print(f"标题: {result['title']}")
    print(f"关键词匹配数: {result['keyword_matches']}")
```

### 5. 查询建议

```python
# 获取查询建议
suggestions = engine.suggest_queries("股票", max_suggestions=5)

for suggestion in suggestions:
    print(f"建议: {suggestion}")
```

### 6. 热门关键词

```python
# 获取热门关键词
popular_keywords = engine.get_popular_keywords(top_k=20)

for keyword, freq in popular_keywords:
    print(f"{keyword}: {freq} 次")
```

## API接口

### BM25SearchEngine 类

#### 初始化
```python
BM25SearchEngine(db_path="data/crawler/crawler.db", index_path="data/indexer")
```

#### 主要方法

##### search(query, max_results=None)
执行基础搜索
- `query`: 查询字符串
- `max_results`: 最大结果数 (默认使用配置值)
- 返回: 搜索结果列表

##### search_by_domain(domain, max_results=None)
按域名搜索
- `domain`: 域名字符串
- `max_results`: 最大结果数
- 返回: 搜索结果列表

##### search_by_keywords(keywords, max_results=None)
按关键词搜索
- `keywords`: 关键词列表
- `max_results`: 最大结果数
- 返回: 搜索结果列表

##### suggest_queries(partial_query, max_suggestions=5)
获取查询建议
- `partial_query`: 部分查询字符串
- `max_suggestions`: 最大建议数
- 返回: 建议列表

##### get_popular_keywords(top_k=20)
获取热门关键词
- `top_k`: 返回前k个关键词
- 返回: (关键词, 频率) 元组列表

##### get_search_stats()
获取搜索统计信息
- 返回: 统计信息字典

##### get_index_status()
获取索引状态
- 返回: 索引状态字典

##### get_shard_info()
获取分片信息
- 返回: 分片信息字典

##### clear_cache()
清空文档缓存

## 搜索结果格式

搜索结果包含以下字段：

```python
{
    'id': 123,                    # 文档ID
    'url': 'https://example.com', # 文档URL
    'title': '文档标题',           # 文档标题
    'content': '文档内容',         # 文档内容
    'keywords': ['关键词1', '关键词2'], # 文档关键词
    'domain': 'example.com',      # 域名
    'crawl_time': 1234567890.0,  # 爬取时间
    'score': 0.1234,             # BM25评分
    'highlights': [               # 高亮片段
        '标题: 文档标题',
        '...高亮内容片段...'
    ]
}
```

## 性能优化

### 内存管理
- 文档缓存减少重复数据库查询
- 分片索引减少内存使用
- 智能内存管理避免内存溢出

### 查询优化
- BM25算法提供准确的评分
- 分片并行处理提高查询速度
- 索引预加载减少查询延迟

### 缓存策略
- 文档缓存提高重复查询性能
- 索引缓存减少磁盘I/O
- 统计信息缓存减少计算开销

## 监控和维护

### 状态监控
```python
# 获取搜索统计
stats = engine.get_search_stats()
print(f"总文档数: {stats['total_documents']}")
print(f"平均文档长度: {stats['avg_doc_length']}")
print(f"索引可用: {stats['index_available']}")

# 获取索引状态
index_status = engine.get_index_status()
for index_type, status in index_status.items():
    print(f"{index_type}: {'已构建' if status['built'] else '未构建'}")

# 获取分片信息
shard_info = engine.get_shard_info()
for shard_id, info in shard_info.items():
    print(f"分片 {shard_id}: {info['term_count']} 词条")
```

### 性能测试
```python
import time

# 性能测试
queries = ["股票", "投资", "基金", "比特币"]
total_time = 0

for query in queries:
    start_time = time.time()
    results = engine.search(query, max_results=10)
    search_time = time.time() - start_time
    total_time += search_time
    
    print(f"查询 '{query}': {len(results)} 结果, {search_time:.3f}秒")

print(f"平均查询时间: {total_time/len(queries):.3f}秒")
```

## 故障排除

### 常见问题

1. **索引不可用**
   ```
   错误: BM25 index not available
   解决: 运行索引构建器
   python indexer/run_indexer.py build --type bm25
   ```

2. **查询无结果**
   - 检查查询词是否正确
   - 确认索引已构建
   - 检查数据库连接

3. **性能问题**
   - 减少查询结果数量
   - 清空文档缓存
   - 检查索引状态

### 日志分析
系统提供详细的日志输出：
- 索引加载状态
- 查询执行时间
- 错误和警告信息
- 性能统计

## 测试和演示

### 运行测试
```bash
# 运行所有测试
python engine/test_search_engine.py

# 查看测试帮助
python engine/test_search_engine.py --help
```

### 运行演示
```bash
# 运行功能演示
python engine/demo_search.py
```

## 配置说明

### 搜索引擎配置
在 `config/settings.py` 中配置：

```python
SEARCH_CONFIG = {
    'bm25_k1': 1.5,        # BM25参数k1
    'bm25_b': 0.75,        # BM25参数b
    'max_results': 20      # 默认最大结果数
}
```

### 数据库配置
- 数据库路径: `data/crawler/crawler.db`
- 索引路径: `data/indexer/`
- 支持SQLite数据库

## 扩展开发

### 添加新的搜索类型
1. 在 `BM25SearchEngine` 类中添加新方法
2. 实现搜索逻辑
3. 添加相应的测试用例

### 自定义评分算法
1. 修改BM25参数
2. 实现自定义评分函数
3. 更新索引构建器

### 优化性能
1. 调整缓存策略
2. 优化分片数量
3. 改进查询算法

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。
