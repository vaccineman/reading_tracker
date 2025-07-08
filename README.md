# BookmarkPy

## Project Description
The purpose of this project is to offer an easy way to track reading progress for books, novels and other forms of literature. Users can add their books to their collection and track their progress. Book progress can be saved as page progress or chapter progress. The reason for adding the option to choose between tracking progress by pages or chapters is because literature such as comics, manga, light novels have many chapters and will be much easier to track by chapter progress. Additionally, users can add images for their books to distinguish them more easily. This project uses Tkinter, which is Python's library for GUIs in addition to Pillow, which is a package for image processing. The 'Add With ISBN' feature uses the Open Library Books API to request title and author data of a book. Information about this API can be found here: [openlibrary.org](https://openlibrary.org/developers/api/)

## Installation
1. Ensure you have Python installed (3.11). Python can be downloaded from [python.org](https://www.python.org/downloads/).
2. Clone the repository or download the source code.
3. Navigate to the project directory and install the required packages using:
    '''bash
    pip install -r requirements.txt
4. From the directory, run the program using:
    '''bash
    python main.py

## Usage
1. Run the program.
2. Click the 'Add Book' button, or the 'Add From ISBN' button.
3. Enter information about your book, including the title, author, total pages (or chapters), current page (or chapter), and select an image. Adding a book with an ISBN will autofill the title and author fields.
4. Click 'Save' to add the book to your collection
5. View book progress percentage of the books in your collection.
5. Click 'Edit' on a book to change its information, or click 'Delete' to remove a book from your collection.
