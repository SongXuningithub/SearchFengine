import os
import logging
import json
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

from .inverted_index import InvertedIndexBuilder
from .bm25_indexer import BM25IndexBuilder
from config.settings import INDEXER_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndexManager:
    """索引管理器，统一管理不同类型的索引"""
    
    def __init__(self, db_path: str = "data/crawler/crawler.db", 
                 index_path: str = "data/indexer"):
        """
        初始化索引管理器
        
        Args:
            db_path: 数据库文件路径
            index_path: 索引存储路径
        """
        self.db_path = db_path
        self.index_path = index_path
        
        # 创建索引目录
        os.makedirs(index_path, exist_ok=True)
        
        # 索引构建器
        self.basic_indexer: Optional[InvertedIndexBuilder] = None
        self.bm25_indexer: Optional[BM25IndexBuilder] = None
        
        # 索引状态
        self.index_status = self._load_index_status()
        
        logger.info("IndexManager initialized")
    
    def _load_index_status(self) -> Dict[str, Any]:
        """加载索引状态"""
        status_file = os.path.join(self.index_path, "index_status.json")
        if os.path.exists(status_file):
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading index status: {e}")
        
        return {
            'basic_index': {'built': False, 'last_updated': None},
            'bm25_index': {'built': False, 'last_updated': None}
        }
    
    def _save_index_status(self):
        """保存索引状态"""
        status_file = os.path.join(self.index_path, "index_status.json")
        try:
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(self.index_status, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving index status: {e}")
    
    def build_basic_index(self, num_shards: int = 16, batch_size: int = 1000, 
                         max_memory_size: int = 10000) -> bool:
        """构建基础倒排索引"""
        try:
            logger.info("Building basic inverted index...")
            
            # 创建索引构建器
            self.basic_indexer = InvertedIndexBuilder(
                db_path=self.db_path,
                index_path=self.index_path,
                num_shards=num_shards,
                batch_size=batch_size,
                max_memory_size=max_memory_size
            )
            
            # 构建索引
            self.basic_indexer.build_index()
            
            # 更新状态
            self.index_status['basic_index']['built'] = True
            self.index_status['basic_index']['last_updated'] = time.time()
            self._save_index_status()
            
            logger.info("Basic inverted index built successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error building basic index: {e}")
            return False
    
    def build_bm25_index(self, num_shards: int = 16, batch_size: int = 1000, 
                        max_memory_size: int = 10000) -> bool:
        """构建BM25倒排索引"""
        try:
            logger.info("Building BM25 inverted index...")
            
            # 创建BM25索引构建器
            self.bm25_indexer = BM25IndexBuilder(
                db_path=self.db_path,
                index_path=self.index_path,
                num_shards=num_shards,
                batch_size=batch_size,
                max_memory_size=max_memory_size
            )
            
            # 构建索引
            self.bm25_indexer.build_index()
            
            # 更新状态
            self.index_status['bm25_index']['built'] = True
            self.index_status['bm25_index']['last_updated'] = time.time()
            self._save_index_status()
            
            logger.info("BM25 inverted index built successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error building BM25 index: {e}")
            return False
    
    def build_all_indexes(self, num_shards: int = 16, batch_size: int = 1000, 
                         max_memory_size: int = 10000) -> Dict[str, bool]:
        """构建所有类型的索引"""
        results = {}
        
        # 构建基础索引
        results['basic_index'] = self.build_basic_index(
            num_shards=num_shards,
            batch_size=batch_size,
            max_memory_size=max_memory_size
        )
        
        # 构建BM25索引
        results['bm25_index'] = self.build_bm25_index(
            num_shards=num_shards,
            batch_size=batch_size,
            max_memory_size=max_memory_size
        )
        
        return results
    
    def load_basic_index(self) -> Optional[InvertedIndexBuilder]:
        """加载基础索引"""
        if not self.index_status['basic_index']['built']:
            logger.warning("Basic index not built yet")
            return None
        
        try:
            # 检查索引文件是否存在
            shard_files = [f for f in os.listdir(self.index_path) if f.startswith('shard_') and f.endswith('.pkl')]
            if not shard_files:
                logger.warning("No basic index files found")
                return None
            
            # 创建索引构建器（用于搜索）
            self.basic_indexer = InvertedIndexBuilder(
                db_path=self.db_path,
                index_path=self.index_path,
                num_shards=64,  # 默认分片数
                batch_size=1000,
                max_memory_size=10000
            )
            
            logger.info("Basic index loaded successfully")
            return self.basic_indexer
            
        except Exception as e:
            logger.error(f"Error loading basic index: {e}")
            return None
    
    def load_bm25_index(self) -> Optional[BM25IndexBuilder]:
        """加载BM25索引"""
        if not self.index_status['bm25_index']['built']:
            logger.warning("BM25 index not built yet")
            return None
        
        try:
            # 检查索引文件是否存在
            shard_files = [f for f in os.listdir(self.index_path) if f.startswith('bm25_shard_') and f.endswith('.pkl')]
            if not shard_files:
                logger.warning("No BM25 index files found")
                return None
            
            # 创建BM25索引构建器（用于搜索）
            self.bm25_indexer = BM25IndexBuilder(
                db_path=self.db_path,
                index_path=self.index_path,
                num_shards=16,  # 默认分片数
                batch_size=1000,
                max_memory_size=10000
            )
            
            logger.info("BM25 index loaded successfully")
            return self.bm25_indexer
            
        except Exception as e:
            logger.error(f"Error loading BM25 index: {e}")
            return None
    
    def search(self, query: str, index_type: str = "bm25", max_results: int = 20) -> List[Dict]:
        """搜索功能
        
        Args:
            query: 查询字符串
            index_type: 索引类型 ("basic" 或 "bm25")
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        if index_type == "basic":
            if not self.basic_indexer:
                self.basic_indexer = self.load_basic_index()
            
            if self.basic_indexer:
                return self.basic_indexer.search(query, max_results)
            else:
                logger.error("Basic index not available")
                return []
                
        elif index_type == "bm25":
            if not self.bm25_indexer:
                self.bm25_indexer = self.load_bm25_index()
            
            if self.bm25_indexer:
                return self.bm25_indexer.search(query, max_results)
            else:
                logger.error("BM25 index not available")
                return []
        else:
            logger.error(f"Unknown index type: {index_type}")
            return []
    
    def get_index_stats(self, index_type: str = "bm25") -> Dict[str, Any]:
        """获取索引统计信息"""
        if index_type == "basic":
            if not self.basic_indexer:
                self.basic_indexer = self.load_basic_index()
            
            if self.basic_indexer:
                return self.basic_indexer.get_stats()
            else:
                return {}
                
        elif index_type == "bm25":
            if not self.bm25_indexer:
                self.bm25_indexer = self.load_bm25_index()
            
            if self.bm25_indexer:
                return self.bm25_indexer.get_stats()
            else:
                return {}
        else:
            logger.error(f"Unknown index type: {index_type}")
            return {}
    
    def get_shard_info(self, index_type: str = "bm25") -> Dict[int, Dict]:
        """获取分片信息"""
        if index_type == "basic":
            if not self.basic_indexer:
                self.basic_indexer = self.load_basic_index()
            
            if self.basic_indexer:
                return self.basic_indexer.get_shard_info()
            else:
                return {}
                
        elif index_type == "bm25":
            if not self.bm25_indexer:
                self.bm25_indexer = self.load_bm25_index()
            
            if self.bm25_indexer:
                return self.bm25_indexer.get_shard_info()
            else:
                return {}
        else:
            logger.error(f"Unknown index type: {index_type}")
            return {}
    
    def get_index_status(self) -> Dict[str, Any]:
        """获取索引状态"""
        return self.index_status.copy()
    
    def check_database(self) -> Dict[str, Any]:
        """检查数据库状态"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查pages表
            cursor.execute("SELECT COUNT(*) FROM pages")
            total_docs = cursor.fetchone()[0]
            
            # 检查最近更新的文档
            cursor.execute("""
                SELECT COUNT(*) FROM pages 
                WHERE crawl_time > ?
            """, (time.time() - 86400,))  # 最近24小时
            recent_docs = cursor.fetchone()[0]
            
            # 检查文档长度分布
            cursor.execute("""
                SELECT AVG(LENGTH(content)), MIN(LENGTH(content)), MAX(LENGTH(content))
                FROM pages
            """)
            content_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'total_documents': total_docs,
                'recent_documents': recent_docs,
                'avg_content_length': content_stats[0] if content_stats[0] else 0,
                'min_content_length': content_stats[1] if content_stats[1] else 0,
                'max_content_length': content_stats[2] if content_stats[2] else 0
            }
            
        except Exception as e:
            logger.error(f"Error checking database: {e}")
            return {'error': str(e)}
    
    def cleanup_old_indexes(self, keep_days: int = 7):
        """清理旧的索引文件"""
        try:
            current_time = time.time()
            cutoff_time = current_time - (keep_days * 86400)
            
            cleaned_files = 0
            for file_path in Path(self.index_path).glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > cutoff_time:
                        file_path.unlink()
                        cleaned_files += 1
            
            logger.info(f"Cleaned up {cleaned_files} old index files")
            
        except Exception as e:
            logger.error(f"Error cleaning up old indexes: {e}")

def main():
    """主函数，用于测试索引管理器"""
    # 创建索引管理器
    manager = IndexManager(
        db_path="data/crawler/crawler.db",
        index_path="data/indexer"
    )
    
    # 检查数据库状态
    db_status = manager.check_database()
    print("Database status:")
    for key, value in db_status.items():
        print(f"  {key}: {value}")
    
    # 检查索引状态
    index_status = manager.get_index_status()
    print("\nIndex status:")
    for index_type, status in index_status.items():
        print(f"  {index_type}: {'Built' if status['built'] else 'Not built'}")
        if status['last_updated']:
            print(f"    Last updated: {time.ctime(status['last_updated'])}")
    
    # 构建所有索引
    print("\nBuilding all indexes...")
    results = manager.build_all_indexes(
        num_shards=16,
        batch_size=1000,
        max_memory_size=10000
    )
    
    for index_type, success in results.items():
        print(f"  {index_type}: {'Success' if success else 'Failed'}")
    
    # 测试搜索
    if results['bm25_index']:
        print("\nTesting search...")
        test_queries = ["股票", "投资", "基金", "比特币"]
        
        for query in test_queries:
            results = manager.search(query, index_type="bm25", max_results=3)
            print(f"\nSearch results for '{query}':")
            for result in results:
                print(f"  Doc {result['doc_id']}: {result['score']:.4f}")
    
    # 获取统计信息
    if results['bm25_index']:
        stats = manager.get_index_stats("bm25")
        print(f"\nBM25 Index Statistics:")
        for key, value in stats.items():
            if key != 'doc_lengths':  # 跳过大的字典
                print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
