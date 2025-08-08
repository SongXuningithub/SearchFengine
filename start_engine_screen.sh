#!/bin/bash

# 使用screen启动搜索引擎服务

echo "使用screen启动搜索引擎服务..."

# 检查screen是否安装
if ! command -v screen &> /dev/null; then
    echo "错误: 未安装screen，请先安装: sudo apt install screen"
    exit 1
fi

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

# 创建日志目录
mkdir -p logs

# 检查是否已有screen会话
if screen -list | grep -q "search-engine"; then
    echo "发现已存在的search-engine会话，正在终止..."
    screen -S search-engine -X quit
    sleep 2
fi

# 启动新的screen会话
echo "启动screen会话..."
screen -dmS search-engine bash -c "cd /home/xun/SearchFengine && source venv/bin/activate && python3 engine/run_engine.py 2>&1 | tee logs/engine.log"

echo "搜索引擎已启动！"
echo "Screen会话名: search-engine"
echo "访问地址: http://localhost:5000"
echo ""
echo "查看会话: screen -list"
echo "连接会话: screen -r search-engine"
echo "断开会话: Ctrl+A, D"
echo "停止服务: screen -S search-engine -X quit" 