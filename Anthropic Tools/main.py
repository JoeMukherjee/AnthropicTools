"""
Main entry point for the Anthropic Tools application
This file provides a CLI interface for the book library assistant
"""
import logging
import argparse

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_book_assistant():
    """Run the book library assistant"""
    from responseService import ResponseService
    from db import init_db, init_conversation_db
    
    # Initialize databases
    init_db()
    init_conversation_db()
    
    # Create the response service
    service = ResponseService()
    
    # Interactive loop
    print("\n=== Book Library Assistant ===")
    print("Type 'exit' to quit")
    
    conversation_id = None
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        try:
            # Generate response
            result = service.generate_full_response(user_input, conversation_id)
            conversation_id = result["conversation_id"]
            
            # Print response
            print(f"\nAssistant: {result['full_response']}")
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            print(f"Error: {str(e)}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Book Library Assistant")
    
    args = parser.parse_args()
    run_book_assistant()

if __name__ == "__main__":
    main() 