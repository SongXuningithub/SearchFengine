from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from typing import Dict, List

from engine.search_engine import BM25SearchEngine

app = Flask(__name__)
CORS(app)

# 创建搜索引擎实例
search_engine = BM25SearchEngine()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/search', methods=['GET'])
def search():
    """搜索接口"""
    try:
        query = request.args.get('q', '')
        max_results = request.args.get('max_results', 20, type=int)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter is required'
            }), 400
        
        # 执行搜索
        results = search_engine.search(query, max_results)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total': len(results)
        })
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/suggest', methods=['GET'])
def suggest():
    """查询建议接口"""
    try:
        partial_query = request.args.get('q', '')
        max_suggestions = request.args.get('max', 5, type=int)
        
        if not partial_query:
            return jsonify({
                'success': False,
                'error': 'Query parameter is required'
            }), 400
        
        # 获取建议
        suggestions = search_engine.suggest_queries(partial_query, max_suggestions)
        
        return jsonify({
            'success': True,
            'query': partial_query,
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
    """获取统计信息"""
    try:
        stats = search_engine.get_search_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/keywords', methods=['GET'])
def popular_keywords():
    """获取热门关键词"""
    try:
        top_k = request.args.get('top', 20, type=int)
        
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

@app.route('/api/search/domain', methods=['GET'])
def search_by_domain():
    """按域名搜索"""
    try:
        domain = request.args.get('domain', '')
        max_results = request.args.get('max_results', 20, type=int)
        
        if not domain:
            return jsonify({
                'success': False,
                'error': 'Domain parameter is required'
            }), 400
        
        results = search_engine.search_by_domain(domain, max_results)
        
        return jsonify({
            'success': True,
            'domain': domain,
            'results': results,
            'total': len(results)
        })
        
    except Exception as e:
        logger.error(f"Domain search error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search/keywords', methods=['GET'])
def search_by_keywords():
    """按关键词搜索"""
    try:
        keywords_str = request.args.get('keywords', '')
        max_results = request.args.get('max_results', 20, type=int)
        
        if not keywords_str:
            return jsonify({
                'success': False,
                'error': 'Keywords parameter is required'
            }), 400
        
        keywords = [kw.strip() for kw in keywords_str.split(',')]
        results = search_engine.search_by_keywords(keywords, max_results)
        
        return jsonify({
            'success': True,
            'keywords': keywords,
            'results': results,
            'total': len(results)
        })
        
    except Exception as e:
        logger.error(f"Keywords search error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'engine_loaded': search_engine.total_docs > 0
    })

if __name__ == '__main__':
    from config.settings import FRONTEND_CONFIG
    
    app.run(
        host=FRONTEND_CONFIG['host'],
        port=FRONTEND_CONFIG['port'],
        debug=FRONTEND_CONFIG['debug']
    ) 