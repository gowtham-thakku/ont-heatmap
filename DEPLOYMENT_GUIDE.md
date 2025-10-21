# Deploying CZID Heatmap as a Web App

This guide covers multiple options for deploying your Streamlit app online so others can access it via a URL.

## Option 1: Streamlit Community Cloud (Recommended - FREE)

**Best for**: Public apps, easiest deployment, completely free

### Steps:

1. **Push your code to GitHub**
   ```bash
   git init
   git add app.py requirements.txt STREAMLIT_README.md
   git commit -m "Initial commit - CZID Heatmap Streamlit App"
   git remote add origin https://github.com/YOUR_USERNAME/ont-heatmap.git
   git push -u origin main
   ```

2. **Sign up for Streamlit Community Cloud**
   - Go to https://share.streamlit.io
   - Sign in with your GitHub account
   - It's completely FREE!

3. **Deploy your app**
   - Click "New app"
   - Select your repository: `YOUR_USERNAME/ont-heatmap`
   - Set main file path: `app.py`
   - Click "Deploy"

4. **Access your app**
   - You'll get a URL like: `https://YOUR_USERNAME-ont-heatmap-app-xxxxx.streamlit.app`
   - Share this URL with anyone!

### Pros:
- ✅ Completely free
- ✅ Super easy deployment (3 clicks)
- ✅ Auto-redeploys on git push
- ✅ Built-in HTTPS
- ✅ No server management

### Cons:
- ❌ Public apps only (code must be on public GitHub)
- ❌ Resource limits (1 GB RAM per app)
- ❌ Apps sleep after inactivity

---

## Option 2: Hugging Face Spaces (FREE)

**Best for**: Public apps, ML/data science apps, generous free tier

### Steps:

1. **Sign up at Hugging Face**
   - Go to https://huggingface.co
   - Create a free account

2. **Create a new Space**
   - Click on your profile → "New Space"
   - Select "Streamlit" as the SDK
   - Name your space (e.g., "czid-heatmap")
   - Choose "Public" or "Private"

3. **Upload your files**
   - Upload `app.py` (rename to `app.py` if needed)
   - Upload `requirements.txt`
   - Optionally add a README.md

4. **Access your app**
   - URL will be: `https://huggingface.co/spaces/YOUR_USERNAME/czid-heatmap`

### Pros:
- ✅ Free for public AND private apps
- ✅ Better resource limits (16 GB RAM available)
- ✅ Great for data science community
- ✅ Can upgrade to persistent hardware

### Cons:
- ❌ Slightly slower cold starts
- ❌ Less Streamlit-specific features

---

## Option 3: Render (FREE tier available)

**Best for**: More control, can have private apps, professional hosting

### Steps:

1. **Create a `render.yaml` file** (optional but recommended)
   ```yaml
   services:
     - type: web
       name: czid-heatmap
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```

2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Render config"
   git push
   ```

3. **Deploy on Render**
   - Go to https://render.com
   - Sign up/login with GitHub
   - Click "New" → "Web Service"
   - Connect your repository
   - Render will auto-detect Streamlit
   - Click "Create Web Service"

4. **Access your app**
   - URL: `https://czid-heatmap.onrender.com`

### Pros:
- ✅ Free tier available
- ✅ Can have private repos
- ✅ More professional deployment
- ✅ Easy scaling options

### Cons:
- ❌ Free tier apps sleep after 15 min inactivity
- ❌ Free tier has limited hours per month
- ❌ Slower cold starts

---

## Option 4: Google Cloud Run (Pay-as-you-go)

**Best for**: Enterprise use, custom domains, maximum control

### Steps:

1. **Create a `Dockerfile`**
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY app.py .
   EXPOSE 8080
   CMD streamlit run app.py --server.port 8080 --server.address 0.0.0.0
   ```

2. **Install Google Cloud CLI**
   - Follow: https://cloud.google.com/sdk/docs/install

3. **Deploy**
   ```bash
   gcloud run deploy czid-heatmap \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

4. **Access your app**
   - You'll get a URL like: `https://czid-heatmap-xxxxx-uc.a.run.app`

### Pros:
- ✅ Extremely scalable
- ✅ Only pay for actual usage
- ✅ Custom domains easy
- ✅ Private by default

### Cons:
- ❌ Requires billing account
- ❌ More complex setup
- ❌ Costs money (though usually <$5/month for low traffic)

---

## Option 5: AWS EC2 / Azure / DigitalOcean (Traditional VPS)

**Best for**: Maximum control, existing cloud infrastructure

### General Steps:

1. **Create a virtual machine**
   - AWS EC2, Azure VM, or DigitalOcean Droplet
   - Ubuntu 22.04 recommended

2. **SSH into your server**
   ```bash
   ssh user@your-server-ip
   ```

3. **Install dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip nginx
   pip3 install -r requirements.txt
   ```

4. **Run with process manager**
   ```bash
   # Install PM2
   sudo npm install -g pm2

   # Start app
   pm2 start "streamlit run app.py" --name czid-heatmap
   pm2 save
   pm2 startup
   ```

5. **Configure reverse proxy (Nginx)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

### Pros:
- ✅ Complete control
- ✅ Can customize everything
- ✅ No platform restrictions

### Cons:
- ❌ Most expensive
- ❌ Requires server management skills
- ❌ You handle security, backups, etc.

---

## Quick Comparison Table

| Platform | Cost | Ease | Public/Private | Best For |
|----------|------|------|----------------|----------|
| **Streamlit Cloud** | Free | ⭐⭐⭐⭐⭐ | Public only | Quick sharing |
| **Hugging Face** | Free | ⭐⭐⭐⭐ | Both | Data science |
| **Render** | Free tier | ⭐⭐⭐⭐ | Both | Professional free |
| **Cloud Run** | Pay-per-use | ⭐⭐⭐ | Both | Enterprise |
| **VPS** | $5-50/mo | ⭐⭐ | Both | Full control |

---

## Recommended Approach for Your App

For the **CZID Heatmap app**, I recommend:

### 🏆 Start with Streamlit Community Cloud (FREE)
Perfect for:
- Sharing with collaborators
- Quick demos
- Public health research sharing

### 🔒 If you need private deployment:
Use **Hugging Face Spaces** (free private apps) or **Render** (free tier with private repos)

### 💼 For production/enterprise:
Use **Google Cloud Run** or **AWS** with proper authentication

---

## Next Steps for Streamlit Cloud Deployment

Would you like me to help you:
1. Create the necessary files for GitHub deployment?
2. Set up a `.streamlit/config.toml` for custom settings?
3. Add authentication if needed?

Let me know which platform you'd like to use, and I can provide more specific guidance!
