"""
AI-Based Financial Fraud Detection System
Flask Backend API
Run: python app.py
API runs on: http://localhost:5000
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
from functools import wraps
from dotenv import load_dotenv
import os

load_dotenv()
# ─────────────────────────────────────────────────────────────
# App Configuration
# ─────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="../frontend")
CORS(app)

SECRET_KEY = os.environ.get("JWT_SECRET", "fraud_detect_secret_2024")

# MySQL Config — update with your credentials
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT"))
}
# Feature columns — must match training order
FEATURES = ["amount", "hour_of_day", "merchant_category",
            "transaction_count_24h", "distance_from_home_km", "is_online"]

# ─────────────────────────────────────────────────────────────
# Load ML Model
# ─────────────────────────────────────────────────────────────
try:
    model = joblib.load("fraud_model.pkl")
    scaler = joblib.load("scaler.pkl")
    print("✅ ML model loaded successfully")
except FileNotFoundError:
    print("⚠️  Model not found. Run ml/train_model.py first!")
    model, scaler = None, None

# ─────────────────────────────────────────────────────────────
# Database Helper
# ─────────────────────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(**DB_CONFIG)

# ─────────────────────────────────────────────────────────────
# JWT Auth Decorator
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
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────────────────────────
# ROUTE: Serve Frontend
# ─────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")

# ─────────────────────────────────────────────────────────────
# ROUTE: Register
# ─────────────────────────────────────────────────────────────
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username", "").strip()
    email    = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "All fields required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed)
        )
        db.commit()
        cursor.close(); db.close()
        return jsonify({"message": "Registration successful"}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Username or email already exists"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────────────────────
# ROUTE: Login
# ─────────────────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():
    data     = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    try:
        db = get_db(); cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close(); db.close()

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        # Safe bcrypt check — handles plain text passwords too
        try:
            ok = bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8"))
        except Exception:
            ok = (password == user["password"])
            if ok:
                # Auto-upgrade plain text to bcrypt
                new_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
                db2 = get_db(); cur2 = db2.cursor()
                cur2.execute("UPDATE users SET password=%s WHERE username=%s", (new_hash, username))
                db2.commit(); cur2.close(); db2.close()

        if not ok:
            return jsonify({"error": "Invalid credentials"}), 401

        token = jwt.encode({
            "user_id":  user["id"],
            "username": user["username"],
            "role":     user["role"],
            "exp":      datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({
            "token":    token,
            "username": user["username"],
            "role":     user["role"],
            "message":  "Login successful"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
