#!/bin/bash

# 搜索引擎启动脚本

echo "启动搜索引擎..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 检查数据目录
if [ ! -d "data/indexer" ]; then
    echo "错误: 索引目录不存在，请先运行索引器"
    echo "运行: python indexer/run_indexer.py"
    exit 1
fi

if [ ! -f "data/crawler/crawler.db" ]; then
    echo "错误: 数据库文件不存在，请先运行爬虫"
    echo "运行: python crawler/run_crawler.py"
    exit 1
fi

# 启动API服务器
echo "启动API服务器..."
python engine/run_engine.py 