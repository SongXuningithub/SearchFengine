#!/usr/bin/env python3
"""
打印特定term的详细信息
"""

import os
import json
import pickle
from typing import Dict, List

index_path = "data/indexer"

def print_term_details(term: str, shard_id: int = 0):
    """打印特定term的详细信息"""
    
    shard_file = os.path.join(index_path, "shards", f"shard_{shard_id}.pkl")
    
    if not os.path.exists(shard_file):
        print(f"shard文件不存在: {shard_file}")
        return
    
    print(f"正在查找term: '{term}' 在shard_{shard_id}中的信息...")
    
    with open(shard_file, "rb") as f:
        shard = pickle.load(f)
    
    if 'word_to_docs' not in shard:
        print("shard中没有word_to_docs数据")
        return
    
    word_to_docs = shard['word_to_docs']
    
    if term in word_to_docs:
        docs = word_to_docs[term]
        print(f"✅ 找到term '{term}'")
        print(f"   出现在 {len(docs)} 个文档中")
        print(f"   文档ID列表: {docs}")
        
        # 如果有doc_frequencies，显示频率信息
        if 'doc_frequencies' in shard:
            doc_frequencies = shard['doc_frequencies']
            if term in doc_frequencies:
                frequencies = doc_frequencies[term]
                print(f"   频率信息: {frequencies}")
    else:
        print(f"❌ 未找到term '{term}'")
        
        # 显示相似的term
        similar_terms = [t for t in word_to_docs.keys() if term in t or t in term]
        if similar_terms:
            print(f"   相似的term: {similar_terms[:10]}")

def search_term_in_all_shards(term: str):
    """在所有shard中搜索term"""
    
    shards_dir = os.path.join(index_path, "shards")
    if not os.path.exists(shards_dir):
        print("shards目录不存在")
        return
    
    print(f"在所有shard中搜索term: '{term}'")
    print("=" * 50)
    
    found_in_shards = []
    
    for file in os.listdir(shards_dir):
        if file.startswith("shard_") and file.endswith(".pkl"):
            shard_id = file.replace("shard_", "").replace(".pkl", "")
            shard_file = os.path.join(shards_dir, file)
            
            try:
                with open(shard_file, "rb") as f:
                    shard = pickle.load(f)
                
                if 'word_to_docs' in shard:
                    word_to_docs = shard['word_to_docs']
                    if term in word_to_docs:
                        docs = word_to_docs[term]
                        found_in_shards.append((shard_id, len(docs)))
                        print(f"✅ shard_{shard_id}: {len(docs)} 个文档")
            except Exception as e:
                print(f"❌ 读取shard_{shard_id}时出错: {e}")
    
    if found_in_shards:
        print(f"\n总结: term '{term}' 在 {len(found_in_shards)} 个shard中找到")
        for shard_id, doc_count in found_in_shards:
            print(f"  shard_{shard_id}: {doc_count} 个文档")
    else:
        print(f"\n未在任何shard中找到term '{term}'")

def list_common_terms(shard_id: int = 0, limit: int = 20):
    """列出shard中的常见term"""
    
    shard_file = os.path.join(index_path, "shards", f"shard_{shard_id}.pkl")
    
    if not os.path.exists(shard_file):
        print(f"shard文件不存在: {shard_file}")
        return
    
    with open(shard_file, "rb") as f:
        shard = pickle.load(f)
    
    if 'word_to_docs' not in shard:
        print("shard中没有word_to_docs数据")
        return
    
    word_to_docs = shard['word_to_docs']
    
    # 按文档数量排序
    sorted_terms = sorted(word_to_docs.items(), key=lambda x: len(x[1]), reverse=True)
    
    print(f"shard_{shard_id} 中最常见的 {limit} 个term:")
    print("=" * 50)
    
    for i, (term, docs) in enumerate(sorted_terms[:limit]):
        print(f"{i+1:2d}. '{term}' - {len(docs)} 个文档")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        term = sys.argv[1]
        print_term_details(term)
        print("\n" + "=" * 50)
        search_term_in_all_shards(term)
    else:
        # 默认显示常见term
        list_common_terms()
        
        print("\n" + "=" * 50)
        print("用法: python3 debug/print_term_details.py <term>")
        print("例如: python3 debug/print_term_details.py 中国")
