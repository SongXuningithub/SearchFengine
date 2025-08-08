#!/bin/bash

echo "停止金融搜索引擎..."

# 停止所有相关进程
pkill -f "crawler.main"
pkill -f "indexer.main"
pkill -f "engine.main"
pkill -f "frontend.app"

# 删除PID文件
rm -f .crawler.pid .indexer.pid .engine.pid .frontend.pid

echo "所有服务已停止"
