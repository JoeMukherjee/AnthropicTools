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
        
        return self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.system_prompt,
            messages=messages,
            tools=tools,
        ) 