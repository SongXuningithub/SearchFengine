#!/usr/bin/env python3
import sqlite3
import os

def check_crawler_db():
    """检查爬虫数据库结构"""
    db_path = "data/crawler/crawler.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 检查pages表结构
        if ('pages',) in tables:
            cursor.execute("PRAGMA table_info(pages);")
            columns = cursor.fetchall()
            print("\npages表的列结构:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # 检查数据量
            cursor.execute("SELECT COUNT(*) FROM pages;")
            count = cursor.fetchone()[0]
            print(f"\npages表中的记录数: {count}")
            
            # 查看前几条记录
            cursor.execute("SELECT * FROM pages LIMIT 3;")
            rows = cursor.fetchall()
            print("\n前3条记录:")
            for i, row in enumerate(rows, 1):
                print(f"  记录 {i}: {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据库时出错: {e}")

if __name__ == "__main__":
    check_crawler_db()
