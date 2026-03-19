# ⬡ FraudShield — AI Financial Fraud Detection System

A full-stack AI-powered fraud detection system built using **Machine Learning, Flask APIs, MySQL database, and an interactive frontend dashboard**.

---

## 📁 Project Structure

```
fraud_detection/
├── ml/
│   └── train_model.py        ← Train the ML model
├── backend/
│   ├── app.py                ← Flask REST API
│   ├── setup_db.sql          ← MySQL schema
│   ├── fraud_model.pkl       ← Trained model
│   └── scaler.pkl            ← Feature scaler
├── frontend/
│   └── index.html            ← Web UI
├── requirements.txt
└── README.md
```

---

## 🚀 Setup Instructions

### STEP 1 — Install dependencies

```bash
pip install -r requirements.txt
```

---

### STEP 2 — Setup MySQL database

```bash
mysql -u root -p < backend/setup_db.sql
```

Creates:

- Database: `fraud_detection`
- Tables: `users`, `transactions`, `audit_log`

Default login:

```
username: admin
password: admin123
```

---

### STEP 3 — Configure database

Edit `backend/app.py`:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "fraud_detection"
}
```

---

### STEP 4 — Train ML Model

```bash
cd ml
python train_model.py
```

Generates:

- `fraud_model.pkl`
- `scaler.pkl`

---

### STEP 5 — Run Backend

```bash
cd backend
python app.py
```

Runs at:

```
http://localhost:5000
```

---

### STEP 6 — Open Frontend

Open `frontend/index.html` in your browser.

---

## 🔌 API Endpoints

| Method | Endpoint            | Auth | Description          |
|--------|---------------------|------|----------------------|
| POST   | `/api/register`     | No   | Register user        |
| POST   | `/api/login`        | No   | Login (returns JWT)  |
| POST   | `/api/predict`      | Yes  | Fraud prediction     |
| GET    | `/api/transactions` | Yes  | Transaction history  |
| GET    | `/api/stats`        | Yes  | Dashboard stats      |
| GET    | `/api/health`       | No   | API health check     |

---

## 🧠 Machine Learning Model

### Features Used

| Feature                 | Description               |
|-------------------------|---------------------------|
| `amount`                | Transaction amount        |
| `hour_of_day`           | Time (0–23 format)        |
| `merchant_category`     | Category code (0–9)       |
| `transaction_count_24h` | Frequency of transactions |
| `distance_from_home_km` | Location deviation        |
| `is_online`             | 1 = online, 0 = in-person |

### Model Details

- **Algorithm:** Random Forest (100 trees)
- **Scaling:** StandardScaler
- **Imbalance Handling:** SMOTE (only on training data)
- **Dataset:** Synthetic with realistic fraud patterns
- **Accuracy:** ~92–96%

> ⚠️ **Note on Dataset:** The model is trained on a **synthetic dataset** designed to simulate real-world fraud behavior. It includes noise and overlapping distributions to avoid unrealistic perfect accuracy and ensure better generalization.

---

## 🔄 System Architecture

```
User Input (Frontend)
        ↓
Flask API (/predict)
        ↓
Feature Mapping
        ↓
StandardScaler
        ↓
Random Forest Model
        ↓
Prediction + Probability
        ↓
Stored in MySQL + Sent to UI
```

---

## 🔐 Security Features

- JWT Authentication (8-hour expiry)
- Automatic logout on token expiry
- bcrypt password hashing
- Role-based access control
- Input validation on all endpoints

---

## 🎯 Key Highlights

- Full-stack integration (Frontend + Backend + ML)
- Real-time fraud prediction system
- Clean and interactive dashboard UI
- Proper ML practices (no data leakage)
- Risk scoring system (LOW / MEDIUM / HIGH)
- Token-based secure authentication

---

## 📊 Sample Use Cases

### ✅ Legitimate Transaction

```
Amount: 450
Hour: 14
Transactions: 2
Distance: 3
→ Prediction: SAFE
```

### 🚨 Fraudulent Transaction

```
Amount: 25000
Hour: 2
Transactions: 20
Distance: 800
→ Prediction: FRAUD
```

---


---

## 🚀 Future Enhancements

- Real-world dataset integration
- Explainable AI (SHAP)
- Live fraud alerts
- Cloud deployment (AWS / Render)

---

## 👨‍💻 Developer

**Nagabhooshan**
F-ull Stack Developer · ML Engineer
