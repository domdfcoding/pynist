# stdlib
import re
import sqlite3

conn = sqlite3.connect(".coverage")
c = conn.cursor()

old_base = "C:\\Users\\dom13"
new_base = "/home/domdf"

for (idx, filename) in c.execute("SELECT * FROM file").fetchall():
	new_filename = re.sub(r"^\.tox/.*/site-packages/", "src/", filename)
	print(idx, filename, "->", new_filename)
	c.execute("UPDATE file SET path=? WHERE id=?", (new_filename, idx))

conn.commit()
conn.close()
