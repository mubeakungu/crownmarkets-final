# Crown Markets - Quick Start Guide

Get up and running with Crown Markets in 5 minutes! 🚀

---

## For Local Development

### 1. Setup (2 minutes)

```bash
# Clone and enter directory
cd crown-markets

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Application (1 minute)

```bash
python app.py
```

Visit: **http://localhost:5000**

### 3. Login with Demo Account

- **Email**: demo@crownmarkets.com
- **Password**: demo1234

---

## For Deployment to Render.com

### 1. Prepare GitHub (1 minute)

Push your code to GitHub:
```bash
git init
git add .
git commit -m "Crown Markets v2.0"
git push origin main
```

### 2. Deploy to Render (2 minutes)

1. Go to https://render.com
2. Click "New" → "Web Service"
3. Connect your GitHub repo
4. Fill in:
   - **Name**: crown-markets
   - **Build Cmd**: `pip install -r requirements.txt`
   - **Start Cmd**: `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Click "Deploy"

### 3. Set Environment Variables (1 minute)

In Render dashboard → Environment:
```
SECRET_KEY=<random-secure-key>
```

Generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Done! Your app is live in 5 minutes. ✨

---

## Test Your Installation

### Verify Everything Works

1. **Homepage**: http://localhost:5000 (or your Render URL)
   - Should show Crown Markets landing page

2. **Login**: http://localhost:5000/login
   - Use demo account above

3. **Dashboard**: http://localhost:5000/dashboard
   - After login, should see trading dashboard

4. **Admin**: http://localhost:5000/admin
   - Admin login page
   - Default: admin@crownmarkets.com / admin123

---

## Customization

### Change Logo
Update in HTML templates:
```html
<div class="logo-icon">👑</div>
<div class="logo-text">Crown <span>Markets</span></div>
```

### Change Colors
Update CSS in templates (find and replace):
- `#4a9eff` → Your primary color
- `#0a1428` → Your background

### Change Tagline
Update in `index.html`:
```html
<h1>Trade forex like a <span>pro</span>, without the risk</h1>
```

---

## API Quick Reference

### User Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@crownmarkets.com",
    "password": "demo1234",
    "admin": false
  }'
```

### Get Account Summary
```bash
curl http://localhost:5000/api/client/summary \
  -H "Authorization: Bearer <token>"
```

### Open Trading Position
```bash
curl -X POST http://localhost:5000/api/client/trade/open \
  -H "Content-Type: application/json" \
  -d '{
    "pair": "EUR/USD",
    "type": "buy",
    "amount": 1000
  }'
```

---

## Troubleshooting

### Port 5000 Already in Use
```bash
# Use different port
python app.py --port 5001

# Or kill existing process
lsof -ti:5000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :5000   # Windows
```

### Database Connection Error
```bash
# Database should auto-create
# If issues persist, delete crown.db and restart
rm crown.db
python app.py
```

### Module Not Found Error
```bash
# Make sure you're in virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

---

## Default Credentials

| Role | Email | Password | PIN |
|------|-------|----------|-----|
| Admin | admin@crownmarkets.com | admin123 | 000000 |
| Demo User | demo@crownmarkets.com | demo1234 | 111111 |

⚠️ **CHANGE THESE IN PRODUCTION!**

---

## What's Included

✅ Fully functional Flask application  
✅ Modern landing page with hero section  
✅ User registration & login  
✅ Admin dashboard  
✅ Trading dashboard with charts  
✅ M-Pesa payment integration (optional)  
✅ Referral system  
✅ Performance analytics  
✅ Responsive design  
✅ Production-ready code  

---

## Next Steps

1. **Deploy** using DEPLOYMENT.md
2. **Customize** branding in templates
3. **Configure** M-Pesa (if needed)
4. **Test** all flows thoroughly
5. **Launch** to production

---

## Useful Commands

```bash
# Run with debug mode
FLASK_ENV=development python app.py

# Run with custom port
python app.py --port 8000

# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Check if port is available
netstat -an | grep 5000

# View database
sqlite3 crown.db ".tables"
```

---

## Documentation

- **README.md** - Complete documentation
- **DEPLOYMENT.md** - Deployment guide for all platforms
- **CHANGES.md** - What's new in v2.0 rebranding
- **app.py** - Code comments for implementation details

---

## Support

Having issues? Check:
1. ✅ Python 3.8+ installed
2. ✅ Virtual environment activated
3. ✅ Dependencies installed (`pip install -r requirements.txt`)
4. ✅ Port 5000 is available
5. ✅ Crown Markets README.md

---

**That's it! You're ready to launch Crown Markets! 🎉**

For production deployment, follow DEPLOYMENT.md next.
