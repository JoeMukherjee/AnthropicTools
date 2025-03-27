# Anthropic Tools Demo

This project demonstrates how to use Anthropic's Claude 3.5 Sonnet API with tools functionality in two different applications:

1. **Book Library Assistant** - An assistant to help users browse, search, and get information about their book collection.
2. **Customer Service Assistant** - A customer service bot that can retrieve customer information, order details, and process cancellations.

## Project Structure

```
├── config.py                 # Configuration settings and API key
├── db.py                     # Database utilities for books and conversations
├── main.py                   # Main entry point with CLI arguments
├── Tools.py                  # Generic tools framework for Claude integration
├── responseService.py        # Book library response service
├── book-data/                # Directory for database files
│   ├── books.db              # Books database with sample collection
│   └── conversations.db      # Conversation history database
├── services/                 # Services directory
│   └── anthropic_service.py  # Anthropic API client service
└── tools/                    # Tools directory
    └── book_tools.py         # Book library tools definitions
```

## Setup

1. Install the required package:
   ```
   pip install anthropic
   ```

2. The `config.py` file is already set up with a working API key and the Claude 3.5 Sonnet model.

## Usage

Run the application with:

```
# For the Book Library Assistant (default)
python main.py

# For the Customer Service Assistant
python main.py --mode customer
```

When you first run the application, it will automatically:
1. Create the database files in the book-data directory
2. Initialize the book database with 25 sample books from popular authors
3. Set up the conversation tracking database

### Book Library Assistant

This assistant helps users manage their book collection with the following tools:

- `list_books` - Lists books in the collection, with optional filtering by genre or author
- `get_book_details` - Gets detailed information about a specific book
- `list_genres` - Lists all available genres in the collection
- `list_authors` - Lists all authors in the collection

Examples of questions you can ask:
- "Show me all books in the Fantasy genre"
- "What books do you have by J.K. Rowling?"
- "Tell me about book ID 6"
- "What genres are available in the collection?"

### Customer Service Assistant

This assistant helps users with customer service inquiries using the following tools:

- `get_customer_info` - Retrieves customer information based on customer ID
- `get_order_details` - Retrieves details about a specific order
- `cancel_order` - Cancels an order

Sample customer IDs: C1, C2  
Sample order IDs: O1, O2

Examples of questions you can ask:
- "What's the email address for customer C1?"
- "Tell me about order O2"
- "Can you please cancel my order O1?"

## Technical Details

This demo uses:
- Claude 3.5 Sonnet (claude-3-5-sonnet-20240620) - Anthropic's advanced AI model
- SQLite databases for storing books and conversation history
- Tool-based architecture that allows Claude to retrieve information and take actions

## Extending the Framework

The `ToolsFramework` class in `Tools.py` provides a generic framework for building Claude-powered applications with tools. To create a new assistant:

1. Define tool schemas following the Anthropic API format
2. Create handler functions for each tool
3. Initialize the framework with your tools and handlers

See the examples in `main.py` for how to implement your own assistant.

## License

MIT 