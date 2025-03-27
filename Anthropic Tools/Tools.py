import anthropic
import json
import logging
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, MAX_TOKENS

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class ToolsFramework:
    """A generic framework for using Anthropic's Claude API with tools"""
    
    def __init__(self, tools, tool_handlers, system_prompt=None):
        """
        Initialize the tools framework
        
        Args:
            tools (list): List of tool definitions in the format expected by Anthropic API
            tool_handlers (dict): Dictionary mapping tool names to their handler functions
            system_prompt (str, optional): System prompt to use for the model
        """
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = ANTHROPIC_MODEL
        self.max_tokens = MAX_TOKENS
        self.tools = tools
        self.tool_handlers = tool_handlers
        self.system_prompt = system_prompt
        logger.info(f"Initialized ToolsFramework with model: {self.model}")

    def process_message(self, user_message, conversation_history=None):
        """
        Process a user message and return the model's response with tool handling
        
        Args:
            user_message (str): The user's message
            conversation_history (list, optional): List of previous messages in the conversation
        
        Returns:
            dict: The model's response and any tool call results
        """
        print(f"\n{'='*50}\nUser Message: {user_message}\n{'='*50}")
        
        # Create the messages list for the API
        if conversation_history is None or len(conversation_history) == 0:
            messages = [{"role": "user", "content": user_message}]
        else:
            messages = conversation_history + [{"role": "user", "content": user_message}]
        
        # Get the initial response from the model
        response = self._create_message(messages)
        
        print(f"\nInitial Response:")
        print(f"Stop Reason: {response.stop_reason}")
        
        # Handle tool calls if needed
        while response.stop_reason == "tool_use":
            tool_use = next(block for block in response.content if block.type == "tool_use")
            tool_name = tool_use.name
            tool_input = tool_use.input

            print(f"\nTool Used: {tool_name}")
            print(f"Tool Input:")
            print(json.dumps(tool_input, indent=2))

            # Process the tool call
            if tool_name in self.tool_handlers:
                tool_result = self.tool_handlers[tool_name](tool_input)
            else:
                print(f"Unknown tool: {tool_name}")
                tool_result = {"error": f"Unknown tool: {tool_name}"}

            print(f"\nTool Result:")
            print(json.dumps(tool_result, indent=2))

            # Add the tool result to the conversation
            messages = [
                *messages,
                {"role": "assistant", "content": response.content},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": json.dumps(tool_result) if isinstance(tool_result, (dict, list)) else str(tool_result),
                        }
                    ],
                },
            ]

            # Get the next response
            response = self._create_message(messages)

            print(f"\nResponse:")
            print(f"Stop Reason: {response.stop_reason}")

        # Extract the final text response
        final_response = next(
            (block.text for block in response.content if block.type == "text"),
            None,
        )

        print(f"\nFinal Response: {final_response}")

        return {
            "final_response": final_response,
            "full_response": response,
            "conversation": messages + [{"role": "assistant", "content": response.content}]
        }
    
    def _create_message(self, messages):
        """Create a message using the Anthropic API with the format provided"""
        logger.info(f"Creating message with model: {self.model}")
        
        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages
        }
        
        if self.system_prompt:
            kwargs["system"] = self.system_prompt
        
        if self.tools:
            kwargs["tools"] = self.tools
            
        return self.client.messages.create(**kwargs)