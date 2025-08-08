import sqlite3
import logging
import math
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
import time

from indexer.inverted_index import InvertedIndexReader, Posting
from utils.text_processor import TextProcessor
from config.settings import SEARCH_CONFIG

logger = logging.getLogger(__name__)

class SearchEngine:
    """搜索引擎核心类"""
    
    def __init__(self, 
                 index_path: str = "data/indexer",
                 db_path: str = "data/crawler/crawler.db",
                 num_shards: int = 64):
        """
        初始化搜索引擎
        
        Args:
            index_path: 索引文件路径
            db_path: 数据库文件路径
            num_shards: 索引分片数量
        """
        self.index_path = index_path
        self.db_path = db_path
        self.num_shards = num_shards
        
        # 初始化组件
        self.index_reader = InvertedIndexReader(index_path, num_shards)
        self.text_processor = TextProcessor()
        
        # BM25参数
        self.k1 = SEARCH_CONFIG.get('bm25_k1', 1.2)
        self.b = SEARCH_CONFIG.get('bm25_b', 0.75)
        
        # 加载文档统计信息
        self._load_document_stats()
        
        logger.info(f"Search engine initialized with {num_shards} shards")
    
    def _load_document_stats(self):
        """加载文档统计信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取文档总数和平均长度
            cursor.execute("SELECT COUNT(*) FROM pages")
            self.total_docs = cursor.fetchone()[0]
            
            # 计算平均文档长度
            cursor.execute("SELECT AVG(LENGTH(content)) FROM pages")
            avg_length = cursor.fetchone()[0]
            self.avg_doc_length = avg_length if avg_length else 100
            
            # 获取每个文档的长度
            cursor.execute("SELECT id, LENGTH(content) FROM pages")
            self.doc_lengths = dict(cursor.fetchall())
            
            conn.close()
            
            logger.info(f"Loaded {self.total_docs} documents, avg length: {self.avg_doc_length}")
            
        except Exception as e:
            logger.error(f"Error loading document stats: {e}")
            self.total_docs = 0
            self.avg_doc_length = 100
            self.doc_lengths = {}
    
    def search(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        执行搜索
        
        Args:
            query: 查询字符串
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        start_time = time.time()
        
        # 1. 查询预处理
        query_terms = self.text_processor.tokenize(query)
        print(f"query_terms: {query_terms}")
        if not query_terms:
            return []
        
        # 2. 获取倒排列表
        postings_lists = []
        print(f"query_terms: {query_terms}")
        for term in query_terms:
            postings = self.index_reader.get_posting(term)
            if postings:
                postings_lists.append((term, postings))
        print(f"postings_lists: {postings_lists}")
        if not postings_lists:
            return []
        
        # 3. 求交操作
        candidate_docs = self._intersect_postings(postings_lists)
        print(f"candidate_docs: {candidate_docs}")
        # 4. BM25评分
        scored_docs = self._calculate_bm25_scores(query_terms, candidate_docs)
        print(f"scored_docs: {scored_docs}")
        # 5. 排序并获取文档详情
        results = self._get_document_details(scored_docs, max_results)
        print(f"results: {results}")
        search_time = time.time() - start_time
        logger.info(f"Search completed in {search_time:.3f}s, found {len(results)} results")
        
        return results
    
    def _intersect_postings(self, postings_lists: List[Tuple[str, List[Posting]]]) -> Set[int]:
        """
        对倒排列表进行求交操作
        
        Args:
            postings_lists: [(term, postings), ...]
            
        Returns:
            包含所有查询词的文档ID集合
        """
        if not postings_lists:
            return set()
        
        # 按倒排列表长度排序，从最短的开始求交
        postings_lists.sort(key=lambda x: len(x[1]))
        
        # 获取第一个倒排列表的所有文档ID
        result = set(posting.doc_id for posting in postings_lists[0][1])
        
        # 与其他倒排列表求交
        for term, postings in postings_lists[1:]:
            current_docs = set(posting.doc_id for posting in postings)
            result = result.intersection(current_docs)
            
            if not result:  # 如果没有交集，提前返回
                break
        
        return result
    
    def _calculate_bm25_scores(self, query_terms: List[str], candidate_docs: Set[int]) -> List[Tuple[int, float]]:
        """
        计算BM25评分
        
        Args:
            query_terms: 查询词列表
            candidate_docs: 候选文档ID集合
            
        Returns:
            [(doc_id, score), ...]
        """
        doc_scores = defaultdict(float)
        
        for term in query_terms:
            # 计算IDF
            idf = self._calculate_idf(term)
            
            # 获取该词的倒排列表
            postings = self.index_reader.get_posting(term)
            
            for posting in postings:
                if posting.doc_id in candidate_docs:
                    # 计算TF
                    doc_length = self.doc_lengths.get(posting.doc_id, self.avg_doc_length)
                    tf = posting.tf
                    
                    # BM25公式
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length)
                    
                    if denominator > 0:
                        bm25_score = idf * (numerator / denominator)
                        doc_scores[posting.doc_id] += bm25_score
        
        # 转换为列表并排序
        scored_docs = [(doc_id, score) for doc_id, score in doc_scores.items() if score > 0]
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        return scored_docs
    
    def _calculate_idf(self, term: str) -> float:
        """
        计算逆文档频率(IDF)
        
        Args:
            term: 查询词
            
        Returns:
            IDF值
        """
        postings = self.index_reader.get_posting(term)
        df = len(postings)  # 文档频率
        
        if df == 0:
            return 0
        
        # 防止数学域错误
        if self.total_docs <= df:
            return 0
        
        # IDF = log((N - df + 0.5) / (df + 0.5))
        numerator = self.total_docs - df + 0.5
        denominator = df + 0.5
        
        if denominator <= 0 or numerator <= 0:
            return 0
        
        idf = math.log(numerator / denominator)
        return idf
    
    def _get_document_details(self, scored_docs: List[Tuple[int, float]], max_results: int) -> List[Dict]:
        """
        获取文档详细信息
        
        Args:
            scored_docs: [(doc_id, score), ...]
            max_results: 最大结果数
            
        Returns:
            文档详情列表
        """
        results = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for doc_id, score in scored_docs[:max_results]:
                cursor.execute(
                    "SELECT title, url, content, created_at FROM pages WHERE id = ?",
                    (doc_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    title, url, content, created_at = row
                    
                    # 提取摘要
                    summary = self._extract_summary(content, 200)
                    
                    results.append({
                        'doc_id': doc_id,
                        'title': title,
                        'url': url,
                        'summary': summary,
                        'score': round(score, 4),
                        'created_at': created_at
                    })
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error getting document details: {e}")
        
        return results
    
    def _extract_summary(self, content: str, max_length: int = 200) -> str:
        """
        提取文档摘要
        
        Args:
            content: 文档内容
            max_length: 最大长度
            
        Returns:
            摘要文本
        """
        if not content:
            return ""
        
        # 简单截取前max_length个字符
        summary = content[:max_length]
        
        # 如果截取位置在词中间，找到最后一个空格
        if len(content) > max_length:
            last_space = summary.rfind(' ')
            if last_space > max_length * 0.8:  # 如果空格位置合理
                summary = summary[:last_space]
        
        return summary + "..." if len(content) > max_length else summary
    
    def get_stats(self) -> Dict[str, Any]:
        """获取搜索引擎统计信息"""
        return {
            'total_documents': self.total_docs,
            'avg_document_length': round(self.avg_doc_length, 2),
            'num_shards': self.num_shards,
            'bm25_k1': self.k1,
            'bm25_b': self.b
        }
    
    def suggest(self, partial_query: str, max_suggestions: int = 5) -> List[str]:
        """
        查询建议
        
        Args:
            partial_query: 部分查询
            max_suggestions: 最大建议数
            
        Returns:
            建议列表
        """
        # 简单实现：返回包含该前缀的词
        suggestions = []
        
        # 这里可以实现更复杂的建议算法
        # 比如基于用户查询历史、热门查询等
        
        return suggestions[:max_suggestions]
    
    def get_popular_keywords(self, top_k: int = 20) -> List[Tuple[str, int]]:
        """
        获取热门关键词
        
        Args:
            top_k: 返回前k个关键词
            
        Returns:
            [(keyword, frequency), ...]
        """
        # 这里可以实现基于查询频率的热门关键词
        # 暂时返回空列表
        return [] 