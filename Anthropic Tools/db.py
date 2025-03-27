import sqlite3
import os
import uuid
from config import DB_DIR
import datetime

# Define the database paths
BOOKS_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), DB_DIR, "books.db"))
CONVERSATION_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), DB_DIR, "conversations.db"))

def init_db():
    """Initialize the books database with the schema and sample data"""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(BOOKS_DB_PATH), exist_ok=True)

    conn = sqlite3.connect(BOOKS_DB_PATH)
    cursor = conn.cursor()

    # Create genres table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS genres (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    )
    """)

    # Create authors table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS authors (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        birth_year INTEGER
    )
    """)

    # Create books table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author_id INTEGER NOT NULL,
        genre_id INTEGER NOT NULL,
        year_published INTEGER,
        rating INTEGER,
        notes TEXT,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (author_id) REFERENCES authors (id),
        FOREIGN KEY (genre_id) REFERENCES genres (id)
    )
    """)

    # Add sample genres
    genres = [
        (1, "Fiction"),
        (2, "Non-Fiction"),
        (3, "Science Fiction"),
        (4, "Mystery"),
        (5, "Biography"),
        (6, "Fantasy"),
        (7, "Historical Fiction"),
        (8, "Romance"),
        (9, "Thriller"),
        (10, "Self-Help")
    ]
    
    cursor.execute("DELETE FROM genres")
    cursor.executemany("INSERT OR IGNORE INTO genres (id, name) VALUES (?, ?)", genres)
    
    # Add sample authors
    authors = [
        (1, "J.K. Rowling", 1965),
        (2, "George Orwell", 1903),
        (3, "Jane Austen", 1775),
        (4, "Stephen King", 1947),
        (5, "Agatha Christie", 1890),
        (6, "Frank Herbert", 1920),
        (7, "J.R.R. Tolkien", 1892),
        (8, "Harper Lee", 1926),
        (9, "Fyodor Dostoevsky", 1821),
        (10, "Gabriel García Márquez", 1927),
        (11, "Leo Tolstoy", 1828),
        (12, "Ernest Hemingway", 1899),
        (13, "Mark Twain", 1835),
        (14, "C.S. Lewis", 1898),
        (15, "Charles Dickens", 1812)
    ]
    
    cursor.execute("DELETE FROM authors")
    cursor.executemany("INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (?, ?, ?)", authors)
    
    # Add sample books
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    books = [
        (1, "Harry Potter and the Philosopher's Stone", 1, 6, 1997, 5, "The first book in the Harry Potter series.", current_date),
        (2, "1984", 2, 3, 1949, 5, "A dystopian social science fiction novel.", current_date),
        (3, "Pride and Prejudice", 3, 8, 1813, 4, "A romantic novel of manners.", current_date),
        (4, "The Shining", 4, 9, 1977, 4, "A horror novel set in an isolated hotel.", current_date),
        (5, "Murder on the Orient Express", 5, 4, 1934, 4, "A detective novel featuring Hercule Poirot.", current_date),
        (6, "Dune", 6, 3, 1965, 5, "A science fiction novel set in the distant future.", current_date),
        (7, "The Hobbit", 7, 6, 1937, 5, "A fantasy novel and children's book.", current_date),
        (8, "To Kill a Mockingbird", 8, 1, 1960, 5, "A novel about racial inequality in the American South.", current_date),
        (9, "Crime and Punishment", 9, 1, 1866, 4, "A novel focused on the mental anguish of a murderer.", current_date),
        (10, "One Hundred Years of Solitude", 10, 1, 1967, 5, "A landmark of magical realism.", current_date),
        (11, "War and Peace", 11, 7, 1869, 5, "A novel about Russian society during the Napoleonic era.", current_date),
        (12, "The Old Man and the Sea", 12, 1, 1952, 4, "A short novel about an aging Cuban fisherman.", current_date),
        (13, "The Adventures of Huckleberry Finn", 13, 1, 1884, 4, "A novel about a boy's journey down the Mississippi River.", current_date),
        (14, "The Chronicles of Narnia: The Lion, the Witch and the Wardrobe", 14, 6, 1950, 5, "A fantasy novel set in the magical land of Narnia.", current_date),
        (15, "Great Expectations", 15, 1, 1861, 4, "A novel about an orphan's rise in society.", current_date),
        (16, "Harry Potter and the Chamber of Secrets", 1, 6, 1998, 4, "The second book in the Harry Potter series.", current_date),
        (17, "Harry Potter and the Prisoner of Azkaban", 1, 6, 1999, 5, "The third book in the Harry Potter series.", current_date),
        (18, "Animal Farm", 2, 1, 1945, 4, "An allegorical novella about the Russian Revolution.", current_date),
        (19, "Emma", 3, 8, 1815, 4, "A novel about youthful hubris and romantic misunderstandings.", current_date),
        (20, "It", 4, 9, 1986, 4, "A horror novel about a shapeshifting entity.", current_date),
        (21, "Death on the Nile", 5, 4, 1937, 4, "A murder mystery set in Egypt.", current_date),
        (22, "Dune Messiah", 6, 3, 1969, 4, "The second novel in the Dune series.", current_date),
        (23, "The Lord of the Rings: The Fellowship of the Ring", 7, 6, 1954, 5, "The first volume of the Lord of the Rings trilogy.", current_date),
        (24, "Go Set a Watchman", 8, 1, 2015, 3, "A novel featuring characters from To Kill a Mockingbird.", current_date),
        (25, "The Brothers Karamazov", 9, 1, 1880, 5, "A philosophical novel about faith, doubt, and reason.", current_date)
    ]
    
    cursor.execute("DELETE FROM books")
    cursor.executemany("""
    INSERT INTO books (id, title, author_id, genre_id, year_published, rating, notes, date_added) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, books)

    conn.commit()
    conn.close()

    print(f"Books database initialized at {BOOKS_DB_PATH} with {len(books)} sample books")

def init_conversation_db():
    """Initialize the conversation database"""
    os.makedirs(os.path.dirname(CONVERSATION_DB), exist_ok=True)

    conn = sqlite3.connect(CONVERSATION_DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT,
        role TEXT,
        content TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tool_calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT,
        message_id INTEGER,
        tool_name TEXT,
        tool_parameters TEXT,
        tool_response TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations (id),
        FOREIGN KEY (message_id) REFERENCES messages (id)
    )
    """)

    conn.commit()
    conn.close()
    
    print(f"Conversation database initialized at {CONVERSATION_DB}")

def get_connection():
    """Get a database connection to the books database"""
    os.makedirs(os.path.dirname(BOOKS_DB_PATH), exist_ok=True)
    return sqlite3.connect(BOOKS_DB_PATH)

def get_conversation_connection():
    """Get a connection to the conversation database"""
    os.makedirs(os.path.dirname(CONVERSATION_DB), exist_ok=True)
    return sqlite3.connect(CONVERSATION_DB)

def get_messages_by_conversation_id(conversation_id):
    """Retrieve all messages for a specific conversation"""
    conn = get_conversation_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY timestamp",
        (conversation_id,),
    )

    messages = [
        {"role": row["role"], "content": row["content"]} for row in cursor.fetchall()
    ]

    conn.close()
    return messages

def add_message(conversation_id, role, content):
    """Add a new message to the database"""
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())

    conn = get_conversation_connection()
    cursor = conn.cursor()

    try:
        # Check if conversation exists
        cursor.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO conversations (id) VALUES (?)", (conversation_id,)
            )

        cursor.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, content),
        )

        message_id = cursor.lastrowid
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
        conn.rollback()
        raise e
    finally:
        conn.close()

    return conversation_id, message_id

def add_tool_call(conversation_id, message_id, tool_name, tool_parameters, tool_response):
    """Record a tool call in the database"""
    conn = get_conversation_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO tool_calls 
            (conversation_id, message_id, tool_name, tool_parameters, tool_response) 
            VALUES (?, ?, ?, ?, ?)
            """,
            (conversation_id, message_id, tool_name, tool_parameters, tool_response),
        )

        conn.commit()
        tool_call_id = cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error when adding tool call: {str(e)}")
        conn.rollback()
        raise e
    finally:
        conn.close()

    return tool_call_id 