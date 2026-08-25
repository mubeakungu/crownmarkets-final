# Crown Markets - Deployment Guide

This guide covers deploying Crown Markets to various hosting platforms.

## Quick Deploy to Render.com (Recommended)

### Step 1: Prepare Your Repository

1. Push the `crown-markets` folder to GitHub
```bash
git init
git add .
git commit -m "Initial Crown Markets setup"
git remote add origin https://github.com/your-username/crown-markets.git
git push -u origin main
```

### Step 2: Create Render Service

1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Fill in the details:
   - **Name**: crown-markets
   - **Environment**: Python 3
   - **Region**: Choose closest to your users
   - **Branch**: main
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

### Step 3: Set Environment Variables

In the Render dashboard, add these environment variables:

```
SECRET_KEY=<generate-a-random-secure-key>
BINANCE_API_KEY=<optional-your-key>
BINANCE_API_SECRET=<optional-your-secret>
```

To generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 4: Configure Database

Render.com provides SQLite by default. To use PostgreSQL:

1. Add PostgreSQL database service (optional, SQLite works fine)
2. Copy the database URL
3. Update `app.py` if using PostgreSQL:
```python
import os
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///crown.db')
```

### Step 5: Deploy

1. Click "Deploy"
2. Watch the build logs
3. Once deployed, your app is live at `crown-markets-xxxxx.onrender.com`

---

## Deploy to Heroku

### Step 1: Install Heroku CLI

```bash
curl https://cli.heroku.com/install.sh | sh
heroku login
```

### Step 2: Create Procfile

```bash
echo "web: gunicorn app:app" > Procfile
```

### Step 3: Create and Deploy

```bash
heroku create crown-markets
git push heroku main
```

### Step 4: Set Config Variables

```bash
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
heroku config:set BINANCE_API_KEY=your-key
heroku config:set BINANCE_API_SECRET=your-secret
```

### Step 5: Add PostgreSQL (Optional)

```bash
heroku addons:create heroku-postgresql:hobby-dev
```

---

## Deploy to DigitalOcean App Platform

### Step 1: Prepare Repository

Push code to GitHub as above.

### Step 2: Connect to DigitalOcean

1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Connect GitHub account
4. Select your repository

### Step 3: Configure

1. Set runtime to Python
2. Add build command: `pip install -r requirements.txt`
3. Add run command: `gunicorn app:app --bind 0.0.0.0:$PORT`
4. Configure environment variables

### Step 4: Deploy

1. Review and create
2. DigitalOcean will build and deploy

---

## Deploy to AWS Elastic Beanstalk

### Step 1: Install EB CLI

```bash
pip install awsebcli
```

### Step 2: Initialize

```bash
eb init -p python-3.10 crown-markets --region us-east-1
```

### Step 3: Create Environment

```bash
eb create crown-markets-env
```

### Step 4: Set Environment Variables

```bash
eb setenv SECRET_KEY=your-key BINANCE_API_KEY=your-key
```

### Step 5: Deploy

```bash
git push
eb deploy
```

---

## Deploy to PythonAnywhere

### Step 1: Create Account

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Get a free or paid account

### Step 2: Upload Code

1. Go to Files
2. Upload `crown-markets` folder or clone from GitHub

### Step 3: Configure Web App

1. Go to Web Apps
2. Add new web app → Python 3.10 → Flask
3. Set working directory to your project folder
4. Edit WSGI configuration:

```python
import sys
path = '/home/your-username/crown-markets'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

### Step 4: Set Environment Variables

1. Go to Web tab
2. Scroll to environment variables
3. Add your keys

### Step 5: Reload

Click "Reload" button to restart app

---

## Deploy Locally (Development)

### Step 1: Clone Repository

```bash
git clone https://github.com/your-username/crown-markets.git
cd crown-markets
```

### Step 2: Setup Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run Application

```bash
python app.py
```

Visit `http://localhost:5000`

---

## Post-Deployment Checklist

After deploying to production:

- [ ] Change default admin password
- [ ] Change demo user password
- [ ] Update SECRET_KEY to production value
- [ ] Enable HTTPS/SSL (auto on Render, Heroku, DO)
- [ ] Configure custom domain name
- [ ] Set up email notifications (if using SMTP)
- [ ] Configure M-Pesa credentials if needed
- [ ] Test all payment flows
- [ ] Set up monitoring/alerts
- [ ] Create database backups
- [ ] Review security settings
- [ ] Test on mobile devices

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | Flask session encryption key |
| `BINANCE_API_KEY` | No | - | For real market data (optional) |
| `BINANCE_API_SECRET` | No | - | For real market data (optional) |
| `MPESA_CONSUMER_KEY` | No | - | M-Pesa integration key |
| `MPESA_CONSUMER_SECRET` | No | - | M-Pesa integration secret |
| `MPESA_SHORTCODE` | No | - | M-Pesa business shortcode |
| `MPESA_PASSKEY` | No | - | M-Pesa passkey |
| `DATABASE_URL` | No | sqlite:///crown.db | Database connection string |

---

## Troubleshooting Deployment

### Build Fails: Module Not Found
- Ensure `requirements.txt` is in root directory
- Check Python version compatibility

### Port Binding Issues
- Render.com uses $PORT environment variable
- Ensure gunicorn bind is correct

### Database Connection Fails
- Check DATABASE_URL format
- Verify database credentials
- Run migrations if needed

### 500 Errors in Production
- Check Render logs: `heroku logs --tail` (Heroku) or Render dashboard
- Verify all environment variables are set
- Check file permissions

### M-Pesa Callbacks Not Working
- Verify callback URL in M-Pesa configuration
- Check webhook signature validation
- Ensure public IP is whitelisted

---

## Scaling Crown Markets

For production with many users:

1. **Database**: Upgrade to PostgreSQL
2. **Caching**: Add Redis for sessions
3. **CDN**: Use Cloudflare for static assets
4. **Load Balancing**: Use multiple app instances
5. **Monitoring**: Set up error tracking (Sentry)
6. **Performance**: Optimize database queries and indexes

---

## Support

For deployment issues:
- Check Render/Heroku/AWS documentation
- Review application logs
- Test locally first
- Contact hosting provider support

Good luck with your Crown Markets deployment! 🚀
