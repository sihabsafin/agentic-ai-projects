# 🚀 Deploy APEX to Render.com

## Why Render.com?
✅ Free tier with 750 hours/month  
✅ Automatic HTTPS  
✅ Easy environment variables  
✅ Great for Python apps  
✅ Auto-deploy from GitHub  

---

## Step-by-Step Deployment

### 1️⃣ Prepare Your Code

1. Create a GitHub repository (if you haven't already)
2. Upload these files to your repo:
   - `app.py`
   - `firebase_config.py`
   - `requirements.txt`
   - `.gitignore`
   - `.env.example`

**DO NOT** upload `.env` file (it's in `.gitignore`)

---

### 2️⃣ Sign Up for Render

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (recommended)
4. Authorize Render to access your repositories

---

### 3️⃣ Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:

**Basic Settings:**
- **Name:** `apex-rag-chatbot` (or your choice)
- **Region:** Choose closest to your users
- **Branch:** `main` (or your default branch)
- **Runtime:** `Python 3`

**Build Settings:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python app.py`

**Instance Type:**
- Select **"Free"** tier

---

### 4️⃣ Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these variables one by one:

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
```

---

### 5️⃣ Deploy!

1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Your app will be live at: `https://apex-rag-chatbot.onrender.com`

---

### 6️⃣ Update app.py for Render

Change the last line in `app.py` from:

```python
if __name__ == "__main__":
    demo.launch()
```

To:

```python
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", 7860)),
        share=False
    )
```

---

## 🔄 Automatic Deployments

Once set up, every push to GitHub automatically deploys to Render!

```bash
git add .
git commit -m "Update app"
git push origin main
```

Render will automatically rebuild and redeploy.

---

## 🐛 Troubleshooting

### Build Failed?
- Check logs in Render dashboard
- Verify `requirements.txt` is correct
- Make sure Python version is compatible

### App Not Loading?
- Check environment variables are set
- View logs: Dashboard → Your Service → Logs
- Verify Firebase Realtime Database is enabled

### Out of Memory?
- Free tier has 512MB RAM
- Consider upgrading to Starter plan ($7/month)

---

## 💰 Pricing

**Free Tier:**
- 750 hours/month
- 512MB RAM
- Shared CPU
- Auto-sleeps after 15min inactivity

**Starter ($7/month):**
- Always on
- 1GB RAM
- Better performance

---

## 📊 Monitoring

View your app's:
- **Logs:** Real-time application logs
- **Metrics:** CPU, Memory usage
- **Events:** Deployment history

All in the Render dashboard!

---

## ✅ Post-Deployment Checklist

- [ ] App loads successfully
- [ ] Sign up works
- [ ] Login works
- [ ] File upload works
- [ ] Chat works
- [ ] Quotas are tracked correctly

---

## 🎉 Success!

Your APEX RAG Chatbot is now live and accessible worldwide! 🌍

Share your link: `https://your-app-name.onrender.com`
