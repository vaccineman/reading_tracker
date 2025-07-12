import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import json
import requests
import threading

class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        # set window title
        self.root.title('BookmarkPy')

         # set window size and location
        self.root.geometry('660x440+50+50')

        # themes
        self.current_theme = 'light'
        self._define_themes()

        # data files
        self.data_file = 'books.json'
        self.books = []

        # load existing books
        self._load_data() # attempt to load books on startup

        # load icon Windows
        try:
            self.root.iconbitmap('./assets/book.ico')
        except tk.TclError:
            print ("Windows icon file not found")
        # load icon Linux
        try:
            photo = tk.PhotoImage(file='./assets/book_icon.png')
            self.root.iconphoto(False, photo)
        except tk.TclError:
            print("Linux icon file not found")

        self._load_default_images() # pre-load book image placeholder
        self._create_widgets() # build main app UI
        self._apply_theme() # apply initial theme and refresh the book list display

        # bind window close function to save function
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        """
        Handles window closing.
        Saves current book data to file before destroying the window.
        """
        self._save_data()
        self.root.destroy() # Close Tkinter application properly

    def _load_data(self):
        """
        Loads book data and theme selection from the JSON file.
        If the file doesn't exist or is invalid, an empty list is initialized.
        """
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.books = data.get('books', [])
                    self.current_theme = data.get('theme', 'light')
                print(f"Loaded {len(self.books)} books and theme '{self.current_theme}' from {self.data_file}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {self.data_file}: {e}. Starting with empty book list and default theme.")
                self.books = [] # Reset if file is corrupted
                self.current_theme = 'light'
            except Exception as e:
                print(f"An unexpected error occurred while loading books: {e}. Starting with empty book list and default theme.")
                self.books = []
                self.current_theme = 'light'
        else:
            print(f"no data file found at {self.data_file}. Starting with an empty book list and default theme.")
            self.books = [] # Initialize empty list if file doesn't exist
            self.current_theme = 'light'

    def _save_data(self):
        """
        Saves current book data and theme selection to the JSON file.
        """
        try:
            data_to_save = {
                'books': self.books,
                'theme': self.current_theme
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=4)
            print(f"Saved {len(self.books)} books and theme '{self.current_theme}' to {self.data_file}")
        except Exception as e:
                print(f"Error saving books to {self.data_file}: {e}")

    def _define_themes(self):
        """
        Defines the color palettes for light and dark themes.
        """
        self.themes = {
            'light': {
                'root_bg': '#f0f0f0',
                'frame_bg': '#e6e6fa',
                'label_bg': '#e6e6fa',
                'text_color': '#333333',
                'canvas_bg': 'white',
                'button_bg': '#d3d3d3',
                'button_fg': '#333333',
                'entry_bg': 'white',
                'entry_fg': '#333333',
                'dialog_bg': '#f0f0f0',
                'dialog_frame_bg': '#f0f0f0'
            },
            'dark': {
                'root_bg': '#2e2e2e',
                'frame_bg': '#3c3c3c',
                'label_bg': '#3c3c3c',
                'text_color': '#f0f0f0',
                'canvas_bg': '#1e1e1e',
                'button_bg': '#555555',
                'button_fg': '#f0f0f0',
                'entry_bg': '#444444',
                'entry_fg': '#f0f0f0',
                'dialog_bg': '#2e2e2e',
                'dialog_frame_bg': '#2e2e2e'
            }
        }
    
    def _apply_theme(self):
        """
        Applies the current theme to all relevant widgets.
        """
        theme_colors = self.themes[self.current_theme]
        style = ttk.Style()

        # 'clam' style allows button backgrounds to be colored fully.
        style.theme_use('clam')

        # Root window background
        self.root.config(bg=theme_colors['root_bg'])

        # Main frames and canvas
        style.configure("Themed.TFrame", background=theme_colors['root_bg'])
        style.configure("CanvasFrame.TFrame", background=theme_colors['canvas_bg'])

        # Configure custom ttk styles for book entries
        style.configure("BookCard.TFrame", background=theme_colors['frame_bg'],
            foreground=theme_colors['text_color'], borderwidth=2, relief="ridge", padding=5)
        style.configure("BookCard.TLabel", background=theme_colors['label_bg'],
            foreground=theme_colors['text_color'])

        # Configure general ttk styles for buttons, labels, entries, checkbuttons
        style.configure("TFrame", background=theme_colors['root_bg'])
        style.configure("TLabel", background=theme_colors['root_bg'], foreground=theme_colors['text_color'])
        style.configure("Themed.TButton",
            background=theme_colors['button_bg'],
            foreground=theme_colors['button_fg'],
            bordercolor=theme_colors['button_bg'],
            lightcolor=theme_colors['button_bg'],
            darkcolor=theme_colors['button_bg'],
            relief='flat',
            focusthickness=0,
            padding=5
            )
        # Make sure theme applies when hovering over
        style.map("Themed.TButton",
            background=[('active', theme_colors['button_bg'])],
            foreground=[('active', theme_colors['button_fg'])])

        style.configure("TEntry", fieldbackground=theme_colors['entry_bg'], foreground=theme_colors['entry_fg'])
        style.configure("Themed.TCheckbutton", background=theme_colors['root_bg'],
         foreground=theme_colors['text_color'],
         focusthickness=0,
         relief='flat')
         # Make sure theme applies when hovering over
        style.map("Themed.TCheckbutton", 
            background=[('active', theme_colors['root_bg'])],
            foreground=[('active', theme_colors['text_color'])])

        self.book_canvas.config(bg=theme_colors['canvas_bg'])
        
        # Re-apply theme to existing book entries
        self._refresh_book_display()
    
    def _toggle_theme(self):
        """
        Switches between light and dark themes.
        """
        if self.current_theme == 'light':
            self.current_theme = 'dark'
        else:
            self.current_theme = 'light'
        self._apply_theme()

    def _load_default_images(self):
        """
        Loads a default placeholder image.
        When a book doesn't have a selected image, or its file can't be found, a placeholder will be displayed.
        """ 
        try:
            """if os.path.exists('./assets/no_image.png'): # Attempt to load pre-existing 'no_image.png' from assets folder
                img = Image.open('./assets/no_image.png')
            else:"""
            # Attempt to draw a 'No Image' placeholder image
            img = Image.new('RGB', (100, 150), color = (200, 200, 200))
            d = ImageDraw.Draw(img)

            font = None
            common_fonts = ["arial.ttf", "DejaVuSans.ttf", "FreeSans.ttf"]
            for font_name in common_fonts:
                try:
                    font = ImageFont.truetype(font_name, 15)
                    break # Found a font
                except IOError:
                    pass # Try next font
            
            if font is None:
                try:
                    # Fallback to default font if no truetype font is found
                    font = ImageFont._load_default()
                except Exception as e:
                    print(f"Warning: Could not load any font for 'No Image' placeholder: {e}")
                    
            if font: # Only draw text if a font is loaded
                # Calculate text position to center it
                text_width, text_height = d.textbbox((0, 0), "No Image", font=font)[2:]
                x = (100 - text_width) / 2
                y = (100 - text_height) / 2
                d.text((x, y), "No Image", fill=(50, 50, 50), font=font)

            self.no_image_photo = ImageTk.PhotoImage(img) # Convert PIL Image to Tkinter Photoimage
        except Exception as e:
            print(f"Error creating 'no image' placeholder: {e}")
            self.no_image_photo = tk.PhotoImage(width=1, height=1)



    
    def _create_widgets(self):
        """
        This sets up the main layout and widgets for the application.
        """
        # Configure a custom style for the book entry frames
        style = ttk.Style()
        # Define a generic style for frames configured by theme
        style.configure("Themed.TFrame", background=self.themes[self.current_theme]['root_bg'])
        # Style for frame inside canvas
        style.configure("CanvasFrame.TFrame", background=self.themes[self.current_theme]['canvas_bg'])

        # Configure Grid for the Root Window
        self.root.grid_rowconfigure(0, weight=1) # Allow the single row to expand vertically
        self.root.grid_columnconfigure(0, weight=0) # Button column has fixed width
        self.root.grid_columnconfigure(1, weight=1) # Book list column expands horizontally

        # Left Column: Button Frame
        self.button_frame = ttk.Frame(self.root, width=150, relief=tk.RAISED, borderwidth=1, style="Themed.TFrame")
        self.button_frame.grid(row=0, column=0, sticky='ns', padx=5,pady=5) #'ns' - north-south
        self.button_frame.grid_propagate(False) # Prevent frame from resizing itself to fit contents

        # Add Book Button within the button frame
        add_book_btn = ttk.Button(self.button_frame, text="Add Book", command=self._open_add_book_dialog, style="Themed.TButton")
        add_book_btn.pack(pady=10,padx=5, fill='x') # Pack button within padding and expand horizontaly

        # Add from ISBN button
        add_isbn_btn = ttk.Button(self.button_frame, text="Add from ISBN", command=self._open_isbn_dialog, style="Themed.TButton")
        add_isbn_btn.pack(pady=5, padx=5, fill='x') # Pack below 'Add Book'

        # Light/Dark mode toggle button
        theme_toggle_btn = ttk.Button(self.button_frame, text="Light/Dark Mode", command=self._toggle_theme, style="Themed.TButton")
        theme_toggle_btn.pack(pady=5, padx=5, fill='x')

        # Right Column: Book List Container
        self.books_list_container = ttk.Frame(self.root, relief=tk.GROOVE, borderwidth=1, style="Themed.TFrame")
        self.books_list_container.grid(row=0, column=1, sticky='nsew', padx=5, pady=5) # 'nsew' fills all directions
        self.books_list_container.grid_rowconfigure(0, weight=1) # Allow the canvas row to expand
        self.books_list_container.grid_columnconfigure(0, weight=1) # Allow the canvas column to expand

        # Canvas for scrollable content
        self.book_canvas = tk.Canvas(self.books_list_container, bg=self.themes[self.current_theme]['canvas_bg'])
        self.book_canvas.grid(row=0, column=0, sticky='nsew')

        # Vertical Scrollbar for the canvas
        self.book_scrollbar = ttk.Scrollbar(self.books_list_container, orient="vertical", command=self.book_canvas.yview)
        self.book_scrollbar.grid(row=0, column=1, sticky='ns')
        self.book_canvas.configure(yscrollcommand=self.book_scrollbar.set)

        # Create a frame inside the canvas to hold all individual book entries
        # The canvas will draw this frame as a scrollable window
        self.book_list_frame = ttk.Frame(self.book_canvas, style="CanvasFrame.TFrame")
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
        book_frame.grid(row=index, column=0, sticky='ew', padx=5, pady=5)
        self.book_list_frame.grid_columnconfigure(0, weight=1) # Expands column with book_frame

        # Configure columns in the individual book_frame
        book_frame.grid_columnconfigure(0, weight=0) # Image column
        book_frame.grid_columnconfigure(1, weight=1) # Details column (expands)
        book_frame.grid_columnconfigure(0, weight=2) # Buttons column

        # Book image display
        image_label = ttk.Label(book_frame)
        image_label.grid(row=0, column=0, rowspan=3, padx=10, pady=5, sticky='n') # Spans 3 rows, alligning to the top

        # Load and display images
        image_path = book.get('image_path', '')
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                # Thumbnail resizes image proportionally to fit within 100x150
                img.thumbnail((100, 150), Image.LANCZOS) # LANCZOS image rescale
                photo = ImageTk.PhotoImage(img)
                image_label.config(image=photo)
                image_label.image = photo # reference to prevent memory from freeing up
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
                # Fallback to "No Image" if there is an error loading the image at the given path
                image_label.config(image=self.no_image_photo)
                image_label.image = self.no_image_photo
        else:
            # Display the placeholder image if no path or file doesn't exist
            image_label.config(image=self.no_image_photo)
            image_label.image = self.no_image_photo

        # Book details (Title, Author, Progress)
        title_label = ttk.Label(book_frame, text=f"Title: {book['title']}", font=('Arial', 12, 'bold'), style="BookCard.TLabel")
        title_label.grid(row=0, column=1, sticky='w', pady=2)

        author_label = ttk.Label(book_frame, text=f"Author: {book['author']}", font=('Arial', 10), style="BookCard.TLabel")
        author_label.grid(row=1, column=1, sticky='w', pady=2)

        progress_str = self._get_progress_string(book) # Get formatted progress string
        progress_label = ttk.Label(book_frame, text=f"Progress: {progress_str}", font=('Arial', 10), style="BookCard.TLabel")
        progress_label.grid(row=2, column=1, sticky='w', pady=2)

        # Edit and delete buttons
        button_container = ttk.Frame(book_frame, style="BookCard.TFrame")
        button_container.grid(row=2, column=2, sticky='se', padx=5, pady=5) # Buttons aligned bottom right

        edit_btn = ttk.Button(button_container, text="Edit", command=lambda b=book, i=index: self._open_edit_book_dialog(b, i), style="Themed.TButton")
        edit_btn.pack(side='left', padx=2) # Buttons packed side by side

        delete_btn = ttk.Button(button_container, text="Delete", command=lambda i=index: self._confirm_delete_book(i), style="Themed.TButton")
        delete_btn.pack(side='left', padx=2)

    def _get_progress_string(self, book):
        """
        Calculates and formats the progress string for a book.
        Args:
            book (dict): A dictionary containing the book's data (title, author, progress, etc.)
        Returns:
            str: The formatted progress string.
        """
        if book['track_chapters']:
            total_units = book['total_chapters']
            current_units = book['current_chapter']
            unit_name = "chapters"
        else:
            total_units = book['total_pages']
            current_units = book['current_progress']
            unit_name = "pages"
        
        # Hande cases where total_units is None or zero to avoid dividing by zero
        if total_units is None or total_units == 0:
            return "N/A"
        if current_units is None:
            current_units = 0 # Treat None as 0

        # Calculate percentage
        if total_units > 0:
            percentage = (current_units / total_units) * 100
        else:
            percentage = 0
        return f"{current_units}/{total_units} ({percentage:.0f}%) {unit_name}"

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
    
    def _open_add_book_dialog(self, initial_title="", initial_author=""):
        """
        Opens the dialog for adding a new book.
        Args:
            initial_title (str): Pre-fill for the title field.
            initial_author (str): Pre-fill for the author field.
        """
        self._open_book_dialog(is_edit=False, initial_title=initial_title, initial_author=initial_author)

    def _open_edit_book_dialog(self, book_data, index):
        """
        Opens the dialog for editing an existing book.
        Args:
            book_data (dict): Dictionary of the book to be edited.
            index (int): index of the book in the 'self.books' list to update.
        """
        self._open_book_dialog(is_edit=True, book_data=book_data, index=index)
    
    def _open_book_dialog(self, is_edit, book_data=None, index=None, initial_title="", initial_author=""):
        """
        Function to create and manage the Add/Edit Book dialog window.
        Args:
            is_edit (bool): True if the window is for editing, False for adding.
            book_data (dict): The data of a book to pre-fill if in edit mode.
            index (int): The list index of the book in edit mode.
            initial_title (str): Pre-fill for the title field.
            initial_author (str): Pre-fill for the author field.
        """
        dialog = tk.Toplevel(self.root) # creates new top level window
        dialog.title("Add New Book" if not is_edit else "Edit Book") # set window title
        dialog.transient(self.root) # window stays on top of main window
        dialog.grab_set() # Make the dialog modal, preventing interaction with main window
        dialog.resizable(False, False) # Prevent window resizing

        # Apply theme to dialog background
        dialog.config(bg=self.themes[self.current_theme]['dialog_bg'])

        dialog_frame = ttk.Frame(dialog, padding="15", style="Themed.TFrame")
        dialog_frame.pack(fill='both', expand=True)

        # Title and Author input fields
        ttk.Label(dialog_frame, text="Title:", font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=2)
        title_entry = ttk.Entry(dialog_frame, width=40, font=('Arial', 10))
        title_entry.grid(row=0, column=1, sticky='ew', pady=2, padx=5)

        ttk.Label(dialog_frame, text="Author:", font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=2)
        author_entry = ttk.Entry(dialog_frame, width=40, font=('Arial', 10))
        author_entry.grid(row=1, column=1, sticky='ew', pady=2, padx=5)

        # Image Selection
        image_path_var = tk.StringVar() # StringVar to hold the selected image file path
        # Display the image path with wraplength to handle long paths
        image_path_label = ttk.Label(dialog_frame, textvariable=image_path_var, font=('Arial', 9), wraplength=250)
        image_path_label.grid(row=2, column=1, sticky='ew', pady=2, padx=5)
        # Button to open file dialog for image selection
        ttk.Button(dialog_frame, text='Select Image', command=lambda: self._select_image_file(image_path_var), style="Themed.TButton").grid(row=2, column=0, sticky='w', pady=2)

        # Progress tracking toggle
        track_chapters_var = tk.BooleanVar() # Track the state of the checkbox
        track_chapters_checkbox = ttk.Checkbutton(dialog_frame, text="Track by chapters instead of pages", variable=track_chapters_var, style="Themed.TCheckbutton")
        track_chapters_checkbox.grid(row=3, column=0, columnspan=2, sticky='w', pady=5)

        # Input fields for page tracking (visability managed by _toggle_chapter_inputs)
        total_pages_label = ttk.Label(dialog_frame, text="Total Pages:", font=('Arial', 10))
        total_pages_entry = ttk.Entry(dialog_frame, width=20, font=("Arial", 10))
        current_progress_label = ttk.Label(dialog_frame, text="Current Page:", font=("Arial", 10))
        current_progress_entry = ttk.Entry(dialog_frame, width=20, font=("Arial", 10))

        # Input fields for chapter tracking (visability managed by _toggle_chapter_inputs)
        total_chapters_label = ttk.Label(dialog_frame, text="Total Chapters:", font=("Arial", 10))
        total_chapters_entry = ttk.Entry(dialog_frame, width=20, font=("Arial", 10))
        current_chapter_label = ttk.Label(dialog_frame, text="Current Chapter:", font=("Arial", 10))
        current_chapter_entry = ttk.Entry(dialog_frame, width=20, font=("Arial", 10))

        # Configure the command for the toggle checkbox. It calls _toggle_chapter_inputs
        track_chapters_checkbox.config(command=lambda: self._toggle_chapter_inputs(
            track_chapters_var.get(),
            total_pages_label, total_pages_entry, current_progress_label, current_progress_entry,
            total_chapters_label, total_chapters_entry, current_chapter_label, current_chapter_entry
        ))

        # Populate fields if in edit mode
        if is_edit and book_data:
            title_entry.insert(0, book_data['title'])
            author_entry.insert(0, book_data['author'])
            image_path_var.set(book_data.get('image_path', ''))
            track_chapters_var.set(book_data['track_chapters'])

            # Initial call to _toggle_chapter_inputs. Sets visibility of page/chapter inputs.
            self._toggle_chapter_inputs(
                track_chapters_var.get(),
                total_pages_label, total_pages_entry, current_progress_label, current_progress_entry,
                total_chapters_label, total_chapters_entry, current_chapter_label, current_chapter_entry
            )

            # Populate chapter/page fields and handle None values
            if book_data['track_chapters']:
                total_chapters_entry.insert(0, str(book_data['total_chapters']) if book_data['total_chapters'] is not None else "")
                current_chapter_entry.insert(0, str(book_data['current_chapter']) if book_data['current_chapter'] is not None else "")
            else:
                total_pages_entry.insert(0, str(book_data['total_pages']) if book_data['total_pages'] is not None else "")
                current_progress_entry.insert(0, str(book_data['current_progress']) if book_data['current_progress'] is not None else "")
        elif initial_title or initial_author: # Fill title and/or author fields with initial data from ISBN search
            title_entry.insert(0, initial_title)
            author_entry.insert(0, initial_author)
            # For new books, default to page tracking and show these fields
            track_chapters_var.set(False)
            self._toggle_chapter_inputs(
                False,
                total_pages_label, total_pages_entry, current_progress_label, current_progress_entry,
                total_chapters_label, total_chapters_entry, current_chapter_label, current_chapter_entry
            )
        else:
            track_chapters_var.set(False)
            self._toggle_chapter_inputs(
                False,
                total_pages_label, total_pages_entry, current_progress_label, current_progress_entry,
                total_chapters_label, total_chapters_entry, current_chapter_label, current_chapter_entry
            )  

        # Save and cancel buttons
        button_frame = ttk.Frame(dialog_frame, style="Themed.TFrame")
        button_frame.grid(row=6, column=0, columnspan=2, pady=10) # Positioned after input fields

        # Define the command for the save Button
        save_command = lambda: self._save_book_data(
            dialog, is_edit, index,
            title_entry.get(), author_entry.get(), image_path_var.get(),
            track_chapters_var.get(),
            total_pages_entry.get(), current_progress_entry.get(),
            total_chapters_entry.get(), current_chapter_entry.get()
        )
        ttk.Button(button_frame, text="Save", command=save_command, style="Themed.TButton").pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, style="Themed.TButton").pack(side='left', padx=5)

        # Make the second column of the dialog_frame expandable
        dialog_frame.grid_columnconfigure(1, weight=1)
    
    def _select_image_file(self, image_path_var):
        """
        Opens a file dialog to select an image.
        Updates the provided image_path_var with the selected file's full path.
        """
        # Get path to the 'book_images' folder from the current working directory 
        current_directory = os.getcwd()
        book_images_folder = os.path.join(current_directory, 'book_images')

        file_path = filedialog.askopenfilename(
            title='Select Book Image',
            # Define allowed image types
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All Files", "*.*")],
            # Open 'book_images' as initial directory
            initialdir=book_images_folder
        )
        if file_path:
            image_path_var.set(file_path) # Update image_path_var with path

    def _toggle_chapter_inputs(self, track_chapters, total_pages_label, total_pages_entry, current_progress_label, current_progress_entry, total_chapters_label, total_chapters_entry, current_chapter_label, current_chapter_entry):
        """
        Manages the visibility of either page or chapter input fields in the
        Add/Edit book dialog based on the 'track_chapters' boolean.
        It hides one set of inputs and shows the other.
        """
        # Define the common grid parameters of the input labels and entries
        label_grid_params = {'column': 0, 'sticky': 'w', 'pady': 2}
        entry_grid_params = {'column': 1, 'sticky': 'ew', 'pady': 2, 'padx': 5}

        if track_chapters:
            # Hide page inputs
            total_pages_label.grid_forget() # Remove from grid layout
            total_chapters_entry.grid_forget()
            current_progress_label.grid_forget()
            current_progress_entry.grid_forget()

            # Show chapter inputs
            total_chapters_label.grid(row=4, **label_grid_params) # Unpack dictionary, add to grid layout
            total_chapters_entry.grid(row=4, **entry_grid_params)
            current_chapter_label.grid(row=5, **label_grid_params)
            current_chapter_entry.grid(row=5, **entry_grid_params)
        else:
            # Show page inputs
            total_pages_label.grid(row=4, **label_grid_params)
            total_pages_entry.grid(row=4, **entry_grid_params)
            current_progress_label.grid(row=5, **label_grid_params)
            current_progress_entry.grid(row=5, **entry_grid_params)

            # Hide chapter inputs
            total_chapters_label.grid_forget()
            total_chapters_entry.grid_forget()
            current_chapter_label.grid_forget()
            current_chapter_entry.grid_forget()

    
    def _save_book_data(self, dialog, is_edit, index, title, author, image_path, track_chapters, total_pages_str, current_progress_str, total_chapters_str, current_chapter_str):
        """
        Saves or updates book data based on the inputs from the Add/Edit Book dialog.
        Validates input values.
        Args:
            dialog (tk.Toplevel): The dialog window to destroy after saving
            is_edit (bool): True when updating an existing book, False when adding a neew book.
            index (int): The list index of the book in edit mode.
            title (str), author(str), image_path(str): basic book details
            track_chapters (bool): True when tracking progress by chapters, False when tracking progress by pages.
            total_pages_str (str), current_progress_str (str): String values of page counts.
            total_chapters_str (str), current_chapter (str): String values of chapter counts.
        """
        # Validate required fields (title and author)
        if not title.strip() or not author.strip(): # Removing leading and trailing whitespace
            messagebox.showerror("Input Error", "Title and Author cannot be empty.")
            return
        
        # Initialize numeric progress variables to None. Populate if valid.
        total_pages = None
        current_progress = None
        total_chapters = None
        current_chapter = None

        try:
            if not track_chapters: # Processing for page tracking
                if total_pages_str.strip(): # Only precess when string isn't empty
                    total_pages = int(total_pages_str)
                if current_progress_str.strip():
                    current_progress = int(current_progress_str)
            else: # Procesing for chapter tracking
                if total_chapters_str.strip():
                    total_chapters = int(total_chapters_str)
                if current_chapter_str.strip():
                    current_chapter = int(current_chapter_str)
        except ValueError:
            messagebox.showerror("Input Error", "Page/Chapter counts must be valid numbers (or left empty).")
            return

        # Validate that counts are not negative
        if (total_pages is not None and total_pages < 0) or \
           (current_progress is not None and current_progress < 0) or \
           (total_chapters is not None and total_chapters < 0) or \
           (current_chapter is not None and current_chapter < 0):
            messagebox.showerror("Input Error", "Counts cannot be negative.")
            return

        # Validate current progress against total count, ensuring current <= total
        if not track_chapters:
            if current_progress is not None and total_pages is not None and current_progress > total_pages:
                messagebox.showerror("Input Error", "Current page cannot exceed total pages.")
                return
        else:
            if current_chapter is not None and total_chapters is not None and current_chapter > total_chapters:
                messagebox.showerror("Inpur Error", "Current chapter cannot exceed total chapters.")
                return
        
        # COnstruct the book data entry
        book_data = {
            'title': title.strip(),
            'author': author.strip(),
            'image_path': image_path,
            'track_chapters': track_chapters,
            'total_pages': total_pages,
            'current_progress': current_progress,
            'total_chapters': total_chapters,
            'current_chapter': current_chapter
        }

        if is_edit:
            self.books[index] = book_data # Update existing book entry
        else:
            self.books.append(book_data) # Add new book entry
        
        dialog.destroy() # Close dialog window
        self._save_data() # Save updated data to file
        self._refresh_book_display() # Refresh display for changes


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
        self._save_data() # Update the data for the file
        self._refresh_book_display() # Update the UI to reflect the deletion
    
    def _open_isbn_dialog(self):
        """
        Opens a dialog for entering an ISBN (either 10 or 13).
        """
        isbn_dialog = tk.Toplevel(self.root)
        isbn_dialog.title("Add Book by ISBN")
        isbn_dialog.transient(self.root)
        isbn_dialog.grab_set()
        isbn_dialog.resizable(False, False)

        # Apply theme to dialong background
        isbn_dialog.config(bg=self.themes[self.current_theme]['dialog_bg'])

        dialog_frame = ttk.Frame(isbn_dialog, padding="15", style="Themed.TFrame")
        dialog_frame.pack(fill='both', expand=True)

        ttk.Label(dialog_frame, text="Enter ISBN (10 and 13 digits):", font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        isbn_entry = ttk.Entry(dialog_frame, width=30, font=('Arial', 10))
        isbn_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=5)

        status_label = ttk.Label(dialog_frame, text="", font=('Arial', 9, 'italic'), foreground=self.themes[self.current_theme]['text_color'])
        status_label.grid(row=1, column=0, columnspan=2, pady=5)

        def search_command():
            isbn = isbn_entry.get().strip()
            self._search_book_by_isbn(isbn, isbn_dialog, status_label)
        
        button_frame = ttk.Frame(dialog_frame, style="Themed.TFrame")
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Search", command=search_command, style="Themed.TButton").pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=isbn_dialog.destroy, style="Themed.TButton").pack(side='left', padx=5)

        dialog_frame.grid_columnconfigure(1, weight=1) # Make ISBN entry expandable

    def _search_book_by_isbn(self, isbn, isbn_dialog, status_label):
        """
        Initiates the book search by ISBN in a separate thread, keeping the UI responsive.
        Args:
            isbn (str): The ISBN entered by the user.
            isbn_dialog (tk.Toplevel): The ISBN dialog window.
            status_label (ttk.Label): The label to update with status messages.
        """
        if not isbn.isdigit() or (len(isbn) != 10 and len(isbn) != 13):
            status_label.config(text="Invalid ISBN. Please enter 10 or 13 digits.", foreground='red')
            return
        
        status_label.config(text="Searching Open Library...", foreground=self.themes[self.current_theme]['text_color'])
        # Start a new thread for the API call
        thread = threading.Thread(target=self._fetch_book_data_thread, args=(isbn, isbn_dialog, status_label))
        thread.daemon = True # Allow the main program to exit even if this thread is running
        thread.start()

    def _fetch_book_data_thread(self, isbn, isbn_dialog, status_label):
        """
        Fetches book data from Open Libray API in a separate thread.
        Args:
            isbn (str): The ISBN to search for.
            isbn_dialog (tk.Toplevel): The ISBN dialog window.
            status_label (ttk.Label): The label to update with status messages.
        """
        try:
            url = f"https://openlibrary.org/isbn/{isbn}.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status() # Raise HTTPError for bad responses
            edition_data = response.json()

            book_info = None
            title = edition_data.get('title', 'Unknown Title')

            # Extract works key and data
            work_key = None
            works_list = edition_data.get('works')
            if works_list:
                # Assuming the first work in the list is the primary one
                work_key = works_list[0].get('key')

            authors_data = []
            if work_key:
                work_url = f"https://openlibrary.org{work_key}.json"
                work_response = requests.get(work_url, timeout = 10)
                work_response.raise_for_status()
                work_data = work_response.json()
                authors_data = work_data.get('authors', [])
            else:
                # If no key found, try to get authors from edition_data
                authors_data = edition_data.get('authors', [])

            author_names = []
            for author_entry in authors_data:
                author_key = author_entry.get('author', {}).get('key')
                if not author_key:
                    author_key = author_entry.get('key')
                if author_key:
                    try:
                        author_url = f"https://openlibrary.org{author_key}.json"
                        author_response = requests.get(author_url, timeout=5)
                        author_response.raise_for_status()
                        author_data = author_response.json()
                        author_name = author_data.get('name', 'Unknown Author')
                        author_names.append(author_name)
                    except requests.exceptions.RequestException as e:
                        print(f"Error fetching author data for {author_key}: {e}")
                        author_names.append("Unknown Author") # 'Unknown Author' for failed author lookup
                    except json.JSONDecodeError:
                        print(f"Could not parse author API response for {author_key}")
                        author_names.append("Unknown Author")
                else:
                    # No key present
                    author_names.append("Unknown Author")

            final_author_string = ", ".join(author_names) if author_names else "Unknown Author"

            book_info = None
            if title != 'Unknown Title' or final_author_string != 'Unknown Author':
                book_info = {'title': title, 'author': final_author_string}

            # Schedule the result processing on the main Tkinter thread
            self.root.after(0, self._process_isbn_results, book_info, isbn_dialog, status_label)
        
        except requests.exceptions.Timeout:
            self.root.after(0, status_label.config, {"text": "API request times out.", "foreground": "red"})
        except requests.exceptions.RequestException as e:
            self.root.after(0, status_label.config, {"text": f"Network Error: {e}", "foreground": "red"})
        except json.JSONDecodeError:
            self.root.after(0, status_label.config, {"text": "Could not parse API response (invalid JSON).", "foreground": "red"})
        except Exception as e:
            self.root.after(0, status_label.config, {"text": f"An unexpected error occured: {e}", "foreground": "red"})
    
    def _process_isbn_results(self, book_info, isbn_dialog, status_label):
        """
        Processes the results of the ISBN search on the main Tkinter thread.
        Args:
            book_info (dict or None): Dictionary containing 'title' and 'author' if found, otherwise None.
            isbn_dialog (tk.Toplevel): The ISBN dialog window.
            status_label (ttk.Label): The label to update with status messages.
        """
        if book_info:
            isbn_dialog.destroy()
            self._open_add_book_dialog(initial_title=book_info['title'], initial_author=book_info['author'])
        else:
            status_label.config(text="Book not found for this ISBN.", foreground='red')

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTrackerApp(root)

    # keep the window displaying for Windows and Linux
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    finally:
        root.mainloop()
