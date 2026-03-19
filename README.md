# ⬡ FraudShield — AI Financial Fraud Detection System
 
A full-stack AI-powered fraud detection system built using **Machine Learning, Flask REST APIs, MySQL database (Railway), and an interactive web dashboard**.
 
---
 
## 📁 Project Structure
 
```
fraud_detection/
├── ml/
│   └── train_model.py        ← Train ML model
├── backend/
│   ├── app.py                ← Flask API
│   ├── setup_db.sql          ← MySQL schema
│   ├── fraud_model.pkl       ← Trained model
│   ├── scaler.pkl            ← Feature scaler
│   └── .env                  ← Environment variables (NOT pushed)
├── frontend/
│   └── index.html            ← UI Dashboard
├── requirements.txt
└── README.md
```
 
---
 
## 🚀 Setup Instructions
 
### STEP 1 — Install Dependencies
 
```bash
pip install -r requirements.txt
```
 
---
 
### STEP 2 — Setup Database (Local or Railway)
 
#### ▶ Option 1: Local MySQL
 
```bash
mysql -u root -p < backend/setup_db.sql
```
 
#### ▶ Option 2: Railway MySQL (Recommended for deployment)
 
Use the Railway connection details and run:
 
```bash
mysql -h <HOST> -u root -p --port <PORT> railway < setup_db.sql
```
 
---
 
### STEP 3 — Configure Environment Variables
 
Create `.env` file inside `backend/`:
 
```env
DB_HOST=your_host
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=railway
DB_PORT=your_port
SECRET_KEY=your_secret_key
```
 
---
 
### STEP 4 — Train ML Model
 
```bash
cd ml
python train_model.py
```
 
Generates:
 
* `fraud_model.pkl`
* `scaler.pkl`
 
---
 
### STEP 5 — Run Backend
 
```bash
cd backend
python app.py
```
 
API runs at:
 
```
http://localhost:5000
```
 
---
 
### STEP 6 — Open Frontend
 
Open:
 
```
frontend/index.html
```
 
Login:
 
```
username: admin
password: admin123
```
 
---
 
## 🔌 API Endpoints
 
| Method | Endpoint            | Auth | Description          |
| ------ | ------------------- | ---- | -------------------- |
| POST   | `/api/register`     | No   | Register user        |
| POST   | `/api/login`        | No   | Login (JWT token)    |
| POST   | `/api/predict`      | Yes  | Fraud prediction     |
| GET    | `/api/transactions` | Yes  | Transaction history  |
| GET    | `/api/stats`        | Yes  | Dashboard statistics |
| GET    | `/api/health`       | No   | API health check     |
 
---
 
## 🧠 Machine Learning Model
 
### Features Used
 
| Feature               | Description               |
| --------------------- | ------------------------- |
| amount                | Transaction amount        |
| hour_of_day           | Time (0–23 format)        |
| merchant_category     | Category code (0–9)       |
| transaction_count_24h | Transaction frequency     |
| distance_from_home_km | Location deviation        |
| is_online             | 1 = online, 0 = in-person |
 
---
 
### Model Details
 
* **Algorithm:** Random Forest Classifier
* **Scaling:** StandardScaler
* **Imbalance Handling:** SMOTE
* **Dataset:** Synthetic dataset with realistic fraud patterns
* **Accuracy:** ~90–95%
 
> ⚠️ Note: Model is trained on synthetic data to simulate fraud scenarios. Accuracy is indicative, not production-grade.
 
---
 
## 🔄 System Architecture
 
```
User Input (Frontend)
        ↓
Flask API (/predict)
        ↓
Feature Extraction
        ↓
StandardScaler
        ↓
Random Forest Model
        ↓
Prediction + Probability
        ↓
Response to UI
```
 
---
 
## 🔐 Security Features
 
* JWT Authentication (8-hour expiry)
* bcrypt password hashing
* Role-Based Access Control (admin / viewer)
* Input validation (frontend + backend)
* Environment variables for DB security
 
---
 
## 🎯 Key Highlights
 
* Full-stack ML system (Frontend + Backend + Model)
* Real-time fraud prediction
* Clean UI with interactive dashboard
* Secure authentication using JWT
* Proper ML pipeline (scaling + prediction)
* Modular and deployable architecture
 
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
 
## 🚀 Future Enhancements
 
* Real dataset integration (Kaggle credit card fraud)
* Explainable AI (SHAP / feature importance)
* Real-time streaming (Kafka)
* Cloud deployment (Render / AWS)
* Admin dashboard for role management
 
---
 
## 👨‍💻 Developer
 
**Nagabhooshan Bhat**
Full Stack Developer · Machine Learning Engineer
 
---