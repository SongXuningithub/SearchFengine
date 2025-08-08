import math
import sqlite3
import logging
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import time

from utils.text_processor import TextProcessor
from indexer.inverted_index import Posting
from engine.index_adapter import AdaptedInvertedIndexBuilder
from config.settings import SEARCH_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchEngine:
    """搜索引擎引擎类"""
    
    def __init__(self, 
                 index_builder: AdaptedInvertedIndexBuilder,
                 db_path: str = "data/crawler/crawler.db"):
        """
        初始化搜索引擎
        
        Args:
            index_builder: 适配后的倒排索引构建器实例
            db_path: 数据库文件路径
        """
        self.index_builder = index_builder
        self.db_path = db_path
        self.text_processor = TextProcessor()
        
        # BM25参数
        self.k1 = SEARCH_CONFIG.get('bm25_k1', 1.5)
        self.b = SEARCH_CONFIG.get('bm25_b', 0.75)
        self.max_results = SEARCH_CONFIG.get('max_results', 20)
        
        # 文档统计信息缓存
        self.doc_stats_cache = {}
        self._load_document_stats()
        
        logger.info("SearchEngine initialized")
    
    def _load_document_stats(self):
        """加载文档统计信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取文档总数
            cursor.execute("SELECT COUNT(*) FROM pages")
            self.total_docs = cursor.fetchone()[0]
            
            # 获取文档长度信息
            cursor.execute("""
                SELECT id, LENGTH(title) + LENGTH(content) as doc_length 
                FROM pages
            """)
            
            self.doc_lengths = {}
            self.avg_doc_length = 0
            total_length = 0
            
            for doc_id, doc_length in cursor.fetchall():
                self.doc_lengths[doc_id] = doc_length
                total_length += doc_length
            
            if self.total_docs > 0:
                self.avg_doc_length = total_length / self.total_docs
            
            conn.close()
            logger.info(f"Loaded document stats: {self.total_docs} docs, avg_length: {self.avg_doc_length:.2f}")
            
        except Exception as e:
            logger.error(f"Error loading document stats: {e}")
            self.total_docs = 0
            self.doc_lengths = {}
            self.avg_doc_length = 0
    
    def tokenize_query(self, query: str) -> List[str]:
        """对查询进行分词"""
        if not query:
            return []
        
        # 使用文本处理器进行分词
        tokens = self.text_processor.tokenize(query)
        logger.info(f"Query '{query}' tokenized to: {tokens}")
        return tokens
    
    def get_postings_for_terms(self, terms: List[str]) -> Dict[str, List[Posting]]:
        """获取多个term的倒排列表"""
        postings_dict = {}
        
        for term in terms:
            postings = self.index_builder.get_posting(term)
            if postings:
                postings_dict[term] = postings
                logger.debug(f"Term '{term}' has {len(postings)} postings")
            else:
                logger.debug(f"Term '{term}' has no postings")
        
        return postings_dict
    
    def intersect_postings(self, postings_dict: Dict[str, List[Posting]]) -> Set[int]:
        """对多个term的倒排列表进行求交"""
        if not postings_dict:
            return set()
        
        # 获取所有term的文档ID集合
        doc_sets = []
        for term, postings in postings_dict.items():
            doc_ids = {posting.doc_id for posting in postings}
            doc_sets.append(doc_ids)
        
        # 求交集
        if doc_sets:
            intersection = doc_sets[0]
            for doc_set in doc_sets[1:]:
                intersection = intersection.intersection(doc_set)
            
            logger.info(f"Intersection found {len(intersection)} documents")
            return intersection
        
        return set()
    
    def calculate_bm25_score(self, 
                           doc_id: int, 
                           query_terms: List[str], 
                           postings_dict: Dict[str, List[Posting]]) -> float:
        """计算BM25相关性分数"""
        if doc_id not in self.doc_lengths:
            return 0.0
        
        doc_length = self.doc_lengths[doc_id]
        score = 0.0
        
        for term in query_terms:
            if term not in postings_dict:
                continue
            
            # 找到该term在文档中的posting
            term_posting = None
            for posting in postings_dict[term]:
                if posting.doc_id == doc_id:
                    term_posting = posting
                    break
            
            if term_posting is None:
                continue
            
            # 计算term在文档中的频率
            tf = term_posting.tf
            
            # 计算逆文档频率 (IDF)
            df = len(postings_dict[term])  # 包含该term的文档数
            if df == 0:
                continue
            
            idf = math.log((self.total_docs - df + 0.5) / (df + 0.5))
            
            # 计算BM25分数
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avg_doc_length))
            
            if denominator > 0:
                bm25_score = idf * (numerator / denominator)
                score += bm25_score
        
        return score
    
    def search(self, query: str, max_results: Optional[int] = None) -> List[Dict]:
        """
        执行搜索
        
        Args:
            query: 查询字符串
            max_results: 最大结果数，如果为None则使用默认值
            
        Returns:
            搜索结果列表，每个结果包含doc_id, score, title, url等信息
        """
        start_time = time.time()
        
        if max_results is None:
            max_results = self.max_results
        
        # 1. 对查询进行分词
        query_terms = self.tokenize_query(query)
        if not query_terms:
            logger.warning("No valid terms found in query")
            return []
        
        # 2. 获取所有term的倒排列表
        postings_dict = self.get_postings_for_terms(query_terms)
        if not postings_dict:
            logger.warning("No postings found for any query terms")
            return []
        
        # 3. 对倒排列表进行求交
        candidate_docs = self.intersect_postings(postings_dict)
        if not candidate_docs:
            logger.warning("No documents found in intersection")
            return []
        
        # 4. 对候选文档计算BM25分数
        doc_scores = {}
        for doc_id in candidate_docs:
            score = self.calculate_bm25_score(doc_id, query_terms, postings_dict)
            if score > 0:
                doc_scores[doc_id] = score
        
        # 5. 按分数排序
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 6. 获取文档详细信息
        results = self._get_document_details(sorted_docs[:max_results])
        
        search_time = time.time() - start_time
        logger.info(f"Search completed in {search_time:.3f}s, found {len(results)} results")
        
        return results
    
    def _get_document_details(self, doc_scores: List[Tuple[int, float]]) -> List[Dict]:
        """获取文档详细信息"""
        if not doc_scores:
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            results = []
            for doc_id, score in doc_scores:
                cursor.execute("""
                    SELECT id, url, title, content, keywords 
                    FROM pages 
                    WHERE id = ?
                """, (doc_id,))
                
                row = cursor.fetchone()
                if row:
                    doc_id, url, title, content, keywords = row
                    
                    # 截取内容摘要
                    content_preview = content[:200] + "..." if len(content) > 200 else content
                    
                    results.append({
                        'doc_id': doc_id,
                        'url': url,
                        'title': title,
                        'content_preview': content_preview,
                        'keywords': keywords,
                        'score': score
                    })
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting document details: {e}")
            # 返回简化结果
            return [{'doc_id': doc_id, 'score': score} for doc_id, score in doc_scores]
    
    def search_with_fallback(self, query: str, max_results: Optional[int] = None) -> List[Dict]:
        """
        带回退的搜索：如果求交结果为空，则使用OR逻辑
        
        Args:
            query: 查询字符串
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        # 首先尝试AND搜索（求交）
        results = self.search(query, max_results)
        
        if results:
            return results
        
        # 如果AND搜索没有结果，使用OR搜索
        logger.info("AND search returned no results, trying OR search")
        return self._or_search(query, max_results)
    
    def _or_search(self, query: str, max_results: Optional[int] = None) -> List[Dict]:
        """OR搜索：使用所有term的并集"""
        if max_results is None:
            max_results = self.max_results
        
        # 分词
        query_terms = self.tokenize_query(query)
        if not query_terms:
            return []
        
        # 获取所有term的倒排列表
        postings_dict = self.get_postings_for_terms(query_terms)
        if not postings_dict:
            return []
        
        # 收集所有文档ID
        all_docs = set()
        for term, postings in postings_dict.items():
            doc_ids = {posting.doc_id for posting in postings}
            all_docs.update(doc_ids)
        
        # 计算每个文档的BM25分数
        doc_scores = {}
        for doc_id in all_docs:
            score = self.calculate_bm25_score(doc_id, query_terms, postings_dict)
            if score > 0:
                doc_scores[doc_id] = score
        
        # 排序并获取详细信息
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        results = self._get_document_details(sorted_docs[:max_results])
        
        logger.info(f"OR search found {len(results)} results")
        return results
    
    def get_search_stats(self) -> Dict:
        """获取搜索统计信息"""
        return {
            'total_docs': self.total_docs,
            'avg_doc_length': self.avg_doc_length,
            'bm25_k1': self.k1,
            'bm25_b': self.b,
            'max_results': self.max_results
        }
