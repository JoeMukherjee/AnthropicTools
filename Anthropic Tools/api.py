"""
API for the Anthropic Tools Demo
Provides a REST API for the multi-user book library assistant
"""
from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import json
import logging
import os

from db import (
    init_db, 
    init_conversation_db, 
    get_messages_by_conversation_id,
    add_message, 
    get_conversation, 
    get_user_conversations,
    create_conversation,
    update_conversation_title,
    delete_conversation
)
from user_manager import user_manager
from responseService import ResponseService

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a secure secret key
CORS(app)  # Enable CORS for all routes

# Configure Swagger UI
SWAGGER_URL = '/docs'  # URL for exposing Swagger UI
API_URL = '/static/swagger.json'  # Our API url (can be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Book Library Assistant API"
    }
)

# Register blueprint at URL
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Initialize services
book_service = ResponseService()

# Initialize databases
init_db()
init_conversation_db()

@app.route('/static/swagger.json')
def swagger_json():
    """Serve the swagger.json file"""
    swagger_definition = {
        "swagger": "2.0",
        "info": {
            "title": "Book Library Assistant API",
            "description": "API for interacting with the multi-user book library assistant",
            "version": "1.0.0"
        },
        "basePath": "/",
        "schemes": [
            "http",
            "https"
        ],
        "paths": {
            "/api/health": {
                "get": {
                    "summary": "Health check endpoint",
                    "produces": ["application/json"],
                    "responses": {
                        "200": {
                            "description": "Health status of the API"
                        }
                    }
                }
            },
            "/api/register": {
                "post": {
                    "summary": "Register a new user",
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "description": "User registration details",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "required": ["username", "password"],
                                "properties": {
                                    "username": {"type": "string"},
                                    "email": {"type": "string"},
                                    "password": {"type": "string"}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "User registered successfully"
                        },
                        "400": {
                            "description": "Bad request"
                        }
                    }
                }
            },
            "/api/login": {
                "post": {
                    "summary": "Login a user",
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "description": "User credentials",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "required": ["username", "password"],
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string"}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "User logged in successfully"
                        },
                        "401": {
                            "description": "Unauthorized"
                        }
                    }
                }
            },
            "/api/conversations/{conversation_id}/messages": {
                "post": {
                    "summary": "Send a message to a conversation",
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "conversation_id",
                            "description": "ID of the conversation or 'new' for a new conversation",
                            "required": True,
                            "type": "string"
                        },
                        {
                            "in": "body",
                            "name": "body",
                            "description": "Message content",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "required": ["message"],
                                "properties": {
                                    "message": {"type": "string"}
                                }
                            }
                        },
                        {
                            "in": "header",
                            "name": "X-Session-Token",
                            "description": "Session token for authentication",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Message sent and response received"
                        },
                        "401": {
                            "description": "Unauthorized"
                        },
                        "403": {
                            "description": "Forbidden"
                        },
                        "404": {
                            "description": "Conversation not found"
                        }
                    }
                }
            }
        }
    }
    return jsonify(swagger_definition)

@app.route('/', methods=['GET'])
def root():
    """Root endpoint - provides basic API information"""
    return jsonify({
        "name": "Book Library Assistant API",
        "version": "1.0.0",
        "description": "API for the multi-user book library assistant",
        "documentation": request.url_root + "docs",
        "endpoints": {
            "health": "/api/health",
            "register": "/api/register",
            "login": "/api/login",
            "conversations": "/api/conversations"
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username:
        return jsonify({"success": False, "error": "Username is required"}), 400
    
    success, result = user_manager.register_user(username, email, password)
    
    if success:
        return jsonify({"success": True, "user_id": result})
    else:
        return jsonify({"success": False, "error": result}), 400

@app.route('/api/login', methods=['POST'])
def login():
    """Login a user"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username:
        return jsonify({"success": False, "error": "Username is required"}), 400
    
    success, result = user_manager.authenticate(username, password)
    
    if success:
        session['session_token'] = result
        return jsonify({
            "success": True, 
            "session_token": result,
            "username": username
        })
    else:
        return jsonify({"success": False, "error": result}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout a user"""
    session_token = request.headers.get('X-Session-Token') or session.get('session_token')
    
    if not session_token:
        return jsonify({"success": False, "error": "No session token provided"}), 401
    
    success = user_manager.logout(session_token)
    
    if 'session_token' in session:
        session.pop('session_token')
    
    return jsonify({"success": success})

@app.route('/api/me', methods=['GET'])
def get_current_user():
    """Get the current user's information"""
    session_token = request.headers.get('X-Session-Token') or session.get('session_token')
    
    if not session_token:
        return jsonify({"success": False, "error": "No session token provided"}), 401
    
    user = user_manager.get_user_from_session(session_token)
    
    if not user:
        return jsonify({"success": False, "error": "Invalid or expired session"}), 401
    
    # Don't return sensitive information
    user_info = {
        "id": user.get('id'),
        "username": user.get('username'),
        "email": user.get('email')
    }
    
    return jsonify({"success": True, "user": user_info})

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations for the current user"""
    session_token = request.headers.get('X-Session-Token') or session.get('session_token')
    
    if not session_token:
        return jsonify({"success": False, "error": "No session token provided"}), 401
    
    user = user_manager.get_user_from_session(session_token)
    
    if not user:
        return jsonify({"success": False, "error": "Invalid or expired session"}), 401
    
    conversations = get_user_conversations(user['id'], "books")
    
    return jsonify({"success": True, "conversations": conversations})

@app.route('/api/conversations', methods=['POST'])
def create_new_conversation():
    """Create a new conversation"""
    session_token = request.headers.get('X-Session-Token') or session.get('session_token')
    
    if not session_token:
        return jsonify({"success": False, "error": "No session token provided"}), 401
    
    user = user_manager.get_user_from_session(session_token)
    
    if not user:
        return jsonify({"success": False, "error": "Invalid or expired session"}), 401
    
    data = request.json
    title = data.get('title')
    
    conversation_id = create_conversation(user['id'], "books", title)
    
    return jsonify({
        "success": True, 
        "conversation_id": conversation_id,
        "title": title
    })

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation_details(conversation_id):
    """Get details and messages for a specific conversation"""
    session_token = request.headers.get('X-Session-Token') or session.get('session_token')
    
    if not session_token:
        return jsonify({"success": False, "error": "No session token provided"}), 401
    
    user = user_manager.get_user_from_session(session_token)
    
    if not user:
        return jsonify({"success": False, "error": "Invalid or expired session"}), 401
    
    conversation = get_conversation(conversation_id)
    
    if not conversation:
        return jsonify({"success": False, "error": "Conversation not found"}), 404
    
    # Check if this conversation belongs to the current user
    if conversation['user_id'] != user['id']:
        return jsonify({"success": False, "error": "Unauthorized access to conversation"}), 403
    
    messages = get_messages_by_conversation_id(conversation_id)
    
    return jsonify({
        "success": True,
        "conversation": conversation,
        "messages": messages
    })

@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation_endpoint(conversation_id):
    """Delete a conversation"""
    session_token = request.headers.get('X-Session-Token') or session.get('session_token')
    
    if not session_token:
        return jsonify({"success": False, "error": "No session token provided"}), 401
    
    user = user_manager.get_user_from_session(session_token)
    
    if not user:
        return jsonify({"success": False, "error": "Invalid or expired session"}), 401
    
    conversation = get_conversation(conversation_id)
    
    if not conversation:
        return jsonify({"success": False, "error": "Conversation not found"}), 404
    
    # Check if this conversation belongs to the current user
    if conversation['user_id'] != user['id']:
        return jsonify({"success": False, "error": "Unauthorized access to conversation"}), 403
    
    success = delete_conversation(conversation_id)
    
    return jsonify({"success": success})

@app.route('/api/conversations/<conversation_id>/title', methods=['PUT'])
def update_conversation_title_endpoint(conversation_id):
    """Update a conversation's title"""
    session_token = request.headers.get('X-Session-Token') or session.get('session_token')
    
    if not session_token:
        return jsonify({"success": False, "error": "No session token provided"}), 401
    
    user = user_manager.get_user_from_session(session_token)
    
    if not user:
        return jsonify({"success": False, "error": "Invalid or expired session"}), 401
    
    data = request.json
    new_title = data.get('title')
    
    if not new_title:
        return jsonify({"success": False, "error": "Title is required"}), 400
    
    conversation = get_conversation(conversation_id)
    
    if not conversation:
        return jsonify({"success": False, "error": "Conversation not found"}), 404
    
    # Check if this conversation belongs to the current user
    if conversation['user_id'] != user['id']:
        return jsonify({"success": False, "error": "Unauthorized access to conversation"}), 403
    
    success = update_conversation_title(conversation_id, new_title)
    
    return jsonify({"success": success})

@app.route('/api/conversations/<conversation_id>/messages', methods=['POST'])
def send_message(conversation_id):
    """Send a message to a conversation"""
    session_token = request.headers.get('X-Session-Token') or session.get('session_token')
    
    if not session_token:
        return jsonify({"success": False, "error": "No session token provided"}), 401
    
    user = user_manager.get_user_from_session(session_token)
    
    if not user:
        return jsonify({"success": False, "error": "Invalid or expired session"}), 401
    
    # For a new conversation
    if conversation_id == 'new':
        conversation_id = create_conversation(user['id'], "books")
    else:
        # Check if this conversation exists and belongs to the user
        conversation = get_conversation(conversation_id)
        
        if not conversation:
            return jsonify({"success": False, "error": "Conversation not found"}), 404
        
        if str(conversation.get('user_id')) != str(user['id']):
            return jsonify({"success": False, "error": "Unauthorized access to conversation"}), 403
    
    data = request.json
    message = data.get('message')
    
    if not message:
        return jsonify({"success": False, "error": "Message is required"}), 400
    
    # Add the user message to the database
    conversation_id, message_id = add_message(conversation_id, "user", message, user['id'])
    
    try:
        # Use the book library service with the full conversation history
        logger.info(f"Generating response in conversation {conversation_id} with message: {message}")
        
        # Log all previous messages in this conversation for debugging
        previous_messages = get_messages_by_conversation_id(conversation_id)
        logger.info(f"Conversation has {len(previous_messages)} messages in history")
        for i, msg in enumerate(previous_messages):
            logger.info(f"Message {i+1} - {msg['role']}: {msg['content'][:50]}...")
        
        # Generate the response
        result = book_service.generate_full_response(message, conversation_id)
        
        # Log successful response generation
        logger.info(f"Response generated successfully for conversation {conversation_id}")
        
        response = {
            "success": True,
            "conversation_id": result["conversation_id"],
            "response": result["full_response"],
            "speakable_chunks": result["speakable_chunks"]
        }
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        response = {
            "success": False,
            "error": f"Error generating response: {str(e)}"
        }
    
    return jsonify(response)

if __name__ == '__main__':
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True) 