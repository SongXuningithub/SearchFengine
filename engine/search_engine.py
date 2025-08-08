import sqlite3
import hashlib
import logging
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict
import math
from rank_bm25 import BM25Okapi

from indexer.inverted_index import InvertedIndexReader, Posting
from utils.text_processor import TextProcessor
from config.settings import SEARCH_CONFIG

logger = logging.getLogger(__name__)

class SearchEngine:
    """搜索引擎引擎类"""
    
    def __init__(self, index_path: str = "data/indexer", db_path: str = "data/crawler/crawler.db"):
        """
        初始化搜索引擎
        
        Args:
            index_path: 倒排索引路径
            db_path: 文档数据库路径
        """
        self.index_reader = InvertedIndexReader(index_path)
        self.text_processor = TextProcessor()
        self.db_path = db_path
        
        # BM25参数
        self.bm25_k1 = SEARCH_CONFIG.get('bm25_k1', 1.5)
        self.bm25_b = SEARCH_CONFIG.get('bm25_b', 0.75)
        self.max_results = SEARCH_CONFIG.get('max_results', 20)
        
        # 文档统计信息
        self.doc_stats = self._load_document_stats()
        
        # 预计算词频统计信息
        self.term_doc_freq = self._calculate_term_doc_frequency()
        
        logger.info("SearchEngine initialized")
    
    def _load_document_stats(self) -> Dict[int, Dict]:
        """加载文档统计信息"""
        doc_stats = {}
        # 统计耗时
        try:
            start_time = time.time()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, content FROM pages
            ''')
            
            for row in cursor.fetchall():
                doc_id, title, content = row
                # 计算文档长度（词数）
                tokens = self.text_processor.tokenize(content or "")
                doc_stats[doc_id] = {
                    'title': title,
                    'content': content,
                    'length': len(tokens),
                    'tokens': tokens
                }
            
            conn.close()
            end_time = time.time()
            logger.info(f"Loaded {len(doc_stats)} document stats in {end_time - start_time} seconds")
            
        except Exception as e:
            logger.error(f"Error loading document stats: {e}")
        
        return doc_stats
    
    def _calculate_term_doc_frequency(self) -> Dict[str, int]:
        """预计算每个词的文档频率"""
        term_doc_freq = defaultdict(int)
        
        for doc_info in self.doc_stats.values():
            # 统计文档中出现的唯一词
            unique_terms = set(doc_info['tokens'])
            for term in unique_terms:
                term_doc_freq[term] += 1
        
        logger.info(f"Calculated document frequency for {len(term_doc_freq)} terms")
        return dict(term_doc_freq)
    
    def tokenize_query(self, query: str) -> List[str]:
        """
        对查询进行分词
        
        Args:
            query: 查询字符串
            
        Returns:
            分词后的词列表
        """
        return self.text_processor.tokenize(query)
    
    def get_postings(self, term: str) -> List[Posting]:
        """
        获取指定term的倒排列表
        
        Args:
            term: 查询词
            
        Returns:
            倒排列表
        """
        return self.index_reader.get_posting(term)
    
    def intersect_postings(self, postings_list: List[List[Posting]]) -> List[int]:
        """
        对多个倒排列表进行求交操作
        
        Args:
            postings_list: 倒排列表的列表
            
        Returns:
            求交后的文档ID列表
        """
        if not postings_list:
            return []
        
        # 按倒排列表长度排序，优先处理短的列表
        sorted_postings = sorted(postings_list, key=len)
        
        # 获取第一个倒排列表的文档ID集合
        result_docs = set(posting.doc_id for posting in sorted_postings[0])
        
        # 与其他倒排列表求交
        for postings in sorted_postings[1:]:
            current_docs = set(posting.doc_id for posting in postings)
            result_docs = result_docs.intersection(current_docs)
            
            # 如果结果为空，提前返回
            if not result_docs:
                break
        
        return list(result_docs)
    
    def calculate_bm25_score(self, query_terms: List[str], doc_id: int) -> float:
        """
        计算BM25相关性分数
        
        Args:
            query_terms: 查询词列表
            doc_id: 文档ID
            
        Returns:
            BM25分数
        """
        if doc_id not in self.doc_stats:
            return 0.0
        
        doc_info = self.doc_stats[doc_id]
        doc_length = doc_info['length']
        
        # 计算平均文档长度
        avg_doc_length = sum(doc['length'] for doc in self.doc_stats.values()) / len(self.doc_stats)
        
        score = 0.0
        
        for term in query_terms:
            # 获取该term在文档中的词频（包括标题和内容）
            title_tokens = self.tokenize_query(doc_info['title'])
            content_freq = doc_info['tokens'].count(term)
            title_freq = title_tokens.count(term)
            total_freq = content_freq + title_freq * 2  # 标题中的词权重更高
            
            if total_freq == 0:
                continue
            
            # 获取该term的文档频率（使用预计算的值）
            doc_freq = self.term_doc_freq.get(term, 0)
            if doc_freq == 0:
                continue
            
            # 计算IDF
            idf = math.log((len(self.doc_stats) - doc_freq + 0.5) / (doc_freq + 0.5))
            
            # 计算BM25分数
            numerator = total_freq * (self.bm25_k1 + 1)
            denominator = total_freq + self.bm25_k1 * (1 - self.bm25_b + self.bm25_b * doc_length / avg_doc_length)
            
            score += idf * numerator / denominator
        
        return score
    
    def search(self, query: str) -> List[Dict]:
        """
        执行搜索
        
        Args:
            query: 查询字符串
            
        Returns:
            搜索结果列表，每个结果包含doc_id、title、content、score
        """
        # 1. 对查询进行分词
        query_terms = self.tokenize_query(query)
        logger.info(f"Query terms: {query_terms}")
        
        if not query_terms:
            return []
        
        # 2. 获取每个分词的倒排列表
        postings_list = []
        for term in query_terms:
            postings = self.get_postings(term)
            if postings:
                postings_list.append(postings)
                logger.info(f"Term '{term}' has {len(postings)} postings")
            else:
                logger.info(f"Term '{term}' has no postings")
        
        if not postings_list:
            return []
        
        # 3. 对倒排列表进行求交
        intersection_docs = self.intersect_postings(postings_list)
        logger.info(f"Intersection result: {len(intersection_docs)} documents")
        
        if not intersection_docs:
            return []
        
        # 4. 使用BM25计算相关性分数
        doc_scores = []
        logger.info(f"Calculating BM25 scores for {len(intersection_docs)} documents")
        for i, doc_id in enumerate(intersection_docs):
            if i < 5:  # 只记录前5个文档的调试信息
                score = self.calculate_bm25_score(query_terms, doc_id)
                logger.info(f"Doc {doc_id}: score = {score}")
                doc_scores.append((doc_id, score))
            else:
                score = self.calculate_bm25_score(query_terms, doc_id)
                doc_scores.append((doc_id, score))
        
        logger.info(f"Calculated scores for {len(doc_scores)} documents")
        
        # 5. 按分数排序
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 6. 构建搜索结果
        results = []
        for doc_id, score in doc_scores[:self.max_results]:
            if doc_id in self.doc_stats:
                doc_info = self.doc_stats[doc_id]
                results.append({
                    'doc_id': doc_id,
                    'title': doc_info['title'],
                    'content': doc_info['content'][:200] + '...' if len(doc_info['content']) > 200 else doc_info['content'],
                    'score': score,
                    'length': doc_info['length']
                })
        
        logger.info(f"Search completed, returned {len(results)} results")
        return results
    
    def search_with_highlight(self, query: str) -> List[Dict]:
        """
        执行搜索并高亮显示匹配的词
        
        Args:
            query: 查询字符串
            
        Returns:
            搜索结果列表，包含高亮信息
        """
        results = self.search(query)
        query_terms = self.tokenize_query(query)
        
        for result in results:
            # 在标题和内容中高亮查询词
            highlighted_title = result['title']
            highlighted_content = result['content']
            
            for term in query_terms:
                # 高亮标题
                highlighted_title = highlighted_title.replace(
                    term, f"<mark>{term}</mark>"
                )
                
                # 高亮内容
                highlighted_content = highlighted_content.replace(
                    term, f"<mark>{term}</mark>"
                )
            
            result['highlighted_title'] = highlighted_title
            result['highlighted_content'] = highlighted_content
        
        return results
    
    def get_search_stats(self) -> Dict:
        """获取搜索统计信息"""
        return {
            'total_documents': len(self.doc_stats),
            'avg_document_length': sum(doc['length'] for doc in self.doc_stats.values()) / len(self.doc_stats) if self.doc_stats else 0,
            'bm25_k1': self.bm25_k1,
            'bm25_b': self.bm25_b,
            'max_results': self.max_results
        }
