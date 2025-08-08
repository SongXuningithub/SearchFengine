"""
搜索引擎索引系统

这是一个高性能的倒排索引构建系统，支持分批处理、哈希分片和内存管理。

主要组件:
- InvertedIndexBuilder: 基础倒排索引构建器
- BM25IndexBuilder: BM25算法索引构建器  
- IndexManager: 统一索引管理器
"""

from .inverted_index import InvertedIndexBuilder, Posting
from .bm25_indexer import BM25IndexBuilder, BM25Posting
from .index_manager import IndexManager

__version__ = "1.0.0"
__author__ = "Search Engine Team"

__all__ = [
    "InvertedIndexBuilder",
    "BM25IndexBuilder", 
    "IndexManager",
    "Posting",
    "BM25Posting"
]
