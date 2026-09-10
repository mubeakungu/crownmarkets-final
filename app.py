import os
import secrets
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_hex(32))

# Database Connection Helper
def get_db_connection():
    # Retrieve DATABASE_URL environment variable (e.g., PostgreSQL string)
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    return conn

# Authentication Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'status': 'error', 'message': 'Unauthorized access'}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- API ROUTES ---

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    ref_code_input = data.get('referral_code', '').strip()

    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email and password are required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Check if user already exists
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return jsonify({'status': 'error', 'message': 'Email already registered'}), 400

        # Generate unique referral code for the new user
        new_ref_code = secrets.token_hex(4).upper()
        hashed_password = generate_password_hash(password)

        # Insert new user
        cur.execute(
            """
            INSERT INTO users (email, password_hash, referral_code, created_at)
            VALUES (%s, %s, %s, NOW())
            RETURNING id;
            """,
            (email, hashed_password, new_ref_code)
        )
        new_user_id = cur.fetchone()['id']

        # Handle referral process if a referral code was provided
        if ref_code_input:
            cur.execute("SELECT id FROM users WHERE referral_code = %s", (ref_code_input,))
            referrer = cur.fetchone()
            if referrer and referrer['id'] != new_user_id:
                # Insert pending referral record immediately upon registration
                cur.execute(
                    """
                    INSERT INTO referrals (referrer_id, referred_id, status, commission_earned, created_at)
                    VALUES (%s, %s, 'pending', 0.00, NOW());
                    """,
                    (referrer['id'], new_user_id)
                )

        conn.commit()
        
        # Log user in
        session['user_id'] = new_user_id
        session['email'] = email

        return jsonify({'status': 'success', 'message': 'Registration successful'}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email and password required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id, email, password_hash FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            return jsonify({'status': 'success', 'message': 'Logged in successfully'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
    finally:
        cur.close()
        conn.close()


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'status': 'success', 'message': 'Logged out'}), 200


@app.route('/api/client/referrals', methods=['GET'])
@login_required
def client_referrals():
    user_id = session.get('user_id')
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Get current user's referral code
        cur.execute("SELECT referral_code FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        referral_code = user_data['referral_code'] if user_data else ''

        # LEFT JOIN query ensures all referred accounts appear on the dashboard 
        # regardless of whether a deposit/commission has occurred[cite: 1]
        cur.execute(
            """
            SELECT 
                u.email AS referred_email,
                u.created_at AS registration_date,
                COALESCE(r.status, 'pending') AS status,
                COALESCE(r.commission_earned, 0.00) AS commission_earned
            FROM users u
            LEFT JOIN referrals r ON r.referred_id = u.id AND r.referrer_id = %s
            WHERE r.referrer_id = %s OR u.id IN (
                SELECT referred_id FROM referrals WHERE referrer_id = %s
            );
            """,
            (user_id, user_id, user_id)
        )
        referrals = cur.fetchall()

        # Calculate totals
        total_referrals = len(referrals)
        total_earnings = sum(float(ref['commission_earned']) for ref in referrals)

        return jsonify({
            'status': 'success',
            'referral_code': referral_code,
            'stats': {
                'total_referrals': total_referrals,
                'total_earnings': total_earnings
            },
            'referrals': referrals
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# --- PAGE ROUTE HANDLERS ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
