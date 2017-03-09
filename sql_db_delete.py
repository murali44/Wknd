import sqlite3
conn = sqlite3.connect('wknd.db')
cur = conn.cursor()

cur.execute('''DROP TABLE wknd''')

conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
