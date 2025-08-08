# 金融搜索引擎

一个专注于金融信息的搜索引擎，包含爬虫、索引器和搜索引擎三个主要组件。

## 项目结构

```
search_engine/
├── crawler/          # 爬虫组件
├── indexer/          # 索引器组件
├── engine/           # 搜索引擎组件
├── frontend/         # 前端界面
├── data/             # 数据存储
├── config/           # 配置文件
└── utils/            # 工具函数
```

## 主要特性

- **批量处理爬虫**: 使用batch模式，每次处理固定数量的URL，并发爬取，串行处理
- **SQLite数据库**: 使用SQLite存储爬取数据，支持高效查询和索引
- **丰富的数据源**: 66个高质量金融新闻网站，涵盖全球财经媒体
- **智能内容过滤**: 基于金融关键词的内容识别和过滤
- **BM25算法**: 使用BM25算法进行相关性评分
- **简约UI**: 参考USENIX风格的简约前端设计

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 一键启动（推荐）

```bash
chmod +x start.sh
./start.sh
```

### 3. 手动启动各个组件

```bash
# 启动爬虫
python -m crawler.main --max-pages 100 --concurrent 5

# 启动索引器
python -m indexer.main

# 启动搜索引擎API
python -m engine.main

# 启动前端
python -m frontend.app
```

### 4. 访问系统

- 前端界面: http://localhost:5001
- API接口: http://localhost:5000

## 配置说明

### 爬虫配置

在 `config/settings.py` 中可以调整：

- `max_concurrent`: 最大并发数
- `request_delay`: 请求间隔
- `timeout`: 请求超时时间
- `FINANCIAL_SEED_URLS`: 种子URL列表

### 索引器配置

- `batch_size`: 批处理大小
- `flush_interval`: 刷新间隔
- `max_memory_mb`: 最大内存使用量

### 搜索引擎配置

- `bm25_k1`: BM25参数k1
- `bm25_b`: BM25参数b
- `max_results`: 最大结果数

## API接口

### 搜索接口
```
GET /api/search?q=<查询词>&max_results=<最大结果数>
```

### 查询建议
```
GET /api/suggest?q=<部分查询词>&max=<最大建议数>
```

### 统计信息
```
GET /api/stats
```

### 热门关键词
```
GET /api/keywords?top=<数量>
```

## 开发说明

### 添加新的金融网站

在 `config/settings.py` 中的 `FINANCIAL_SEED_URLS` 列表中添加新的URL。

### 自定义搜索算法

修改 `engine/search_engine.py` 中的BM25参数或实现新的排序算法。

### 前端样式定制

修改 `frontend/static/css/style.css` 来自定义界面样式。

## 故障排除

### 常见问题

1. **ModuleNotFoundError**: 确保已安装所有依赖
2. **端口占用**: 修改 `config/settings.py` 中的端口配置
3. **内存不足**: 调整索引器的 `max_memory_mb` 参数

### 日志查看

各个组件的日志会输出到控制台，可以通过重定向保存：

```bash
python -m crawler.main > crawler.log 2>&1
```

## 停止服务

```bash
chmod +x stop.sh
./stop.sh
```

或者手动停止：

```bash
pkill -f "crawler.main"
pkill -f "indexer.main"
pkill -f "engine.main"
pkill -f "frontend.app"
```

## 许可证

MIT License 