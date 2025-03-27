"""
Main entry point for the Anthropic Tools application
This file provides examples of how to use both the book library and customer service implementations
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

def run_customer_service():
    """Run the customer service assistant"""
    from Tools import ToolsFramework, CUSTOMER_SERVICE_TOOLS, get_customer_info, get_order_details, cancel_order
    
    # Create tool handlers dictionary
    customer_service_handlers = {
        "get_customer_info": get_customer_info,
        "get_order_details": get_order_details,
        "cancel_order": cancel_order
    }
    
    system_prompt = "You are a helpful customer service assistant. Be friendly and concise in your responses."
    
    # Initialize the framework
    framework = ToolsFramework(
        tools=CUSTOMER_SERVICE_TOOLS, 
        tool_handlers=customer_service_handlers,
        system_prompt=system_prompt
    )
    
    # Interactive loop
    print("\n=== Customer Service Assistant ===")
    print("Type 'exit' to quit")
    print("Sample customer IDs: C1, C2")
    print("Sample order IDs: O1, O2")
    
    conversation_history = []
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        try:
            # Process the message
            result = framework.process_message(user_input, conversation_history)
            conversation_history = result["conversation"]
            
            # Print response
            print(f"\nAssistant: {result['final_response']}")
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            print(f"Error: {str(e)}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Anthropic Tools Demo")
    parser.add_argument(
        "--mode", 
        choices=["books", "customer"], 
        default="books",
        help="Which assistant to run: books (library assistant) or customer (customer service)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "books":
        run_book_assistant()
    else:
        run_customer_service()

if __name__ == "__main__":
    main() 