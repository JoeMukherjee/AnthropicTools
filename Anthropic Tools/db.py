import sqlite3
import os
import uuid
from config import DB_DIR
import datetime
import json
import random

# Define the database paths
BOOKS_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), DB_DIR, "books.db"))
CONVERSATION_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), DB_DIR, "conversations.db"))
USER_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), DB_DIR, "users.db"))

def init_user_db():
    """Initialize the user database"""
    os.makedirs(DB_DIR, exist_ok=True)
    
    conn = sqlite3.connect(USER_DB)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT,
        password_hash TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"User database initialized at {USER_DB}")

def init_db():
    """Initialize all databases"""
    init_user_db()
    init_books_db()
    init_conversation_db()
    
def init_books_db():
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
    os.makedirs(DB_DIR, exist_ok=True)
    
    conn = sqlite3.connect(CONVERSATION_DB)
    cursor = conn.cursor()
    
    # Create conversations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        assistant_type TEXT,
        title TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER,
        sender TEXT,
        content TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER
    )
    ''')
    
    # Create tool_calls table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tool_calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER,
        message_id INTEGER,
        tool_name TEXT,
        parameters TEXT,
        result TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Conversation database initialized at {CONVERSATION_DB}")

def create_user(username, email=None, password_hash=None):
    """
    Create a new user
    
    Args:
        username (str): The user's username
        email (str, optional): The user's email
        password_hash (str, optional): The user's password hash
    
    Returns:
        int: The user ID
    """
    conn = sqlite3.connect(USER_DB)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password_hash)
    )
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return user_id

def get_user_by_username(username):
    """
    Get a user by username
    
    Args:
        username (str): The username to look up
    
    Returns:
        dict or None: The user data if found, None otherwise
    """
    conn = sqlite3.connect(USER_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_user_conversations(user_id, assistant_type=None):
    """Get all conversations for a specific user"""
    conn = sqlite3.connect(CONVERSATION_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
    SELECT c.id, c.title, c.assistant_type, c.created_at, c.last_updated,
           COUNT(m.id) as message_count
    FROM conversations c
    LEFT JOIN messages m ON c.id = m.conversation_id
    WHERE c.user_id = ?
    """
    params = [user_id]
    
    if assistant_type:
        query += " AND c.assistant_type = ?"
        params.append(assistant_type)
        
    query += " GROUP BY c.id ORDER BY c.created_at DESC"
    
    cursor.execute(query, params)
    conversations = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return conversations

def create_conversation(user_id, assistant_type="books", title=None):
    """Create a new conversation for a user"""
    conn = sqlite3.connect(CONVERSATION_DB)
    cursor = conn.cursor()
    
    # If title is not provided, create a default one
    if not title:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = f"{assistant_type} Conversation - {timestamp}"
    
    cursor.execute(
        """
        INSERT INTO conversations 
        (user_id, assistant_type, title) 
        VALUES (?, ?, ?)
        """,
        (user_id, assistant_type, title)
    )
    
    conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return conversation_id

def update_conversation_title(conversation_id, new_title):
    """Update a conversation's title"""
    conn = sqlite3.connect(CONVERSATION_DB)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE conversations SET title = ? WHERE id = ?",
        (new_title, conversation_id)
    )
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success

def get_conversation(conversation_id):
    """Get conversation details by ID"""
    conn = sqlite3.connect(CONVERSATION_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT * FROM conversations
        WHERE id = ?
        """, 
        (conversation_id,)
    )
    
    conversation = cursor.fetchone()
    conn.close()
    
    if conversation:
        return dict(conversation)
    return None

def get_messages_by_conversation_id(conversation_id):
    """Retrieve all messages for a specific conversation"""
    conn = sqlite3.connect(CONVERSATION_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, sender, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC",
        (conversation_id,),
    )

    rows = cursor.fetchall()
    messages = []
    
    # Process each message - ensure proper role names and content format
    for row in rows:
        # Convert 'user' and 'assistant' to proper API format
        role = row["sender"]
        
        # Ensure content is properly formatted
        content = row["content"]
        
        # Create a clean message object without metadata for API compatibility
        message = {
            "role": role, 
            "content": content
        }
        messages.append(message)
    
    conn.close()
    
    # If there are no messages, insert an empty system message to start the conversation
    if not messages:
        messages.append({
            "role": "system", 
            "content": "This is the start of a new conversation."
        })
        
    return messages

def add_message(conversation_id, sender, content, user_id=None):
    """
    Add a message to a conversation
    
    Args:
        conversation_id (int or str): The conversation ID or 'new' for a new conversation
        sender (str): The message sender ('user' or 'assistant')
        content (str): The message content
        user_id (int, optional): The user ID for a new conversation
    
    Returns:
        tuple: (conversation_id, message_id)
    """
    # Create a new conversation if needed
    if conversation_id == 'new' and user_id:
        conversation_id = create_conversation(user_id)
    
    conn = sqlite3.connect(CONVERSATION_DB)
    cursor = conn.cursor()
    
    # Add the message
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO messages (conversation_id, sender, content, user_id, timestamp) VALUES (?, ?, ?, ?, ?)",
        (conversation_id, sender, content, user_id, current_time)
    )
    
    message_id = cursor.lastrowid
    
    # Update the conversation's last_updated timestamp
    cursor.execute(
        "UPDATE conversations SET last_updated = ? WHERE id = ?",
        (current_time, conversation_id)
    )
    
    conn.commit()
    conn.close()
    
    return conversation_id, message_id

def add_tool_call(conversation_id, message_id, tool_name, parameters, result):
    """
    Add a tool call to a conversation
    
    Args:
        conversation_id (int): The conversation ID
        message_id (int): The message ID that triggered the tool call
        tool_name (str): The name of the tool called
        parameters (str): The tool parameters (JSON string)
        result (str): The tool result (JSON string)
    
    Returns:
        int: The tool call ID
    """
    conn = sqlite3.connect(CONVERSATION_DB)
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO tool_calls
        (conversation_id, message_id, tool_name, parameters, result)
        VALUES (?, ?, ?, ?, ?)
        """,
        (conversation_id, message_id, tool_name, parameters, result)
    )
    
    tool_call_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return tool_call_id

def delete_conversation(conversation_id):
    """
    Delete a conversation and all its messages
    
    Args:
        conversation_id (int): The conversation ID
    
    Returns:
        bool: Success flag
    """
    conn = sqlite3.connect(CONVERSATION_DB)
    cursor = conn.cursor()
    
    # Delete tool calls first (foreign key constraint)
    cursor.execute(
        "DELETE FROM tool_calls WHERE conversation_id = ?",
        (conversation_id,)
    )
    
    # Delete messages
    cursor.execute(
        "DELETE FROM messages WHERE conversation_id = ?",
        (conversation_id,)
    )
    
    # Delete the conversation
    cursor.execute(
        "DELETE FROM conversations WHERE id = ?",
        (conversation_id,)
    )
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success

def get_all_users():
    """
    Get all users
    
    Returns:
        list: List of all users
    """
    conn = sqlite3.connect(USER_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    
    conn.close()
    
    return [dict(row) for row in rows]

def get_connection():
    """Get a connection to the books database"""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(BOOKS_DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(BOOKS_DB_PATH)
    return conn 