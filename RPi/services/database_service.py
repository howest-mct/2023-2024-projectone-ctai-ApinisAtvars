import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../repos')))
from sql import DatabaseRepository

class DatabaseService:
    def __init__(self, repository: DatabaseRepository) -> None:
        self._repository = repository
    
    def check_if_table_exists(self, tblname) -> bool:
        return self._repository.check_if_table_exists()
    
    def delete_class_table(self):
        answer = input("Are you sure you want to delete the 'class' table? (Y/n)")
        if answer == "Y" or answer == "y":
            self._repository.delete_class_table()
            print("class table dropped")
    
    def delete_measurements_table(self):
        answer = input("Are you sure you want to delete the 'measurements' table? (Y/n)")
        if answer == "Y" or answer == "y":
            self._repository.delete_measurements_table()
            print("measurements table dropped")
    
    def close_connection(self):
        self._repository.close_connection()
        print("connection to database closed")
    
    def add_class(self, subject: str, teacher: str, room_number: str, date: str, start_time: str, end_time: str, number_of_students: int, line_start_X_coord = "NULL", line_start_Y_coord = "NULL", line_end_X_coord = "NULL", line_end_Y_coord = "NULL"):
        self._repository.add_class(subject, teacher, room_number, date, start_time, end_time, number_of_students, line_start_X_coord, line_start_Y_coord, line_end_X_coord, line_end_Y_coord)
        print("Class {} added!".format(subject))
    
    def add_measurement(self, class_id: int, people_in: int, people_out: int, time: str):
        self._repository.add_measurement(class_id, people_in, people_out, time)
    
    def query_all_classes(self) -> list:
        return self._repository.query_all_classes()
    
    def query_all_measurements(self) -> list:
        return self._repository.query_all_measurements()
    
    def remove_measurement(self):
        print("Select measurement to remove:\n")
        print("Id, ClassId, PeopleIn, PeopleOut, Time")
        for measurement in self.query_all_measurements():
            print(measurement)
        measurement_id = int(input("Enter the measurement id:"))
        self._repository.remove_measurement(measurement_id)
    
    def remove_class(self):
        print("Select class id:\n")
        print("ClassId, Subject, Teacher, RoomNo, Date, StartTime, EndTime, NumberOfStudents")
        for subject in self.query_all_classes():
            print(subject)
        class_id = int(input("Enter the class id:"))
        self._repository.remove_class(class_id)
    
    def get_coordinates(self):
        print("Select class id:\n")
        print("ClassId, Subject, Teacher, RoomNo, Date, StartTime, EndTime, NumberOfStudents")
        for subject in self.query_all_classes():
            print(subject)
        class_id = int(input("Enter the class id:"))
        return self._repository.get_coordinates(class_id)
    
    def get_coordinates_by_id(self, class_id):
        return self._repository.get_coordinates(class_id)

    def change_coordinates(self, classId, newStartX, newStartY, newEndX, newEndY):
        self._repository.change_coordinates(classId, newStartX, newStartY, newEndX, newEndY)

    def get_last_class_id(self):
        #Neet to trim string, because the end result is this: (X,)
        return self._repository.get_last_class_id()

if __name__=="__main__":
    ds = DatabaseService(DatabaseRepository())
    print(ds.query_all_classes())
    # print(ds.query_all_measurements())
    # ds.remove_class()
    # ds.remove_measurement()
    # ds.add_measurement(2, 50, 45, "10:45")
    # ds.add_class("ASE", "Dieter", "KWE.A.2.302", "07.06.2024", "10:30", "12:30", 40, 400, 400, 600, 400)
    # ds.delete_class_table()
    # ds.delete_measurements_table()
    classid = ds.get_last_class_id()
    ds.change_coordinates(classid, 200, 200, 400, 200)
    # print("coordinates changed")
    # print(ds.get_coordinates())
    # print(ds.get_last_class_id())
    ds.close_connection()