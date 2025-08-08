# SmartQueue 智能队列类

## 概述

`SmartQueue` 是一个智能队列类，它可以将数据自动卸载到数据库，需要时再读取出来。这样内存中的队列元素适中保持在合适数量，不至于内存溢出。使用先进先出（FIFO）顺序。

## 特性

- **自动内存管理**: 当内存队列满时，自动将最旧的数据移动到数据库
- **先进先出（FIFO）**: 按照添加顺序获取元素
- **线程安全**: 使用锁机制确保多线程环境下的安全性
- **持久化存储**: 数据自动保存到SQLite数据库，支持程序重启后恢复
- **统计信息**: 提供详细的队列统计信息，包括内存使用率、数据库大小等
- **类型安全**: 使用泛型支持，确保类型安全

## 使用方法

### 基本使用

```python
from crawler import SmartQueue

# 创建一个最大内存大小为1000的队列
queue = SmartQueue(max_memory_size=1000, db_path="data/crawler/my_queue.db")

# 添加元素
queue.put({"id": 1, "name": "Alice", "age": 25})

# 获取元素（FIFO）
item = queue.get()
if item:
    print(f"获取到元素: {item['name']}")

# 查看队列大小
print(f"队列大小: {len(queue)}")
```

### 查看队列状态

```python
# 获取队列统计信息
stats = queue.get_stats()
print(f"内存中元素数量: {stats['memory_size']}")
print(f"数据库中元素数量: {stats['database_size']}")
print(f"总元素数量: {stats['total_size']}")
print(f"内存使用率: {stats['memory_usage_percent']:.1f}%")
```

### 其他操作

```python
# 查看队列头部的元素（不移除）
peek_item = queue.peek()

# 清空队列
queue.clear()

# 检查队列是否为空
if queue:
    print("队列不为空")
else:
    print("队列为空")
```

## API 参考

### 构造函数

```python
SmartQueue(max_memory_size: int = 1000, db_path: str = "data/crawler/smart_queue.db")
```

**参数:**
- `max_memory_size`: 内存中最大元素数量，默认为1000
- `db_path`: 数据库文件路径，默认为 "data/crawler/smart_queue.db"

### 方法

#### `put(item: T) -> None`
将元素添加到队列。

**参数:**
- `item`: 要添加的元素

#### `get() -> Optional[T]`
从队列中获取元素（先进先出）。

**返回:**
- 队列中的元素，如果队列为空则返回None

#### `peek() -> Optional[T]`
查看队列头部的元素，但不移除。

**返回:**
- 队列头部的元素，如果队列为空则返回None

#### `size() -> int`
获取队列总大小（内存 + 数据库）。

**返回:**
- 队列中的总元素数量

#### `memory_size() -> int`
获取内存中队列的大小。

**返回:**
- 内存中队列的元素数量

#### `clear() -> None`
清空队列（内存和数据库）。

#### `get_stats() -> Dict[str, Any]`
获取队列统计信息。

**返回:**
- 包含队列统计信息的字典，包括：
  - `memory_size`: 内存中元素数量
  - `database_size`: 数据库中元素数量
  - `total_size`: 总元素数量
  - `max_memory_size`: 最大内存大小
  - `memory_usage_percent`: 内存使用率

### 特殊方法

#### `__len__() -> int`
返回队列的总大小。

#### `__bool__() -> bool`
检查队列是否为空。

## 性能考虑

1. **内存使用**: 队列会自动管理内存使用，当内存队列满时会自动将数据移动到数据库
2. **数据库性能**: 使用索引优化查询性能，支持大量数据的快速存取
3. **序列化**: 使用JSON序列化数据，支持大多数Python数据类型
4. **并发安全**: 使用线程锁确保多线程环境下的安全性

## 使用场景

1. **爬虫队列**: 管理待爬取的URL队列，避免内存溢出
2. **任务队列**: 管理后台任务队列，支持FIFO调度
3. **数据缓冲**: 作为数据缓冲区，平衡内存使用和性能
4. **消息队列**: 简单的消息队列实现，支持持久化存储

## 注意事项

1. **数据库文件**: 确保数据库文件路径存在且有写入权限
2. **数据类型**: 支持大多数Python数据类型，但复杂对象需要实现`__dict__`方法
3. **并发使用**: 虽然线程安全，但在高并发场景下可能需要考虑使用专门的队列库
4. **数据持久化**: 数据会自动保存到数据库，程序重启后可以恢复

## 示例

完整的示例代码请参考 `test_smart_queue.py` 文件。
