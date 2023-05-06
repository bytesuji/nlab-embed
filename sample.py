import sqlite3
import random

conn_full = sqlite3.connect('files_full.db')
conn_small = sqlite3.connect('files_small.db')

c_full = conn_full.cursor()
c_small = conn_small.cursor()

c_small.execute('''CREATE TABLE IF NOT EXISTS files
                         (path TEXT, content TEXT)''')

c_full.execute('SELECT * FROM files')
all_rows = c_full.fetchall()
sample_rows = random.sample(all_rows, 20)

c_small.executemany('INSERT INTO files VALUES (?, ?)', sample_rows)

conn_small.commit()
conn_full.close()
conn_small.close()
