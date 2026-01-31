# 🚂 Deploy APEX to Railway.app

## Why Railway.app?
✅ $5 free credit monthly  
✅ Very fast deployments  
✅ Built-in databases  
✅ Excellent developer experience  
✅ Simple configuration  

---

## Step-by-Step Deployment

### 1️⃣ Prepare Your Code

1. Create a GitHub repository
2. Upload these files:
   - `app.py`
   - `firebase_config.py`
   - `requirements.txt`
   - `.gitignore`
   - `.env.example`

**DO NOT** upload `.env` file

---

### 2️⃣ Sign Up for Railway

1. Go to https://railway.app
2. Click **"Login"**
3. Sign in with **GitHub** (recommended)
4. Get $5 free credit (no credit card required for trial)

---

### 3️⃣ Create New Project

1. Click **"+ New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository
4. Railway will auto-detect it's a Python app

---

### 4️⃣ Configure Settings

Railway auto-detects most settings, but verify:

**Settings Tab:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python app.py`

---

### 5️⃣ Add Environment Variables

Click **"Variables"** tab and add:

```
GROQ_API_KEY=your_actual_groq_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=APEX-RAG-Chatbot
FIREBASE_API_KEY=AIzaSyAkJEPytk9vwEST6uZKZYuOWdkm-kEayJE
FIREBASE_AUTH_DOMAIN=apex-rag-chatbot.firebaseapp.com
FIREBASE_PROJECT_ID=apex-rag-chatbot
FIREBASE_STORAGE_BUCKET=apex-rag-chatbot.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=544926934861
FIREBASE_APP_ID=1:544926934861:web:eddc396c862666fab5b904
FIREBASE_DATABASE_URL=https://apex-rag-chatbot-default-rtdb.firebaseio.com
PORT=7860
```

---

### 6️⃣ Update app.py for Railway

Change the last lines in `app.py`:

```python
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", 7860)),
        share=False
    )
```

---

### 7️⃣ Generate Public URL

1. Go to **"Settings"** tab
2. Scroll to **"Networking"**
3. Click **"Generate Domain"**
4. You'll get a URL like: `apex-rag-chatbot-production.up.railway.app`

---

### 8️⃣ Deploy!

1. Railway automatically deploys on first commit
2. Watch the **"Deployments"** tab for progress
3. Deployment takes 3-5 minutes
4. Your app will be live at the generated domain!

---

## 🔄 Automatic Deployments

Every push to GitHub triggers auto-deploy:

```bash
git add .
git commit -m "Update features"
git push origin main
```

Railway rebuilds and redeploys automatically.

---

## 🐛 Troubleshooting

### Build Failed?
- Check **"Deploy Logs"** in Railway dashboard
- Verify all dependencies in `requirements.txt`
- Check environment variables are set

### App Crashes?
- View **"Application Logs"**
- Check memory usage (free tier has limits)
- Verify Firebase credentials

### Can't Access App?
- Make sure public domain is generated
- Check if deployment is "Active"
- Verify port is set correctly in environment variables

---

## 💰 Pricing

**Hobby Plan (Free Trial):**
- $5 free credit/month
- 500MB RAM
- 1GB Disk
- Enough for testing and small apps

**Developer Plan ($5/month):**
- $5 usage credit
- Pay for what you use
- Better resources
- Priority support

**Usage Estimate:**
- Small app: ~$2-3/month
- Medium traffic: ~$5-8/month

---

## 📊 Monitoring

Railway provides:
- **Real-time logs**
- **Metrics** (CPU, Memory, Network)
- **Deployment history**
- **Usage tracking**

All in one beautiful dashboard!

---

## 🎯 Railway vs Render

| Feature | Railway | Render |
|---------|---------|--------|
| Free Credit | $5/month | 750 hrs/month |
| Setup Speed | ⚡ Fastest | Fast |
| Auto-sleep | No | Yes (15min) |
| Dashboard | Best UI | Good UI |
| Learning Curve | Easiest | Easy |

**Recommendation:** 
- Railway for development & small apps
- Render for production & always-on apps

---

## ✅ Post-Deployment Checklist

- [ ] App loads at public URL
- [ ] Sign up functionality works
- [ ] Login works correctly
- [ ] Document upload works
- [ ] Chat responses work
- [ ] Quotas are tracked
- [ ] Firebase integration works

---

## 🎉 Success!

Your APEX RAG Chatbot is live on Railway! 🎊

**Next Steps:**
1. Share your Railway URL
2. Monitor usage in dashboard
3. Consider upgrading if needed
4. Set up custom domain (optional)

---

## 🔗 Useful Links

- Railway Docs: https://docs.railway.app
- Status Page: https://status.railway.app
- Discord Community: https://discord.gg/railway
