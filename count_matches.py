import sqlite3
c = sqlite3.connect('02-workbench/georgia-closing-attorneys/data/directory.sqlite').cursor()
matches = c.execute("SELECT COUNT(*) FROM attorneys WHERE appointments != '[]' AND appointments IS NOT NULL").fetchone()[0]
print("Matches:", matches)
