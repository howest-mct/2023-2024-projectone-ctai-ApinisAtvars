from tkinter import *
from tkinter import ttk
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../services')))
from database_service import DatabaseService

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../repos')))
from sql import DatabaseRepository


class DatabaseUI():
    def __init__(self, databaseService: DatabaseService) -> None:
        self.database = databaseService
        self.root = Tk()

        self.padding = 50
        self.height = 500
        self.width = 500
        
        self.selected_class = None  # Variable to store the selected class
        self.frame = None
        self.line_coords = (1,2,3,4) # (StartLineX, StartLineY, EndLineX, EndLineY)
        self.save_line_coords = False
        self.override_line = False

    def choose_to_save_coords(self):
        
        self.frame = ttk.Frame(self.root, padding=self.padding, height=self.height, width=self.width)
        self.frame.grid()
        ttk.Label(self.frame, text="Do You wish to save the line coordinates?").grid(row=0, column=0)
        ttk.Button(self.frame, text="Yes", command=self.save_coords_yes).grid(row=1, column=0)
        ttk.Button(self.frame, text="No", command=self.root.destroy).grid(row=2, column=0)
        self.root.mainloop()
    
    def choose_class(self):
        self.frame = ttk.Frame(self.root, padding=self.padding, height=self.height, width=self.width)
        self.frame.grid()  # Add frame to the root window
        all_classes = self.database.query_all_classes()
        clicked = StringVar()
        clicked.set(all_classes[0])
        drop = OptionMenu(self.frame, clicked, *all_classes)
        drop.grid(row=2, column=0)
        
        ttk.Label(self.frame, text="Choose a class from the dropdown menu, or create a new one").grid(row=0, column=0)
        ttk.Label(self.frame, text="ClassId, Name, Teacher, Room, Date, StartT, EndT, Counter line coords").grid(row=1,column=0)

        # Use lambda to pass the current value of clicked to select_class
        button = Button(self.frame, text="Choose class", command=lambda: self.select_class(clicked.get()))
        button.grid(row=3, column=0)
        Button(self.frame, text="Create new class", command=lambda: self.create_new_class()).grid(row=4, column=0)
        
    
    def create_new_class(self):
        self.frame.destroy()
        self.frame = ttk.Frame(self.root, padding=self.padding)
        self.frame.grid()

        # Create labels and text inputs
        ttk.Label(self.frame, text="Subject:").grid(row=0, column=0, sticky=E)
        subject_entry = ttk.Entry(self.frame, width=30)
        subject_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.frame, text="Teacher:").grid(row=1, column=0, sticky=E)
        teacher_entry = ttk.Entry(self.frame, width=30)
        teacher_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.frame, text="Room Number:").grid(row=2, column=0, sticky=E)
        room_entry = ttk.Entry(self.frame, width=30)
        room_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.frame, text="Date (YYYY-MM-DD):").grid(row=3, column=0, sticky=E)
        date_entry = ttk.Entry(self.frame, width=30)
        date_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self.frame, text="Start Time:").grid(row=5, column=0, sticky=E)
        start_time_entry = ttk.Entry(self.frame, width=30)
        start_time_entry.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(self.frame, text="End Time:").grid(row=6, column=0, sticky=E)
        end_time_entry = ttk.Entry(self.frame, width=30)
        end_time_entry.grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(self.frame, text="Number of Students:").grid(row=7, column=0, sticky=E)
        students_entry = ttk.Entry(self.frame, width=30)
        students_entry.grid(row=7, column=1, padx=5, pady=5)

        # Submit button
        submit_button = ttk.Button(self.frame, text="Submit", command=lambda: self.database.add_class(
            subject_entry.get(),
            teacher_entry.get(),
            room_entry.get(),
            date_entry.get(),
            start_time_entry.get(),
            end_time_entry.get(),
            int(students_entry.get())
        ))
        submit_button.grid(row=8, column=1, pady=10)
    
    def check_if_coords_exist(self): # Check if the selected class has coorda already assigned to it
        self.frame = ttk.Frame(self.root, padding=self.padding)
        self.frame.grid()  # Add frame to the root window
        if self.database.get_coordinates_by_id(self.selected_class[0]) != (None, None, None, None): # If it has coords assigned to it
            ttk.Label(self.frame, text="There already are line coordinates mapped to this class").grid(column=0, row=0)
            ttk.Label(self.frame, text="Do you wish to override them?").grid(row=1, column=0)
            Button(self.frame, text="Yes", command=lambda: self.override_existing_coords()).grid(row=2, column=0)
            Button(self.frame, text="No, Create a new entry", command=lambda: self.create_duplicate_entry()).grid(row=3, column=0)
        else:
            ttk.Label(self.frame, text="This class does not have coordinates saved.").grid(row=0, column=0)
            ttk.Label(self.frame, text="Do you wish to save them here, or create a new entry?").grid(row=1, column=0)
            ttk.Button(self.frame, text="Save them here", command=lambda: self.override_existing_coords()).grid(row=2, column=0)
            ttk.Button(self.frame, text="Create a new entry", command=lambda: self.create_duplicate_entry()).grid(row=3, column=0)

    def override_existing_coords(self): # Override coordinates of existing class
        self.frame.destroy()
        self.frame = ttk.Frame(self.root, padding=self.padding)
        self.frame.grid()
        self.override_line = True # Set this variable to true, which will be checked at the end of the main code to see whether to override coordinates or not
        # self.database.change_coordinates(self.selected_class[0], self.line_coords[0], self.line_coords[1], self.line_coords[2], self.line_coords[3])
        ttk.Label(self.frame, text="Coordinates overridden!").grid(row=0, column=0)
        Button(self.frame, text="Close", command=self.root.destroy).grid(row=1, column=0)

    def create_duplicate_entry(self):
        self.frame.destroy()
        self.frame = ttk.Frame(self.root, padding=self.padding)
        self.frame.grid()
        self.database.add_class(self.selected_class[1], # subject
                                self.selected_class[2], # teacher
                                self.selected_class[3], # room_number
                                self.selected_class[4], # date
                                self.selected_class[5], # start_time
                                self.selected_class[6], # end_time
                                self.selected_class[7]  # number_of_students
                                # self.line_coords[0],
                                # self.line_coords[1], 
                                # self.line_coords[2], 
                                # self.line_coords[3]
                                )
        ttk.Label(self.frame, text="New Class entry created successfully!").grid(row=0, column=0)
        Button(self.frame, text="Okay", command=self.root.destroy).grid(row=1, column=0)

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
        self.save_line_coords = True
        self.choose_class()  # Proceed to choose_class

if __name__ == "__main__":
    ds = DatabaseService(DatabaseRepository())
    dui = DatabaseUI(ds)
    dui.choose_to_save_coords()
