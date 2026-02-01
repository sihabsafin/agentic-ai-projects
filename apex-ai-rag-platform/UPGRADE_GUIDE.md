# 🚀 Apex AI SaaS Upgrade - Implementation Guide

## Quick Start

This guide will help you deploy all the upgrades to your Apex AI application.

---

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ Existing Apex AI application running
- ✅ Firebase project with Firestore enabled
- ✅ Groq API key
- ✅ Stripe account (sign up at stripe.com if needed)
- ✅ Access to HuggingFace Spaces settings

---

## 🎯 Step-by-Step Deployment

### Step 1: Backup Current Application

1. Download your current codebase as backup
2. Export Firestore data (optional but recommended)
3. Document current secrets/environment variables

### Step 2: Update Application Files

Replace the following files with the updated versions:

1. **Replace `firebase_config.py`** with `firebase_config_updated.py`
   ```bash
   # In your project directory
   mv firebase_config.py firebase_config_backup.py
   mv firebase_config_updated.py firebase_config.py
   ```

2. **Replace `app.py`** with `app_updated.py`
   ```bash
   mv app.py app_backup.py
   mv app_updated.py app.py
   ```

3. **Replace `requirements.txt`** with `requirements_updated.txt`
   ```bash
   mv requirements.txt requirements_backup.txt
   mv requirements_updated.txt requirements.txt
   ```

### Step 3: Set Up Stripe

1. **Create Stripe Account** (if you don't have one)
   - Go to https://stripe.com
   - Sign up and verify your account
   - For testing, use TEST mode

2. **Create Premium Product**
   - Go to Products → Create product
   - Name: "Apex AI Premium"
   - Description: "Unlimited AI messages and document uploads"
   - Pricing: $9.99/month (recurring)
   - Save and copy the **Price ID** (starts with `price_`)

3. **Get Stripe API Keys**
   - Go to Developers → API keys
   - Copy **Publishable key** (starts with `pk_test_` or `pk_live_`)
   - Copy **Secret key** (starts with `sk_test_` or `sk_live_`)

### Step 4: Configure Secrets

Add the following secrets to your HuggingFace Space:

Go to **Settings → Repository secrets** and add:

```bash
# Existing secrets (keep these)
GROQ_API_KEY=gsk_...
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-key-id
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n
FIREBASE_CLIENT_EMAIL=your-service-account@....iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_API_KEY=your-web-api-key

# NEW: Stripe secrets
STRIPE_SECRET_KEY=sk_test_...    # Your Stripe secret key
STRIPE_PUBLISHABLE_KEY=pk_test_... # Your Stripe publishable key
STRIPE_PRICE_ID=price_...         # Your Premium plan price ID
```

### Step 5: Update Stripe Checkout URLs

In `firebase_config.py`, update the base URL (line ~355):

```python
# Change this line:
base_url = "https://your-app.hf.space"

# To your actual HuggingFace Space URL:
base_url = "https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME"
```

### Step 6: Run Database Migration

After deploying, you need to migrate existing users to add new fields.

**Option A: Via Streamlit (Recommended)**

Add this temporary admin page to `app.py`:

```python
# Add at the end of app.py, before the router
if st.session_state.authenticated and st.session_state.role == "admin":
    if st.sidebar.button("🔧 Run Migration"):
        from firebase_config import migrate_existing_users
        count = migrate_existing_users()
        st.success(f"✅ Migrated {count} users!")
```

Then:
1. Sign in as an admin user
2. Click "🔧 Run Migration" in sidebar
3. Wait for completion
4. Remove the temporary code

**Option B: Via Python Script**

Create a file `migrate.py`:

```python
from firebase_config import migrate_existing_users

if __name__ == "__main__":
    count = migrate_existing_users()
    print(f"Migration complete! Updated {count} users.")
```

Run it:
```bash
python migrate.py
```

### Step 7: Create First Admin User

You need at least one admin user to access the admin dashboard.

**Method 1: Manually in Firestore**

1. Sign up a regular account (e.g., admin@yourcompany.com)
2. Go to Firebase Console → Firestore
3. Find the user document under `users` collection
4. Edit the document and change `role` field from `"user"` to `"admin"`
5. Sign out and sign back in

**Method 2: Via Code**

Temporarily modify `sign_up()` in `firebase_config.py`:

```python
# Create one admin account
sign_up("admin@yourcompany.com", "your_password", "Admin User", role="admin")
```

Then remove this code after creating the admin.

### Step 8: Test Everything

Run through this checklist:

**Authentication Tests:**
- [ ] Sign up new user (Free plan)
- [ ] Sign in with correct password
- [ ] Sign in with wrong password (should fail)
- [ ] Sign out

**User Dashboard Tests:**
- [ ] View user dashboard
- [ ] See message count (should start at 0)
- [ ] See document count (should start at 0)
- [ ] See plan status (should show "Free")

**Usage Limit Tests:**
- [ ] Send a message (count increments)
- [ ] Upload a document (count increments)
- [ ] Manually update Firestore to set `messages_sent: 100`
- [ ] Try to send message (should be blocked)
- [ ] See upgrade prompt

**Stripe Payment Tests (Test Mode):**
- [ ] Click "Upgrade to Premium"
- [ ] Redirected to Stripe Checkout
- [ ] Complete test payment (use test card: 4242 4242 4242 4242)
- [ ] Redirected back to app
- [ ] Plan upgraded to Premium
- [ ] Limits removed (unlimited)
- [ ] Premium badge shows in sidebar

**Admin Dashboard Tests:**
- [ ] Sign in as admin user
- [ ] Access admin dashboard (should work)
- [ ] See system-wide metrics
- [ ] Sign in as regular user
- [ ] Try to access admin dashboard (should be blocked)

---

## 🔧 Configuration Options

### Customize Pricing

To change the premium price:

1. Update in Stripe Dashboard (Products → Edit)
2. Update in `firebase_config.py`:
   ```python
   MONTHLY_PRICE = 19.99  # Change to your price
   ```

### Customize Free Plan Limits

In `firebase_config.py`, modify:

```python
FREE_PLAN_LIMITS = {
    "messages": 100,    # Change to desired message limit
    "documents": 10,    # Change to desired document limit
}
```

### Add More Plan Tiers

To add a "Pro" plan between Free and Premium:

1. Create new Stripe product/price
2. Add to `firebase_config.py`:
   ```python
   PRO_PLAN_LIMITS = {
       "messages": 500,
       "documents": 50,
   }
   ```
3. Update UI to show 3 plan options
4. Add plan selection logic

---

## 🐛 Troubleshooting

### Issue: "Stripe not configured"

**Solution**: Check that `STRIPE_SECRET_KEY` and `STRIPE_PRICE_ID` are set in secrets.

### Issue: Payment succeeds but plan not upgraded

**Possible causes**:
1. Stripe redirect URL is wrong
2. Session verification failed
3. Firestore permissions issue

**Solution**:
1. Check Stripe Dashboard → Payments for successful payment
2. Manually update user in Firestore: set `plan: "premium"`
3. Check HuggingFace logs for errors

### Issue: Admin can't access admin dashboard

**Solution**: Verify the user document in Firestore has `role: "admin"`.

### Issue: User sees "You've reached your limit" immediately

**Solution**: 
1. Check Firestore user document
2. Verify `messages_sent` and `docs_uploaded` fields
3. Run migration script to add missing fields

### Issue: Uploaded documents not adding to knowledge base

**Expected behavior**: The current implementation tracks uploads but doesn't automatically add to RAG.

**Solution (future enhancement)**:
1. Parse uploaded document content
2. Add to existing knowledge base text
3. Rebuild vector store with new content

---

## 📊 Monitoring After Launch

### Daily Checks
- [ ] Review error logs in HuggingFace
- [ ] Check Stripe Dashboard for failed payments
- [ ] Monitor user signups in Firebase

### Weekly Checks
- [ ] Review conversion rate (Free → Premium)
- [ ] Check average messages per user
- [ ] Review customer feedback/ratings

### Monthly Checks
- [ ] Analyze MRR growth
- [ ] Review churn rate
- [ ] Update pricing if needed
- [ ] Plan feature updates

---

## 🔄 Rollback Plan

If something goes wrong, you can quickly rollback:

1. **Restore backup files**:
   ```bash
   mv app_backup.py app.py
   mv firebase_config_backup.py firebase_config.py
   mv requirements_backup.txt requirements.txt
   ```

2. **Remove Stripe secrets** (optional)

3. **Redeploy** to HuggingFace Spaces

Note: User data in Firestore is not affected by rollback. The new fields will remain but won't be used by the old code.

---

## 🚀 Going Live

When ready to move from test to production:

1. **Switch Stripe to Live Mode**:
   - Get live API keys from Stripe
   - Update secrets with `sk_live_...` and `pk_live_...`
   - Test with real payment

2. **Update Terms of Service** (if needed)

3. **Set up monitoring**:
   - Stripe webhook monitoring
   - Error tracking (Sentry, etc.)
   - Uptime monitoring

4. **Announce to users**:
   - Email existing users about Premium plan
   - Add announcement banner in app
   - Update marketing materials

---

## 📝 Post-Deployment Checklist

After successful deployment:

- [ ] All existing AI features working
- [ ] Users can sign up/sign in
- [ ] Free plan limits enforced
- [ ] Premium upgrades working
- [ ] Admin dashboard accessible
- [ ] User dashboard showing correct stats
- [ ] No errors in logs
- [ ] Stripe test payment successful
- [ ] Documentation updated
- [ ] Team trained on new features

---

## 🎉 Success Criteria

Your upgrade is successful when:

✅ Users can create accounts and sign in
✅ Free users see usage limits
✅ Premium upgrades work via Stripe
✅ Admin can access system analytics
✅ Regular users see personal dashboard
✅ All AI features work unchanged
✅ No breaking errors in production

---

## 🆘 Need Help?

If you encounter issues:

1. Check the logs in HuggingFace Spaces
2. Review Firebase Console for data issues
3. Test in Stripe's test mode first
4. Verify all secrets are set correctly
5. Ensure database migration completed

---

## 📚 Additional Resources

- **Stripe Documentation**: https://stripe.com/docs
- **Firebase Auth Guide**: https://firebase.google.com/docs/auth
- **Streamlit Docs**: https://docs.streamlit.io
- **LangChain Docs**: https://python.langchain.com

---

**Estimated Deployment Time**: 2-3 hours (including testing)

**Support**: For issues specific to this implementation, review the deployment strategy document or check the code comments for inline documentation.

Good luck with your deployment! 🚀
