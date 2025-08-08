#!/bin/bash

# 安装systemd服务脚本

echo "安装搜索引擎systemd服务..."

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用sudo运行此脚本"
    exit 1
fi

# 复制服务文件
cp search-engine.service /etc/systemd/system/

# 重新加载systemd配置
systemctl daemon-reload

# 启用服务（开机自启）
systemctl enable search-engine.service

echo "服务已安装并启用"
echo ""
echo "使用方法:"
echo "启动服务: sudo systemctl start search-engine"
echo "停止服务: sudo systemctl stop search-engine"
echo "重启服务: sudo systemctl restart search-engine"
echo "查看状态: sudo systemctl status search-engine"
echo "查看日志: sudo journalctl -u search-engine -f"
echo ""
echo "服务将在系统启动时自动运行" 