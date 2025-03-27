# Configuration settings for the book library application


ANTHROPIC_MODEL = "claude-3-5-sonnet-20240620"
MAX_TOKENS = 1024

# Conversation database settings
DB_DIR = "book-data"

# System prompt for the assistant
SYSTEM_PROMPT = """
You are a helpful book library assistant. You can help users browse their book collection, 
get information about specific books, and provide recommendations.
Be concise, friendly, and informative in your responses.
""" 