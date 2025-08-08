# 搜索引擎引擎模块

本模块实现了搜索引擎的核心功能，包括查询处理、倒排索引求交和BM25排序算法。

## 文件结构

```
engine/
├── search_engine.py      # 搜索引擎核心类
├── api_server.py         # API服务器
├── run_engine.py         # 启动脚本
├── test_engine.py        # 测试脚本
└── README.md            # 说明文档
```

## 核心功能

### SearchEngine 类

搜索引擎的核心类，提供以下功能：

- **查询处理**: 对用户查询进行分词和预处理
- **倒排索引求交**: 高效地找到包含所有查询词的文档
- **BM25排序**: 使用BM25算法对搜索结果进行相关性排序
- **文档详情获取**: 从数据库获取文档的完整信息

#### 主要方法

- `search(query, max_results=20)`: 执行搜索
- `suggest(partial_query, max_suggestions=5)`: 查询建议
- `get_popular_keywords(top_k=20)`: 获取热门关键词
- `get_stats()`: 获取系统统计信息

### API服务器

提供RESTful API接口，支持以下端点：

- `GET /api/search`: 搜索接口
- `GET /api/suggest`: 查询建议
- `GET /api/stats`: 系统统计
- `GET /api/keywords`: 热门关键词
- `GET /api/health`: 健康检查
- `GET /api/info`: 系统信息

## 使用方法

### 1. 启动API服务器

```bash
# 方法1: 直接运行
python engine/run_engine.py

# 方法2: 使用模块方式
cd engine
python -m api_server
```

### 2. 测试搜索引擎

```bash
# 测试核心功能
python engine/test_engine.py
```

### 3. API调用示例

```python
import requests

# 搜索
response = requests.get("http://localhost:5000/api/search", 
                       params={'q': '股票投资', 'max_results': 10})
results = response.json()

# 查询建议
response = requests.get("http://localhost:5000/api/suggest", 
                       params={'q': '股票', 'max': 5})
suggestions = response.json()

# 系统统计
response = requests.get("http://localhost:5000/api/stats")
stats = response.json()
```

## 配置

在 `config/settings.py` 中配置API服务器：

```python
API_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': False,
    'index_path': 'data/indexer',
    'db_path': 'data/crawler/crawler.db',
    'num_shards': 64
}
```

## BM25算法

搜索引擎使用BM25算法进行相关性排序：

```
BM25(q,d) = Σ IDF(qi) * (f(qi,d) * (k1 + 1)) / (f(qi,d) + k1 * (1 - b + b * |d| / avgdl))
```

其中：
- `k1`: 控制词频饱和度的参数（默认1.2）
- `b`: 控制文档长度归一化的参数（默认0.75）
- `f(qi,d)`: 词qi在文档d中的频率
- `|d|`: 文档d的长度
- `avgdl`: 平均文档长度

## 性能优化

1. **分片索引**: 使用64个分片分散存储倒排索引
2. **求交优化**: 按倒排列表长度排序，从最短的开始求交
3. **内存管理**: 合理控制内存使用，避免内存溢出
4. **并发处理**: 支持多线程并发查询

## 错误处理

- 参数验证：检查查询参数的有效性
- 异常捕获：优雅处理各种异常情况
- 日志记录：详细记录运行日志便于调试

## 扩展功能

可以扩展以下功能：

1. **查询扩展**: 基于同义词或相关词扩展查询
2. **个性化搜索**: 基于用户历史记录个性化搜索结果
3. **实时索引**: 支持实时更新索引
4. **缓存机制**: 添加查询结果缓存提高性能
5. **多语言支持**: 支持多语言搜索 