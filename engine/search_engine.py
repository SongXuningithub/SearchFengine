import math
import logging
import sqlite3
import hashlib
import pickle
import os
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import time

from config.settings import SEARCH_CONFIG
from utils.text_processor import TextProcessor
from indexer.index_manager import IndexManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BM25SearchEngine:
    """基于BM25算法的搜索引擎，使用分片索引"""
    
    def __init__(self, db_path: str = "data/crawler/crawler.db", 
                 index_path: str = "data/indexer"):
        self.config = SEARCH_CONFIG
        self.text_processor = TextProcessor()
        
        # 数据库和索引路径
        self.db_path = db_path
        self.index_path = index_path
        
        # BM25参数
        self.k1 = self.config['bm25_k1']
        self.b = self.config['bm25_b']
        
        # 索引管理器
        self.index_manager = IndexManager(db_path, index_path)
        
        # 文档缓存
        self.doc_cache: Dict[int, Dict] = {}
        self.doc_stats = {
            'total_docs': 0,
            'avg_doc_length': 0
        }
        
        # 加载索引和文档统计
        self._load_index()
        self._load_document_stats()
        
        logger.info(f"BM25SearchEngine initialized with {self.doc_stats['total_docs']} documents")
    
    def _load_index(self):
        """加载索引"""
        try:
            # 尝试加载BM25索引
            self.bm25_indexer = self.index_manager.load_bm25_index()
            if not self.bm25_indexer:
                logger.warning("BM25 index not found. Please run the indexer first.")
                return
            
            logger.info("BM25 index loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading index: {e}")
    
    def _load_document_stats(self):
        """加载文档统计信息"""
        try:
            # 从数据库获取文档统计
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取总文档数
            cursor.execute("SELECT COUNT(*) FROM pages")
            self.doc_stats['total_docs'] = cursor.fetchone()[0]
            
            # 获取文档长度统计
            cursor.execute("""
                SELECT AVG(LENGTH(content)), MIN(LENGTH(content)), MAX(LENGTH(content))
                FROM pages
            """)
            content_stats = cursor.fetchone()
            
            if content_stats and content_stats[0]:
                self.doc_stats['avg_doc_length'] = content_stats[0]
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error loading document stats: {e}")
    
    def _get_document(self, doc_id: int) -> Optional[Dict]:
        """从数据库获取文档"""
        if doc_id in self.doc_cache:
            return self.doc_cache[doc_id]
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, url, title, content, keywords, domain, crawl_time
                FROM pages WHERE id = ?
            """, (doc_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                doc = {
                    'id': row[0],
                    'url': row[1],
                    'title': row[2],
                    'content': row[3],
                    'keywords': row[4].split(',') if row[4] else [],
                    'domain': row[5],
                    'crawl_time': row[6]
                }
                
                # 缓存文档
                self.doc_cache[doc_id] = doc
                return doc
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {e}")
            return None
    
    def search(self, query: str, max_results: int = None) -> List[Dict]:
        """搜索功能"""
        if max_results is None:
            max_results = self.config['max_results']
        
        if not self.bm25_indexer:
            logger.warning("BM25 index not available. Please run the indexer first.")
            return []
        
        # 查询分词
        query_tokens = self.text_processor.tokenize(query)
        
        if not query_tokens:
            return []
        
        # 使用索引管理器进行搜索
        search_results = self.index_manager.search(
            query=query,
            index_type="bm25",
            max_results=max_results
        )
        
        # 获取完整文档信息
        results = []
        for result in search_results:
            doc_id = result['doc_id']
            score = result['score']
            
            doc = self._get_document(doc_id)
            if doc:
                doc['score'] = score
                doc['highlights'] = self._generate_highlights(doc, query_tokens)
                results.append(doc)
        
        return results
    
    def _generate_highlights(self, doc: Dict, query_tokens: List[str]) -> List[str]:
        """生成高亮片段"""
        content = doc.get('content', '')
        title = doc.get('title', '')
        
        highlights = []
        
        # 在标题中查找匹配
        for token in query_tokens:
            if token.lower() in title.lower():
                highlights.append(f"标题: {title}")
                break
        
        # 在内容中查找匹配
        if content:
            # 简单的片段提取
            words = content.split()
            for i, word in enumerate(words):
                for token in query_tokens:
                    if token.lower() in word.lower():
                        start = max(0, i - 5)
                        end = min(len(words), i + 6)
                        snippet = ' '.join(words[start:end])
                        if snippet not in highlights:
                            highlights.append(f"...{snippet}...")
                        break
        
        return highlights[:3]  # 最多返回3个片段
    
    def search_by_domain(self, domain: str, max_results: int = None) -> List[Dict]:
        """按域名搜索"""
        if max_results is None:
            max_results = self.config['max_results']
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, url, title, content, keywords, domain, crawl_time
                FROM pages 
                WHERE domain LIKE ? 
                ORDER BY crawl_time DESC
                LIMIT ?
            """, (f"%{domain}%", max_results))
            
            results = []
            for row in cursor.fetchall():
                doc = {
                    'id': row[0],
                    'url': row[1],
                    'title': row[2],
                    'content': row[3],
                    'keywords': row[4].split(',') if row[4] else [],
                    'domain': row[5],
                    'crawl_time': row[6]
                }
                results.append(doc)
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error searching by domain: {e}")
            return []
    
    def search_by_keywords(self, keywords: List[str], max_results: int = None) -> List[Dict]:
        """按关键词搜索"""
        if max_results is None:
            max_results = self.config['max_results']
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 构建关键词查询条件
            keyword_conditions = []
            params = []
            for keyword in keywords:
                keyword_conditions.append("keywords LIKE ?")
                params.append(f"%{keyword}%")
            
            where_clause = " OR ".join(keyword_conditions)
            
            cursor.execute(f"""
                SELECT id, url, title, content, keywords, domain, crawl_time
                FROM pages 
                WHERE {where_clause}
                ORDER BY crawl_time DESC
                LIMIT ?
            """, params + [max_results])
            
            results = []
            for row in cursor.fetchall():
                doc = {
                    'id': row[0],
                    'url': row[1],
                    'title': row[2],
                    'content': row[3],
                    'keywords': row[4].split(',') if row[4] else [],
                    'domain': row[5],
                    'crawl_time': row[6]
                }
                
                # 计算关键词匹配数
                doc_keywords = doc['keywords']
                matches = sum(1 for kw in keywords if kw.lower() in [dk.lower() for dk in doc_keywords])
                doc['keyword_matches'] = matches
                
                results.append(doc)
            
            # 按匹配数排序
            results.sort(key=lambda x: x['keyword_matches'], reverse=True)
            conn.close()
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching by keywords: {e}")
            return []
    
    def get_search_stats(self) -> Dict:
        """获取搜索统计信息"""
        stats = {
            'total_documents': self.doc_stats['total_docs'],
            'avg_doc_length': self.doc_stats['avg_doc_length'],
            'bm25_k1': self.k1,
            'bm25_b': self.b,
            'index_available': self.bm25_indexer is not None
        }
        
        # 获取索引统计信息
        if self.bm25_indexer:
            index_stats = self.index_manager.get_index_stats("bm25")
            stats.update({
                'total_terms': index_stats.get('total_terms', 0),
                'total_postings': index_stats.get('total_postings', 0),
                'processing_time': index_stats.get('processing_time', 0)
            })
        
        return stats
    
    def suggest_queries(self, partial_query: str, max_suggestions: int = 5) -> List[str]:
        """查询建议"""
        if not partial_query:
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 从标题中查找建议
            cursor.execute("""
                SELECT title FROM pages 
                WHERE title LIKE ? 
                LIMIT 100
            """, (f"%{partial_query}%",))
            
            suggestions = []
            partial_lower = partial_query.lower()
            
            for (title,) in cursor.fetchall():
                if partial_lower in title.lower():
                    # 提取包含查询词的短语
                    words = title.split()
                    for i, word in enumerate(words):
                        if partial_lower in word.lower():
                            start = max(0, i - 2)
                            end = min(len(words), i + 3)
                            suggestion = ' '.join(words[start:end])
                            if suggestion not in suggestions:
                                suggestions.append(suggestion)
                            break
                
                if len(suggestions) >= max_suggestions:
                    break
            
            conn.close()
            return suggestions[:max_suggestions]
            
        except Exception as e:
            logger.error(f"Error generating query suggestions: {e}")
            return []
    
    def get_popular_keywords(self, top_k: int = 20) -> List[Tuple[str, int]]:
        """获取热门关键词"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT keywords FROM pages 
                WHERE keywords IS NOT NULL AND keywords != ''
            """)
            
            keyword_freq = defaultdict(int)
            
            for (keywords_str,) in cursor.fetchall():
                if keywords_str:
                    keywords = keywords_str.split(',')
                    for keyword in keywords:
                        keyword = keyword.strip()
                        if keyword:
                            keyword_freq[keyword] += 1
            
            conn.close()
            
            # 按频率排序
            sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
            return sorted_keywords[:top_k]
            
        except Exception as e:
            logger.error(f"Error getting popular keywords: {e}")
            return []
    
    def get_index_status(self) -> Dict:
        """获取索引状态"""
        return self.index_manager.get_index_status()
    
    def get_shard_info(self) -> Dict:
        """获取分片信息"""
        return self.index_manager.get_shard_info("bm25")
    
    def clear_cache(self):
        """清空文档缓存"""
        self.doc_cache.clear()
        logger.info("Document cache cleared")

# 创建全局搜索引擎实例
search_engine = BM25SearchEngine() 