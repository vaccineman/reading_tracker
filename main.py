import tkinter as tk
from tkinter import ttk

import os
import json

class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        # set window title
        self.root.title('Reading Tracker')

         # set window size and location
        self.root.geometry('600x400+50+50')

        # data files
        self.data_file = 'books.json'
        self.books = []

        # load existing books
        self._load_books() # attempt to load books on startup

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

        self._load_default_images() # pre-load book image placeholder
        self._create_widgets() # build main app UI
        self._refresh_book_display() # refresh the book list display

        # bind window close function to save function
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        """
        Handles window closing.
        Saves current book data to file before destroying the window.
        """
        self._save_books()
        self.root.destroy() # Close Tkinter application properly

    def _load_books(self):
        """
        Loads book data from the JSON file.
        If the file doesn't exist or is invalid, an empty list is initialized.
        """
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.books = json.load(f)
                print(f"Loaded {len(self.books)} books from {self.data_file}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {self.data_file}: {e}. Starting with empty book list.")
                self.books = [] # Reset if file is corrupted
            except Exception as e:
                print(f"An unexpected error occurred while loading books: {e}. Starting with empty book list")
                self.books = []
        else:
            print(f"no data file found at {self.data_file}. Starting with an empty book list.")
            self.books = [] # Initialize empty list if file doesn't exist

        # TODO

    def _save_books(self):
        """
        Saves current book data to the JSON file.
        """
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.books, f, indent=4)
            print(f"Saved {len(self.books)} books to {self.data_file}")
        except Exception as e:
                print(f"Error saving books to {self.data_file}: {e}")

    def _load_default_images(self):
        """
        Loads a default placeholder image.
        When a book doesn't have a selected image, or its file can't be found, a placeholder will be displayed.
        """
        # TODO
    
    def _create_widgets(self):
        """
        This sets up the main layout and widgets for the application.
        """
        # Configure a custom style for the book entry frames
        style = ttk.Style()
        # Define a 'BookCard.TFrame' style for book entries and ensure lebels have the same background
        style.configure("BookCard.TFrame", background = "#e6e6fa", borderwidth=2, relief="ridge", padding=5)
        style.configure("BookCard.TLabel", background="#e6e6fa")

        # Configure Grif for the Root Window
        self.root.grid_rowconfigure(0, weight=1) # Allow the single row to expand vertically
        self.root.grid_columnconfigure(0, weight=0) # Button column has fixed width
        self.root.grid_columnconfigure(1, weight=1) # Book list column expands horizontally

        # Left Column: Button Frame
        self.button_frame = ttk.Frame(self.root, width=150, relief=tk.RAISED, borderwidth=1)
        self.button_frame.grid(row=0, column=0, sticky='ns', padx=5,pady=5) #'ns' - north-south
        self.button_frame.grid_propagate(False) # Prevent frame from resizing itself to fit contents

        # Add Book Button within the button frame
        add_book_btn = ttk.Button(self.button_frame, text="Add Book", command=self._open_add_book_dialog)
        add_book_btn.pack(pady=10,padx=5, fill='x') # Pack button within padding and expand horizontaly

        # Right Column: Book List Container
        self.books_list_container = ttk.Frame(self.root, relief=tk.GROOVE, borderwidth=1)
        self.books_list_container.grid(row=0, column=1, sticky='nsew', padx=5, pady=5) # 'nsew' fills all directions
        self.books_list_container.grid_rowconfigure(0, weight=1) # Allow the canvas row to expand
        self.books_list_container.grid_columnconfigure(0, weight=1) # Allow the canvas column to expand

        # Canvas for scrollable content
        self.book_canvas = tk.Canvas(self.books_list_container, bg='white')
        self.book_canvas.grid(row=0, column=1, sticky='nsew')

        # Vertical Scrollbar for the canvas
        self.book_scrollbar = ttk.Scrollbar(self.books_list_container, orient="vertical", command=self.book_canvas.yview)
        self.book_scrollbar.grid(row=0, column=1, sticky='ns')
        self.book_canvas.configure(yscrollcommand=self.book_scrollbar.set)

        # Create a frame inside the canvas to hold all individual book entries
        # The canvas will draw this frame as a scrollable window
        self.book_list_frame = ttk.Frame(self.book_canvas)
        self.book_canvas.create_window((0,0), window=self.book_list_frame, anchor='nw') #anchor top left

        # Bind events to update the canvas scroll region and the inner frame's width, ensuring proper scrolling and that entries fill width
        self.book_list_frame.bind("<Configure>", lambda e: self.book_canvas.configure(scrollregion=self.book_canvas.bbox("all"))) # lamda used to wrap function with arguments
        self.book_canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_canvas_configure(self, event):
        """
        Callback function executed when the main canvas has been resized.
        This updates the width of the inner book list frame to match the canvas width,
        ensuring that book entries expand correctly and horizontal scrollbars are not needed.
        """
        canvas_width = event.width
        # Get the ID of the window item embedded within the canvas (book_list_frame)
        canvas_window_id = self.book_canvas.find_all()[-1]
        self.book_canvas.itemconfig(canvas_window_id, width=canvas_width)

    def _refresh_book_display(self):
        """
        Clears all existing book entry widgets from the display and redraws them based on
        the current state of the 'self.books' list.
        Called after adding, editing, or deleting a book.
        """

        # Destroy all existing widfets within the book_list_frame
        for widget in self.book_list_frame.winfo_children():
            widget.destroy()
        
        # Iterate through 'self.books' list and display each book
        for i, book in enumerate(self.books):
            self._display_book_entry(book, i)
        
        # After rendering widgets, update the canvas scroll reguib to ensure the scrollbar reflects the total height of the content.
        self.root.update_idletasks() # Ensures geometry calculations are complete before getting bbox.
        self.book_canvas.config(scrollregion=self.book_canvas.bbox("all"))

    def _display_book_entry(self, book, index):
        """
        Creates and displays a single book entry row within the book list.
        Args:
            book (dict): A dictionary containing the book's data (title, author, progress, etc.)
            index (int): The index of the book in the 'self.books' list, identifying which book to edit/delete when requested
        """
        book_frame = ttk.Frame(self.book_list_frame, style="BookCard.TFrame") # Use the custom style

        #TODO



    def add_book_entry(self, title, author, total_pages, current_progress, image_path, track_chapters, total_chapters, current_chapter):
        """
        Method to add a new book dictionary to the 'self.books' list.
        """
        new_book = {
            'title': title,
            'author': author,
            'image_path': image_path,
            'track_chapters': track_chapters,
            'total_pages': total_pages,
            'current_progress': current_progress,
            'total_chapters': total_chapters,
            'current_chapter': current_chapter
        }
        self.books.append(new_book)
    
    def _open_add_book_dialog(self):
        """
        Opens the dialog for adding a new book.
        """
        self._open_book_dialog(is_edit=False)

    def _open_add_book_dialog(self, book_data, index):
        """
        Opens the dialog for editing an existing book.
        Args:
            book_data (dict): Dictionary of the book to be edited.
            index (int): index of the book in the 'self.books' list to update.
        """
        self._open_book_dialog(is_edit=True, book_data=book_data, index=index)
    
    def _open_book_dialog(self, is_edit, book_data=None, index=None):
        """
        Function to create and manage the Add/Edit Book dialog window.
        Args:
            is_edit (bool): True if the window is for editing, False for adding.
            book_data (dict): The data of a book to pre-fill if in edit mode.
            index (int): The list index of the book in edit mode.
        """
        dialog = tk.Toplevel(self.root) # creates new top level window
        dialog.title("Add New Book" if not is_edit else "Edit Book") # set window title
        dialog.transient(self.root) # window stays on top of main window
        dialog.grab_set() # Make the dialog modal, preventing interaction with main window
        dialog.resizable(False, False) # Prevent window resizing

        dialog_frame = ttk.Frame(dialog, padding="15")
        dialog_frame.pack(fill='both', expand=True)

        # Title and Author input fields
        ttk.Label(dialog_frame, text="Title:", font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=2)
        title_entry = ttk.Entry(dialog_frame, width=40, font=('Arial', 10))
        title_entry.grid(row=0, column=1, sticky='ew', pady=2, padx=5)

        ttk.Label(dialog_frame, text="Author:", font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=2)
        author_entry = ttk.Entry(dialog_frame, width=40, font=('Arial', 10))
        author_entry.grid(row=1, column=1, sticky='ew', pady=2, padx=5)

        #TODO

    def _confirm_delete_book(self, index):
        """
        Displays a confirmation message box before deleting a book
        Args:
            index (int): The index of the book to be deleted
        """
        book_title = self.books[index]['title']
        # Message box returns True or False for 'Yes' or 'No' selected respectively
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{book_title}'?\nThis action cannot be undone."
        ):
            self._delete_book(index) # Proceed with deletion

    def _delete_book(self, index):
        """
        Deletes a book from the list and refreshes the display
        Args:
            index (int): The index of the book to be deleted
        """
        del self.books[index] # Removes the book from the list
        self._save_books() # Update the data for the file
        self._refresh_book_display() # Update the UI to reflect the deletion

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTrackerApp(root)

    # keep the window displaying for Windows macOS and Linux
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    finally:
        root.mainloop()
