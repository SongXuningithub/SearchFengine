#!/usr/bin/env python3
"""
搜索引擎命令行界面
"""

import sys
import os
import logging
import argparse
from typing import List, Dict

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.search_engine import SearchEngine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SearchCLI:
    """搜索引擎命令行界面"""
    
    def __init__(self):
        self.search_engine = None
        self.init_search_engine()
    
    def init_search_engine(self):
        """初始化搜索引擎"""
        try:
            print("正在初始化搜索引擎...")
            self.search_engine = SearchEngine()
            print("搜索引擎初始化完成！")
            
            # 显示统计信息
            stats = self.search_engine.get_search_stats()
            print(f"\n统计信息:")
            print(f"  文档总数: {stats['total_documents']}")
            print(f"  平均文档长度: {stats['avg_document_length']:.2f}")
            print(f"  BM25参数 - k1: {stats['bm25_k1']}, b: {stats['bm25_b']}")
            print(f"  最大结果数: {stats['max_results']}")
            
        except Exception as e:
            print(f"初始化搜索引擎失败: {e}")
            sys.exit(1)
    
    def search(self, query: str, highlight: bool = False, max_results: int = 10):
        """执行搜索"""
        try:
            print(f"\n正在搜索: '{query}'")
            
            if highlight:
                results = self.search_engine.search_with_highlight(query)
            else:
                results = self.search_engine.search(query)
            
            print(f"找到 {len(results)} 个结果")
            
            if results:
                for i, result in enumerate(results[:max_results], 1):
                    print(f"\n{i}. 文档ID: {result['doc_id']}")
                    print(f"   标题: {result['title']}")
                    
                    if highlight and 'highlighted_content' in result:
                        print(f"   内容: {result['highlighted_content'][:150]}...")
                    else:
                        print(f"   内容: {result['content'][:150]}...")
                    
                    print(f"   分数: {result['score']:.4f}")
                    print(f"   长度: {result['length']}")
            else:
                print("  没有找到相关结果")
                
        except Exception as e:
            print(f"搜索失败: {e}")
    
    def analyze_query(self, query: str):
        """分析查询"""
        try:
            print(f"\n分析查询: '{query}'")
            
            # 分词
            terms = self.search_engine.tokenize_query(query)
            print(f"分词结果: {terms}")
            
            # 获取每个词的倒排列表信息
            for term in terms:
                postings = self.search_engine.get_postings(term)
                print(f"  词 '{term}': {len(postings)} 个倒排项")
                if postings:
                    doc_ids = [p.doc_id for p in postings[:5]]
                    print(f"    前5个文档ID: {doc_ids}")
            
            # 求交测试
            postings_list = []
            for term in terms:
                postings = self.search_engine.get_postings(term)
                if postings:
                    postings_list.append(postings)
            
            if postings_list:
                intersection = self.search_engine.intersect_postings(postings_list)
                print(f"  求交结果: {len(intersection)} 个文档")
                if intersection:
                    print(f"    前5个文档ID: {intersection[:5]}")
            else:
                print("  没有可求交的倒排列表")
                
        except Exception as e:
            print(f"查询分析失败: {e}")
    
    def interactive_mode(self):
        """交互模式"""
        print("\n=== 搜索引擎交互模式 ===")
        print("输入 'help' 查看帮助")
        print("输入 'quit' 退出")
        
        while True:
            try:
                query = input("\n请输入搜索查询: ").strip()
                
                if not query:
                    continue
                
                if query.lower() == 'quit':
                    print("再见！")
                    break
                elif query.lower() == 'help':
                    self.show_help()
                elif query.lower().startswith('analyze '):
                    # 分析查询
                    analyze_query = query[8:].strip()
                    if analyze_query:
                        self.analyze_query(analyze_query)
                elif query.lower().startswith('highlight '):
                    # 高亮搜索
                    highlight_query = query[10:].strip()
                    if highlight_query:
                        self.search(highlight_query, highlight=True)
                else:
                    # 普通搜索
                    self.search(query)
                    
            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                print(f"错误: {e}")
    
    def show_help(self):
        """显示帮助信息"""
        print("\n=== 帮助信息 ===")
        print("命令格式:")
        print("  <查询>                    - 执行普通搜索")
        print("  analyze <查询>            - 分析查询（显示分词和倒排列表信息）")
        print("  highlight <查询>          - 执行高亮搜索")
        print("  help                      - 显示此帮助信息")
        print("  quit                      - 退出程序")
        print("\n示例:")
        print("  股票                      - 搜索包含'股票'的文档")
        print("  analyze 股票投资          - 分析'股票投资'查询")
        print("  highlight 人工智能        - 高亮搜索'人工智能'")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='搜索引擎命令行界面')
    parser.add_argument('query', nargs='?', help='搜索查询')
    parser.add_argument('--highlight', action='store_true', help='启用高亮显示')
    parser.add_argument('--analyze', action='store_true', help='分析查询')
    parser.add_argument('--max-results', type=int, default=10, help='最大结果数')
    
    args = parser.parse_args()
    
    cli = SearchCLI()
    
    if args.query:
        # 单次搜索模式
        if args.analyze:
            cli.analyze_query(args.query)
        else:
            cli.search(args.query, highlight=args.highlight, max_results=args.max_results)
    else:
        # 交互模式
        cli.interactive_mode()

if __name__ == "__main__":
    main()
