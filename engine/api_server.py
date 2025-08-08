from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import time
from typing import Dict, Any

from search_engine import SearchEngine
from config.settings import API_CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 设置JSON编码
app.config['JSON_AS_ASCII'] = False

# 初始化搜索引擎
search_engine = None

def init_search_engine():
    """初始化搜索引擎"""
    global search_engine
    try:
        search_engine = SearchEngine(
            index_path=API_CONFIG.get('index_path', 'data/indexer'),
            db_path=API_CONFIG.get('db_path', 'data/crawler/crawler.db'),
            num_shards=API_CONFIG.get('num_shards', 64)
        )
        logger.info("Search engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize search engine: {e}")
        raise

@app.route('/api/search', methods=['GET'])
def search():
    """
    搜索API
    
    GET参数:
        q: 查询字符串
        max_results: 最大结果数 (默认20)
        
    Returns:
        {
            "success": true,
            "query": "查询字符串",
            "total_results": 结果总数,
            "search_time": 搜索耗时,
            "results": [
                {
                    "doc_id": 文档ID,
                    "title": "标题",
                    "url": "URL",
                    "summary": "摘要",
                    "score": 评分,
                    "created_at": "创建时间"
                }
            ]
        }
    """
    try:
        # 获取参数
        query = request.args.get('q', '').strip()
        # 处理URL编码问题
        if query:
            try:
                import urllib.parse
                query = urllib.parse.unquote(query)
            except:
                pass
        max_results = request.args.get('max_results', 20, type=int)
        
        # 调试信息
        logger.info(f"Received query: '{query}' (length: {len(query)})")
        if query:
            logger.info(f"Query bytes: {query.encode('utf-8')}")
        # 参数验证
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter is required'
            }), 400
        
        if max_results <= 0 or max_results > 100:
            return jsonify({
                'success': False,
                'error': 'max_results must be between 1 and 100'
            }), 400
        
        # 执行搜索
        start_time = time.time()
        results = search_engine.search(query, max_results)
        search_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'query': query,
            'total_results': len(results),
            'search_time': round(search_time, 3),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/suggest', methods=['GET'])
def suggest():
    """
    查询建议API
    
    GET参数:
        q: 部分查询字符串
        max: 最大建议数 (默认5)
        
    Returns:
        {
            "success": true,
            "suggestions": ["建议1", "建议2", ...]
        }
    """
    try:
        partial_query = request.args.get('q', '').strip()
        # 处理URL编码问题
        if partial_query:
            try:
                import urllib.parse
                partial_query = urllib.parse.unquote(partial_query)
            except:
                pass
        max_suggestions = request.args.get('max', 5, type=int)
        
        if not partial_query:
            return jsonify({
                'success': False,
                'error': 'Query parameter is required'
            }), 400
        
        if max_suggestions <= 0 or max_suggestions > 20:
            return jsonify({
                'success': False,
                'error': 'max must be between 1 and 20'
            }), 400
        
        # 获取建议
        suggestions = search_engine.suggest(partial_query, max_suggestions)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        logger.error(f"Suggestion error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def stats():
    """
    系统统计API
    
    Returns:
        {
            "success": true,
            "total_documents": 文档总数,
            "avg_document_length": 平均文档长度,
            "num_shards": 分片数量,
            "bm25_k1": BM25参数k1,
            "bm25_b": BM25参数b
        }
    """
    try:
        stats_data = search_engine.get_stats()
        
        return jsonify({
            'success': True,
            **stats_data
        })
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/keywords', methods=['GET'])
def keywords():
    """
    热门关键词API
    
    GET参数:
        top: 返回前k个关键词 (默认20)
        
    Returns:
        {
            "success": true,
            "keywords": [["关键词1", 频率1], ["关键词2", 频率2], ...]
        }
    """
    try:
        top_k = request.args.get('top', 20, type=int)
        
        if top_k <= 0 or top_k > 100:
            return jsonify({
                'success': False,
                'error': 'top must be between 1 and 100'
            }), 400
        
        # 获取热门关键词
        keywords = search_engine.get_popular_keywords(top_k)
        
        return jsonify({
            'success': True,
            'keywords': keywords
        })
        
    except Exception as e:
        logger.error(f"Keywords error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """
    健康检查API
    
    Returns:
        {
            "success": true,
            "status": "healthy",
            "timestamp": 时间戳
        }
    """
    try:
        # 简单的健康检查
        stats = search_engine.get_stats()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': time.time(),
            'total_documents': stats.get('total_documents', 0)
        })
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500

@app.route('/api/info', methods=['GET'])
def info():
    """
    系统信息API
    
    Returns:
        {
            "success": true,
            "name": "搜索引擎API",
            "version": "1.0.0",
            "description": "基于BM25算法的搜索引擎API"
        }
    """
    return jsonify({
        'success': True,
        'name': 'Search Engine API',
        'version': '1.0.0',
        'description': '基于BM25算法的搜索引擎API',
        'endpoints': [
            'GET /api/search - 搜索接口',
            'GET /api/suggest - 查询建议',
            'GET /api/stats - 系统统计',
            'GET /api/keywords - 热门关键词',
            'GET /api/health - 健康检查',
            'GET /api/info - 系统信息'
        ]
    })

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

def main():
    """主函数"""
    try:
        # 初始化搜索引擎
        init_search_engine()
        
        # 启动服务器
        host = API_CONFIG.get('host', '0.0.0.0')
        port = API_CONFIG.get('port', 5000)
        debug = API_CONFIG.get('debug', False)
        
        logger.info(f"Starting API server on {host}:{port}")
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        raise

if __name__ == '__main__':
    main() 