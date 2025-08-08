from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import logging

from config.settings import FRONTEND_CONFIG

app = Flask(__name__)
CORS(app)

# 搜索引擎API地址
SEARCH_API_URL = f"http://{FRONTEND_CONFIG['host']}:{FRONTEND_CONFIG['port']}/api"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/search')
def search_page():
    """搜索页面"""
    query = request.args.get('q', '')
    return render_template('search.html', query=query)

@app.route('/api/search')
def search():
    """搜索代理接口"""
    try:
        query = request.args.get('q', '')
        max_results = request.args.get('max_results', 20, type=int)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter is required'
            }), 400
        
        # 调用搜索引擎API
        response = requests.get(f"{SEARCH_API_URL}/search", params={
            'q': query,
            'max_results': max_results
        })
        
        return jsonify(response.json())
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/suggest')
def suggest():
    """查询建议代理接口"""
    try:
        partial_query = request.args.get('q', '')
        max_suggestions = request.args.get('max', 5, type=int)
        
        if not partial_query:
            return jsonify({
                'success': False,
                'error': 'Query parameter is required'
            }), 400
        
        # 调用搜索引擎API
        response = requests.get(f"{SEARCH_API_URL}/suggest", params={
            'q': partial_query,
            'max': max_suggestions
        })
        
        return jsonify(response.json())
        
    except Exception as e:
        logger.error(f"Suggestion error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
def stats():
    """统计信息代理接口"""
    try:
        response = requests.get(f"{SEARCH_API_URL}/stats")
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/keywords')
def keywords():
    """热门关键词代理接口"""
    try:
        top_k = request.args.get('top', 20, type=int)
        response = requests.get(f"{SEARCH_API_URL}/keywords", params={'top': top_k})
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Keywords error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(
        host=FRONTEND_CONFIG['host'],
        port=FRONTEND_CONFIG['port'] + 1,  # 前端使用不同端口
        debug=FRONTEND_CONFIG['debug']
    ) 