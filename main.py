import tkinter as tk
from tkinter import ttk

class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        # set window title
        self.root.title('Reading Tracker')

         # set window size and location
        self.root.geometry('600x400+50+50')

        # load icon Windows
        try:
            self.root.iconbitmap('./assets/book.ico')
        except tk.TclError:
            print ("Windows icon file not found")
        # load icon Linux/MacOS
        try:
            photo = tk.PhotoImage(file='./assets/book_icon.png')
            self.root.iconphoto(False, photo)
        except tk.TclError:
            print("Linux/MacOS icon file not found")
        
        # Add Book button

        # Frame for input Selection

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTrackerApp(root)

    # keep the window displaying for Windows macOS and Linux
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    finally:
        root.mainloop()
