#!/usr/bin/env python3
"""
搜索引擎API服务器
"""

import logging
import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.search_engine import SearchEngine
from config.settings import FRONTEND_CONFIG

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 全局搜索引擎实例
search_engine = None

def init_search_engine():
    """初始化搜索引擎"""
    global search_engine
    try:
        search_engine = SearchEngine()
        logger.info("Search engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize search engine: {e}")
        raise

@app.route('/api/search', methods=['GET', 'POST'])
def search():
    """
    搜索接口
    
    GET参数:
        q: 查询字符串
        highlight: 是否高亮显示 (true/false)
        max_results: 最大结果数
        
    POST参数:
        query: 查询字符串
        highlight: 是否高亮显示
        max_results: 最大结果数
    """
    try:
        # 获取参数
        if request.method == 'GET':
            query = request.args.get('q', '')
            highlight = request.args.get('highlight', 'false').lower() == 'true'
            max_results = int(request.args.get('max_results', 20))
        else:
            data = request.get_json() or {}
            query = data.get('query', '')
            highlight = data.get('highlight', False)
            max_results = int(data.get('max_results', 20))
        
        if not query:
            return jsonify({
                'error': 'Query parameter is required',
                'message': 'Please provide a query string'
            }), 400
        
        # 记录搜索请求
        logger.info(f"Search request: '{query}', highlight={highlight}, max_results={max_results}")
        
        # 执行搜索
        start_time = time.time()
        
        if highlight:
            results = search_engine.search_with_highlight(query)
        else:
            results = search_engine.search(query)
        
        search_time = time.time() - start_time
        
        # 限制结果数量
        if max_results > 0:
            results = results[:max_results]
        
        # 构建响应
        response = {
            'query': query,
            'total_results': len(results),
            'search_time': round(search_time, 4),
            'results': results
        }
        
        logger.info(f"Search completed: {len(results)} results in {search_time:.4f}s")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({
            'error': 'Search failed',
            'message': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取搜索引擎统计信息"""
    try:
        stats = search_engine.get_search_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({
            'error': 'Failed to get stats',
            'message': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        # 简单的健康检查
        stats = search_engine.get_search_stats()
        return jsonify({
            'status': 'healthy',
            'total_documents': stats['total_documents'],
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500

@app.route('/api/suggest', methods=['GET'])
def suggest():
    """
    搜索建议接口
    
    GET参数:
        q: 查询前缀
        limit: 建议数量限制
    """
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({'suggestions': []})
        
        # 简单的建议实现：基于文档标题和内容中的词
        suggestions = set()
        
        # 从文档统计中提取建议
        for doc_info in search_engine.doc_stats.values():
            # 从标题中提取建议
            title_tokens = search_engine.tokenize_query(doc_info['title'])
            for token in title_tokens:
                if token.startswith(query) and len(token) > len(query):
                    suggestions.add(token)
            
            # 从内容中提取建议
            content_tokens = doc_info['tokens']
            for token in content_tokens:
                if token.startswith(query) and len(token) > len(query):
                    suggestions.add(token)
            
            if len(suggestions) >= limit:
                break
        
        return jsonify({
            'query': query,
            'suggestions': list(suggestions)[:limit]
        })
        
    except Exception as e:
        logger.error(f"Suggest error: {e}")
        return jsonify({
            'error': 'Failed to get suggestions',
            'message': str(e)
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_query():
    """
    查询分析接口
    
    POST参数:
        query: 查询字符串
    """
    try:
        data = request.get_json() or {}
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                'error': 'Query parameter is required'
            }), 400
        
        # 分词
        terms = search_engine.tokenize_query(query)
        
        # 获取每个词的倒排列表信息
        term_info = []
        for term in terms:
            postings = search_engine.get_postings(term)
            term_info.append({
                'term': term,
                'posting_count': len(postings),
                'doc_ids': [p.doc_id for p in postings[:5]]  # 前5个文档ID
            })
        
        return jsonify({
            'query': query,
            'terms': terms,
            'term_info': term_info
        })
        
    except Exception as e:
        logger.error(f"Analyze error: {e}")
        return jsonify({
            'error': 'Failed to analyze query',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An internal server error occurred'
    }), 500

def main():
    """主函数"""
    try:
        # 初始化搜索引擎
        print("Initializing search engine...")
        init_search_engine()
        
        # 获取配置
        host = FRONTEND_CONFIG.get('host', '0.0.0.0')
        port = FRONTEND_CONFIG.get('port', 5000)
        debug = FRONTEND_CONFIG.get('debug', False)
        
        print(f"Starting API server on {host}:{port}")
        print("Available endpoints:")
        print("  GET  /api/search?q=<query>")
        print("  POST /api/search")
        print("  GET  /api/stats")
        print("  GET  /api/health")
        print("  GET  /api/suggest?q=<prefix>")
        print("  POST /api/analyze")
        
        # 启动服务器
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
