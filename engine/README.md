# 搜索引擎引擎

这个目录包含了搜索引擎的核心引擎类，实现了查询处理、倒排索引检索、文档求交和BM25相关性排序等功能。

## 文件结构

- `search_engine.py`: 主要的搜索引擎引擎类
- `test_search_engine.py`: 测试脚本，演示如何使用搜索引擎
- `README.md`: 本说明文档

## 主要功能

### SearchEngine 类

`SearchEngine` 类是搜索引擎的核心，提供以下功能：

1. **查询分词**: 使用 `TextProcessor` 对用户查询进行分词
2. **倒排索引检索**: 通过 `InvertedIndexBuilder` 获取每个分词的倒排列表
3. **文档求交**: 对多个term的倒排列表进行求交操作
4. **BM25排序**: 使用BM25算法对搜索结果进行相关性排序
5. **回退搜索**: 当AND搜索无结果时，自动使用OR搜索

### 主要方法

#### `__init__(index_builder, db_path)`
初始化搜索引擎
- `index_builder`: 倒排索引构建器实例
- `db_path`: 数据库文件路径

#### `search(query, max_results=None)`
执行搜索
- `query`: 查询字符串
- `max_results`: 最大结果数
- 返回: 搜索结果列表

#### `search_with_fallback(query, max_results=None)`
带回退的搜索，如果AND搜索无结果则使用OR搜索

#### `tokenize_query(query)`
对查询进行分词

#### `get_postings_for_terms(terms)`
获取多个term的倒排列表

#### `intersect_postings(postings_dict)`
对多个term的倒排列表进行求交

#### `calculate_bm25_score(doc_id, query_terms, postings_dict)`
计算BM25相关性分数

## 使用方法

### 基本使用

```python
from indexer.inverted_index import InvertedIndexBuilder
from engine.search_engine import SearchEngine

# 创建索引构建器
index_builder = InvertedIndexBuilder(
    db_path="data/crawler/crawler.db",
    index_path="data/indexer",
    num_shards=16
)

# 创建搜索引擎
search_engine = SearchEngine(index_builder, "data/crawler/crawler.db")

# 执行搜索
results = search_engine.search("股票投资", max_results=10)

# 打印结果
for result in results:
    print(f"标题: {result['title']}")
    print(f"分数: {result['score']:.3f}")
    print(f"URL: {result['url']}")
    print(f"预览: {result['content_preview']}")
    print("---")
```

### 测试脚本

运行测试脚本：

```bash
# 运行自动测试
python engine/test_search_engine.py

# 运行交互式搜索
python engine/test_search_engine.py --interactive
```

## BM25算法

搜索引擎使用BM25算法进行相关性排序，该算法考虑了：

1. **词频(TF)**: 查询词在文档中出现的频率
2. **逆文档频率(IDF)**: 查询词在整个文档集合中的稀有程度
3. **文档长度归一化**: 考虑文档长度对分数的影响

BM25公式：
```
BM25(q,d) = Σ IDF(qi) * (f(qi,d) * (k1 + 1)) / (f(qi,d) + k1 * (1 - b + b * |d|/avgdl))
```

其中：
- `f(qi,d)`: 词qi在文档d中的频率
- `|d|`: 文档d的长度
- `avgdl`: 平均文档长度
- `k1`, `b`: BM25参数（默认k1=1.5, b=0.75）

## 搜索策略

### AND搜索（默认）
- 要求所有查询词都出现在文档中
- 使用倒排列表求交操作
- 适合精确搜索

### OR搜索（回退）
- 当AND搜索无结果时自动启用
- 使用倒排列表求并操作
- 适合模糊搜索

## 配置参数

搜索引擎的配置参数在 `config/settings.py` 中定义：

```python
SEARCH_CONFIG = {
    'bm25_k1': 1.5,        # BM25参数k1
    'bm25_b': 0.75,        # BM25参数b
    'max_results': 20      # 最大结果数
}
```

## 性能优化

1. **分片索引**: 使用分片技术提高索引检索效率
2. **文档统计缓存**: 预先加载文档统计信息，避免重复计算
3. **批量处理**: 支持批量获取文档详细信息
4. **内存管理**: 合理控制内存使用，避免内存溢出

## 错误处理

搜索引擎包含完善的错误处理机制：

1. **数据库连接错误**: 自动重试和错误恢复
2. **索引文件缺失**: 提供清晰的错误提示
3. **查询处理错误**: 优雅处理异常情况
4. **结果获取错误**: 返回简化结果而不是完全失败

## 扩展性

搜索引擎设计具有良好的扩展性：

1. **模块化设计**: 各组件独立，易于替换和扩展
2. **配置驱动**: 通过配置文件控制行为
3. **接口标准化**: 提供标准化的搜索接口
4. **插件支持**: 可以轻松添加新的排序算法或过滤条件
