# 搜索引擎索引系统

这是一个高性能的倒排索引构建系统，支持分批处理、哈希分片和内存管理。

## 功能特性

### 🚀 核心特性
- **分批处理**: 支持大批量文档的分批处理，避免内存溢出
- **哈希分片**: 使用MD5哈希将不同term分片存储，提高并行性能
- **内存管理**: 智能内存管理，当分片达到阈值时自动卸载到磁盘
- **BM25算法**: 支持BM25评分算法，提供更准确的搜索结果
- **多索引类型**: 支持基础倒排索引和BM25索引

### 📊 性能优化
- **并发处理**: 支持多线程安全的索引操作
- **磁盘缓存**: 智能的磁盘缓存机制，平衡内存和磁盘使用
- **元数据管理**: 完整的索引元数据管理，支持增量更新
- **统计信息**: 详细的索引统计信息，便于性能监控

## 系统架构

```
indexer/
├── inverted_index.py      # 基础倒排索引构建器
├── bm25_indexer.py       # BM25索引构建器
├── index_manager.py       # 索引管理器
├── run_indexer.py        # 命令行工具
└── README.md            # 说明文档
```

### 核心组件

1. **InvertedIndexBuilder**: 基础倒排索引构建器
   - 支持分批处理文档
   - 哈希分片存储
   - 内存管理

2. **BM25IndexBuilder**: BM25算法索引构建器
   - 支持BM25评分算法
   - 文档长度统计
   - IDF计算

3. **IndexManager**: 统一索引管理器
   - 多索引类型管理
   - 状态监控
   - 搜索接口

## 安装和使用

### 环境要求
- Python 3.7+
- 依赖包: `jieba`, `sqlite3`, `pickle`, `json`

### 快速开始

1. **查看系统状态**
```bash
python indexer/run_indexer.py status
```

2. **构建索引**
```bash
# 构建所有索引
python indexer/run_indexer.py build --type all

# 构建BM25索引
python indexer/run_indexer.py build --type bm25 --shards 32 --batch-size 500

# 构建基础索引
python indexer/run_indexer.py build --type basic --shards 16
```

3. **测试搜索**
```bash
python indexer/run_indexer.py search --query "股票投资" --type bm25 --max-results 10
```

4. **查看统计信息**
```bash
python indexer/run_indexer.py stats --type bm25
```

5. **查看分片信息**
```bash
python indexer/run_indexer.py shards --type bm25
```

## 配置参数

### 索引构建参数
- `--shards`: 分片数量 (默认: 16)
- `--batch-size`: 批处理大小 (默认: 1000)
- `--max-memory`: 最大内存大小 (默认: 10000)

### 搜索参数
- `--query`: 查询字符串
- `--type`: 索引类型 (basic/bm25)
- `--max-results`: 最大结果数 (默认: 10)

## 数据结构

### Posting (倒排列表项)
```python
@dataclass
class Posting:
    doc_id: int          # 文档ID
    positions: List[int]  # 词在文档中的位置
    tf: int              # 词频
```

### BM25Posting (BM25倒排列表项)
```python
@dataclass
class BM25Posting:
    doc_id: int          # 文档ID
    positions: List[int]  # 词在文档中的位置
    tf: int              # 词频
    doc_length: int      # 文档长度
```

## 文件结构

### 索引文件
```
data/indexer/
├── shard_0.pkl              # 基础索引分片0
├── shard_1.pkl              # 基础索引分片1
├── ...
├── bm25_shard_0.pkl         # BM25索引分片0
├── bm25_shard_1.pkl         # BM25索引分片1
├── ...
├── shard_0_metadata.json    # 基础索引分片0元数据
├── bm25_shard_0_metadata.json # BM25索引分片0元数据
├── index_stats.json          # 基础索引统计信息
├── bm25_index_stats.json    # BM25索引统计信息
└── index_status.json        # 索引状态信息
```

## 性能优化

### 内存管理
- 每个分片独立管理内存使用
- 当内存使用超过阈值时自动刷新到磁盘
- 支持内存和磁盘数据的智能合并

### 分片策略
- 使用MD5哈希函数计算分片ID
- 确保term的均匀分布
- 支持自定义分片数量

### 批处理优化
- 支持自定义批处理大小
- 减少数据库连接开销
- 提高内存使用效率

## API接口

### IndexManager 主要方法

```python
# 构建索引
manager.build_basic_index(num_shards=16, batch_size=1000, max_memory_size=10000)
manager.build_bm25_index(num_shards=16, batch_size=1000, max_memory_size=10000)

# 搜索
results = manager.search(query="股票投资", index_type="bm25", max_results=20)

# 获取统计信息
stats = manager.get_index_stats(index_type="bm25")

# 检查数据库状态
db_status = manager.check_database()
```

## 监控和维护

### 状态监控
- 数据库文档数量
- 索引构建状态
- 分片使用情况
- 内存使用统计

### 维护操作
- 自动清理旧索引文件
- 索引状态备份
- 性能统计收集

## 故障排除

### 常见问题

1. **内存不足**
   - 减少 `max_memory_size` 参数
   - 增加分片数量
   - 减少批处理大小

2. **构建速度慢**
   - 增加批处理大小
   - 减少分片数量
   - 检查磁盘I/O性能

3. **搜索结果不准确**
   - 检查文本预处理
   - 调整BM25参数
   - 验证索引完整性

### 日志分析
系统提供详细的日志输出，包括：
- 索引构建进度
- 内存使用情况
- 错误和警告信息
- 性能统计

## 扩展开发

### 添加新的索引类型
1. 继承 `InvertedIndexBuilder` 或 `BM25IndexBuilder`
2. 实现自定义的评分算法
3. 在 `IndexManager` 中注册新索引类型

### 自定义分片策略
1. 修改 `_get_shard_id` 方法
2. 实现自定义的哈希函数
3. 调整分片数量配置

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。
