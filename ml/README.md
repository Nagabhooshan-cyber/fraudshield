# ⬡ FraudShield — AI Financial Fraud Detection System

A full-stack AI-powered fraud detection system built using **Machine Learning, Flask REST APIs, Railway MySQL database, Vercel frontend, and Render backend deployment**.

---

# 🚀 Live Architecture

```
Frontend  → Vercel
Backend   → Render
Database  → Railway MySQL
ML Model  → Flask API
```

---

## 📁 Project Structure

```
fraud_detection/
├── ml/
│   └── train_model.py
├── backend/
│   ├── app.py
│   ├── setup_db.sql
│   ├── fraud_model.pkl
│   ├── scaler.pkl
│   └── .env
├── frontend/
│   ├── index.html
│   └── reset.html
├── requirements.txt
└── README.md
```

---

# 🚀 Features

## 🔐 Authentication

- User Registration
- Email OTP Verification
- Remember Me Option
- Forgot Password
- Reset Password via Email
- Account Lock after 5 Failed Attempts
- Auto Unlock after 1 Hour

---

## 🤖 Fraud Detection

- Real-time Fraud Prediction
- ML Model (Random Forest)
- Risk Probability Score
- Fraud Detection Dashboard
- Transaction History

---

## 📊 Dashboard Features

- Total Transactions
- Fraud Count
- Fraud Rate
- Fraud Amount
- Role Based Access

---

# 🚀 Setup Instructions

## STEP 1 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

## STEP 2 — Setup Database

### ▶ Railway MySQL (Recommended)

Run:

```bash
mysql -h <HOST> -u root -p --port <PORT> railway < backend/setup_db.sql
```

---

## STEP 3 — Configure Environment Variables

Create `.env` file inside `backend/`

```env
DB_HOST=your_host
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=railway
DB_PORT=your_port

EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
```

---

## STEP 4 — Train Model

```bash
cd ml
python train_model.py
```

Generates:

- fraud_model.pkl
- scaler.pkl

---

## STEP 5 — Run Backend

```bash
cd backend
python app.py
```

Runs at:

```
http://localhost:5000
```

---

## STEP 6 — Open Frontend

Open:

```
frontend/index.html
```

---

# 🔌 API Endpoints

| Method | Endpoint             | Auth | Description      |
| ------ | -------------------- | ---- | ---------------- |
| POST   | /api/register        | No   | Register user    |
| POST   | /api/verify-otp      | No   | OTP verification |
| POST   | /api/login           | No   | Login            |
| POST   | /api/forgot-password | No   | Send reset email |
| POST   | /api/reset-password  | No   | Reset password   |
| POST   | /api/predict         | Yes  | Fraud prediction |
| GET    | /api/transactions    | Yes  | Transactions     |
| GET    | /api/stats           | Yes  | Dashboard stats  |
| GET    | /api/health          | No   | Health check     |

---

# 🧠 Machine Learning Model

## Features Used

| Feature               | Description         |
| --------------------- | ------------------- |
| amount                | Transaction amount  |
| hour_of_day           | Time of transaction |
| merchant_category     | Category code       |
| transaction_count_24h | Frequency           |
| distance_from_home_km | Location deviation  |
| is_online             | Online transaction  |

---

# Model Details

- Algorithm: Random Forest
- Scaling: StandardScaler
- Imbalance Handling: SMOTE
- Dataset: Synthetic dataset
- Accuracy: ~90–95%

---

# 🔐 Security Features

- JWT Authentication
- bcrypt password hashing
- OTP Email Verification
- Forgot Password Reset
- Account Lock Protection
- Role Based Access Control
- Environment Variable Security

---

# 🚀 Deployment

## Frontend (Netlify)

Deploy:

```
frontend/
```

---

## Backend (Render)

Deploy:

```
backend/
```

---

## Database (Railway)

Railway MySQL Cloud Database

---

# 🎯 Key Highlights

- Full-stack AI Fraud Detection
- Production-level Authentication
- Secure API Design
- Real-time Fraud Prediction
- Clean UI Dashboard
- Cloud Deployment Ready

---

# 📊 Example

## Legitimate

```
Amount: 450
Hour: 14
Distance: 3
Prediction: SAFE
```

## Fraud

```
Amount: 25000
Hour: 2
Distance: 800
Prediction: FRAUD
```

---

# 🚀 Future Improvements

- Real dataset integration
- Explainable AI
- Real-time streaming
- Admin user management
- Multi-factor authentication

---

# 👨‍💻 Developer

**Nagabhooshan Bhat**

AI/ML Engineer
Full Stack Developer

---

