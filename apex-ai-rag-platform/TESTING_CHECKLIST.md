# 🧪 Apex AI SaaS Upgrade - Testing Checklist

## Pre-Deployment Testing

Complete this checklist BEFORE deploying to production.

---

## 1️⃣ Authentication & User Management

### Sign Up Flow
- [ ] **Test 1**: Sign up with valid email and 6+ char password
  - Expected: Account created, success message shown
  - Expected: Redirected to sign-in after creation
  
- [ ] **Test 2**: Sign up with existing email
  - Expected: Error "This email is already registered"
  
- [ ] **Test 3**: Sign up with password < 6 characters
  - Expected: Error "Password must be at least 6 characters"
  
- [ ] **Test 4**: Sign up with empty fields
  - Expected: Error "Please fill in all fields"
  
- [ ] **Test 5**: Verify new user in Firestore
  - Expected: Document created with correct fields:
    - `email`, `full_name`, `role: "user"`, `plan: "free"`
    - `messages_sent: 0`, `docs_uploaded: 0`
    - `limits: { messages: 100, documents: 10 }`

### Sign In Flow
- [ ] **Test 6**: Sign in with correct credentials
  - Expected: Success, redirected to chat
  
- [ ] **Test 7**: Sign in with wrong password
  - Expected: Error "Sign-in failed"
  
- [ ] **Test 8**: Sign in with non-existent email
  - Expected: Error "Sign-in failed"
  
- [ ] **Test 9**: Sign out and verify session cleared
  - Expected: Redirected to auth page
  - Expected: All session state cleared

### Role-Based Access
- [ ] **Test 10**: Create admin user (via migration script or Firestore)
  - Expected: User document has `role: "admin"`
  
- [ ] **Test 11**: Sign in as admin
  - Expected: See "Admin" button in navigation
  
- [ ] **Test 12**: Sign in as regular user
  - Expected: No "Admin" button visible
  
- [ ] **Test 13**: Regular user tries to access admin dashboard
  - Expected: Blocked with "Access Denied" message

---

## 2️⃣ User Dashboard

### Dashboard Display
- [ ] **Test 14**: View user dashboard as new user
  - Expected: Shows 0 messages, 0 documents
  - Expected: Shows "Free" plan
  
- [ ] **Test 15**: Send a message, then check dashboard
  - Expected: Message count incremented
  
- [ ] **Test 16**: Upload a document, then check dashboard
  - Expected: Document count incremented
  
- [ ] **Test 17**: View as premium user
  - Expected: Shows premium badge
  - Expected: Shows "Unlimited" for limits
  
- [ ] **Test 18**: Plan comparison visible for free users
  - Expected: Shows Free vs Premium comparison
  - Expected: Upgrade button visible

---

## 3️⃣ Usage Limits & Enforcement

### Message Limits (Free Plan)
- [ ] **Test 19**: Send message as free user (under 100)
  - Expected: Message sent successfully
  
- [ ] **Test 20**: Manually set `messages_sent: 90` in Firestore
  - Expected: Warning shown "10 messages remaining"
  
- [ ] **Test 21**: Set `messages_sent: 100`
  - Expected: Chat interface blocked
  - Expected: Upgrade prompt shown
  
- [ ] **Test 22**: Try to send message at limit
  - Expected: Blocked with error
  
- [ ] **Test 23**: Verify premium user has no limits
  - Expected: Can send unlimited messages

### Document Limits (Free Plan)
- [ ] **Test 24**: Upload document as free user (under 10)
  - Expected: Upload successful
  
- [ ] **Test 25**: Set `docs_uploaded: 10`
  - Expected: Upload interface blocked
  - Expected: Upgrade prompt shown
  
- [ ] **Test 26**: Try to upload at limit
  - Expected: Blocked with error
  
- [ ] **Test 27**: Verify premium user has no limits
  - Expected: Can upload unlimited documents

---

## 4️⃣ Stripe Payment Integration

### Checkout Flow (Test Mode)
- [ ] **Test 28**: Click "Upgrade to Premium" as free user
  - Expected: Redirected to Stripe Checkout
  
- [ ] **Test 29**: Complete payment with test card
  - Test card: 4242 4242 4242 4242
  - Expected: Payment successful
  - Expected: Redirected back to app
  
- [ ] **Test 30**: Verify plan upgrade after payment
  - Expected: User plan changed to "premium"
  - Expected: Limits set to unlimited (-1)
  - Expected: Premium badge shown
  
- [ ] **Test 31**: Cancel Stripe checkout
  - Expected: Redirected back to app
  - Expected: Plan still "free"
  
- [ ] **Test 32**: Check Firestore conversion log
  - Expected: Document created in `conversions` collection
  - Expected: Contains: uid, timestamp, plan_before, plan_after

### Stripe Dashboard Verification
- [ ] **Test 33**: Check Stripe Dashboard → Payments
  - Expected: Test payment visible
  - Expected: Status "Succeeded"
  
- [ ] **Test 34**: Check customer created
  - Expected: Customer record exists
  - Expected: Metadata contains firebase_uid

---

## 5️⃣ Admin Dashboard

### Access Control
- [ ] **Test 35**: Access as admin user
  - Expected: Dashboard loads with metrics
  
- [ ] **Test 36**: Access as regular user
  - Expected: Blocked with error message

### Metrics Display
- [ ] **Test 37**: Verify user metrics shown
  - Expected: Total users, active users, churn rate, growth rate
  
- [ ] **Test 38**: Verify usage metrics shown
  - Expected: Total messages, avg per user, total docs, peak hour chart
  
- [ ] **Test 39**: Verify revenue metrics shown
  - Expected: MRR, conversion rate, ARPU, LTV
  - Expected: Plan distribution pie chart
  
- [ ] **Test 40**: Verify performance metrics shown
  - Expected: Avg response time, success rate, error rate, satisfaction
  - Expected: Response time trend chart
  
- [ ] **Test 41**: Change time range filter
  - Expected: Metrics update accordingly

---

## 6️⃣ AI Features (Unchanged - Regression Testing)

### RAG Chatbot
- [ ] **Test 42**: Send message and receive AI response
  - Expected: Response from Llama 3.3 70B
  
- [ ] **Test 43**: Verify knowledge base retrieval
  - Expected: Sources shown if available
  
- [ ] **Test 44**: Check conversation memory
  - Expected: AI remembers context from previous messages
  
- [ ] **Test 45**: Test with empty knowledge base
  - Expected: Fallback to general LLM (without RAG)

### Document Upload (Processing)
- [ ] **Test 46**: Upload .txt file
  - Expected: File accepted, count incremented
  
- [ ] **Test 47**: Upload .pdf file
  - Expected: File accepted, count incremented
  
- [ ] **Test 48**: Try to upload unsupported file type
  - Expected: Rejected with error

### Performance Tracking
- [ ] **Test 49**: Send message and check performance log
  - Expected: Response time logged in Firestore
  - Expected: Success/error status recorded
  
- [ ] **Test 50**: Rate a response (1-5 stars)
  - Expected: Rating logged in Firestore

---

## 7️⃣ UI/UX Polish

### Visual Design
- [ ] **Test 51**: Verify auth page design
  - Expected: Professional, modern layout
  - Expected: Clear "Sign In" / "Create Account" buttons
  
- [ ] **Test 52**: Verify premium badge display
  - Expected: Gold/yellow badge for premium users
  
- [ ] **Test 53**: Verify limit warnings
  - Expected: Warning shown when approaching limit
  - Expected: Clear upgrade CTA
  
- [ ] **Test 54**: Verify upgrade success animation
  - Expected: Balloons/confetti on successful upgrade

### Responsive Design
- [ ] **Test 55**: Test on desktop (1920x1080)
  - Expected: All elements properly aligned
  
- [ ] **Test 56**: Test on tablet (768x1024)
  - Expected: Layout adapts, no overflow
  
- [ ] **Test 57**: Test on mobile (375x667)
  - Expected: Usable on small screens

---

## 8️⃣ Database Migration

### Migration Script
- [ ] **Test 58**: Run migration on test database
  - Expected: All users updated with new fields
  
- [ ] **Test 59**: Verify no data loss
  - Expected: Existing fields unchanged
  
- [ ] **Test 60**: Run migration twice (idempotency)
  - Expected: Second run skips already-migrated users
  
- [ ] **Test 61**: Create admin via migration script
  - Expected: Admin user created with role="admin"

---

## 9️⃣ Error Handling

### Edge Cases
- [ ] **Test 62**: Disconnect internet mid-message
  - Expected: Graceful error message
  
- [ ] **Test 63**: Invalid Firebase credentials
  - Expected: Clear error, not app crash
  
- [ ] **Test 64**: Stripe API key missing
  - Expected: Upgrade button shows error, doesn't crash
  
- [ ] **Test 65**: Database write permission denied
  - Expected: Error shown to user
  
- [ ] **Test 66**: Malformed Firestore data
  - Expected: App handles gracefully with defaults

---

## 🔟 Security Testing

### Authentication Security
- [ ] **Test 67**: SQL injection in email field
  - Expected: Handled safely by Firebase
  
- [ ] **Test 68**: XSS in full name field
  - Expected: Escaped properly in display
  
- [ ] **Test 69**: Session hijacking attempt
  - Expected: Session tokens secure
  
- [ ] **Test 70**: Password strength validation
  - Expected: Min 6 chars enforced

### Payment Security
- [ ] **Test 71**: Verify no credit card data stored locally
  - Expected: All payment via Stripe
  
- [ ] **Test 72**: Check Stripe webhook signature verification
  - Expected: Invalid signatures rejected
  
- [ ] **Test 73**: Test webhook replay attack
  - Expected: Duplicate events handled

---

## 1️⃣1️⃣ Performance Testing

### Load Testing
- [ ] **Test 74**: Concurrent user signups (10 users)
  - Expected: All successful
  
- [ ] **Test 75**: Rapid message sending (20 messages/min)
  - Expected: No rate limit issues
  
- [ ] **Test 76**: Large document upload (5MB PDF)
  - Expected: Handled within reasonable time
  
- [ ] **Test 77**: Admin dashboard with 1000+ users
  - Expected: Loads within 5 seconds

### Caching
- [ ] **Test 78**: Verify embeddings cached
  - Expected: Second load faster than first
  
- [ ] **Test 79**: Verify vector store cached
  - Expected: No rebuild on every query

---

## 1️⃣2️⃣ Production Readiness

### Configuration
- [ ] **Test 80**: All secrets configured
  - [ ] GROQ_API_KEY
  - [ ] All Firebase secrets (9 total)
  - [ ] STRIPE_SECRET_KEY
  - [ ] STRIPE_PRICE_ID
  
- [ ] **Test 81**: Stripe base URL updated
  - Expected: Points to actual HuggingFace Space URL
  
- [ ] **Test 82**: Test mode vs Live mode
  - Expected: Using test keys in staging
  - Expected: Ready to switch to live keys

### Monitoring
- [ ] **Test 83**: Check error logs in HuggingFace
  - Expected: No critical errors
  
- [ ] **Test 84**: Verify Firestore usage
  - Expected: Within quota
  
- [ ] **Test 85**: Check Stripe webhook logs
  - Expected: Events being received

---

## ✅ Final Go/No-Go Checklist

Before deploying to production, verify:

- [ ] All 85 tests passed
- [ ] No critical bugs found
- [ ] Database migration completed successfully
- [ ] At least one admin user created
- [ ] All secrets configured correctly
- [ ] Stripe test payments working end-to-end
- [ ] Documentation updated
- [ ] Backup of current production created
- [ ] Rollback plan documented
- [ ] Team trained on new features

---

## 🐛 Bug Tracking Template

Use this template to report issues found during testing:

```
**Bug ID**: BUG-001
**Severity**: Critical | High | Medium | Low
**Test Number**: Test #42
**Description**: [What went wrong]
**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
**Expected Result**: [What should happen]
**Actual Result**: [What actually happened]
**Screenshots**: [If applicable]
**Status**: Open | In Progress | Fixed | Closed
```

---

## 📊 Testing Summary Report

After completing all tests, fill out:

```
Total Tests: 85
Passed: ___
Failed: ___
Blocked: ___
Not Applicable: ___

Pass Rate: ____%

Critical Bugs: ___
High Priority Bugs: ___
Medium Priority Bugs: ___
Low Priority Bugs: ___

Recommendation: ✅ Ready for Production | ⚠️ Issues Need Fixing | ❌ Not Ready
```

---

**Last Updated**: [Date]
**Tester**: [Name]
**Environment**: Staging | Production
**App Version**: v2.0.0 (SaaS Upgrade)
