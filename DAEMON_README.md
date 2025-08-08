# 搜索引擎后台运行指南

本指南提供了多种让搜索引擎在后台运行的方法，你可以根据需求选择合适的方案。

## 方案1：使用nohup（推荐）

这是最简单的方法，适合临时使用。

### 启动服务
```bash
./start_engine_daemon.sh
```

### 停止服务
```bash
./stop_engine.sh
```

### 查看状态
```bash
./status_engine.sh
```

### 查看日志
```bash
tail -f logs/engine.log
```

## 方案2：使用systemd服务（专业）

这是最专业的方法，适合长期运行，支持开机自启。

### 安装服务
```bash
sudo ./install_service.sh
```

### 启动服务
```bash
sudo systemctl start search-engine
```

### 停止服务
```bash
sudo systemctl stop search-engine
```

### 重启服务
```bash
sudo systemctl restart search-engine
```

### 查看状态
```bash
sudo systemctl status search-engine
```

### 查看日志
```bash
sudo journalctl -u search-engine -f
```

### 启用开机自启
```bash
sudo systemctl enable search-engine
```

## 方案3：使用screen

适合需要随时查看和交互的场景。

### 启动服务
```bash
./start_engine_screen.sh
```

### 查看会话列表
```bash
screen -list
```

### 连接到会话
```bash
screen -r search-engine
```

### 断开会话
在screen会话中按 `Ctrl+A, D`

### 停止服务
```bash
screen -S search-engine -X quit
```

## 方案4：使用tmux

类似screen，但功能更强大。

### 安装tmux
```bash
sudo apt install tmux
```

### 启动服务
```bash
tmux new-session -d -s search-engine 'cd /home/xun/SearchFengine && source venv/bin/activate && python3 engine/run_engine.py'
```

### 连接到会话
```bash
tmux attach-session -t search-engine
```

### 断开会话
在tmux会话中按 `Ctrl+B, D`

### 停止服务
```bash
tmux kill-session -t search-engine
```

## 推荐方案

### 开发测试环境
- 使用 **方案1 (nohup)** 或 **方案3 (screen)**
- 简单易用，便于调试

### 生产环境
- 使用 **方案2 (systemd)**
- 稳定可靠，支持开机自启
- 便于管理和监控

## 注意事项

1. **端口占用**: 确保5000端口没有被其他服务占用
2. **权限问题**: 确保脚本有执行权限
3. **虚拟环境**: 确保虚拟环境已正确安装依赖
4. **数据文件**: 确保索引和数据库文件存在

## 故障排除

### 服务无法启动
```bash
# 检查端口占用
netstat -tlnp | grep :5000

# 检查进程
ps aux | grep run_engine

# 查看详细日志
tail -f logs/engine.log
```

### 服务无法访问
```bash
# 检查防火墙
sudo ufw status

# 检查服务状态
./status_engine.sh
# 或
sudo systemctl status search-engine
```

### 内存不足
```bash
# 检查内存使用
free -h

# 检查进程内存使用
ps aux | grep run_engine
```

## 性能监控

### 查看资源使用
```bash
# 查看CPU和内存使用
top -p $(cat logs/engine.pid)

# 查看网络连接
netstat -an | grep :5000
```

### 查看API响应时间
```bash
# 测试API响应
curl -w "@-" -o /dev/null -s "http://localhost:5000/api/health" <<'EOF'
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
EOF
``` 