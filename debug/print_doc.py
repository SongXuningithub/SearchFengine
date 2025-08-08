# 从数据库读取doc_id对应的doc

import sqlite3

conn = sqlite3.connect("data/crawler/crawler.db")
cursor = conn.cursor()

# 打印所有doc_id
cursor.execute("SELECT id FROM pages")
result = cursor.fetchall()
print(result)

doc_id = 467
cursor.execute("SELECT url, title, content, keywords, domain, crawl_time FROM pages WHERE id = ?", (doc_id,))
result = cursor.fetchall()

print(result)

conn.close()