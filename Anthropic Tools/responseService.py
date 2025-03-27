import json
import logging
import traceback
from db import get_messages_by_conversation_id, add_message, add_tool_call, init_conversation_db
from services.anthropic_service import AnthropicService
from tools.book_tools import (
    LIST_BOOKS_TOOL,
    GET_BOOK_DETAILS_TOOL,
    LIST_GENRES_TOOL,
    LIST_AUTHORS_TOOL,
    list_books,
    get_book_details,
    list_genres,
    list_authors,
    format_books_response,
    format_book_details_response,
    format_genres_response,
    format_authors_response
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# List of available tools
TOOLS = [LIST_BOOKS_TOOL, GET_BOOK_DETAILS_TOOL, LIST_GENRES_TOOL, LIST_AUTHORS_TOOL]

# Dictionary mapping tool names to their handler functions
TOOL_HANDLERS = {
    "list_books": list_books,
    "get_book_details": get_book_details,
    "list_genres": list_genres,
    "list_authors": list_authors
}

# Dictionary mapping tool names to their response formatters
RESPONSE_FORMATTERS = {
    "list_books": format_books_response,
    "get_book_details": format_book_details_response,
    "list_genres": format_genres_response,
    "list_authors": format_authors_response
}

class ResponseService:
    def __init__(self):
        """Initialize the response service"""
        self.anthropic_service = AnthropicService()
        init_conversation_db()

    def generate_full_response(self, user_message, conversation_id=None):
        """Generate a full response using the Anthropic API with tool support"""
        conversation_id, user_message_id = add_message(
            conversation_id, "user", user_message
        )
        logger.info(f"New user message in conversation {conversation_id}")
        logger.info(f"User: {user_message}")

        messages = get_messages_by_conversation_id(conversation_id)

        # Validate messages
        if not messages or not isinstance(messages, list) or len(messages) == 0:
            raise ValueError("No messages found for this conversation")

        model = self.anthropic_service.model
        logger.info(f"Starting full response with model: {model}")
        logger.info(f"Messages count: {len(messages)}")
        logger.info(f"Tools enabled: {[tool['name'] for tool in TOOLS]}")

        # Pass TOOLS to create_message
        response = self.anthropic_service.create_message(messages, TOOLS)
        
        # Check if tool use is needed
        if response.stop_reason == "tool_use":
            logger.info("Tool use requested by model")
            response = self._handle_tool_use(response, user_message, conversation_id, user_message_id)

        # Process the final response
        full_response = ""
        history_response = ""
        speakable_chunks = []

        for content_block in response.content:
            if content_block.type == "text":
                text_content = content_block.text
                full_response += text_content
                history_response += text_content
                speakable_chunks.append({"text": text_content, "speakable": True})
                
        # Add the assistant's response to the conversation history
        add_message(conversation_id, "assistant", history_response)
        
        return {
            "conversation_id": conversation_id,
            "full_response": full_response,
            "speakable_chunks": speakable_chunks
        }
        
    def _handle_tool_use(self, response, user_message, conversation_id, user_message_id):
        """Handle tool use in the response"""
        current_response = response
        
        while current_response.stop_reason == "tool_use":
            # Get the tool use block
            tool_use = next((block for block in current_response.content if block.type == "tool_use"), None)
            
            if not tool_use:
                logger.warning("Tool use indicated but no tool_use block found")
                break
                
            tool_name = tool_use.name
            tool_input = tool_use.input
            
            logger.info(f"Tool requested: {tool_name}")
            logger.info(f"Tool input: {json.dumps(tool_input)}")
            
            # Check if we have a handler for this tool
            if tool_name in TOOL_HANDLERS:
                try:
                    # Call the tool handler
                    tool_result = TOOL_HANDLERS[tool_name](tool_input)
                    
                    # Log and store the tool call
                    tool_params_json = json.dumps(tool_input)
                    tool_result_json = json.dumps(tool_result)
                    
                    logger.info(f"Tool result: {tool_result_json[:100]}...")
                    add_tool_call(
                        conversation_id, 
                        user_message_id, 
                        tool_name, 
                        tool_params_json, 
                        tool_result_json
                    )
                    
                    # Create messages with tool result
                    messages = [
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": current_response.content},
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_use.id,
                                    "content": tool_result_json,
                                }
                            ],
                        },
                    ]
                    
                    # Get the next response
                    current_response = self.anthropic_service.create_message(messages, TOOLS)
                    
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {str(e)}")
                    logger.error(traceback.format_exc())
                    
                    # Create an error message for the tool
                    error_message = f"Error executing tool {tool_name}: {str(e)}"
                    messages = [
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": current_response.content},
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_use.id,
                                    "content": json.dumps({"error": error_message}),
                                }
                            ],
                        },
                    ]
                    
                    # Get the next response
                    current_response = self.anthropic_service.create_message(messages, TOOLS)
            else:
                logger.error(f"Unknown tool requested: {tool_name}")
                # Create an error message for the tool
                error_message = f"Unknown tool requested: {tool_name}"
                messages = [
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": current_response.content},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": json.dumps({"error": error_message}),
                            }
                        ],
                    },
                ]
                
                # Get the next response
                current_response = self.anthropic_service.create_message(messages, TOOLS)
                
        return current_response
