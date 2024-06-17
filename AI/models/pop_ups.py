from tkinter import *
from tkinter import ttk
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Services')))
from database_service import DatabaseService

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Repositories')))
from sql import DatabaseRepository


class DatabaseUI():
    def __init__(self, databaseService: DatabaseService) -> None:
        self.database = databaseService
        self.root = Tk()
        
        self.selected_class = None  # Variable to store the selected class
        self.frame = None
        self.line_coords = (1,2,3,4) # (StartLineX, StartLineY, EndLineX, EndLineY)

    def choose_to_save_coords(self):
        
        self.frame = ttk.Frame(self.root, padding=5)
        self.frame.grid()
        ttk.Label(self.frame, text="Do You wish to save the line coordinates?").grid(row=0, column=0)
        ttk.Button(self.frame, text="Yes", command=self.save_coords_yes).grid(row=1, column=0)
        ttk.Button(self.frame, text="No", command=self.root.destroy).grid(row=2, column=0)
        self.root.mainloop()
    
    def choose_class(self):
        self.frame = ttk.Frame(self.root, padding=5)
        self.frame.grid()  # Add frame to the root window
        all_classes = self.database.query_all_classes()
        clicked = StringVar()
        clicked.set(all_classes[0])
        drop = OptionMenu(self.frame, clicked, *all_classes)
        drop.grid(row=2, column=0)
        
        ttk.Label(self.frame, text="Choose a class from the dropdown menu.").grid(row=0, column=0)
        ttk.Label(self.frame, text="ClassId, Name, Teacher, Room, Date, StartT, EndT, Counter line coords").grid(row=1,column=0)

        # Use lambda to pass the current value of clicked to select_class
        button = Button(self.frame, text="Choose class", command=lambda: self.select_class(clicked.get()))
        button.grid(row=3, column=0)
        
        # Create Label 
        label = Label(self.frame, text=" ")
        label.grid(row=4, column=0)
    
    def check_if_coords_exist(self):
        self.frame = ttk.Frame(self.root, padding=5)
        self.frame.grid()  # Add frame to the root window
        if self.database.get_coordinates_by_id(self.selected_class[0]) != (None, None, None, None):
            ttk.Label(self.frame, text="There already are line coordinates mapped to this class").grid(column=0, row=0)
            ttk.Label(self.frame, text="Do you wish to override them?").grid(row=1, column=0)
            Button(self.frame, text="Yes", command=lambda: self.override_existing_coords()).grid(row=2, column=0)
            Button(self.frame, text="No, Create a new entry", command=lambda: self.create_new_class_entry()).grid(row=3, column=0)
        else:
            ttk.Label(self.frame, text="This class does not have coordinates saved.").grid(row=0, column=0)
            ttk.Label(self.frame, text="Do you wish to save them here, or create a new entry?").grid(row=1, column=0)
            ttk.Button(self.frame, text="Save them here", command=lambda: self.override_existing_coords()).grid(row=2, column=0)
            ttk.Button(self.frame, text="Create a new entry", command=lambda: self.create_new_class_entry()).grid(row=3, column=0)

    def override_existing_coords(self):
        self.frame.destroy()
        self.frame = ttk.Frame(self.root, padding=5)
        self.frame.grid()
        self.database.change_coordinates(self.selected_class[0], self.line_coords[0], self.line_coords[1], self.line_coords[2], self.line_coords[3])
        ttk.Label(self.frame, text="Succesfully changed coordinates!").grid(row=0, column=0)
        Button(self.frame, text="Okay, cool", command=self.root.destroy).grid(row=1, column=0)

    def create_new_class_entry(self):
        self.frame.destroy()
        self.frame = ttk.Frame(self.root, padding=5)
        self.frame.grid()
        # def add_class(self, subject: str, teacher: str, room_number: str, date: str, start_time: str, end_time: str, number_of_students: int, line_start_X_coord = "NULL", line_start_Y_coord = "NULL", line_end_X_coord = "NULL", line_end_Y_coord = "NULL"):
        self.database.add_class(self.selected_class[1], self.selected_class[2], self.selected_class[3], self.selected_class[4], self.selected_class[5], self.selected_class[6], self.selected_class[7], self.line_coords[0], self.line_coords[1], self.line_coords[2], self.line_coords[3])
        ttk.Label(self.frame, text="New Class entry created successfully!").grid(row=0, column=0)
        Button(self.frame, text="Thank God!", command=self.root.destroy).grid(row=1, column=0)

    def change_coordinates_for_class_entry(self, classId, newStartX, newStartY, newEndX, newEndY):
        self.database.change_coordinates(classId, newStartX, newStartY, newEndX, newEndY)

    def parse_tuple_from_string(self, data_str):
        # Remove the surrounding parentheses
        data_str = data_str.strip('()')

        # Split the string by commas
        data_list = data_str.split(',')

        # Convert each item to the appropriate type (int or str)
        parsed_data = []
        for item in data_list:
            item = item.strip()
            if item.isdigit():
                parsed_data.append(int(item))
            else:
                parsed_data.append(item.strip("'"))

        return tuple(parsed_data)


    def select_class(self, value):
        self.selected_class = self.parse_tuple_from_string(value)  # Store the selected class, parse the string to be a tuple
        self.frame.destroy()
        print(value)
        self.check_if_coords_exist()

    def save_coords_yes(self):
        self.frame.destroy()  # Destroy the frame
        self.choose_class()  # Proceed to choose_class

if __name__ == "__main__":
    ds = DatabaseService(DatabaseRepository())
    dui = DatabaseUI(ds)
    dui.choose_to_save_coords()
