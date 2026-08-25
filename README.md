# 👑 Crown Markets - Simulated Forex Trading Platform

Crown Markets is a modern, feature-rich simulated forex trading platform built with Flask and Python. It provides a risk-free environment for learning and practicing forex trading strategies with virtual capital.

## Features

### Core Trading Features
- **Live Market Dashboard** - Real-time forex data and candlestick charts
- **Virtual Portfolio** - Manage simulated trading positions with virtual capital
- **Order Execution** - Execute trades with realistic spreads and market conditions
- **Position Management** - Open, modify, and close positions with real-time P&L
- **Performance Tracking** - Comprehensive analytics and historical trade data

### User Features
- **User Authentication** - Secure registration and login system
- **Account Management** - Customizable trader profiles and settings
- **Referral System** - Earn commissions by referring other traders (16% commission)
- **Leaderboards** - Compete with other traders and track rankings
- **Notifications** - Real-time alerts for trades, withdrawals, and account updates
- **Mobile Responsive** - Works seamlessly on desktop and mobile devices

### Admin Features
- **Admin Dashboard** - Complete oversight of all user accounts and trades
- **User Management** - Edit, suspend, or monitor user accounts
- **Trade Administration** - Manual trade execution and adjustments
- **Financial Management** - Handle deposits, withdrawals, and balance corrections
- **Reporting** - Comprehensive analytics and performance reports
- **Broadcasting** - Send notifications to individual users or all traders

### Payment Integration
- **M-Pesa Integration** - Direct integration with Safaricom's M-Pesa payment system
- **Daraja API** - STK Push for seamless mobile payments
- **Manual Deposits** - Admin-approved deposit system for other payment methods
- **Withdrawal Management** - Controlled withdrawal process with admin approval

## Technology Stack

- **Backend**: Flask (Python 3.8+)
- **Database**: PostgreSQL or SQLite
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Charts**: Chart.js for real-time data visualization
- **Hosting**: Render.com (with deployment support)
- **Payment**: M-Pesa (Daraja API)

## Project Structure

```
crown-markets/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── render.yaml           # Render.com deployment config
├── templates/
│   ├── index.html        # Landing page
│   ├── login.html        # User login
│   ├── register.html     # User registration
│   ├── dashboard.html    # Main trading dashboard
│   ├── admin_login.html  # Admin login
│   ├── admin_dashboard.html  # Admin control panel
│   └── forgot_password.html  # Password recovery
└── crown.db             # SQLite database (auto-created)
```

## Installation & Setup

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd crown-markets
```

2. **Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variables** (create `.env` file)
```bash
SECRET_KEY=your-secret-key-here
BINANCE_API_KEY=your-binance-key
BINANCE_API_SECRET=your-binance-secret
```

5. **Run the application**
```bash
python app.py
```

The app will be available at `http://localhost:5000`

### Deployment to Render.com

1. **Connect your repository** to Render.com
2. **Create a new Web Service** pointing to this repository
3. **Set environment variables** in Render dashboard:
   - `SECRET_KEY` (generate a secure value)
   - `BINANCE_API_KEY` (optional, for real data)
   - `BINANCE_API_SECRET` (optional)
4. **Deploy** - Render will automatically run the build and start commands

The app will be available at your Render deployment URL (e.g., `crown-markets-xxxxx.onrender.com`)

## Default Credentials

### Admin Account
- **Email**: admin@crownmarkets.com
- **Password**: admin123
- **PIN**: 000000

### Demo User Account
- **Email**: demo@crownmarkets.com
- **Password**: demo1234
- **PIN**: 111111

⚠️ **IMPORTANT**: Change these credentials in production!

## Configuration

### Key Settings in app.py

```python
MIN_BALANCE = 100.0          # Minimum deposit to be eligible for daily trades
PROFIT_BASIS_USD = 90.0      # Profit is $4.5 per $90 of net deposits
REFERRAL_COMMISSION = 0.16   # 16% commission on referral earnings
MIN_WITHDRAWAL = 10.0        # Minimum withdrawal amount
```

### M-Pesa Configuration

To enable M-Pesa payments, add to environment:
```bash
MPESA_CONSUMER_KEY=your-key
MPESA_CONSUMER_SECRET=your-secret
MPESA_SHORTCODE=your-shortcode
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://your-domain.com/api/mpesa/callback
```

## Database Schema

The application uses SQLite/PostgreSQL with the following main tables:
- `users` - User accounts and profiles
- `transactions` - Deposits, withdrawals, adjustments
- `positions` - Open and closed trading positions
- `daily_trade_log` - Automated daily profit distributions
- `referrals` - Referral relationships and commissions
- `notifications` - User notifications and messages
- `admin_actions` - Audit log of admin activities

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/forgot-password` - Password recovery
- `POST /api/auth/logout` - Logout

### Trading
- `POST /api/client/trade/open` - Open a position
- `POST /api/client/trade/close` - Close a position
- `GET /api/client/positions` - Get open positions
- `GET /api/client/balance/history` - Get balance history

### Account
- `GET /api/client/summary` - Get account summary
- `POST /api/client/withdraw` - Request withdrawal
- `GET /api/client/transactions` - Get transaction history

### Payments (M-Pesa)
- `POST /api/client/mpesa/stk-push` - Initiate STK Push payment
- `GET /api/client/mpesa/status` - Check payment status
- `POST /api/mpesa/callback` - M-Pesa callback handler

### Admin
- `GET /api/admin/clients` - List all users
- `POST /api/admin/client/<uid>/reset-password` - Reset user password
- `POST /api/admin/trade/run-daily` - Run daily profit distributions
- `POST /api/admin/trade/run-single` - Run trade for specific user

## Features Overview

### Daily Trading System
- Each eligible user receives daily simulated profits
- Profit rate: $4.5 per $90 of net deposits
- Automatic distribution via scheduled task
- Idempotent (can't double-charge)

### Referral System
- Users can share referral links
- 16% commission on referred user's earnings
- Referral withdrawals tracked separately

### Security Features
- Password hashing (bcrypt)
- CSRF protection
- Rate limiting on auth endpoints
- Admin audit logging
- Session management

### Mobile Payments (M-Pesa)
- Daraja API integration for STK Push
- Automatic payment confirmation
- Callback handling for payment updates
- Transaction tracking and reporting

## Styling & Branding

The Crown Markets design features:
- **Color Scheme**: Dark navy backgrounds (#0a1428, #1a2a4a) with blue accents (#4a9eff)
- **Typography**: Modern system fonts (-apple-system, Segoe UI, Roboto)
- **Components**: Card-based layouts with subtle animations
- **Responsiveness**: Mobile-first design that works on all screen sizes

To customize branding, edit the CSS in template files or create a `static/css/custom.css` file.

## Troubleshooting

### Database Issues
```bash
# Reset database (WARNING: Deletes all data)
python -c "import app; app.init_db()"
```

### Port Already in Use
```bash
# Use different port
python app.py --port 5001
```

### M-Pesa Callback Issues
- Ensure callback URL is publicly accessible
- Check M-Pesa credentials are correct
- Verify IP whitelisting in M-Pesa dashboard

## Performance Notes

- Database queries are optimized with indexes
- Chart rendering uses Chart.js for efficiency
- Static files should be served via CDN in production
- Consider Redis for session caching at scale
- Monitor gunicorn workers (default 4)

## Security Considerations

1. **Change default credentials** immediately
2. **Use HTTPS** in production (enforced by Render)
3. **Set strong SECRET_KEY** (use `secrets.token_urlsafe(32)`)
4. **Validate all user input** server-side
5. **Use environment variables** for sensitive config
6. **Enable CSRF protection** (enabled by default)
7. **Implement rate limiting** for API endpoints
8. **Regular security audits** of payment integration

## License

This project is proprietary and confidential. All rights reserved.

## Support & Documentation

For issues, questions, or feature requests, contact the development team or check the inline code comments for detailed explanations of complex logic.

---

**Built with ❤️ for forex traders worldwide**  
Crown Markets v2.0 - Simulated Trading Platform
