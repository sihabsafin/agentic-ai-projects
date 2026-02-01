#!/usr/bin/env python3
"""
Database Migration Script for Apex AI Upgrade

This script adds new fields to existing user documents in Firestore
to support the new authentication, pricing, and usage limit features.

Run this ONCE after deploying the updated code.

Usage:
    python migrate_database.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from firebase_config import get_db, FREE_PLAN_LIMITS
from datetime import datetime
import pytz


def migrate_users():
    """
    Migrate all existing users by adding required new fields.
    
    New fields added:
    - role: "user" | "admin"
    - full_name: extracted from email or set to "User"
    - limits: { messages: 100, documents: 10 }
    - stripe_customer_id: None
    - stripe_subscription_id: None
    - subscription_status: None
    - plan_changed_at: created_at or current time
    """
    print("🚀 Starting database migration...")
    print("-" * 50)
    
    db = get_db()
    users_ref = db.collection("users")
    users = users_ref.stream()
    
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    for user_doc in users:
        uid = user_doc.id
        data = user_doc.to_dict()
        email = data.get("email", "unknown")
        
        try:
            updates = {}
            
            # 1. Add role (default to "user")
            if "role" not in data:
                updates["role"] = "user"
                print(f"  → Adding role: user")
            
            # 2. Add full_name
            if "full_name" not in data:
                # Try to extract a nice name from email
                if email and "@" in email:
                    name_part = email.split("@")[0]
                    # Convert john.doe or john_doe to John Doe
                    name_part = name_part.replace(".", " ").replace("_", " ")
                    full_name = name_part.title()
                else:
                    full_name = "User"
                
                updates["full_name"] = full_name
                print(f"  → Adding full_name: {full_name}")
            
            # 3. Add usage limits based on current plan
            if "limits" not in data:
                current_plan = data.get("plan", "free")
                
                if current_plan == "premium":
                    limits = {"messages": -1, "documents": -1}  # unlimited
                else:
                    limits = FREE_PLAN_LIMITS.copy()
                
                updates["limits"] = limits
                print(f"  → Adding limits: {limits}")
            
            # 4. Add Stripe fields
            if "stripe_customer_id" not in data:
                updates["stripe_customer_id"] = None
                print("  → Adding stripe_customer_id: None")
            
            if "stripe_subscription_id" not in data:
                updates["stripe_subscription_id"] = None
                print("  → Adding stripe_subscription_id: None")
            
            if "subscription_status" not in data:
                updates["subscription_status"] = None
                print("  → Adding subscription_status: None")
            
            # 5. Add plan_changed_at
            if "plan_changed_at" not in data:
                # Use created_at if available, otherwise current time
                plan_changed_at = data.get("created_at", datetime.now(pytz.utc))
                updates["plan_changed_at"] = plan_changed_at
                print(f"  → Adding plan_changed_at: {plan_changed_at}")
            
            # Apply updates if any
            if updates:
                users_ref.document(uid).update(updates)
                migrated_count += 1
                print(f"✅ Migrated user: {email}")
            else:
                skipped_count += 1
                print(f"⏭️  Skipped (already up-to-date): {email}")
            
            print("-" * 50)
        
        except Exception as e:
            error_count += 1
            print(f"❌ Error migrating {email}: {str(e)}")
            print("-" * 50)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Migration Summary")
    print("=" * 50)
    print(f"✅ Successfully migrated: {migrated_count} users")
    print(f"⏭️  Skipped (up-to-date): {skipped_count} users")
    print(f"❌ Errors: {error_count} users")
    print(f"📈 Total processed: {migrated_count + skipped_count + error_count} users")
    print("=" * 50)
    
    if error_count == 0:
        print("\n🎉 Migration completed successfully!")
    else:
        print(f"\n⚠️  Migration completed with {error_count} errors. Please review.")
    
    return {
        "migrated": migrated_count,
        "skipped": skipped_count,
        "errors": error_count,
        "total": migrated_count + skipped_count + error_count
    }


def verify_migration():
    """
    Verify that all users have the required fields.
    
    Returns:
        bool: True if all users are properly migrated, False otherwise
    """
    print("\n🔍 Verifying migration...")
    print("-" * 50)
    
    db = get_db()
    users = db.collection("users").stream()
    
    required_fields = [
        "role",
        "full_name",
        "limits",
        "stripe_customer_id",
        "stripe_subscription_id",
        "subscription_status",
        "plan_changed_at"
    ]
    
    all_valid = True
    issues = []
    
    for user_doc in users:
        uid = user_doc.id
        data = user_doc.to_dict()
        email = data.get("email", "unknown")
        
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            all_valid = False
            issues.append(f"User {email}: Missing fields {missing_fields}")
            print(f"❌ {email}: Missing {missing_fields}")
        else:
            print(f"✅ {email}: All fields present")
    
    print("-" * 50)
    
    if all_valid:
        print("✅ All users have been properly migrated!")
        return True
    else:
        print(f"❌ Found {len(issues)} users with missing fields:")
        for issue in issues:
            print(f"  - {issue}")
        return False


def create_admin_user(email: str, password: str, full_name: str):
    """
    Create an admin user for accessing the admin dashboard.
    
    Args:
        email: Admin email address
        password: Admin password (min 6 characters)
        full_name: Admin's full name
    """
    print(f"\n👤 Creating admin user: {email}")
    print("-" * 50)
    
    try:
        from firebase_config import sign_up
        
        user = sign_up(email, password, full_name, role="admin")
        print(f"✅ Admin user created successfully!")
        print(f"  UID: {user.uid}")
        print(f"  Email: {email}")
        print(f"  Role: admin")
        print("-" * 50)
        
        return user
    
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        print("-" * 50)
        return None


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║         Apex AI Database Migration Script                ║
║                                                          ║
║  This script will update all existing user documents     ║
║  to support the new SaaS features.                       ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # Confirm before proceeding
    response = input("\n⚠️  Are you sure you want to run the migration? (yes/no): ")
    
    if response.lower() not in ["yes", "y"]:
        print("❌ Migration cancelled.")
        sys.exit(0)
    
    # Run migration
    results = migrate_users()
    
    # Verify migration
    if input("\n🔍 Run verification check? (yes/no): ").lower() in ["yes", "y"]:
        verify_migration()
    
    # Offer to create admin user
    if input("\n👤 Create an admin user? (yes/no): ").lower() in ["yes", "y"]:
        email = input("  Admin email: ")
        password = input("  Admin password (min 6 chars): ")
        full_name = input("  Admin full name: ")
        
        if len(password) < 6:
            print("❌ Password must be at least 6 characters.")
        else:
            create_admin_user(email, password, full_name)
    
    print("\n✅ Migration script complete!")
    print("You can now deploy your updated application.\n")
