import sqlite3

class DatabaseRepository:
    def __init__(self) -> None:
        self.path_to_db = r"D:\Project 1\2023-2024-projectone-ctai-ApinisAtvars\Sending_data_to_RPi\AI\Databases\occupation_meter.db"
        self.con = sqlite3.connect(self.path_to_db)
        
        self.cur = self.con.cursor() # Create Cursor

        if self.check_if_table_exists("class") == False: # If the occupation_meter table doesn't exist, create a new one
            self.create_class_table() # Create the table "Class"
            print("'class' table created")
        
        else:
            print("'class' table already exists")
        
        if self.check_if_table_exists("measurements") == False:
            self.create_measurements_table()
            print("'measurements' table created")

        else:
            print("'measurements' table already exists")


    def check_if_table_exists(self, tblname) -> bool:
        #Returns True if this table exists
        command = "SELECT name FROM sqlite_master WHERE name = '{}'".format(tblname)
        check = self.cur.execute(command)

        return not check.fetchone() is None
    
    def create_class_table(self):
        self.cur.execute("CREATE TABLE class (ClassID INT NOT NULL PRIMARY KEY,Subject VARCHAR(45) NOT NULL,Teacher VARCHAR(45) NOT NULL,RoomNo VARCHAR(45) NOT NULL,Date VARCHAR(45) NOT NULL,StartTime VARCHAR(45) NOT NULL,EndTime VARCHAR(45) NOT NULL,NumberOfStudents VARCHAR(45) NOT NULL);")
        self.con.commit()

    def create_measurements_table(self):
        self.cur.execute("CREATE TABLE measurements (MeasurementID INT NOT NULL PRIMARY KEY, PeopleIn INT NOT NULL, PeopleOut INT NOT NULL, Time VARCHAR(45), FOREIGN KEY(ClassID) REFERENCES class(ClassID))")
        self.con.commit()

    
    def delete_class_table(self):
        self.cur.execute("DROP TABLE class;")
        self.con.commit()
        print("om table dropped")
    
    def close_connection(self):
        self.con.close()
        print("Connection to db closed")
    
if __name__ == "__main__":
    db = DatabaseRepository()
    db.close_connection()