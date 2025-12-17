# Deployment Guide

## Deploy to Render (Free)

### Prerequisites
1. GitHub account
2. Render account (sign up at https://render.com)

### Steps

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to https://render.com
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: welcome-to-mtl (or any name)
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:server`
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)

3. **Your app will be live at**: `https://your-app-name.onrender.com`

### Notes
- Render free tier spins down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- Free tier includes 750 hours/month

## Deploy to Railway (Alternative)

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Deploy: `railway up`

## Deploy to Fly.io (Alternative)

1. Install Fly CLI
2. Run: `fly launch`
3. Follow the prompts

## Important Files Created
- `requirements.txt` - Python dependencies
- `Procfile` - Tells Render how to run your app
- `app.py` - Your Dash application (already has server exposed)

## Troubleshooting

If deployment fails:
1. Check that all dependencies are in `requirements.txt`
2. Ensure `Procfile` has correct command: `web: gunicorn app:server`
3. Check Render logs for errors
4. Make sure all file paths are relative (not absolute)


