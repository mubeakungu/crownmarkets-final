"""
Crown Markets Trading Platform
Full Flask App with Referral System
"""

import os
import uuid
from datetime import datetime, timedelta
from functools import wraps
from decimal import Decimal

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://user:password@localhost/crown_markets'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

# ════════════════════════════════════════════════════════════════════════════
# REFERRAL & COMMISSION SETTINGS
# ════════════════════════════════════════════════════════════════════════════
REFERRAL_COMMISSION_PCT = 0.15  # ✓ 15% commission (ENABLED)
MIN_DEPOSIT_FOR_COMMISSION = 250  # $250 minimum
MIN_REFERRAL_WITHDRAWAL = 16  # $16 minimum
REFERRAL_CODE_LENGTH = 8

# M-Pesa Settings (for Kenya)
MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY', '')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', '')
MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE', '174379')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY', '')

db = SQLAlchemy(app)

# ════════════════════════════════════════════════════════════════════════════
# DATABASE MODELS
# ════════════════════════════════════════════════════════════════════════════

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    pin_hash = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    kyc_verified = db.Column(db.Boolean, default=False)
    
    # Balances
    deposit_balance = db.Column(db.Numeric(15, 2), default=0)
    ref_balance = db.Column(db.Numeric(15, 2), default=0)
    
    # Referral tracking
    referrer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    referral_code = db.Column(db.String(REFERRAL_CODE_LENGTH), unique=True, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    referrals = db.relationship('Referral', foreign_keys='Referral.referrer_id', backref='referrer')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_pin(self, pin):
        self.pin_hash = generate_password_hash(pin)
    
    def check_pin(self, pin):
        return check_password_hash(self.pin_hash, pin)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'deposit_balance': float(self.deposit_balance),
            'ref_balance': float(self.ref_balance),
            'referral_code': self.referral_code,
            'is_admin': self.is_admin,
            'kyc_verified': self.kyc_verified,
            'created_at': self.created_at.isoformat()
        }


class Referral(db.Model):
    __tablename__ = 'referrals'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    referrer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    referred_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    status = db.Column(db.String(20), default='PENDING')  # PENDING, CREDITED, CANCELLED
    commission_amount = db.Column(db.Numeric(15, 2), default=0)
    commission_pct = db.Column(db.Numeric(5, 2), default=REFERRAL_COMMISSION_PCT)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    credited_at = db.Column(db.DateTime, nullable=True)
    
    referred_user = db.relationship('User', foreign_keys=[referred_id], backref='referred_by_rel')
    
    def to_dict(self):
        return {
            'id': self.id,
            'referrer_id': self.referrer_id,
            'referred_name': self.referred_user.name,
            'referred_email': self.referred_user.email,
            'status': self.status,
            'commission_amount': float(self.commission_amount),
            'commission_pct': float(self.commission_pct),
            'created_at': self.created_at.isoformat()
        }


class Deposit(db.Model):
    __tablename__ = 'deposits'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(10), default='USD')
    payment_method = db.Column(db.String(50))  # mpesa, crypto, card, etc.
    
    status = db.Column(db.String(20), default='PENDING')  # PENDING, APPROVED, REJECTED, COMPLETED
    reference = db.Column(db.String(255), unique=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', backref='deposits')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'payment_method': self.payment_method,
            'status': self.status,
            'reference': self.reference,
            'created_at': self.created_at.isoformat()
        }


class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    type = db.Column(db.String(50), nullable=False)  # DEPOSIT, REFERRAL_COMMISSION, WITHDRAWAL, etc.
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    balance_before = db.Column(db.Numeric(15, 2))
    balance_after = db.Column(db.Numeric(15, 2))
    description = db.Column(db.String(255))
    reference = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'amount': float(self.amount),
            'balance_after': float(self.balance_after),
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }


# ════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION DECORATORS
# ════════════════════════════════════════════════════════════════════════════

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated


# ════════════════════════════════════════════════════════════════════════════
# AUTH ROUTES
# ════════════════════════════════════════════════════════════════════════════

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user with optional referral code"""
    data = request.get_json()
    
    # Validation
    required = ['name', 'email', 'phone', 'password', 'pin']
    if not all(data.get(k) for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    if len(data['password']) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    if len(data['pin']) != 6 or not data['pin'].isdigit():
        return jsonify({'error': 'PIN must be 6 digits'}), 400
    
    # Create user
    user = User(
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        referral_code=str(uuid.uuid4()).hex[:REFERRAL_CODE_LENGTH].upper()
    )
    user.set_password(data['password'])
    user.set_pin(data['pin'])
    
    # Handle referral
    ref_code = data.get('ref_code', '').strip().upper()
    if ref_code:
        referrer = User.query.filter_by(referral_code=ref_code).first()
        if referrer:
            user.referrer_id = referrer.id
    
    db.session.add(user)
    db.session.commit()
    
    # Create referral record if referred
    if user.referrer_id:
        referral = Referral(
            referrer_id=user.referrer_id,
            referred_id=user.id,
            status='PENDING'
        )
        db.session.add(referral)
        db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Account created successfully',
        'user': user.to_dict()
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is inactive'}), 403
    
    session['user_id'] = user.id
    session['is_admin'] = user.is_admin
    
    return jsonify({
        'success': True,
        'message': 'Logged in successfully',
        'user': user.to_dict()
    })


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})


# ════════════════════════════════════════════════════════════════════════════
# CLIENT REFERRAL ROUTES
# ════════════════════════════════════════════════════════════════════════════

@app.route('/api/client/referrals', methods=['GET'])
@login_required
def get_referrals():
    """Get user's referrals and earnings"""
    user_id = session['user_id']
    
    referrals = Referral.query.filter_by(referrer_id=user_id).all()
    
    return jsonify({
        'success': True,
        'data': [r.to_dict() for r in referrals],
        'count': len(referrals)
    })


@app.route('/api/client/referral-balance', methods=['GET'])
@login_required
def get_referral_balance():
    """Get referral balance"""
    user = User.query.get(session['user_id'])
    
    return jsonify({
        'success': True,
        'balance': float(user.ref_balance),
        'referral_code': user.referral_code,
        'referral_link': f"{request.host_url}register?ref={user.referral_code}"
    })


@app.route('/api/client/referral-withdraw', methods=['POST'])
@login_required
def withdraw_referral():
    """Withdraw referral earnings"""
    data = request.get_json()
    user = User.query.get(session['user_id'])
    
    amount = Decimal(str(data.get('amount', 0)))
    
    if amount < MIN_REFERRAL_WITHDRAWAL:
        return jsonify({
            'error': f'Minimum withdrawal is ${MIN_REFERRAL_WITHDRAWAL}'
        }), 400
    
    if amount > user.ref_balance:
        return jsonify({'error': 'Insufficient referral balance'}), 400
    
    # Validate PIN
    if not user.check_pin(data.get('pin', '')):
        return jsonify({'error': 'Invalid PIN'}), 401
    
    # Create withdrawal transaction
    user.ref_balance -= amount
    
    withdrawal = Transaction(
        user_id=user.id,
        type='REFERRAL_WITHDRAWAL',
        amount=amount,
        balance_before=user.ref_balance + amount,
        balance_after=user.ref_balance,
        description=f'Referral withdrawal to {data.get("network")}: {data.get("wallet_address")}',
        reference=str(uuid.uuid4())
    )
    
    db.session.add(withdrawal)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Withdrawal initiated',
        'transaction': withdrawal.to_dict()
    })


# ════════════════════════════════════════════════════════════════════════════
# ADMIN ROUTES
# ════════════════════════════════════════════════════════════════════════════

@app.route('/api/admin/referrals', methods=['GET'])
@admin_required
def admin_get_referrals():
    """Get all referrals"""
    referrals = Referral.query.all()
    
    return jsonify({
        'success': True,
        'data': [r.to_dict() for r in referrals],
        'count': len(referrals)
    })


@app.route('/api/admin/referral/create', methods=['POST'])
@admin_required
def admin_create_referral():
    """Admin: Create referral between two users"""
    data = request.get_json()
    
    referrer = User.query.get(data.get('referrer_id'))
    referred = User.query.get(data.get('referred_id'))
    
    if not referrer or not referred:
        return jsonify({'error': 'User not found'}), 404
    
    existing = Referral.query.filter_by(
        referrer_id=referrer.id,
        referred_id=referred.id
    ).first()
    
    if existing:
        return jsonify({'error': 'Referral already exists'}), 400
    
    referral = Referral(
        referrer_id=referrer.id,
        referred_id=referred.id,
        status='PENDING'
    )
    
    db.session.add(referral)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Referral created',
        'referral': referral.to_dict()
    }), 201


@app.route('/api/admin/deposit/<deposit_id>/approve', methods=['POST'])
@admin_required
def admin_approve_deposit(deposit_id):
    """Admin: Approve deposit and process referral commission"""
    data = request.get_json()
    deposit = Deposit.query.get(deposit_id)
    
    if not deposit:
        return jsonify({'error': 'Deposit not found'}), 404
    
    if deposit.status != 'PENDING':
        return jsonify({'error': 'Deposit already processed'}), 400
    
    # Approve deposit
    deposit.status = 'APPROVED'
    deposit.approved_at = datetime.utcnow()
    
    user = deposit.user
    user.deposit_balance += deposit.amount
    
    # Add deposit transaction
    txn = Transaction(
        user_id=user.id,
        type='DEPOSIT',
        amount=deposit.amount,
        balance_before=user.deposit_balance - deposit.amount,
        balance_after=user.deposit_balance,
        description='Deposit approved',
        reference=deposit.reference
    )
    db.session.add(txn)
    
    # Process referral commission if applicable
    if (user.referrer_id and 
        deposit.amount >= MIN_DEPOSIT_FOR_COMMISSION and
        REFERRAL_COMMISSION_PCT > 0):
        
        # Find pending referral
        referral = Referral.query.filter_by(
            referrer_id=user.referrer_id,
            referred_id=user.id,
            status='PENDING'
        ).first()
        
        if referral:
            commission = deposit.amount * Decimal(str(REFERRAL_COMMISSION_PCT))
            referrer = user.referrer  # The person who referred this user
            
            # Credit commission
            referrer.ref_balance += commission
            referral.commission_amount = commission
            referral.status = 'CREDITED'
            referral.credited_at = datetime.utcnow()
            
            # Add referral commission transaction
            ref_txn = Transaction(
                user_id=referrer.id,
                type='REFERRAL_COMMISSION',
                amount=commission,
                balance_before=referrer.ref_balance - commission,
                balance_after=referrer.ref_balance,
                description=f'Commission from {user.name}\'s ${deposit.amount} deposit',
                reference=f'REF_{referral.id}'
            )
            db.session.add(ref_txn)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Deposit approved and commission processed',
        'deposit': deposit.to_dict()
    })


@app.route('/api/admin/deposit/<deposit_id>/reject', methods=['POST'])
@admin_required
def admin_reject_deposit(deposit_id):
    """Admin: Reject deposit"""
    deposit = Deposit.query.get(deposit_id)
    
    if not deposit:
        return jsonify({'error': 'Deposit not found'}), 404
    
    if deposit.status != 'PENDING':
        return jsonify({'error': 'Deposit already processed'}), 400
    
    deposit.status = 'REJECTED'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Deposit rejected'
    })


# ════════════════════════════════════════════════════════════════════════════
# PAGE ROUTES
# ════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Login page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')


@app.route('/register')
def register_page():
    """Registration page"""
    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """Client dashboard"""
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    return render_template('admin/dashboard.html')


# ════════════════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ════════════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    return jsonify({'error': 'Server error'}), 500


# ════════════════════════════════════════════════════════════════════════════
# CLI COMMANDS FOR TESTING
# ════════════════════════════════════════════════════════════════════════════

@app.cli.command()
def init_db():
    """Initialize database"""
    db.create_all()
    print('✓ Database initialized')


@app.cli.command()
def create_admin():
    """Create admin user"""
    name = input('Admin name: ')
    email = input('Admin email: ')
    password = input('Admin password: ')
    phone = input('Admin phone: ')
    
    admin = User(
        name=name,
        email=email,
        phone=phone,
        is_admin=True,
        referral_code=str(uuid.uuid4()).hex[:REFERRAL_CODE_LENGTH].upper()
    )
    admin.set_password(password)
    admin.set_pin('000000')
    
    db.session.add(admin)
    db.session.commit()
    
    print(f'✓ Admin created: {email}')


if __name__ == '__main__':
    app.run(debug=True)
