import firebase_admin
from firebase_admin import credentials, firestore, auth
import streamlit as st
import os
import json
from datetime import datetime, timedelta
import pytz
import stripe

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
FREE_PLAN_LIMITS = {
    "messages": 100,
    "documents": 10,
}

PREMIUM_PLAN_LIMITS = {
    "messages": -1,  # unlimited
    "documents": -1,  # unlimited
}

# ─────────────────────────────────────────────
# Firebase Initialization
# ─────────────────────────────────────────────
def get_firebase_config():
    """Load Firebase config from Streamlit secrets or environment."""
    try:
        # Try to load from Streamlit secrets (HuggingFace format)
        # Secrets are stored individually, not as nested JSON
        config = {
            "type": st.secrets.get("FIREBASE_TYPE", "service_account"),
            "project_id": st.secrets.get("FIREBASE_PROJECT_ID"),
            "private_key_id": st.secrets.get("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": st.secrets.get("FIREBASE_PRIVATE_KEY"),
            "client_email": st.secrets.get("FIREBASE_CLIENT_EMAIL"),
            "client_id": st.secrets.get("FIREBASE_CLIENT_ID"),
            "auth_uri": st.secrets.get("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": st.secrets.get("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
            "api_key": st.secrets.get("FIREBASE_API_KEY"),
            "auth_provider_x509_cert_url": st.secrets.get("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs"),
            "client_x509_cert_url": st.secrets.get("FIREBASE_CLIENT_X509_CERT_URL", ""),
        }
        
        # Validate required fields
        required_fields = ["project_id", "private_key", "client_email"]
        for field in required_fields:
            if not config.get(field):
                raise ValueError(f"Missing required Firebase config: {field}")
        
        return config
        
    except Exception as e:
        # Fallback: try environment variable (JSON string)
        config_json = os.environ.get("FIREBASE_CONFIG", "{}")
        if config_json != "{}":
            return json.loads(config_json)
        else:
            raise Exception(f"Firebase configuration error: {str(e)}")


def init_firebase():
    """Initialize Firebase app (only once)."""
    if not firebase_admin._apps:
        config = get_firebase_config()
        cred = credentials.Certificate(config)
        firebase_admin.initialize_app(cred)
    return firebase_admin.get_app()


def get_db():
    """Return Firestore client."""
    init_firebase()
    return firestore.client()


# ─────────────────────────────────────────────
# Stripe Initialization
# ─────────────────────────────────────────────
def init_stripe():
    """Initialize Stripe with API key from secrets."""
    api_key = os.environ.get("STRIPE_SECRET_KEY") or st.secrets.get("STRIPE_SECRET_KEY", "")
    if api_key:
        stripe.api_key = api_key
        return True
    return False


# ─────────────────────────────────────────────
# Auth Helpers
# ─────────────────────────────────────────────
def sign_up(email: str, password: str, full_name: str, role: str = "user"):
    """
    Create a new user via Firebase Auth.
    
    Args:
        email: User's email address
        password: User's password (min 6 chars)
        full_name: User's full name
        role: "user" or "admin" (default: "user")
    
    Returns:
        Firebase user object
    """
    init_firebase()
    user = auth.create_user(email=email, password=password)
    
    # Determine plan limits based on role
    limits = FREE_PLAN_LIMITS.copy()
    
    # Create user profile doc in Firestore
    db = get_db()
    db.collection("users").document(user.uid).set({
        "email": email,
        "full_name": full_name,
        "role": role,
        "created_at": datetime.now(pytz.utc),
        "plan": "free",
        "messages_sent": 0,
        "docs_uploaded": 0,
        "last_active": datetime.now(pytz.utc),
        "limits": limits,
        "stripe_customer_id": None,
        "stripe_subscription_id": None,
        "subscription_status": None,
        "plan_changed_at": datetime.now(pytz.utc),
    })
    return user


def sign_in(email: str, password: str):
    """
    Sign in via Firebase Auth (token-based).
    
    Returns:
        Dict with: idToken, uid, email, and role
    """
    # Firebase Admin SDK doesn't support password sign-in directly.
    # Use the Firebase REST API for that.
    import requests
    config = get_firebase_config()
    api_key = config.get("api_key", "")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    
    result = resp.json()
    
    # Fetch user role from Firestore
    db = get_db()
    user_doc = db.collection("users").document(result["localId"]).get()
    
    if user_doc.exists:
        user_data = user_doc.to_dict()
        result["role"] = user_data.get("role", "user")
        result["full_name"] = user_data.get("full_name", "")
    else:
        result["role"] = "user"
        result["full_name"] = ""
    
    return result


def get_user_by_email(email: str):
    """Fetch Firebase Auth user object by email."""
    init_firebase()
    return auth.get_user_by_email(email)


def get_user_data(uid: str):
    """
    Get complete user data from Firestore.
    
    Returns:
        Dict with all user fields or None if not found
    """
    db = get_db()
    user_doc = db.collection("users").document(uid).get()
    
    if user_doc.exists:
        return user_doc.to_dict()
    return None


# ─────────────────────────────────────────────
# Usage Limit Checks
# ─────────────────────────────────────────────
def check_message_limit(uid: str):
    """
    Check if user can send another message.
    
    Returns:
        Tuple (can_send: bool, remaining: int, limit: int)
    """
    user_data = get_user_data(uid)
    if not user_data:
        return False, 0, 0
    
    plan = user_data.get("plan", "free")
    messages_sent = user_data.get("messages_sent", 0)
    
    if plan == "premium":
        return True, -1, -1  # unlimited
    
    # Free plan
    limit = user_data.get("limits", {}).get("messages", FREE_PLAN_LIMITS["messages"])
    remaining = limit - messages_sent
    can_send = remaining > 0
    
    return can_send, remaining, limit


def check_document_limit(uid: str):
    """
    Check if user can upload another document.
    
    Returns:
        Tuple (can_upload: bool, remaining: int, limit: int)
    """
    user_data = get_user_data(uid)
    if not user_data:
        return False, 0, 0
    
    plan = user_data.get("plan", "free")
    docs_uploaded = user_data.get("docs_uploaded", 0)
    
    if plan == "premium":
        return True, -1, -1  # unlimited
    
    # Free plan
    limit = user_data.get("limits", {}).get("documents", FREE_PLAN_LIMITS["documents"])
    remaining = limit - docs_uploaded
    can_upload = remaining > 0
    
    return can_upload, remaining, limit


# ─────────────────────────────────────────────
# Usage Tracking (existing, unchanged)
# ─────────────────────────────────────────────
def track_message(uid: str):
    """Increment message counter for a user and log to usage_logs."""
    db = get_db()
    # Atomic increment on user doc
    db.collection("users").document(uid).update({
        "messages_sent": firestore.Increment(1),
        "last_active": datetime.now(pytz.utc),
    })
    # Append a usage log entry
    db.collection("usage_logs").add({
        "uid": uid,
        "event": "message_sent",
        "timestamp": datetime.now(pytz.utc),
    })


def track_document_upload(uid: str):
    """Increment doc counter and log."""
    db = get_db()
    db.collection("users").document(uid).update({
        "docs_uploaded": firestore.Increment(1),
        "last_active": datetime.now(pytz.utc),
    })
    db.collection("usage_logs").add({
        "uid": uid,
        "event": "document_uploaded",
        "timestamp": datetime.now(pytz.utc),
    })


def track_response_time(uid: str, response_ms: int, success: bool):
    """Log response-time and success/error for performance metrics."""
    db = get_db()
    db.collection("performance_logs").add({
        "uid": uid,
        "response_time_ms": response_ms,
        "success": success,
        "timestamp": datetime.now(pytz.utc),
    })


def track_rating(uid: str, rating: int):
    """Log a user satisfaction rating (1-5)."""
    db = get_db()
    db.collection("ratings").add({
        "uid": uid,
        "rating": rating,
        "timestamp": datetime.now(pytz.utc),
    })


# ─────────────────────────────────────────────
# Stripe Payment Functions
# ─────────────────────────────────────────────
def create_checkout_session(uid: str, email: str):
    """
    Create Stripe Checkout session for premium upgrade.
    
    Returns:
        Checkout session URL or None if error
    """
    if not init_stripe():
        return None
    
    try:
        price_id = os.environ.get("STRIPE_PRICE_ID") or st.secrets.get("STRIPE_PRICE_ID", "")
        
        if not price_id:
            st.error("Stripe Price ID not configured")
            return None
        
        # Get current domain for redirect URLs
        # Note: In production, replace with actual domain
        base_url = "https://your-app.hf.space"  # UPDATE THIS
        
        session = stripe.checkout.Session.create(
            customer_email=email,
            mode='subscription',
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            success_url=f'{base_url}?upgrade=success&session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{base_url}?upgrade=cancel',
            metadata={
                'firebase_uid': uid
            },
            allow_promotion_codes=True,  # Enable promo codes
        )
        
        return session.url
    
    except Exception as e:
        st.error(f"Error creating checkout session: {e}")
        return None


def upgrade_to_premium(uid: str, stripe_session_id: str = None):
    """
    Upgrade user to premium plan.
    
    Args:
        uid: Firebase user ID
        stripe_session_id: Stripe checkout session ID (optional)
    """
    db = get_db()
    
    # Get current user data
    user_data = get_user_data(uid)
    if not user_data:
        return False
    
    plan_before = user_data.get("plan", "free")
    
    # Update user to premium
    db.collection("users").document(uid).update({
        "plan": "premium",
        "limits": PREMIUM_PLAN_LIMITS,
        "plan_changed_at": datetime.now(pytz.utc),
        "subscription_status": "active",
    })
    
    # Log conversion
    db.collection("conversions").add({
        "uid": uid,
        "converted_at": datetime.now(pytz.utc),
        "plan_before": plan_before,
        "plan_after": "premium",
        "stripe_session_id": stripe_session_id,
        "amount_paid": 9.99,
        "currency": "usd",
    })
    
    return True


def verify_stripe_session(session_id: str):
    """
    Verify Stripe checkout session and get customer details.
    
    Returns:
        Dict with session data or None if invalid
    """
    if not init_stripe():
        return None
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == "paid":
            return {
                "uid": session.metadata.get("firebase_uid"),
                "customer_id": session.customer,
                "subscription_id": session.subscription,
                "email": session.customer_email,
            }
        
        return None
    
    except Exception as e:
        print(f"Error verifying session: {e}")
        return None


def log_stripe_event(event_type: str, event_id: str, data: dict):
    """Log Stripe webhook event to Firestore."""
    db = get_db()
    db.collection("stripe_events").add({
        "event_type": event_type,
        "event_id": event_id,
        "timestamp": datetime.now(pytz.utc),
        "data": data,
        "processed": False,
    })


# ─────────────────────────────────────────────
# Dashboard Data Fetchers (existing, unchanged)
# ─────────────────────────────────────────────
def get_all_users():
    """Return list of all user documents."""
    db = get_db()
    return [doc.to_dict() for doc in db.collection("users").stream()]


def get_usage_logs(since: datetime = None):
    """Return usage_logs, optionally filtered by start date."""
    db = get_db()
    query = db.collection("usage_logs")
    if since:
        query = query.where("timestamp", ">=", since)
    return [doc.to_dict() for doc in query.stream()]


def get_performance_logs(since: datetime = None):
    """Return performance_logs, optionally filtered by start date."""
    db = get_db()
    query = db.collection("performance_logs")
    if since:
        query = query.where("timestamp", ">=", since)
    return [doc.to_dict() for doc in query.stream()]


def get_ratings(since: datetime = None):
    """Return all rating entries."""
    db = get_db()
    query = db.collection("ratings")
    if since:
        query = query.where("timestamp", ">=", since)
    return [doc.to_dict() for doc in query.stream()]


# ─────────────────────────────────────────────
# Database Migration Helper
# ─────────────────────────────────────────────
def migrate_existing_users():
    """
    Add new fields to existing user documents.
    Run this ONCE after deploying the new code.
    """
    db = get_db()
    users = db.collection("users").stream()
    
    count = 0
    for user_doc in users:
        uid = user_doc.id
        data = user_doc.to_dict()
        
        updates = {}
        
        # Add missing fields with defaults
        if "role" not in data:
            updates["role"] = "user"
        
        if "full_name" not in data:
            # Extract from email as placeholder
            updates["full_name"] = data.get("email", "").split("@")[0].title()
        
        if "limits" not in data:
            updates["limits"] = FREE_PLAN_LIMITS.copy()
        
        if "stripe_customer_id" not in data:
            updates["stripe_customer_id"] = None
        
        if "stripe_subscription_id" not in data:
            updates["stripe_subscription_id"] = None
        
        if "subscription_status" not in data:
            updates["subscription_status"] = None
        
        if "plan_changed_at" not in data:
            updates["plan_changed_at"] = data.get("created_at", datetime.now(pytz.utc))
        
        # Apply updates
        if updates:
            db.collection("users").document(uid).update(updates)
            count += 1
            print(f"✅ Migrated user: {data.get('email', 'unknown')}")
    
    print(f"🎉 Migration complete! Updated {count} users.")
    return count


# ─────────────────────────────────────────────
# Firestore Schema Reference
# ─────────────────────────────────────────────
# Collection: users
#   {uid} → {
#       email, full_name, role, created_at, plan, messages_sent, docs_uploaded,
#       last_active, limits, stripe_customer_id, stripe_subscription_id,
#       subscription_status, plan_changed_at
#   }
#
# Collection: usage_logs
#   {auto} → { uid, event ("message_sent"|"document_uploaded"), timestamp }
#
# Collection: performance_logs
#   {auto} → { uid, response_time_ms, success (bool), timestamp }
#
# Collection: ratings
#   {auto} → { uid, rating (1-5), timestamp }
#
# Collection: conversions
#   {auto} → { uid, converted_at, plan_before, plan_after, stripe_session_id, amount_paid, currency }
#
# Collection: stripe_events
#   {auto} → { event_type, event_id, timestamp, data, processed }