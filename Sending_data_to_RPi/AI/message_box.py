from tkinter import *
from tkinter import ttk

root = Tk() # Initialize an instance of Tkinter class
# frm = ttk.Frame(root, padding=50) # Create a frame (window), and fit it into the root window
# frm.grid() # Fix it to the grid
# ttk.Label(frm, text="Hello World!").grid(column=0, row=0) # Display static text string, grid() method puts it in a specific position
# ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=1) # Create a button, command= is a callback function, but it in column1, row0
# root.mainloop()


def check_if_coords_exist():
    global root
    root.destroy()
    root = Tk()
    frm = ttk.Frame(root, padding=20)
    frm.grid()
    ttk.Label(frm, text="Coords for this class are already saved. Do you wish to override, or save them in a new entry?").grid(column=0, row=0)
    ttk.Button(frm, text="Override", command=root.destroy).grid(row=1, column=0)
    ttk.Button(frm, text="Create new entry", command=root.destroy).grid(row=1, column=1)
    ttk.Button(frm, text="Don't save coords", command=root.destroy).grid(row=1, column=2)
    root.mainloop()

frm = ttk.Frame(root, padding=50) # Create a frame (window), and fit it into the root window
frm.grid()
ttk.Label(frm, text="Do you wish to save the coords to the database?").grid(column=0, row=0)
ttk.Button(frm, text="Yes", command=check_if_coords_exist).grid(row=1, column=0)
ttk.Button(frm, text="No", command=root.destroy).grid(row=1, column=1)
root.mainloop()