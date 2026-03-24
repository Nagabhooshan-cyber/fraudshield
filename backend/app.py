"""
FraudShield - AI Fraud Detection System
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import numpy as np
import mysql.connector
import bcrypt
import jwt
import os
import datetime
import random
import smtplib

from email.mime.text import MIMEText
from functools import wraps
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()
print("EMAIL:", os.getenv("EMAIL_USER"))

# ─────────────────────────────────────────────────────────────
# App Configuration
# ─────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="../frontend")
CORS(app)

SECRET_KEY = os.environ.get("JWT_SECRET", "fraud_detect_secret_2024")

# Database Config
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT"))
}

FEATURES = [
    "amount",
    "hour_of_day",
    "merchant_category",
    "transaction_count_24h",
    "distance_from_home_km",
    "is_online"
]

# ─────────────────────────────────────────────────────────────
# Load ML Model
# ─────────────────────────────────────────────────────────────
try:
    model = joblib.load("fraud_model.pkl")
    scaler = joblib.load("scaler.pkl")
    print("✅ Model Loaded")
except:
    model, scaler = None, None

# ─────────────────────────────────────────────────────────────
# Database Helper
# ─────────────────────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(**DB_CONFIG)

# ─────────────────────────────────────────────────────────────
# Email Sender
# ─────────────────────────────────────────────────────────────
import smtplib
from email.mime.text import MIMEText
import os

def send_email(to_email, subject, body):

    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    print("Sending OTP to:", to_email)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp-relay.brevo.com", 587, timeout=10)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, to_email, msg.as_string())
        server.quit()

        print("Email sent successfully")

    except Exception as e:
        print("Email error:", e)
# ─────────────────────────────────────────────────────────────
# JWT Decorator
# ─────────────────────────────────────────────────────────────
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not token:
            return jsonify({"error": "Token required"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = payload

        except:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated

# ─────────────────────────────────────────────────────────────
# Serve Frontend
# ─────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")

# ─────────────────────────────────────────────────────────────
# Register + OTP
# ─────────────────────────────────────────────────────────────
# Temporary storage
TEMP_USERS = {}

TEMP_USERS = {}

@app.route("/api/register", methods=["POST"])
def register():

    data = request.json

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    otp = str(random.randint(100000,999999))

    print("Sending OTP:", otp)

    TEMP_USERS[email] = {
        "username": username,
        "password": password,
        "otp": otp
    }

    send_email(
        email,
        "FraudShield OTP",
        f"Your OTP is {otp}"
    )

    return jsonify({"message":"OTP sent"})
# ─────────────────────────────────────────────────────────────
# Verify OTP
# ─────────────────────────────────────────────────────────────
@app.route("/api/verify-otp", methods=["POST"])
def verify_otp():

    data = request.json

    email = data.get("email")
    otp = data.get("otp")

    temp = TEMP_USERS.get(email)

    if not temp:
        return jsonify({"error":"Session expired"})

    if temp["otp"] != otp:
        return jsonify({"error":"Invalid OTP"})

    username = temp["username"]
    password = temp["password"]

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    db = get_db()
    cursor = db.cursor()

    # check duplicate
    cursor.execute(
        "SELECT * FROM users WHERE username=%s OR email=%s",
        (username, email)
    )

    existing = cursor.fetchone()

    if existing:
        return jsonify({"error":"User already exists"})

    cursor.execute("""
    INSERT INTO users (username,email,password)
    VALUES (%s,%s,%s)
    """,(username,email,hashed))

    db.commit()

    # remove temp user
    TEMP_USERS.pop(email, None)

    return jsonify({"message":"Account created"})
# ─────────────────────────────────────────────────────────────
# Login with Lock
# ─────────────────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():

    data = request.json
    username = data.get("username")
    password = data.get("password")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "Invalid credentials"})

    # lock check
    if user["lock_time"]:
        unlock = user["lock_time"] + timedelta(hours=1)
        if datetime.datetime.utcnow() < unlock:
            return jsonify({"error": "Account locked for 1 hour"})

    # password check
    if not bcrypt.checkpw(password.encode(), user["password"].encode()):

        attempts = user["failed_attempts"] + 1

        if attempts >= 5:
            cursor.execute("""
            UPDATE users 
            SET failed_attempts=%s, lock_time=%s 
            WHERE username=%s
            """, (attempts, datetime.datetime.utcnow(), username))
        else:
            cursor.execute("""
            UPDATE users 
            SET failed_attempts=%s 
            WHERE username=%s
            """, (attempts, username))

        db.commit()

        return jsonify({"error": "Invalid credentials"})

    cursor.execute("""
    UPDATE users 
    SET failed_attempts=0, lock_time=NULL
    WHERE username=%s
    """, (username,))

    db.commit()

    token = jwt.encode({
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "exp": datetime.datetime.utcnow() + timedelta(hours=8)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "token": token,
        "username": user["username"],
        "role": user["role"]
    })

# ─────────────────────────────────────────────────────────────
# Forgot Password
# ─────────────────────────────────────────────────────────────
@app.route("/api/forgot-password", methods=["POST"])
def forgot_password():

    data = request.json
    email = data.get("email")

    token = jwt.encode({
        "email": email,
        "exp": datetime.datetime.utcnow() + timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")

    reset_link = f"{request.host_url}reset.html?token={token}"

    send_email(
        email,
        "FraudShield Reset Password",
        f"Reset password: {reset_link}"
    )

    return jsonify({"message": "Reset link sent"})
#------------------------------------------------------------
# Serve Reset Password Page
#------------------------------------------------------------
@app.route("/reset.html")
def reset_page():
    return send_from_directory("../frontend", "reset.html")

# ─────────────────────────────────────────────────────────────
# Reset Password
# ─────────────────────────────────────────────────────────────
@app.route("/api/reset-password", methods=["POST"])
def reset_password():

    data = request.json

    token = data.get("token")
    password = data.get("password")

    decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = decoded["email"]

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    UPDATE users 
    SET password=%s 
    WHERE email=%s
    """, (hashed, email))

    db.commit()

    return jsonify({"message": "Password reset successful"})

# ─────────────────────────────────────────────────────────────
# ROUTE: Predict Fraud (Main ML endpoint)
# ─────────────────────────────────────────────────────────────
@app.route("/api/predict", methods=["POST"])
@token_required
def predict():
    if model is None:
        return jsonify({"error": "ML model not loaded. Run train_model.py first."}), 503

    data = request.json

    # Validate input
    required = FEATURES + ["merchant_name", "card_last4", "location"]
    for field in FEATURES:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        features = [float(data[f]) for f in FEATURES]
        features_scaled = scaler.transform([features])

        prediction      = int(model.predict(features_scaled)[0])
        probability     = float(model.predict_proba(features_scaled)[0][1])
        risk_level      = "HIGH" if probability > 0.7 else ("MEDIUM" if probability > 0.4 else "LOW")

        # Save to MySQL
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO transactions
            (user_id, amount, hour_of_day, merchant_category, transaction_count_24h,
             distance_from_home_km, is_online, merchant_name, card_last4, location,
             is_fraud, fraud_probability, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            request.user["user_id"],
            features[0], int(features[1]), int(features[2]),
            int(features[3]), features[4], int(features[5]),
            data.get("merchant_name", "Unknown"),
            data.get("card_last4", "****"),
            data.get("location", "Unknown"),
            prediction, probability,
            "flagged" if prediction == 1 else "cleared"
        ))
        db.commit()
        transaction_id = cursor.lastrowid
        cursor.close(); db.close()

        return jsonify({
            "transaction_id": transaction_id,
            "is_fraud":       prediction,
            "probability":    round(probability * 100, 2),
            "risk_level":     risk_level,
            "message":        "⚠️ FRAUD DETECTED" if prediction else "✅ Transaction is Legitimate"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────────────────────
# ROUTE: Transaction History
# ─────────────────────────────────────────────────────────────
@app.route("/api/transactions", methods=["GET"])
@token_required
def get_transactions():
    try:
        limit = int(request.args.get("limit", 50))
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Admins see all; others see their own
        if request.user["role"] == "admin":
            cursor.execute(
                "SELECT * FROM transactions ORDER BY created_at DESC LIMIT %s", (limit,)
            )
        else:
            cursor.execute(
                "SELECT * FROM transactions WHERE user_id=%s ORDER BY created_at DESC LIMIT %s",
                (request.user["user_id"], limit)
            )

        rows = cursor.fetchall()
        cursor.close(); db.close()

        # Convert datetime to string
        for row in rows:
            if row.get("created_at"):
                row["created_at"] = str(row["created_at"])

        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────────────────────
# ROUTE: Dashboard Stats
# ─────────────────────────────────────────────────────────────
@app.route("/api/stats")
def get_stats():
    try:
        token = request.headers.get("Authorization").split(" ")[1]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        user_id = decoded["user_id"]
        role = decoded["role"]

        db = get_db()
        cursor = db.cursor(dictionary=True)

        if role == "admin":
            # ✅ ALL DATA
            cursor.execute("SELECT COUNT(*) AS total FROM transactions")
            total = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS fraud_count FROM transactions WHERE is_fraud = 1")
            fraud = cursor.fetchone()["fraud_count"]

            cursor.execute("SELECT SUM(amount) AS fraud_amount FROM transactions WHERE is_fraud = 1")
            fraud_amount = cursor.fetchone()["fraud_amount"] or 0

        else:
            # ✅ USER-SPECIFIC DATA
            cursor.execute("SELECT COUNT(*) AS total FROM transactions WHERE user_id = %s", (user_id,))
            total = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS fraud_count FROM transactions WHERE is_fraud = 1 AND user_id = %s", (user_id,))
            fraud = cursor.fetchone()["fraud_count"]

            cursor.execute("SELECT SUM(amount) AS fraud_amount FROM transactions WHERE is_fraud = 1 AND user_id = %s", (user_id,))
            fraud_amount = cursor.fetchone()["fraud_amount"] or 0

        fraud_rate = (fraud / total * 100) if total > 0 else 0

        return jsonify({
            "total": total,
            "fraud_count": fraud,
            "fraud_rate": round(fraud_rate, 2),
            "fraud_amount": fraud_amount
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ─────────────────────────────────────────────────────────────
# ROUTE: Health Check
# ─────────────────────────────────────────────────────────────
@app.route("/api/health")
def health():
    return jsonify({
        "status": "online",
        "model_loaded": model is not None,
        "version": "1.0.0"
    })

# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Fraud Detection API starting on http://localhost:5000")
    app.run(debug=False, host="0.0.0.0", port=5000)
