import tkinter as tk
from tkinter import ttk

if __name__ == "__main__":
    root = tk.Tk()
    # set window title
    root.title('Reading Tracker')

    # set window size and location
    root.geometry('600x400+50+50')

    # load icon Windows
    try:
        root.iconbitmap('./assets/book.ico')
    except tk.TclError:
        print ("Windows icon file not found")
    # load icon Linux/MacOS
    try:
        photo = tk.PhotoImage(file='./assets/book_icon.png')
        root.iconphoto(False, photo)
    except tk.TclError:
        print("Linux/MacOS icon file not found")
    

    # root window label
    message = ttk.Label(root, text="Message")
    # positions label on main window
    message.pack()
    

    # keep the window displaying for Windows macOS and Linux
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    finally:
        root.mainloop()
