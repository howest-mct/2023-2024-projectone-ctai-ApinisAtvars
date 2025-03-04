import sqlite3
import sys
import os


class DatabaseRepository():
    def __init__(self) -> None:
        self.path_to_db = str(sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Databases/occupation_meter.db'))))
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
        self.cur.execute("CREATE TABLE class (ClassID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,Subject VARCHAR(45) NOT NULL,Teacher VARCHAR(45) NOT NULL,RoomNo VARCHAR(45) NOT NULL,Date VARCHAR(45) NOT NULL,StartTime VARCHAR(45) NOT NULL,EndTime VARCHAR(45) NOT NULL,NumberOfStudents INT NOT NULL, LineStartXCoord INT, LineStartYCoord INT, LineEndXCoord INT, LineEndYCoord INT);")
        self.con.commit()

    def create_measurements_table(self):
        self.cur.execute("CREATE TABLE measurements (MeasurementID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, ClassID INT,  PeopleIn INT NOT NULL, PeopleOut INT NOT NULL, Time VARCHAR(45), FOREIGN KEY(ClassID) REFERENCES class(ClassID))")
        self.con.commit()
    
    def delete_class_table(self):
        self.cur.execute("DROP TABLE class;")
        self.con.commit()
    
    def delete_measurements_table(self):
        self.cur.execute("DROP TABLE measurements;")
        self.con.commit()
    
    def close_connection(self):
        self.con.close()
    
    def add_class(self, subject: str, teacher: str, room_number: str, date: str, start_time: str, end_time: str, number_of_students: int, line_start_X_coord = "NULL", line_start_Y_coord = "NULL", line_end_X_coord = "NULL", line_end_Y_coord = "NULL"):
        command = "INSERT INTO class (Subject, Teacher, RoomNo, Date, StartTime, EndTime, NumberOfStudents, LineStartXCoord, LineStartYCoord, LineEndXCoord, LineEndYCoord) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', {}, {}, {}, {}, {})".format(subject, teacher, room_number, date, start_time, end_time, number_of_students, line_start_X_coord, line_start_Y_coord, line_end_X_coord, line_end_Y_coord)
        self.cur.execute(command)
        self.con.commit()

    def add_measurement(self, class_id: int, people_in: int, people_out: int, time: str):
        command = "INSERT INTO measurements (ClassID, PeopleIn, PeopleOut, Time) VALUES ({}, {}, {}, '{}')".format(class_id, people_in, people_out, time)
        self.cur.execute(command)
        self.con.commit()

    def query_all_classes(self):
        query = self.cur.execute("SELECT * FROM class")
        return query.fetchall()

    def query_all_measurements(self):
        query = self.cur.execute("SELECT * FROM measurements")
        return query.fetchall()
    
    def remove_measurement(self, measurementId):
        self.cur.execute("DELETE FROM measurements WHERE MeasurementID = {}".format(measurementId))
        self.con.commit()
    
    def remove_class(self, classId):
        self.cur.execute("DELETE FROM class WHERE ClassID = {}".format(classId))
        self.con.commit()
    
    def get_coordinates(self, classId):
        command = "SELECT LineStartXCoord, LineStartYCoord, LineEndXCoord, LineEndYCoord FROM class WHERE ClassID = {}".format(classId)
        query = self.cur.execute(command)
        return query.fetchone()
    
    def change_coordinates(self, classId, newStartX, newStartY, newEndX, newEndY):
        command = "UPDATE class SET LineStartXCoord = {}, LineStartYCoord = {}, LineEndXCoord = {}, LineEndYCoord = {} WHERE ClassID = {}".format(newStartX, newStartY, newEndX, newEndY, classId)
        self.cur.execute(command)
        self.con.commit()
    
    def update_measurement(self, measurement_id: int,class_id: int, people_in: int, people_out: int, time: str):
        command = "UPDATE measurements SET ClassID = {}, PeopleIn = {}, PeopleOut = {}, Time = {} WHERE MeasurementID = {}".format(class_id, people_in, people_out, time, measurement_id)
        self.cur.execute(command)
        self.con.commit()
    
if __name__ == "__main__":
    db = DatabaseRepository()
    # db.delete_measurements_table()
    db.add_class("Basic Programming", "Marie Dewitte", "KWE.A.2.301", "06-06-2024", "8:30", "10:30", 40)
    db.add_measurement(1, 10, 20, "10:35")
    ac = db.query_all_classes()
    print(ac)
    am = db.query_all_measurements()
    print(am)
    # db.remove_class(1)
    # db.remove_measurement(1)
    db.close_connection()