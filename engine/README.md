# 搜索引擎组件

这是搜索引擎的核心组件，实现了基于倒排索引的搜索功能，支持中文分词、倒排列表求交和BM25相关性排序。

## 主要功能

- **中文分词**: 使用jieba进行中文分词，支持金融专业词汇
- **倒排索引查询**: 通过InvertedIndexReader获取倒排列表
- **倒排列表求交**: 对多个词的倒排列表进行高效的求交操作
- **BM25相关性排序**: 使用BM25算法对搜索结果进行相关性排序
- **高亮显示**: 支持在搜索结果中高亮显示匹配的查询词
- **Web API**: 提供RESTful API接口
- **命令行界面**: 提供交互式命令行界面

## 核心类

### SearchEngine

主要的搜索引擎类，包含以下核心方法：

- `tokenize_query(query)`: 对查询进行分词
- `get_postings(term)`: 获取指定词的倒排列表
- `intersect_postings(postings_list)`: 对多个倒排列表进行求交
- `calculate_bm25_score(query_terms, doc_id)`: 计算BM25相关性分数
- `search(query)`: 执行完整的搜索流程
- `search_with_highlight(query)`: 执行带高亮的搜索

## 使用方法

### 1. 基本使用

```python
from engine.search_engine import SearchEngine

# 初始化搜索引擎
search_engine = SearchEngine()

# 执行搜索
results = search_engine.search("股票投资")
for result in results:
    print(f"文档ID: {result['doc_id']}")
    print(f"标题: {result['title']}")
    print(f"分数: {result['score']}")
```

### 2. 高亮搜索

```python
# 执行带高亮的搜索
results = search_engine.search_with_highlight("人工智能")
for result in results:
    print(f"高亮标题: {result['highlighted_title']}")
    print(f"高亮内容: {result['highlighted_content']}")
```

### 3. 查询分析

```python
# 分词
terms = search_engine.tokenize_query("股票投资")
print(f"分词结果: {terms}")

# 获取倒排列表
for term in terms:
    postings = search_engine.get_postings(term)
    print(f"词 '{term}' 有 {len(postings)} 个倒排项")
```

### 4. 倒排列表求交

```python
# 获取多个词的倒排列表
postings_list = []
for term in ["股票", "投资"]:
    postings = search_engine.get_postings(term)
    if postings:
        postings_list.append(postings)

# 求交
intersection = search_engine.intersect_postings(postings_list)
print(f"求交结果: {len(intersection)} 个文档")
```

## 命令行界面

### 交互模式

```bash
python engine/cli.py
```

进入交互模式后，可以输入：
- `股票` - 搜索包含"股票"的文档
- `analyze 股票投资` - 分析"股票投资"查询
- `highlight 人工智能` - 高亮搜索"人工智能"
- `help` - 显示帮助信息
- `quit` - 退出

### 单次搜索

```bash
# 普通搜索
python engine/cli.py "股票投资"

# 高亮搜索
python engine/cli.py "人工智能" --highlight

# 分析查询
python engine/cli.py "股票投资" --analyze

# 限制结果数
python engine/cli.py "科技" --max-results 5
```

## Web API

### 启动API服务器

```bash
python engine/api_server.py
```

### API接口

#### 搜索接口

```bash
# GET请求
curl "http://localhost:5000/api/search?q=股票投资&highlight=true"

# POST请求
curl -X POST "http://localhost:5000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "股票投资", "highlight": true, "max_results": 10}'
```

#### 统计信息

```bash
curl "http://localhost:5000/api/stats"
```

#### 健康检查

```bash
curl "http://localhost:5000/api/health"
```

#### 搜索建议

```bash
curl "http://localhost:5000/api/suggest?q=股票&limit=5"
```

#### 查询分析

```bash
curl -X POST "http://localhost:5000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "股票投资"}'
```

## 测试

### 运行测试脚本

```bash
python engine/test_search_engine.py
```

测试脚本会：
1. 测试搜索引擎的基本功能
2. 测试倒排列表求交功能
3. 测试各种查询场景

## 配置

搜索引擎的配置在 `config/settings.py` 中：

```python
SEARCH_CONFIG = {
    'bm25_k1': 1.5,        # BM25参数k1
    'bm25_b': 0.75,        # BM25参数b
    'max_results': 20      # 最大结果数
}
```

## 性能优化

1. **倒排列表求交优化**: 按长度排序，优先处理短的倒排列表
2. **BM25计算优化**: 预计算文档统计信息，避免重复计算
3. **内存管理**: 合理使用内存，避免加载过多数据

## 依赖

- `jieba`: 中文分词
- `rank-bm25`: BM25算法实现
- `flask`: Web API框架
- `flask-cors`: 跨域支持

## 文件结构

```
engine/
├── search_engine.py      # 核心搜索引擎类
├── api_server.py         # Web API服务器
├── cli.py               # 命令行界面
├── test_search_engine.py # 测试脚本
└── README.md            # 说明文档
```
