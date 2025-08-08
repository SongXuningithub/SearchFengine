#!/bin/bash

# 停止搜索引擎服务脚本

echo "停止搜索引擎服务..."

# 检查PID文件
if [ -f "logs/engine.pid" ]; then
    PID=$(cat logs/engine.pid)
    echo "找到进程ID: $PID"
    
    # 检查进程是否存在
    if ps -p $PID > /dev/null; then
        echo "正在停止进程 $PID..."
        kill $PID
        
        # 等待进程结束
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null; then
                echo "进程已停止"
                rm -f logs/engine.pid
                break
            fi
            sleep 1
        done
        
        # 如果进程仍然存在，强制杀死
        if ps -p $PID > /dev/null; then
            echo "强制停止进程..."
            kill -9 $PID
            rm -f logs/engine.pid
        fi
    else
        echo "进程 $PID 不存在"
        rm -f logs/engine.pid
    fi
else
    echo "未找到PID文件，尝试通过进程名停止..."
fi

# 通过进程名停止
pkill -f "python3 engine/run_engine.py" 2>/dev/null

echo "搜索引擎服务已停止" 