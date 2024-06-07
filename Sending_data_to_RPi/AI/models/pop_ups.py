from tkinter import *
from tkinter import ttk

class Popups():
    def __init__(self, databaseService) -> None:
        self.database = databaseService

    def choose_to_save_coords():
        root = Tk()
        frame = ttk.Frame(root, padding=5)
        frame.grid()
        ttk.Label(frame, text="Do You wish to save the line coordinates?")
        ttk.Button(frame, text="Yes", command=check_if_coords_exist)