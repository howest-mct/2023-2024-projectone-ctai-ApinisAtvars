import sqlite3

class Database:
    def __init__(self) -> None:
        self.path_to_db = r"D:\Project 1\2023-2024-projectone-ctai-ApinisAtvars\Sending_data_to_RPi\AI\Databases\occupation_meter.db"
        self.con = sqlite3.connect(self.path_to_db)
        
        self.cur = self.con.cursor()

        res = self.cur.execute("SELECT name FROM sqlite_master WHERE name='spam'")
        



if __name__ == "__main__":
    db = Database()