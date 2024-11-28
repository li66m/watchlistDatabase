import sqlite3

class LibraryDatabase:
    def __init__(self, db_path="library.db"):
        """Initialize the database connection."""
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        """Close the database connection."""
        self.conn.close()

    def add_user(self, username, password, videoList_id=None):
        """Add a new user."""
        if not username or not password:
            raise ValueError("Username and password cannot be empty")
        query = "INSERT INTO users (username, password, videoList_id) VALUES (?, ?, ?)"
        self.cursor.execute(query, (username, password, videoList_id))
        self.conn.commit()

    def get_users(self):
        """Fetch all users."""
        query = "SELECT user_id, username FROM users"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_available_books(self, user_id):
        """Fetch all books that are not linked to the specified user."""
        query = """
            SELECT b.book_id, b.book_name, b.author, b.genre
            FROM books b
            WHERE b.book_id NOT IN (
                SELECT bs.book_id
                FROM book_slots bs
                JOIN book_list bl ON bs.bookList_id = bl.bookList_id
                WHERE bl.user_id = ?
            )
        """
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchall()

    def get_user_books(self, user_id):
        """Fetch all books linked to a specific user."""
        query = """
            SELECT b.book_id, b.book_name, b.author, b.genre
            FROM books b
            JOIN book_slots bs ON b.book_id = bs.book_id
            JOIN book_list bl ON bs.bookList_id = bl.bookList_id
            WHERE bl.user_id = ?
        """
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchall()


    def remove_book_from_user(self, user_id, book_id):
        """Remove a book from a user's book list."""
        query_remove_book = """
            DELETE FROM book_slots
            WHERE bookList_id = (SELECT bookList_id FROM book_list WHERE user_id = ?)
            AND book_id = ?
        """
        self.cursor.execute(query_remove_book, (user_id, book_id))
        self.conn.commit()

    def get_available_videos(self, user_id):
        """Fetch all videos that are not linked to the specified user."""
        query = """
            SELECT v.video_id, v.video_name, v.genre, v.director, v.date_published
            FROM videos v
            WHERE v.video_id NOT IN (
                SELECT vs.video_id
                FROM video_slots vs
                JOIN video_list vl ON vs.videoList_id = vl.videoList_id
                WHERE vl.user_id = ?
            )
        """
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchall()

    def get_user_videos(self, user_id):
        """Fetch all videos linked to a specific user."""
        query = """
            SELECT v.video_id, v.video_name, v.genre, v.director, v.date_published
            FROM videos v
            JOIN video_slots vs ON v.video_id = vs.video_id
            JOIN video_list vl ON vs.videoList_id = vl.videoList_id
            WHERE vl.user_id = ?
        """
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchall()


    def remove_video_from_user(self, user_id, video_id):
        """Remove a video from a user's video list."""
        query_remove_video = """
            DELETE FROM video_slots
            WHERE videoList_id = (SELECT videoList_id FROM video_list WHERE user_id = ?)
            AND video_id = ?
        """
        self.cursor.execute(query_remove_video, (user_id, video_id))
        self.conn.commit()

    # Utility Methods
    def link_book_to_user(self, user_id, book_id):
        """Link a book to a user's book list."""
        query_get_booklist = "SELECT bookList_id FROM book_list WHERE user_id = ?"
        self.cursor.execute(query_get_booklist, (user_id,))
        book_list = self.cursor.fetchone()

        if not book_list:
            query_create_booklist = "INSERT INTO book_list (user_id) VALUES (?)"
            self.cursor.execute(query_create_booklist, (user_id,))
            book_list_id = self.cursor.lastrowid
        else:
            book_list_id = book_list[0]

        query_link = "INSERT INTO book_slots (bookList_id, book_id) VALUES (?, ?)"
        self.cursor.execute(query_link, (book_list_id, book_id))
        self.conn.commit()

    def link_video_to_user(self, user_id, video_id):
        """Link a video to a user's video list."""
        query_get_videolist = "SELECT videoList_id FROM video_list WHERE user_id = ?"
        self.cursor.execute(query_get_videolist, (user_id,))
        video_list = self.cursor.fetchone()

        if not video_list:
            query_create_videolist = "INSERT INTO video_list (user_id) VALUES (?)"
            self.cursor.execute(query_create_videolist, (user_id,))
            video_list_id = self.cursor.lastrowid
        else:
            video_list_id = video_list[0]

        query_link = "INSERT INTO video_slots (videoList_id, video_id) VALUES (?, ?)"
        self.cursor.execute(query_link, (video_list_id, video_id))
        self.conn.commit()


def main():
    db = LibraryDatabase("library.db")
    print("WELCOME USER! HAVE AN ACCOUNT? SIGN IN. IF NOT, PLEASE MAKE AN ACCOUNT.")
    
    while True:
        print("\nMenu:")
        print("1. LOGIN")
        print("2. SIGN UP")
        print("3. EXIT")
        
        choice = input("Enter your choice (1/2/3): ").strip()
        
        if choice == "1":
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()
            
            # Check if the user exists
            user = db.cursor.execute(
                "SELECT user_id FROM users WHERE username = ? AND password = ?", 
                (username, password)
            ).fetchone()
            
            if user:
                print(f"Welcome back, {username}!")
                user_id = user[0]
                user_menu(db, user_id)  # Go to the user's menu
            else:
                print("Invalid username or password. Please try again.")
        
        elif choice == "2":
            username = input("Choose a username: ").strip()
            password = input("Choose a password: ").strip()
            
            # Check if username already exists
            existing_user = db.cursor.execute(
                "SELECT username FROM users WHERE username = ?", 
                (username,)
            ).fetchone()
            
            if existing_user:
                print("Username already exists. Please choose a different one.")
            else:
                db.add_user(username, password)
                print(f"Account created successfully! You can now log in, {username}.")
        
        elif choice == "3":
            print("Goodbye!")
            db.close()
            break
        
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def user_menu(db, user_id):
    """Menu for logged-in users."""
    while True:
        print("\nUser Menu:")
        print("1. View Your Books")
        print("2. View Your Videos")
        print("3. Add a Book to Your List")
        print("4. Add a Video to Your List")
        print("5. Remove a Book from Your List")
        print("6. Remove a Video from Your List")
        print("7. Log Out")
        
        choice = input("Enter your choice (1/2/3/4/5/6/7): ").strip()
        
        if choice == "1":
            books = db.get_user_books(user_id)
            if books:
                print("\nYour Books:")
                for book in books:
                    print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Genre: {book[3]}")
            else:
                print("You have no books in your list.")
        
        elif choice == "2":
            videos = db.get_user_videos(user_id)
            if videos:
                print("\nYour Videos:")
                for video in videos:
                    print(f"ID: {video[0]}, Title: {video[1]}, Genre: {video[2]}, Director: {video[3]}, Date: {video[4]}")
            else:
                print("You have no videos in your list.")
        
        elif choice == "3":
            # Add a book to the user's list
            books = db.get_available_books(user_id)
            if books:
                print("\nAvailable Books:")
                for book in books:
                    print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Genre: {book[3]}")
                
                book_id = input("Enter the ID of the book you want to add (or 0 to cancel): ").strip()
                if book_id == "0":
                    print("Add book cancelled.")
                else:
                    try:
                        db.link_book_to_user(user_id, int(book_id))
                        print("Book added to your list!")
                    except Exception as e:
                        print(f"Error: {e}")
            else:
                print("No available books to add.")
        
        elif choice == "4":
            # Add a video to the user's list
            videos = db.get_available_videos(user_id)
            if videos:
                print("\nAvailable Videos:")
                for video in videos:
                    print(f"ID: {video[0]}, Title: {video[1]}, Genre: {video[2]}, Director: {video[3]}, Date: {video[4]}")
                
                video_id = input("Enter the ID of the video you want to add (or 0 to cancel): ").strip()
                if video_id == "0":
                    print("Add video cancelled.")
                else:
                    try:
                        db.link_video_to_user(user_id, int(video_id))
                        print("Video added to your list!")
                    except Exception as e:
                        print(f"Error: {e}")
            else:
                print("No available videos to add.")
        
        elif choice == "5":
            # Remove a book from the user's list
            books = db.get_user_books(user_id)
            if books:
                print("\nYour Books:")
                for book in books:
                    print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Genre: {book[3]}")
                
                book_id = input("Enter the ID of the book you want to remove (or 0 to cancel): ").strip()
                if book_id == "0":
                    print("Remove book cancelled.")
                else:
                    book_ids = [book[0] for book in books]
                    if int(book_id) in book_ids:
                        try:
                            db.remove_book_from_user(user_id, int(book_id))
                            print("Book removed from your list.")
                        except Exception as e:
                            print(f"Error: {e}")
                    else:
                        print("Invalid book ID. Please try again.")
            else:
                print("You have no books to remove.")
        
        elif choice == "6":
            # Remove a video from the user's list
            videos = db.get_user_videos(user_id)
            if videos:
                print("\nYour Videos:")
                for video in videos:
                    print(f"ID: {video[0]}, Title: {video[1]}, Genre: {video[2]}, Director: {video[3]}, Date: {video[4]}")
                
                video_id = input("Enter the ID of the video you want to remove (or 0 to cancel): ").strip()
                if video_id == "0":
                    print("Remove video cancelled.")
                else:
                    video_ids = [video[0] for video in videos]
                    if int(video_id) in video_ids:
                        try:
                            db.remove_video_from_user(user_id, int(video_id))
                            print("Video removed from your list.")
                        except Exception as e:
                            print(f"Error: {e}")
                    else:
                        print("Invalid video ID. Please try again.")
            else:
                print("You have no videos to remove.")
        
        elif choice == "7":
            print("Logging out...")
            break
        
        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()
