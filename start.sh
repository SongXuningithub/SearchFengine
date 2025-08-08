#!/bin/bash

echo "启动金融搜索引擎..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

# 安装依赖
echo "安装依赖..."
pip3 install -r requirements.txt

# 创建必要的目录
echo "创建数据目录..."
mkdir -p data/crawler data/indexer data/engine

# 启动爬虫（后台运行）
echo "启动爬虫..."
python3 -m crawler.main --max-pages 100 --batch-size 8 &
CRAWLER_PID=$!

# 等待爬虫完成一些数据
echo "等待爬虫收集数据..."
sleep 30

# 启动索引器
echo "启动索引器..."
python3 -m indexer.main &
INDEXER_PID=$!

# 等待索引完成
echo "等待索引完成..."
sleep 10

# 启动搜索引擎API
echo "启动搜索引擎API..."
python3 -m engine.main &
ENGINE_PID=$!

# 等待API启动
sleep 5

# 启动前端
echo "启动前端界面..."
python3 -m frontend.app &
FRONTEND_PID=$!

echo "系统启动完成！"
echo "前端地址: http://localhost:5001"
echo "API地址: http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 保存进程ID
echo $CRAWLER_PID > .crawler.pid
echo $INDEXER_PID > .indexer.pid
echo $ENGINE_PID > .engine.pid
echo $FRONTEND_PID > .frontend.pid

# 等待用户中断
trap 'cleanup' INT
wait

cleanup() {
    echo "正在停止服务..."
    kill $(cat .crawler.pid 2>/dev/null) 2>/dev/null
    kill $(cat .indexer.pid 2>/dev/null) 2>/dev/null
    kill $(cat .engine.pid 2>/dev/null) 2>/dev/null
    kill $(cat .frontend.pid 2>/dev/null) 2>/dev/null
    rm -f .crawler.pid .indexer.pid .engine.pid .frontend.pid
    echo "服务已停止"
    exit 0
}
