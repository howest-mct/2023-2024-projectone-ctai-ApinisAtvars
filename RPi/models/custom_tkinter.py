import customtkinter as ctk
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../services')))
from database_service import DatabaseService

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../repos')))
from sql import DatabaseRepository

class DatabaseUI():
    def __init__(self, databaseService) -> None:
        self.database = databaseService
        self.root = ctk.CTk()
        ctk.set_appearance_mode("dark")

        self.frame = None

        self.selected_class = None
        self.line_coords = None

        self.save_line_coords = False
        self.new_class_created = False
        

        self.padding = 50

        self.choose_class()
    

    def destroy_and_create_frame(self):
        self.frame.destroy()
        self.frame = ctk.CTkFrame(self.root, corner_radius=10, fg_color="transparent")
        self.frame.pack(padx=self.padding, pady=self.padding)

    def choose_class(self):
        self.frame = ctk.CTkFrame(self.root, corner_radius=10, fg_color="transparent")
        self.frame.pack(padx=self.padding, pady=self.padding)
        
        all_classes = [str(classroom) for classroom in self.database.query_all_classes()]
        clicked = ctk.StringVar()
        clicked.set(all_classes[0])
        drop = ctk.CTkOptionMenu(self.frame, variable=clicked, values=all_classes)

        drop.pack(pady=(10, 20))

        ctk.CTkLabel(self.frame, text="(ClassId, ClassName, Teacher, Room, Date, StartT, EndT, Counter line coordinates)").pack(pady = (0, 10))
        ctk.CTkLabel(self.frame, text="Choose a class from the dropdown menu, or create a new one.").pack(pady = (0,10))
        ctk.CTkLabel(self.frame, text="Tip: If You choose an existing class, you can create a duplicate later.").pack(pady = (5,10))

        ctk.CTkButton(self.frame, text="Choose class", command=lambda: self.check_if_coords_exist(clicked.get())).pack(pady=(0, 10))
        ctk.CTkButton(self.frame, text="Create new class", command=self.create_new_class).pack()

    @staticmethod
    def parse_tuple_from_string(data_str):
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


    def check_if_coords_exist(self, value):
        self.selected_class = self.parse_tuple_from_string(value)
        print(self.selected_class)
        self.destroy_and_create_frame()
        if self.database.get_coordinates_by_id(self.selected_class[0]) == (None, None, None, None): # If there are no coordinates
            ctk.CTkLabel(self.frame, text="This class doesn't have counter line coordinates assigned to it").pack()
            ctk.CTkLabel(self.frame, text="Do You wish to save them here, or create a duplicate?").pack()
            ctk.CTkButton(self.frame, text="Save them here", command=self.overwrite_class_coords).pack(pady=(5,5))
            ctk.CTkButton(self.frame, text="Create a duplicate class", command=self.create_duplicate_class).pack(pady=(5,5))
        else: # If there are coordinates
            ctk.CTkLabel(self.frame, text="This class already has counter line coordinates assigned to it").pack()
            ctk.CTkLabel(self.frame, text="Do You wish to overwrite them, or create a duplicate?").pack()
            ctk.CTkButton(self.frame, text="Overwrite coordinates", command=self.overwrite_class_coords).pack(pady=(5,5))
            ctk.CTkButton(self.frame, text="Use existing Coordinates", command=self.use_existing_coords).pack(pady=(5,5))
            ctk.CTkButton(self.frame, text="Create a duplicate class", command=self.create_duplicate_class).pack(pady=(5,5))

    def use_existing_coords(self):
        self.line_coords = self.selected_class[-4:]
        print(self.line_coords)
        self.root.destroy()

    def overwrite_class_coords(self):
        self.save_line_coords = True
        self.root.destroy()
    
    def create_duplicate_class(self):
        self.new_class_created_func(
            self.selected_class[1], # Subject
            self.selected_class[2], # Teacher
            self.selected_class[3], # Room number
            self.selected_class[4], # Date
            self.selected_class[5], # Start Time
            self.selected_class[6], # End Time
            self.selected_class[7], # Number of Students
        )
        self.save_line_coords = True

    

    def create_new_class(self):
        
        self.destroy_and_create_frame()

        entries = {}
        fields = ["Subject", "Teacher", "Room Number", "Date (YYYY-MM-DD)", "Start Time (HH:MM:SS)", "End Time (HH:MM:SS)", "Number of Students"]
        for idx, field in enumerate(fields):
            ctk.CTkLabel(self.frame, text=f"{field}:").grid(row=idx, column=0, pady=5, sticky='e')
            entries[field] = ctk.CTkEntry(self.frame, width=200)
            entries[field].grid(row=idx, column=1, pady=5, padx=10)

        submit_button = ctk.CTkButton(self.frame, text="Submit", command=lambda: self.new_class_created_func(
            entries["Subject"].get(),
            entries["Teacher"].get(),
            entries["Room Number"].get(),
            entries["Date (YYYY-MM-DD)"].get(),
            entries["Start Time (HH:MM:SS)"].get(),
            entries["End Time (HH:MM:SS)"].get(),
            int(entries["Number of Students"].get())
        ))
        submit_button.grid(row=len(fields), column=1, pady=20)

    def new_class_created_func(self,
                               subject,
                               teacher,
                               room,
                               date,
                               start,
                               end,
                               student_number):
        self.database.add_class(subject, teacher, room, date, start, end, student_number)
        self.save_line_coords = True
        self.new_class_created = True
        self.root.destroy()

if __name__=="__main__":
    ds = DatabaseService(DatabaseRepository())
    dui = DatabaseUI(ds)
    dui.root.mainloop()
    print("New class created: {}".format(dui.new_class_created))
    print("Save Line Coords: {}".format(dui.save_line_coords))
    print("Line Coordinates: {}".format(dui.line_coords))
    classid = ds.get_last_class_id()
    ds.change_coordinates(classid, 200, 200, 400, 200)
    print("last class id changed")