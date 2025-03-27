import json
import sqlite3
from db import get_connection

# Tool definitions
LIST_BOOKS_TOOL = {
    "name": "list_books",
    "description": "Lists books in the collection, optionally filtered by genre or author",
    "input_schema": {
        "type": "object",
        "properties": {
            "genre_id": {
                "type": "integer",
                "description": "Optional ID of the genre to filter by"
            },
            "author_id": {
                "type": "integer",
                "description": "Optional ID of the author to filter by"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of books to return (default: 10)"
            }
        }
    }
}

GET_BOOK_DETAILS_TOOL = {
    "name": "get_book_details",
    "description": "Gets detailed information about a specific book",
    "input_schema": {
        "type": "object",
        "properties": {
            "book_id": {
                "type": "integer",
                "description": "The ID of the book to get details for"
            }
        },
        "required": ["book_id"]
    }
}

LIST_GENRES_TOOL = {
    "name": "list_genres",
    "description": "Lists all available genres in the collection",
    "input_schema": {
        "type": "object",
        "properties": {}
    }
}

LIST_AUTHORS_TOOL = {
    "name": "list_authors",
    "description": "Lists all authors in the collection",
    "input_schema": {
        "type": "object",
        "properties": {}
    }
}

def list_books(params):
    """List books in the collection with optional filtering"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
    SELECT b.id, b.title, a.name as author, g.name as genre, b.year_published, b.rating
    FROM books b
    JOIN authors a ON b.author_id = a.id
    JOIN genres g ON b.genre_id = g.id
    """

    conditions = []
    query_params = []

    if params.get("genre_id"):
        conditions.append("b.genre_id = ?")
        query_params.append(params["genre_id"])

    if params.get("author_id"):
        conditions.append("b.author_id = ?")
        query_params.append(params["author_id"])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY b.title"
    
    limit = params.get("limit", 10)
    query += f" LIMIT {limit}"

    cursor.execute(query, query_params)
    
    books = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return books

def get_book_details(params):
    """Get detailed information about a specific book"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
    SELECT b.id, b.title, a.name as author, a.id as author_id, 
           g.name as genre, g.id as genre_id, 
           b.year_published, b.rating, b.notes, b.date_added
    FROM books b
    JOIN authors a ON b.author_id = a.id
    JOIN genres g ON b.genre_id = g.id
    WHERE b.id = ?
    """

    cursor.execute(query, (params["book_id"],))
    
    book = cursor.fetchone()
    
    if not book:
        conn.close()
        return {"error": f"Book with ID {params['book_id']} not found"}
    
    book_dict = dict(book)
    
    conn.close()
    return book_dict

def list_genres(params):
    """List all available genres"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
    SELECT g.id, g.name, COUNT(b.id) as book_count
    FROM genres g
    LEFT JOIN books b ON g.id = b.genre_id
    GROUP BY g.id
    ORDER BY g.name
    """

    cursor.execute(query)
    
    genres = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return genres

def list_authors(params):
    """List all authors in the collection"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
    SELECT a.id, a.name, a.birth_year, COUNT(b.id) as book_count
    FROM authors a
    LEFT JOIN books b ON a.id = b.author_id
    GROUP BY a.id
    ORDER BY a.name
    """

    cursor.execute(query)
    
    authors = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return authors

def format_books_response(books):
    """Format the books list response for display"""
    if not books:
        yield {
            "type": "chunk",
            "content": "No books found matching your criteria.",
            "speakable": True
        }
        return

    yield {
        "type": "chunk",
        "content": f"Found {len(books)} books in your collection:\n\n",
        "speakable": True
    }

    for book in books:
        book_info = (
            f"📚 {book['title']} by {book['author']}\n"
            f"   Genre: {book['genre']}, Published: {book['year_published']}\n"
            f"   Rating: {'⭐' * book['rating'] if book['rating'] else 'Not rated'}\n"
        )
        
        yield {
            "type": "chunk",
            "content": book_info,
            "speakable": True
        }

def format_book_details_response(book):
    """Format the book details response for display"""
    if "error" in book:
        yield {
            "type": "chunk",
            "content": book["error"],
            "speakable": True
        }
        return

    book_details = (
        f"📖 Book Details: {book['title']}\n\n"
        f"Author: {book['author']}\n"
        f"Genre: {book['genre']}\n"
        f"Published: {book['year_published']}\n"
        f"Rating: {'⭐' * book['rating'] if book['rating'] else 'Not rated'}\n"
    )
    
    if book.get('notes'):
        book_details += f"\nNotes: {book['notes']}\n"
    
    book_details += f"\nAdded to collection: {book['date_added']}\n"
    
    yield {
        "type": "chunk",
        "content": book_details,
        "speakable": True
    }

def format_genres_response(genres):
    """Format the genres list response for display"""
    if not genres:
        yield {
            "type": "chunk",
            "content": "No genres found in your collection.",
            "speakable": True
        }
        return

    yield {
        "type": "chunk",
        "content": "Available genres in your collection:\n\n",
        "speakable": True
    }

    for genre in genres:
        genre_info = f"🏷️ {genre['name']} ({genre['book_count']} books)\n"
        
        yield {
            "type": "chunk",
            "content": genre_info,
            "speakable": True
        }

def format_authors_response(authors):
    """Format the authors list response for display"""
    if not authors:
        yield {
            "type": "chunk",
            "content": "No authors found in your collection.",
            "speakable": True
        }
        return

    yield {
        "type": "chunk",
        "content": "Authors in your collection:\n\n",
        "speakable": True
    }

    for author in authors:
        author_info = f"✍️ {author['name']}"
        
        if author['birth_year']:
            author_info += f" (born {author['birth_year']})"
        
        author_info += f" - {author['book_count']} books\n"
        
        yield {
            "type": "chunk",
            "content": author_info,
            "speakable": True
        } 