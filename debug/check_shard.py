#!/usr/bin/env python3
"""
检查term应该在哪一个shard中
"""

import hashlib

def get_shard_id(term: str, num_shards: int = 64) -> int:
    """计算term应该在哪一个shard中"""
    hash_value = hashlib.md5(term.encode('utf-8')).hexdigest()
    return int(hash_value, 16) % num_shards

def check_term_shard(term: str, num_shards: int = 64):
    """检查term的shard分布"""
    shard_id = get_shard_id(term, num_shards)
    print(f"term '{term}' 应该在 shard_{shard_id} 中")
    
    # 检查所有shard文件
    import os
    index_path = "data/indexer"
    shards_dir = os.path.join(index_path, "shards")
    
    if os.path.exists(shards_dir):
        shard_files = []
        for file in os.listdir(shards_dir):
            if file.startswith("shard_") and file.endswith(".pkl"):
                shard_files.append(file)
        
        print(f"可用的shard文件: {shard_files}")
        
        target_file = f"shard_{shard_id}.pkl"
        if target_file in shard_files:
            print(f"✅ 目标shard文件存在: {target_file}")
        else:
            print(f"❌ 目标shard文件不存在: {target_file}")
    else:
        print("shards目录不存在")

if __name__ == "__main__":
    # 测试一些term
    test_terms = ["中国", "股票", "投资", "人工智能", "区块链"]
    
    for term in test_terms:
        print(f"\n检查term: '{term}'")
        check_term_shard(term)
