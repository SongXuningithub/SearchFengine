import sqlite3
import pickle
import hashlib
import os
import logging
import time
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict, deque
import threading
from dataclasses import dataclass
import json

from utils.text_processor import TextProcessor
from config.settings import INDEXER_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Posting:
    """倒排索引中的倒排列表项"""
    doc_id: int
    positions: List[int]  # 词在文档中的位置
    tf: int  # 词频
    
    def to_dict(self) -> Dict:
        return {
            'doc_id': self.doc_id,
            'positions': self.positions,
            'tf': self.tf
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Posting':
        return cls(
            doc_id=data['doc_id'],
            positions=data['positions'],
            tf=data['tf']
        )

class InvertedIndexShard:
    """倒排索引分片，负责管理单个分片的内存和磁盘存储"""
    
    def __init__(self, shard_id: int, base_path: str, max_memory_size: int = 100):
        self.shard_id = shard_id
        self.base_path = base_path
        self.max_memory_size = max_memory_size
        
        # 内存中的倒排索引
        self.memory_index: Dict[str, List[Posting]] = {}
        self.memory_size = 0
        
        # 磁盘文件路径
        self.disk_file = os.path.join(base_path, f"shard_{shard_id}.pkl")
        self.metadata_file = os.path.join(base_path, f"shard_{shard_id}_metadata.json")
        
        # 锁用于线程安全
        self.lock = threading.Lock()
        
        # 清空磁盘文件
        if os.path.exists(self.disk_file):
            os.remove(self.disk_file)
        if os.path.exists(self.metadata_file):
            os.remove(self.metadata_file)

        # 加载元数据
        self._load_metadata()
        
        logger.info(f"Initialized shard {shard_id} with max_memory_size={max_memory_size}")
    
    def _load_metadata(self):
        """加载分片元数据"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                logger.error(f"Error loading metadata for shard {self.shard_id}: {e}")
                self.metadata = {'term_count': 0, 'doc_count': 0}
        else:
            self.metadata = {'term_count': 0, 'doc_count': 0}
    
    def _save_metadata(self):
        """保存分片元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving metadata for shard {self.shard_id}: {e}")
    
    def add_posting(self, term: str, posting: Posting):
        """添加倒排列表项"""
        with self.lock:
            if term not in self.memory_index:
                self.memory_index[term] = []
                self.memory_size += 1
            
            self.memory_index[term].append(posting)
            self.memory_size += 1
            
            # 检查是否需要刷新到磁盘
            if self.memory_size >= self.max_memory_size:
                self._flush_to_disk()
    
    def _flush_to_disk(self):
        """将内存中的索引刷新到磁盘"""
        if not self.memory_index:
            return
        
        try:
            # 读取现有的磁盘索引
            existing_index = self._load_from_disk()
            
            # 合并内存和磁盘索引
            for term, postings in self.memory_index.items():
                if term in existing_index:
                    # 合并倒排列表
                    existing_index[term].extend(postings)
                    # 按doc_id排序
                    existing_index[term].sort(key=lambda x: x.doc_id)
                else:
                    existing_index[term] = postings
            
            # 保存到磁盘
            with open(self.disk_file, 'wb') as f:
                pickle.dump(existing_index, f)
            
            # 更新元数据
            self.metadata['term_count'] = len(existing_index)
            self.metadata['doc_count'] = sum(len(postings) for postings in existing_index.values())
            self._save_metadata()
            
            # 清空内存
            self.memory_index.clear()
            self.memory_size = 0
            
            logger.info(f"Flushed shard {self.shard_id} to disk, terms: {self.metadata['term_count']}")
            
        except Exception as e:
            logger.error(f"Error flushing shard {self.shard_id} to disk: {e}")
    
    def _load_from_disk(self) -> Dict[str, List[Posting]]:
        """从磁盘加载索引"""
        if not os.path.exists(self.disk_file):
            return {}
        
        try:
            with open(self.disk_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Error loading shard {self.shard_id} from disk: {e}")
            return {}
    
    def get_postings(self, term: str) -> List[Posting]:
        """获取指定term的倒排列表"""
        with self.lock:
            # 首先检查内存
            if term in self.memory_index:
                return self.memory_index[term].copy()
            
            # 检查磁盘
            disk_index = self._load_from_disk()
            if term in disk_index:
                return disk_index[term].copy()
            
            return []
    
    def get_all_terms(self) -> Set[str]:
        """获取所有term"""
        with self.lock:
            terms = set(self.memory_index.keys())
            
            # 添加磁盘中的term
            disk_index = self._load_from_disk()
            terms.update(disk_index.keys())
            
            return terms
    
    def finalize(self):
        """最终化分片，确保所有数据都写入磁盘"""
        with self.lock:
            self._flush_to_disk()
            logger.info(f"Finalized shard {self.shard_id}")

class InvertedIndexBuilder:
    """倒排索引构建器"""
    
    def __init__(self, db_path: str = "data/crawler/crawler.db", 
                 index_path: str = "data/indexer", 
                 num_shards: int = 16,
                 batch_size: int = 1000,
                 max_memory_size: int = 10000):
        """
        初始化倒排索引构建器
        
        Args:
            db_path: 数据库文件路径
            index_path: 索引存储路径
            num_shards: 分片数量
            batch_size: 批处理大小
            max_memory_size: 每个分片的最大内存大小
        """
        self.db_path = db_path
        self.index_path = index_path
        self.num_shards = num_shards
        self.batch_size = batch_size
        self.max_memory_size = max_memory_size
        
        # 文本处理器
        self.text_processor = TextProcessor()
        
        # 分片管理器
        self.shards: Dict[int, InvertedIndexShard] = {}
        self._init_shards()
        
        # 统计信息
        self.stats = {
            'total_docs': 0,
            'total_terms': 0,
            'total_postings': 0,
            'processing_time': 0
        }
        
        # 创建索引目录
        os.makedirs(index_path, exist_ok=True)
        
        logger.info(f"Initialized InvertedIndexBuilder with {num_shards} shards")
    
    def _init_shards(self):
        """初始化所有分片"""
        for i in range(self.num_shards):
            self.shards[i] = InvertedIndexShard(
                shard_id=i,
                base_path=self.index_path,
                max_memory_size=self.max_memory_size
            )
    
    def _get_shard_id(self, term: str) -> int:
        """根据term计算分片ID"""
        # 使用哈希函数计算分片ID
        hash_value = hashlib.md5(term.encode('utf-8')).hexdigest()
        return int(hash_value, 16) % self.num_shards
    
    def _process_document(self, doc_id: int, title: str, content: str) -> Dict[str, List[int]]:
        """处理单个文档，返回term到位置的映射"""
        # 合并标题和内容
        full_text = f"{title} {content}"
        
        # 分词
        tokens = self.text_processor.tokenize(full_text)
        
        # 构建term到位置的映射
        term_positions = defaultdict(list)
        for pos, token in enumerate(tokens):
            term_positions[token].append(pos)
        
        return dict(term_positions)
    
    def build_index(self):
        """构建倒排索引"""
        start_time = time.time()
        logger.info("Starting inverted index construction...")
        
        try:
            # 连接数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取总文档数
            cursor.execute("SELECT COUNT(*) FROM pages")
            total_docs = cursor.fetchone()[0]
            logger.info(f"Total documents to process: {total_docs}")
            
            if total_docs == 0:
                logger.warning("No documents found in database")
                return
            
            # 分批处理文档
            offset = 0
            processed_docs = 0
            
            while offset < total_docs:
                # 获取一批文档
                cursor.execute("""
                    SELECT id, url, title, content, keywords 
                    FROM pages 
                    ORDER BY id 
                    LIMIT ? OFFSET ?
                """, (self.batch_size, offset))
                
                batch_docs = cursor.fetchall()
                if not batch_docs:
                    break
                
                # 处理这批文档
                self._process_batch(batch_docs)
                
                processed_docs += len(batch_docs)
                offset += self.batch_size
                
                logger.info(f"Processed {processed_docs}/{total_docs} documents")
            
            # 最终化所有分片
            self._finalize_shards()
            
            # 更新统计信息
            self.stats['processing_time'] = time.time() - start_time
            self.stats['total_docs'] = processed_docs
            
            # 保存统计信息
            self._save_stats()
            
            logger.info(f"Index construction completed in {self.stats['processing_time']:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error building index: {e}")
            raise
        finally:
            conn.close()
    
    def _process_batch(self, batch_docs: List[Tuple]):
        """处理一批文档"""
        for doc_id, url, title, content, keywords in batch_docs:
            try:
                # 处理文档
                term_positions = self._process_document(doc_id, title, content)
                
                # 为每个term创建posting并添加到对应分片
                for term, positions in term_positions.items():
                    posting = Posting(
                        doc_id=doc_id,
                        positions=positions,
                        tf=len(positions)
                    )
                    
                    # 计算分片ID
                    shard_id = self._get_shard_id(term)
                    
                    # 添加到对应分片
                    self.shards[shard_id].add_posting(term, posting)
                    
                    # 更新统计信息
                    self.stats['total_postings'] += 1
                
            except Exception as e:
                logger.error(f"Error processing document {doc_id}: {e}")
    
    def _finalize_shards(self):
        """最终化所有分片"""
        logger.info("Finalizing all shards...")
        
        for shard in self.shards.values():
            shard.finalize()
        
        # 计算总term数
        all_terms = set()
        for shard in self.shards.values():
            all_terms.update(shard.get_all_terms())
        
        self.stats['total_terms'] = len(all_terms)
        logger.info(f"Total unique terms: {self.stats['total_terms']}")
    
    def _save_stats(self):
        """保存统计信息"""
        stats_file = os.path.join(self.index_path, "index_stats.json")
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving stats: {e}")

    def get_posting(self, term: str) -> List[Posting]:
        """获取指定term的倒排列表"""
        shard_id = self._get_shard_id(term)
        return self.shards[shard_id].get_postings(term)
    
    def search(self, query: str, max_results: int = 20) -> List[Dict]:
        """搜索功能（简单实现）"""
        # 分词
        query_terms = self.text_processor.tokenize(query)
        
        if not query_terms:
            return []
        
        # 收集所有相关文档
        doc_scores = defaultdict(float)
        
        for term in query_terms:
            shard_id = self._get_shard_id(term)
            postings = self.shards[shard_id].get_postings(term)
            
            for posting in postings:
                # 简单的TF-IDF评分
                score = posting.tf
                doc_scores[posting.doc_id] += score
        
        # 排序并返回结果
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in sorted_docs[:max_results]:
            # 这里需要从数据库获取文档详情
            # 简化实现，只返回doc_id和score
            results.append({
                'doc_id': doc_id,
                'score': score
            })
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        return self.stats.copy()
    
    def get_shard_info(self) -> Dict[int, Dict]:
        """获取分片信息"""
        shard_info = {}
        for shard_id, shard in self.shards.items():
            shard_info[shard_id] = {
                'memory_size': shard.memory_size,
                'term_count': len(shard.get_all_terms()),
                'metadata': shard.metadata
            }
        return shard_info

def main():
    """主函数，用于测试索引构建"""
    # 创建索引构建器
    builder = InvertedIndexBuilder(
        db_path="data/crawler/crawler.db",
        index_path="data/indexer",
        num_shards=16,
        batch_size=1000,
        max_memory_size=10000
    )
    
    # 构建索引
    builder.build_index()
    
    # 打印统计信息
    stats = builder.get_stats()
    print("Index construction completed!")
    print(f"Total documents: {stats['total_docs']}")
    print(f"Total terms: {stats['total_terms']}")
    print(f"Total postings: {stats['total_postings']}")
    print(f"Processing time: {stats['processing_time']:.2f} seconds")
    
    # 打印分片信息
    shard_info = builder.get_shard_info()
    print("\nShard information:")
    for shard_id, info in shard_info.items():
        print(f"Shard {shard_id}: {info['term_count']} terms, {info['memory_size']} in memory")

if __name__ == "__main__":
    main()
