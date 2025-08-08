#!/usr/bin/env python3
"""
搜索引擎启动脚本
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api_server import main

if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n搜索引擎已停止")
    except Exception as e:
        logging.error(f"搜索引擎启动失败: {e}")
        sys.exit(1) 