#!/bin/bash

# 查看搜索引擎服务状态脚本

echo "搜索引擎服务状态检查"
echo "===================="

# 检查PID文件
if [ -f "logs/engine.pid" ]; then
    PID=$(cat logs/engine.pid)
    echo "进程ID: $PID"
    
    # 检查进程是否存在
    if ps -p $PID > /dev/null; then
        echo "状态: ✅ 运行中"
        echo "进程信息:"
        ps -p $PID -o pid,ppid,cmd,etime,pcpu,pmem
        
        # 检查端口是否在监听
        if netstat -tlnp 2>/dev/null | grep ":5000" > /dev/null; then
            echo "端口状态: ✅ 5000端口正在监听"
        else
            echo "端口状态: ❌ 5000端口未监听"
        fi
        
        # 检查API是否响应
        if curl -s http://localhost:5000/api/health > /dev/null; then
            echo "API状态: ✅ API正常响应"
        else
            echo "API状态: ❌ API无响应"
        fi
        
    else
        echo "状态: ❌ 进程不存在"
        echo "清理PID文件..."
        rm -f logs/engine.pid
    fi
else
    echo "状态: ❌ 未运行"
    echo "PID文件不存在"
fi

echo ""
echo "最近日志 (最后10行):"
if [ -f "logs/engine.log" ]; then
    tail -10 logs/engine.log
else
    echo "日志文件不存在"
fi

echo ""
echo "使用方法:"
echo "启动服务: ./start_engine_daemon.sh"
echo "停止服务: ./stop_engine.sh"
echo "查看状态: ./status_engine.sh" 