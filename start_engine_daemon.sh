#!/bin/bash

# 搜索引擎后台启动脚本

echo "启动搜索引擎后台服务..."


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

# 停止已存在的进程
echo "停止已存在的进程..."
pkill -f "python3 engine/run_engine.py" 2>/dev/null
sleep 2

# 启动API服务器（后台运行）
echo "启动API服务器..."
nohup python3 engine/run_engine.py > logs/engine.log 2>&1 &

# 获取进程ID
ENGINE_PID=$!
echo $ENGINE_PID > logs/engine.pid

echo "搜索引擎已启动！"
echo "进程ID: $ENGINE_PID"
echo "日志文件: logs/engine.log"
echo "访问地址: http://localhost:5000"
echo ""
echo "查看日志: tail -f logs/engine.log"
echo "停止服务: ./stop_engine.sh" 