"""
User Management Module for the Anthropic Tools Demo
Handles authentication, session management, and user-related operations
"""
import hashlib
import secrets
import base64
import datetime
import json
import os
from db import create_user, get_user_by_username, get_user_conversations

# Path to store sessions
SESSIONS_FILE = "book-data/sessions.json"

class UserManager:
    """User management class for handling authentication and sessions"""
    
    def __init__(self):
        """Initialize the user manager"""
        self.active_sessions = {}  # session_token -> (user_id, expiry_time)
        self._load_sessions()
        
    def _load_sessions(self):
        """Load sessions from file if it exists"""
        try:
            if os.path.exists(SESSIONS_FILE):
                with open(SESSIONS_FILE, 'r') as f:
                    saved_sessions = json.load(f)
                    # Convert the stored expiry times from string back to datetime
                    for token, (user_id, expiry_str) in saved_sessions.items():
                        self.active_sessions[token] = (
                            user_id, 
                            datetime.datetime.fromisoformat(expiry_str)
                        )
                print(f"Loaded {len(self.active_sessions)} active sessions")
        except Exception as e:
            print(f"Error loading sessions: {str(e)}")
            self.active_sessions = {}
    
    def _save_sessions(self):
        """Save sessions to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(SESSIONS_FILE), exist_ok=True)
            
            # Convert datetime objects to ISO format strings for JSON serialization
            sessions_to_save = {}
            for token, (user_id, expiry_time) in self.active_sessions.items():
                sessions_to_save[token] = (user_id, expiry_time.isoformat())
                
            with open(SESSIONS_FILE, 'w') as f:
                json.dump(sessions_to_save, f)
        except Exception as e:
            print(f"Error saving sessions: {str(e)}")
        
    def register_user(self, username, email=None, password=None):
        """
        Register a new user
        
        Args:
            username (str): The unique username
            email (str, optional): User's email address
            password (str, optional): User's password (will be hashed)
            
        Returns:
            tuple: (success, user_id or error message)
        """
        try:
            # Check if username already exists
            existing_user = get_user_by_username(username)
            if existing_user:
                return False, f"Username '{username}' already exists"
            
            # Hash password if provided
            password_hash = None
            if password:
                password_hash = self._hash_password(password)
            
            # Create the user
            user_id = create_user(username, email, password_hash)
            
            return True, user_id
            
        except Exception as e:
            return False, str(e)
    
    def authenticate(self, username, password=None):
        """
        Authenticate a user and create a session
        
        Args:
            username (str): The username to authenticate
            password (str, optional): The password to verify
            
        Returns:
            tuple: (success, session_token or error message)
        """
        try:
            # Get the user
            user = get_user_by_username(username)
            if not user:
                return False, f"User '{username}' not found"
            
            # If password is provided, verify it
            if password:
                if not user.get('password_hash'):
                    return False, "User has no password set"
                
                password_hash = self._hash_password(password)
                if password_hash != user['password_hash']:
                    return False, "Invalid password"
            
            # Create a session token
            session_token = self._generate_session_token()
            
            # Set session expiry (24 hours from now)
            expiry_time = datetime.datetime.now() + datetime.timedelta(hours=24)
            
            # Store the session
            self.active_sessions[session_token] = (user['id'], expiry_time)
            
            # Save sessions to file
            self._save_sessions()
            
            return True, session_token
            
        except Exception as e:
            return False, str(e)
    
    def get_user_from_session(self, session_token):
        """
        Get the user associated with a session token
        
        Args:
            session_token (str): The session token
            
        Returns:
            dict or None: The user information if session is valid, None otherwise
        """
        if not session_token or session_token not in self.active_sessions:
            print(f"Session token not found: {session_token}")
            return None
        
        user_id, expiry_time = self.active_sessions[session_token]
        
        # Check if session has expired
        if datetime.datetime.now() > expiry_time:
            # Remove expired session
            print(f"Session expired for user_id: {user_id}")
            del self.active_sessions[session_token]
            self._save_sessions()
            return None
        
        # Get the user by querying directly (fix the inefficient method)
        username = self._get_username_from_user_id(user_id)
        if not username:
            print(f"Username not found for user_id: {user_id}")
            return None
            
        user = get_user_by_username(username)
        return user
    
    def _get_username_from_user_id(self, user_id):
        """Helper method to get username from user_id"""
        # This is inefficient but works for this demo
        # In a real implementation, we'd have a direct query for user_id
        all_usernames = self._get_all_usernames()
        for username in all_usernames:
            user = get_user_by_username(username)
            if user and user.get('id') == user_id:
                return username
        return None
    
    def _get_all_usernames(self):
        """Helper method to get all usernames"""
        # In a real implementation, we'd have a direct database query for this
        # For this demo, we'll look for all existing users and create a guest if needed
        try:
            from db import get_all_users
            users = get_all_users()
            
            if not users or len(users) == 0:
                # Create guest user if no users exist
                self.register_user("guest", None, "guest")
                return ["guest"]
                
            return [user['username'] for user in users]
        except Exception as e:
            print(f"Error getting usernames: {str(e)}")
            # Default to guest user if we can't get usernames
            guest_user = get_user_by_username("guest")
            if not guest_user:
                self.register_user("guest", None, "guest")
            return ["guest"]
        
    def logout(self, session_token):
        """
        Log a user out by invalidating their session token
        
        Args:
            session_token (str): The session token to invalidate
            
        Returns:
            bool: True if session was found and removed, False otherwise
        """
        if session_token in self.active_sessions:
            del self.active_sessions[session_token]
            self._save_sessions()
            return True
        return False
    
    def get_user_conversations(self, session_token, assistant_type=None):
        """
        Get conversations for the user associated with a session token
        
        Args:
            session_token (str): The session token
            assistant_type (str, optional): Filter by assistant type
            
        Returns:
            list or None: List of conversations if session is valid, None otherwise
        """
        user = self.get_user_from_session(session_token)
        if not user:
            return None
        
        return get_user_conversations(user['id'], assistant_type)
    
    def _hash_password(self, password):
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_session_token(self):
        """Generate a secure random session token"""
        token_bytes = secrets.token_bytes(32)
        return base64.urlsafe_b64encode(token_bytes).decode('utf-8')

# Create a singleton instance
user_manager = UserManager() 