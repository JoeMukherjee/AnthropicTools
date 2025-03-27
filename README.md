# Anthropic Tools Demo - Book Library Assistant: Extended Guide

This extended guide provides in-depth information about the Book Library Assistant project, including detailed workflows, architecture diagrams, and tutorials to help you understand how the system works and how to use it effectively.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Component Workflows](#component-workflows)
3. [Data Flow Diagrams](#data-flow-diagrams)
4. [Tutorials](#tutorials)
5. [Development Guide](#development-guide)
6. [Troubleshooting](#troubleshooting)

## System Architecture

The Book Library Assistant is built around a modular architecture with several key components:

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│   User Layer   │     │  Service Layer  │     │  Storage Layer │
├────────────────┤     ├────────────────┤     ├────────────────┤
│ - CLI          │     │ - Response Svc │     │ - Books DB     │
│ - REST API     │ ──► │ - Anthropic Svc│ ──► │ - Convos DB    │
│ - User Manager │     │ - Tools        │     │ - Users DB     │
└────────────────┘     └────────────────┘     └────────────────┘
```

### Key Components:

1. **User Layer**
   - `main.py`: CLI interface for direct interaction
   - `api.py`: REST API for multi-user access
   - User authentication and session management

2. **Service Layer**
   - `responseService.py`: Coordinates between user requests and tools
   - `anthropic_service.py`: Interfaces with Anthropic's Claude API
   - `Tools.py`: Generic framework for tool handling
   - `book_tools.py`: Book-specific tools implementation

3. **Storage Layer**
   - Books database: Stores book information
   - Conversation database: Tracks message history
   - User database: Manages user accounts

## Component Workflows

### CLI Workflow

```
┌──────────┐     ┌─────────────────┐     ┌──────────────────┐
│  User    │     │ ResponseService │     │ Anthropic Service│
│  Input   │ ──► │ & Tool Handling │ ──► │      Claude      │
└──────────┘     └─────────────────┘     └──────────────────┘
                          ▲                        │
                          │                        ▼
                     ┌────┴────────────────────────┐
                     │ Database Operations (books) │
                     └─────────────────────────────┘
```

1. User enters a question about books via CLI
2. ResponseService processes the message
3. Claude analyzes the request and decides if tools are needed
4. If tools are needed, the appropriate tool fetches data from the database
5. Claude generates a response using the tool results
6. Response is displayed to the user

### REST API Workflow

```
┌──────────┐     ┌───────────┐     ┌─────────────────┐     ┌──────────────┐
│  Client  │     │   API     │     │ ResponseService │     │   Anthropic  │
│  Request │ ──► │ Endpoints │ ──► │ & Tool Handling │ ──► │    Claude    │
└──────────┘     └───────────┘     └─────────────────┘     └──────────────┘
     ▲                                      ▲                     │
     │                                      │                     ▼
     │                                 ┌────┴─────────────────────┐
     └────────────────────────────────┤ Database Operations       │
                                      └──────────────────────────┘
```

1. Client application sends an HTTP request to an API endpoint
2. API authenticates the user and processes the request
3. For message endpoints, ResponseService handles the message
4. Claude analyzes the request and may use tools
5. Response is returned to the client as JSON

### Tool Call Workflow

```
┌────────────┐     ┌───────────────┐     ┌─────────────┐
│   Claude   │     │ ResponseService│     │  Tool Call  │
│  Request   │ ──► │ Tool Detection │ ──► │  Handler    │
└────────────┘     └───────────────┘     └─────────────┘
                                                │
                                                ▼
┌────────────┐     ┌───────────────┐     ┌─────────────┐
│   Claude   │     │  Process      │     │ Database    │
│  Response  │ ◄── │  Results      │ ◄── │ Operations  │
└────────────┘     └───────────────┘     └─────────────┘
```

1. Claude indicates it wants to use a tool through API response
2. ResponseService detects the tool call and extracts parameters
3. The appropriate tool handler executes DB operations
4. Results are formatted and returned to Claude
5. Claude generates final response with the tool data

## Data Flow Diagrams

### Conversation Flow

```
┌─────────┐     ┌────────────┐     ┌───────────────┐
│  User   │     │ Message    │     │ Conversation  │
│ Message │ ──► │ Processing │ ──► │ History DB    │
└─────────┘     └────────────┘     └───────────────┘
                      │                    ▲
                      ▼                    │
                ┌────────────┐      ┌─────┴────────┐
                │ Anthropic  │      │ Previous     │
                │ API Call   │ ◄─── │ Context      │
                └────────────┘      └──────────────┘
                      │
                      ▼
               ┌──────────────┐
               │ Tool Usage?  │
               └──────────────┘
                 /          \
                Yes          No
                /             \
    ┌───────────────┐    ┌────────────┐
    │ Execute Tool  │    │ Final      │
    │ & Store Result│    │ Response   │
    └───────────────┘    └────────────┘
               \           /
                \         /
             ┌─────────────────┐
             │ Store Response  │
             │ in History      │
             └─────────────────┘
```

### User Authentication Flow

```
┌──────────┐     ┌─────────────┐     ┌──────────────┐
│  Client  │     │ API         │     │ User Manager │
│  Request │ ──► │ Auth        │ ──► │ Authentication│
└──────────┘     └─────────────┘     └──────────────┘
                                             │
                                             ▼
                                     ┌───────────────┐
                                     │ Users Database│
                                     └───────────────┘
                                             │
                                             ▼
┌──────────┐     ┌─────────────┐     ┌──────────────┐
│  Client  │     │ API         │     │ Session Token │
│  Response│ ◄── │ Response    │ ◄── │ Generation   │
└──────────┘     └─────────────┘     └──────────────┘
```

## Tutorials

### Running the CLI Interface

1. Make sure you've set up your environment with the required dependencies and API key.

2. Run the CLI interface:
   ```bash
   python main.py
   ```

3. Start a conversation by asking a question about books:
   ```
   You: What fantasy books do you have in the collection?
   ```

4. The assistant will respond with a list of fantasy books.

5. You can ask follow-up questions that maintain context:
   ```
   You: When was the first one published?
   ```

6. Continue the conversation naturally, or type 'exit' to quit:
   ```
   You: exit
   ```

### Using the REST API

1. Start the API server:
   ```bash
   python api.py
   ```

2. Register a new user:
   ```bash
   curl -X POST http://localhost:5000/api/register \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "securepassword"}'
   ```

3. Log in with the registered user:
   ```bash
   curl -X POST http://localhost:5000/api/login \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "securepassword"}'
   ```

4. Save the session token from the response:
   ```json
   {
     "success": true,
     "session_token": "your-session-token",
     "username": "testuser"
   }
   ```

5. Create a new conversation:
   ```bash
   curl -X POST http://localhost:5000/api/conversations \
     -H "Content-Type: application/json" \
     -H "X-Session-Token: your-session-token" \
     -d '{"title": "My Book Conversation"}'
   ```

6. Send a message to the conversation:
   ```bash
   curl -X POST http://localhost:5000/api/conversations/1/messages \
     -H "Content-Type: application/json" \
     -H "X-Session-Token: your-session-token" \
     -d '{"message": "What fantasy books do you have?"}'
   ```

7. Get all conversations for the current user:
   ```bash
   curl -X GET http://localhost:5000/api/conversations \
     -H "X-Session-Token: your-session-token"
   ```

8. Get details and messages for a specific conversation:
   ```bash
   curl -X GET http://localhost:5000/api/conversations/1 \
     -H "X-Session-Token: your-session-token"
   ```

### Web Client Integration

If you want to integrate with a web client, here's a simple example using JavaScript:

```javascript
// Login
async function login(username, password) {
  const response = await fetch('http://localhost:5000/api/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  localStorage.setItem('sessionToken', data.session_token);
  return data;
}

// Send a message
async function sendMessage(conversationId, message) {
  const sessionToken = localStorage.getItem('sessionToken');
  const response = await fetch(`http://localhost:5000/api/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Session-Token': sessionToken
    },
    body: JSON.stringify({ message })
  });
  return await response.json();
}
```

## Development Guide

### Adding New Tools

To add a new tool to the system:

1. Define the tool in `tools/book_tools.py`:
   ```python
   NEW_TOOL = {
       "name": "new_tool_name",
       "description": "Description of what the tool does",
       "input_schema": {
           "type": "object",
           "properties": {
               "param1": {
                   "type": "string",
                   "description": "Description of parameter 1"
               },
               "param2": {
                   "type": "integer",
                   "description": "Description of parameter 2"
               }
           },
           "required": ["param1"]
       }
   }
   ```

2. Create a handler function:
   ```python
   def new_tool_handler(params):
       """Implementation of the new tool"""
       param1 = params.get("param1")
       param2 = params.get("param2", default_value)
       
       # Database operations or other logic
       result = some_operation(param1, param2)
       
       return result
   ```

3. Create a response formatter:
   ```python
   def format_new_tool_response(result):
       """Format the tool result for display"""
       yield {
           "type": "chunk",
           "content": f"Result: {result}",
           "speakable": True
       }
   ```

4. Add the tool to the TOOLS list:
   ```python
   TOOLS = [LIST_BOOKS_TOOL, GET_BOOK_DETAILS_TOOL, LIST_GENRES_TOOL, LIST_AUTHORS_TOOL, NEW_TOOL]
   ```

5. Register the handler and formatter in their respective dictionaries:
   ```python
   TOOL_HANDLERS = {
       "list_books": list_books,
       "get_book_details": get_book_details,
       "list_genres": list_genres,
       "list_authors": list_authors,
       "new_tool_name": new_tool_handler
   }

   RESPONSE_FORMATTERS = {
       "list_books": format_books_response,
       "get_book_details": format_book_details_response,
       "list_genres": format_genres_response,
       "list_authors": format_authors_response,
       "new_tool_name": format_new_tool_response
   }
   ```

### Extending the Database Schema

If you need to add new tables or columns:

1. Update the initialization function in `db.py`:
   ```python
   def init_books_db():
       # Existing code...
       
       # Add new table
       cursor.execute("""
       CREATE TABLE IF NOT EXISTS new_table (
           id INTEGER PRIMARY KEY,
           name TEXT NOT NULL,
           description TEXT
       )
       """)
       
       # Sample data for the new table
       new_data = [
           (1, "Sample 1", "Description 1"),
           (2, "Sample 2", "Description 2")
       ]
       
       cursor.executemany("INSERT OR IGNORE INTO new_table (id, name, description) VALUES (?, ?, ?)", new_data)
       
       conn.commit()
       conn.close()
   ```

2. Create accessor functions for the new table:
   ```python
   def get_items_from_new_table():
       conn = get_connection()
       conn.row_factory = sqlite3.Row
       cursor = conn.cursor()
       
       cursor.execute("SELECT * FROM new_table")
       items = [dict(row) for row in cursor.fetchall()]
       
       conn.close()
       return items
   ```

## Troubleshooting

### Common Issues

#### API Authentication Failures

If you encounter authentication issues with the API:

1. Check that you're passing the correct session token in the `X-Session-Token` header
2. Verify that the session hasn't expired (they typically expire after 24 hours)
3. Make sure the user exists in the database

#### Claude API Errors

If Claude API calls are failing:

1. Verify your API key is correct and has sufficient permissions
2. Check that you're using a supported model in the configuration
3. Ensure your messages aren't exceeding token limits
4. Check for rate limiting issues

#### Database Errors

If you encounter database issues:

1. Verify the database files exist in the `book-data` directory
2. Check for file permission issues
3. Make sure SQLite is properly installed
4. Try reinitializing the database by running:
   ```python
   from db import init_db
   init_db()
   ```

### Logs and Debugging

The application uses Python's logging module. To increase log verbosity for debugging:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

You can check the logs for information about:
- API requests and responses
- Tool calls and parameters
- Database operations
- Claude API interactions

## Performance Optimization

For better performance with larger book collections:

1. Add indexes to the database:
   ```python
   # In db.py, add to init_books_db()
   cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_author_id ON books(author_id)")
   cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_genre_id ON books(genre_id)")
   cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_title ON books(title)")
   ```

2. Implement pagination for list operations:
   ```python
   def list_books(params):
       # Existing code...
       page = params.get("page", 1)
       per_page = params.get("per_page", 10)
       offset = (page - 1) * per_page
       
       query += f" LIMIT {per_page} OFFSET {offset}"
       # Rest of the function...
   ```

3. Add caching for frequently accessed data:
   ```python
   # Simple in-memory cache
   _genres_cache = None
   _genres_cache_timestamp = 0
   
   def list_genres(params):
       global _genres_cache, _genres_cache_timestamp
       current_time = time.time()
       
       # Return cached data if less than 5 minutes old
       if _genres_cache and (current_time - _genres_cache_timestamp) < 300:
           return _genres_cache
           
       # Otherwise fetch from database
       conn = get_connection()
       # ... existing code ...
       
       _genres_cache = genres
       _genres_cache_timestamp = current_time
       return genres
   ```

## Conclusion

This extended guide should help you understand the architecture, workflows, and implementation details of the Book Library Assistant. By following the tutorials and development guides, you can effectively use the system and extend it to meet your specific needs.

For any further questions or issues, please refer to the documentation in the code comments or raise an issue in the project repository. 
