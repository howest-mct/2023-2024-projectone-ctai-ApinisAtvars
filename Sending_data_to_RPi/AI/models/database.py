import sqlite3

con = sqlite3.connect("tutorial.db") # Establish connection to database

cur = con.cursor() # Create cursor to execute SQL and fetch results

# cur.execute("CREATE TABLE movie(title, year, score)") # Create table

res = cur.execute("SELECT name FROM sqlite_master") # Check if table is created (sqlite_master is a built-in table)
# I guess sqlite_master is a table of tables

print(res.fetchone())

cur.execute("""
    INSERT INTO movie VALUES
        ('Monty Python and the Holy Grail', 1975, 8.2),
        ('And Now for Something Completely Different', 1971, 7.5)
""") # Insert 2 columns in the table, but this only opens the transaction

con.commit() # This is needed to commit the transaction AKA make it happen


data = [
    ("Monty Python Live at the Hollywood Bowl", 1982, 7.9),
    ("Monty Python's The Meaning of Life", 1983, 7.5),
    ("Monty Python's Life of Brian", 1979, 8.0),
] 
cur.executemany("INSERT INTO movie VALUES(?, ?, ?)", data) # To prevent injection, question marks are placeholders, which are filled with lists
con.commit()

res = cur.execute("SELECT name FROM sqlite_master")
print(res.fetchall())
