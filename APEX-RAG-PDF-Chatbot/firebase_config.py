# firebase_config.py
import os
import pyrebase
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 🔥 Firebase Configuration (from environment variables)
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY", "AIzaSyAkJEPytk9vwEST6uZKZYuOWdkm-kEayJE"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "apex-rag-chatbot.firebaseapp.com"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID", "apex-rag-chatbot"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", "apex-rag-chatbot.firebasestorage.app"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", "544926934861"),
    "appId": os.getenv("FIREBASE_APP_ID", "1:544926934861:web:eddc396c862666fab5b904"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL", "https://apex-rag-chatbot-default-rtdb.firebaseio.com")
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

def signup_user(email, password, name):
    """Create new user account"""
    try:
        user = auth.create_user_with_email_and_password(email, password)
        user_id = user['localId']
        
        user_data = {
            "email": email,
            "name": name,
            "tier": "free",
            "messages_used": 0,
            "messages_limit": 50,
            "documents_used": 0,
            "documents_limit": 3,
            "created_at": datetime.utcnow().isoformat()
        }
        
        db.child("users").child(user_id).set(user_data)
        
        return True, "✅ Account created successfully! Please login.", None
    except Exception as e:
        error_msg = str(e)
        if "EMAIL_EXISTS" in error_msg:
            return False, "❌ Email already registered. Please login.", None
        elif "WEAK_PASSWORD" in error_msg:
            return False, "❌ Password must be at least 6 characters.", None
        else:
            return False, f"❌ Signup error: {error_msg}", None

def login_user(email, password):
    """Login existing user"""
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user_id = user['localId']
        token = user['idToken']
        
        # Get user data from database
        user_data = db.child("users").child(user_id).get().val()
        
        # If user data doesn't exist (old account), create it
        if not user_data:
            user_data = {
                "email": email,
                "name": email.split('@')[0],
                "tier": "free",
                "messages_used": 0,
                "messages_limit": 50,
                "documents_used": 0,
                "documents_limit": 3,
                "created_at": datetime.utcnow().isoformat()
            }
            db.child("users").child(user_id).set(user_data)
        
        return True, "✅ Login successful!", user_id, token, user_data
        
    except Exception as e:
        error_msg = str(e)
        if "INVALID_PASSWORD" in error_msg or "INVALID_LOGIN_CREDENTIALS" in error_msg:
            return False, "❌ Invalid email or password.", None, None, None
        elif "EMAIL_NOT_FOUND" in error_msg:
            return False, "❌ Email not found. Please sign up first.", None, None, None
        else:
            return False, f"❌ Login error: {error_msg}", None, None, None

def get_user_data(user_id):
    """Get user information and quota"""
    try:
        return db.child("users").child(user_id).get().val()
    except:
        return None

def update_message_count(user_id):
    """Increment message count"""
    try:
        user_data = get_user_data(user_id)
        if user_data:
            new_count = user_data.get('messages_used', 0) + 1
            db.child("users").child(user_id).update({"messages_used": new_count})
            return True
        return False
    except:
        return False

def update_document_count(user_id):
    """Increment document count"""
    try:
        user_data = get_user_data(user_id)
        if user_data:
            new_count = user_data.get('documents_used', 0) + 1
            db.child("users").child(user_id).update({"documents_used": new_count})
            return True
        return False
    except:
        return False

def check_message_quota(user_id):
    """Check if user can send more messages"""
    user_data = get_user_data(user_id)
    return user_data and user_data.get('messages_used', 0) < user_data.get('messages_limit', 50)

def check_document_quota(user_id):
    """Check if user can upload more documents"""
    user_data = get_user_data(user_id)
    return user_data and user_data.get('documents_used', 0) < user_data.get('documents_limit', 3)
