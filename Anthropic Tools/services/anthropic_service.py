import logging
import anthropic
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, MAX_TOKENS, SYSTEM_PROMPT

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class AnthropicService:
    def __init__(self):
        """Initialize the Anthropic client"""
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = ANTHROPIC_MODEL
        self.max_tokens = MAX_TOKENS
        self.system_prompt = SYSTEM_PROMPT
        logger.info(f"MODEL BEING USED: {self.model}")

    def get_client(self):
        """Return the initialized client"""
        return self.client

    def create_message(self, messages, tools=None):
        """Create a non-streaming message using the format provided"""
        logger.info(f"Creating message with model: {self.model}")
        
        # Enhanced system prompt
        enhanced_system_prompt = self.system_prompt + """
CRITICAL CONTEXT RULES:
1. Assume 'when' refers to publication dates from conversation history
2. If uncertain, use list_books tool with title_search from previous context
3. Never ask for clarification - use tools to find answers
4. Remember these temporal patterns:
   - 'when' without context = most recent book's publication date
   - 'when did [author] write' = use list_books with author search
"""
        
        # Messages should be passed directly from the responseService
        # No need to extract context here since it's already formatted properly
        
        try:
            # Simple API call with direct message passing
            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "system": enhanced_system_prompt,
                "messages": messages,
                "temperature": 0.1
            }
            
            # Add tools if provided
            if tools:
                kwargs["tools"] = tools
            
            response = self.client.messages.create(**kwargs)
            logger.info(f"Got response with stop reason: {response.stop_reason}")
            return response
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            raise