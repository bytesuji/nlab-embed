import sys
import sqlite3

db_name = sys.argv[1]
search_str = sys.argv[2]

conn = sqlite3.connect(db_name)
c = conn.cursor()

c.execute("SELECT * FROM files WHERE content LIKE ?", ('%' + search_str + '%',))

results = c.fetchall()

for row in results:
    print(row)
conn.close()
