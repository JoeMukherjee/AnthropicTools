import json
import logging
import traceback
import sqlite3
from db import get_messages_by_conversation_id, add_message, add_tool_call, init_conversation_db, CONVERSATION_DB
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
        logger.info(f"Initialized ResponseService")

    def generate_full_response(self, user_message, conversation_id=None):
        """Generate a full response using the Anthropic API with tool support"""
        # Before adding the new message, get the conversation context
        previous_exchange = None
        previous_user_message = None
        previous_assistant_response = None
        
        # Build conversation context if this is an existing conversation
        if conversation_id and conversation_id != 'new':
            try:
                # Get the last 2 messages (last exchange) for the conversation
                conn = sqlite3.connect(CONVERSATION_DB)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get the most recent user message (excluding the current one)
                cursor.execute(
                    """
                    SELECT content FROM messages 
                    WHERE conversation_id = ? AND sender = 'user' 
                    ORDER BY timestamp DESC LIMIT 1
                    """,
                    (conversation_id,)
                )
                user_row = cursor.fetchone()
                if user_row:
                    previous_user_message = user_row['content']
                
                # Get the most recent assistant response
                cursor.execute(
                    """
                    SELECT content FROM messages 
                    WHERE conversation_id = ? AND sender = 'assistant' 
                    ORDER BY timestamp DESC LIMIT 1
                    """,
                    (conversation_id,)
                )
                assistant_row = cursor.fetchone()
                if assistant_row:
                    previous_assistant_response = assistant_row['content']
                
                conn.close()
                
                # Create a description of the previous exchange
                if previous_user_message and previous_assistant_response:
                    previous_exchange = f"User asked: \"{previous_user_message}\"\nYou responded: \"{previous_assistant_response}\""
                    logger.info(f"Found previous exchange for conversation {conversation_id}")
                    
            except Exception as e:
                logger.warning(f"Error retrieving previous exchange: {str(e)}")
        
        # Now add the new user message to the database
        conversation_id, user_message_id = add_message(
            conversation_id, "user", user_message
        )
        logger.info(f"New user message in conversation {conversation_id}: {user_message}")
        
        # Create messages array for the model
        messages = []
        
        # Get full conversation history for context
        full_history = get_messages_by_conversation_id(conversation_id)
        
        # Enhanced follow-up detection
        is_follow_up = False
        if len(full_history) > 1:
            # Look for pronouns and references that indicate follow-up
            reference_words = ["it", "they", "that", "this", "the book", "he", "she", "when", "where", "who"]
            lower_message = user_message.lower()
            is_follow_up = any(word in lower_message for word in reference_words)
        
        # Build context-aware prompt
        if is_follow_up and len(full_history) >= 2:
            # Extract last 2 exchanges with their tool results
            context_messages = full_history[-4:]
            
            # Add explicit temporal context
            context_str = "\n".join([
                f"{msg['role']}: {msg['content']}" + 
                (" (contains book dates)" if "published" in msg['content'] else "")
                for msg in context_messages
            ])
            
            messages.append({
                "role": "user",
                "content": f"""Context from previous conversation (most recent first):
{context_str}

Current question: {user_message}

Instructions:
1. "When" refers to publication dates from the context
2. Use list_books tool if unsure about dates
3. Never ask for clarification - use tool if needed"""
            })
        else:
            messages.append({"role": "user", "content": user_message})
        
        # Get model and log info
        model = self.anthropic_service.model
        logger.info(f"Starting response with model: {model}")
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
        
        # Get the full conversation history
        messages = get_messages_by_conversation_id(conversation_id)
        tool_interaction_history = []
        
        # Remove metadata from messages since Anthropic API doesn't accept it
        filtered_messages = []
        for msg in messages:
            # Create a clean copy without metadata
            filtered_msg = {"role": msg["role"], "content": msg["content"]}
            filtered_messages.append(filtered_msg)
        
        messages = filtered_messages
        
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
            
            # Record this tool interaction for future context
            tool_interaction = f"Assistant: I need to use the {tool_name} tool with these parameters: {json.dumps(tool_input)}"
            tool_interaction_history.append(tool_interaction)
            
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
                    
                    # Record the tool result for future context
                    tool_result_msg = f"Tool result: {tool_result_json}"
                    tool_interaction_history.append(tool_result_msg)
                    
                    # Append the assistant response and tool result to the conversation
                    messages.append({"role": "assistant", "content": current_response.content})
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": tool_result_json,
                            }
                        ],
                    })
                    
                    # Create enhanced messages with tool interaction context
                    enhanced_messages = messages.copy()
                    # Add a special message to explicitly describe the tool interaction
                    enhanced_messages.append({
                        "role": "user",
                        "content": f"""[CONTEXT: Tool interaction occurred]
The assistant used the {tool_name} tool with parameters: {tool_params_json}
The tool returned: {tool_result_json}
Please continue with your response based on this tool result."""
                    })
                    
                    # Get the next response with the full message history
                    current_response = self.anthropic_service.create_message(enhanced_messages, TOOLS)
                    
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {str(e)}")
                    logger.error(traceback.format_exc())
                    
                    # Record the error for future context
                    error_message = f"Error executing tool {tool_name}: {str(e)}"
                    tool_interaction_history.append(f"Tool error: {error_message}")
                    
                    # Append the error message as a tool result
                    messages.append({"role": "assistant", "content": current_response.content})
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": json.dumps({"error": error_message}),
                            }
                        ],
                    })
                    
                    # Add a special message to describe the error
                    enhanced_messages = messages.copy()
                    enhanced_messages.append({
                        "role": "user",
                        "content": f"""[CONTEXT: Tool error occurred]
The assistant tried to use the {tool_name} tool but it resulted in an error: {error_message}
Please acknowledge this error and continue with an alternative approach if possible."""
                    })
                    
                    # Get the next response with the full message history
                    current_response = self.anthropic_service.create_message(enhanced_messages, TOOLS)
            else:
                logger.error(f"Unknown tool requested: {tool_name}")
                # Record the unknown tool error for future context
                error_message = f"Unknown tool requested: {tool_name}"
                tool_interaction_history.append(f"Tool error: {error_message}")
                
                # Append the error message as a tool result
                messages.append({"role": "assistant", "content": current_response.content})
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": json.dumps({"error": error_message}),
                        }
                    ],
                })
                
                # Add a special message to describe the unknown tool error
                enhanced_messages = messages.copy()
                enhanced_messages.append({
                    "role": "user",
                    "content": f"""[CONTEXT: Unknown tool error]
The assistant tried to use a tool called '{tool_name}' but this tool does not exist.
Please acknowledge this and continue with an alternative approach using one of the available tools."""
                })
                
                # Get the next response with the full message history
                current_response = self.anthropic_service.create_message(enhanced_messages, TOOLS)
                
        return current_response

    def _maybe_add_tool_prompt(self, messages, user_message, last_assistant_response=None):
        """Add a prompt to encourage tool use and context awareness for follow-up questions"""
        # Make a working copy of messages to avoid modifying the original
        messages = messages.copy()
        
        # Remove any existing system messages which will conflict with the top-level system parameter
        messages = [msg for msg in messages if msg["role"] != "system"]
        
        # Extract conversation ID for tracking
        conversation_id = None
        for msg in messages:
            if msg.get("metadata") and msg["metadata"].get("conversation_id"):
                conversation_id = msg["metadata"]["conversation_id"]
                break
                
        # If we don't have a conversation ID, try to set a placeholder
        if not conversation_id and len(messages) > 0:
            conversation_id = "unknown"
            
        # Include conversation ID in logging
        logger.info(f"Processing tool prompt for conversation {conversation_id} with {len(messages)} messages")
        
        # Clean all messages to remove metadata
        cleaned_messages = []
        for msg in messages:
            cleaned_msg = {"role": msg["role"], "content": msg["content"]}
            cleaned_messages.append(cleaned_msg)
        
        messages = cleaned_messages
        
        # If we have a direct last_assistant_response, create a simplified context prompt
        if last_assistant_response and user_message:
            # Add a context note with the exact last response and current query
            context_note = {
                "role": "user",
                "content": f"""[SYSTEM INSTRUCTION - NOT USER MESSAGE]
THIS IS MY PREVIOUS RESPONSE TO THE USER:

{last_assistant_response}

THE USER'S FOLLOW-UP QUESTION IS:

{user_message}

INSTRUCTIONS:
1. Use the previous response as direct context for interpreting the user's question.
2. NEVER say "I don't have enough context" or apologize for lacking context.
3. If the question relates to books, use the appropriate tools (list_books, etc.).
4. For questions about authors, titles, or book details, use list_books with title_search.
5. For Harry Potter questions, search for "Harry Potter" in the database using list_books with title_search."""
            }
            
            # Insert at the beginning
            messages.insert(0, context_note)
            logger.info(f"Added direct context prompt with previous response for conversation {conversation_id}")
            return messages
        
        # Fall back to standard handling if we don't have a direct last response
        # Check if there's enough message history to build context
        if len(messages) <= 1:
            # For the first message in a conversation, add a special user message with instructions
            context_note = {
                "role": "user", 
                "content": f"""[SYSTEM INSTRUCTION - NOT USER MESSAGE]
Process this first message: "{user_message}"
                
Instructions:
1. If this relates to books, authors, or titles, use the list_books tool with title_search or other appropriate tools.
2. Always search the database before claiming books aren't in the collection.
3. For Harry Potter related queries, search for "Harry Potter" in the book database using list_books with title_search."""
            }
            
            # Insert at the beginning
            messages.insert(0, context_note)
            logger.info(f"Added first-message prompt for conversation {conversation_id}")
            return messages
            
        # For follow-up questions, we need to build strong context
        
        # Extract the message history, preserving order by timestamp if available
        ordered_messages = messages.copy()
        ordered_messages.sort(key=lambda msg: 
            msg.get("metadata", {}).get("timestamp", "0") 
            if msg.get("metadata") and msg["metadata"].get("timestamp") 
            else "0"
        )
        
        history_text = []
        for i, msg in enumerate(ordered_messages[-6:]):  # Just get the last 3 exchanges (6 messages)
            prefix = "User: " if msg["role"] == "user" else "Assistant: "
            if isinstance(msg["content"], str):
                history_text.append(f"{prefix}{msg['content']}")
        
        history_context = "\n".join(history_text)
        
        # Create a context-aware user message with instructions
        context_note = {
            "role": "user",
            "content": f"""[SYSTEM INSTRUCTION - NOT USER MESSAGE]
IMPORTANT: This is conversation {conversation_id}. The user is in an ongoing conversation. Here is the recent conversation history:

{history_context}

Current user message: "{user_message}"

Instructions:
1. This is very likely a follow-up question related to the conversation history above.
2. NEVER respond with "I don't have enough context" or "I need more information."
3. ALWAYS interpret short questions in the context of the previous messages in THIS conversation only.
4. If the conversation mentions books, authors, or titles, search for them using list_books with title_search.
5. For follow-up questions like "when", "who", or "how many", determine what they refer to from context.
6. If you're unsure, make a reasonable assumption based on the conversation flow.
7. For Harry Potter related queries, search for "Harry Potter" in the database using list_books tool.

CRITICAL: The user expects you to maintain the conversation flow without asking for clarification."""
        }
        
        # Insert at the beginning
        messages.insert(0, context_note)
        logger.info(f"Added context-aware prompt for conversation {conversation_id} with {len(history_text)} previous messages")
        
        return messages
