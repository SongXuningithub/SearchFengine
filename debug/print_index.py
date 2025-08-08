# 打印索引

import os
import json
import pickle
from typing import Dict, List

index_path = "data/indexer"

# 打印索引统计信息
with open(os.path.join(index_path, "index_stats.json"), "r") as f:
    index_stats = json.load(f)

print("索引统计信息:")
print(json.dumps(index_stats, indent=2, ensure_ascii=False))

# 打印指定shard的所有term
shard_id = 60  # 可以修改这个值来查看不同的shard
shard_file = os.path.join(index_path, f"shard_{shard_id}.pkl")

# 打印shard_id的term
with open(shard_file, "rb") as f:
    shard = pickle.load(f)

# print(shard.keys())

# 打印一个具体的term
print(shard.get("iPad"))



# 用 index_builder 打印一个具体的term
from indexer.inverted_index import InvertedIndexReader

index_reader = InvertedIndexReader(index_path=index_path, num_shards=64)

print(index_reader.get_posting("iPad"))