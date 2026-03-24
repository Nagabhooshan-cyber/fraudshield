-- =====================================================
-- FraudShield - AI Fraud Detection System Database
-- =====================================================

DROP DATABASE IF EXISTS fraud_detection;
CREATE DATABASE fraud_detection;
USE fraud_detection;

-- ─────────────────────────────────────────────────────
-- Users Table (Authentication + Security Features)
-- ─────────────────────────────────────────────────────
CREATE TABLE users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    email           VARCHAR(100) NOT NULL UNIQUE,
    password        VARCHAR(255) NOT NULL,
    role            ENUM('admin', 'analyst', 'viewer') DEFAULT 'viewer',

    -- Security Features
    otp             VARCHAR(6),
    otp_expiry      DATETIME,
    failed_attempts INT DEFAULT 0,
    lock_time       DATETIME,

    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────
-- Transactions Table
-- ─────────────────────────────────────────────────────
CREATE TABLE transactions (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    user_id                 INT,
    amount                  DECIMAL(12, 2) NOT NULL,
    hour_of_day             INT NOT NULL,
    merchant_category       INT NOT NULL,
    transaction_count_24h   INT NOT NULL,
    distance_from_home_km   FLOAT NOT NULL,
    is_online               TINYINT(1) DEFAULT 0,
    merchant_name           VARCHAR(100),
    card_last4              VARCHAR(4),
    location                VARCHAR(150),
    is_fraud                TINYINT(1),
    fraud_probability       FLOAT,
    status                  ENUM('pending', 'flagged', 'cleared') DEFAULT 'pending',
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ─────────────────────────────────────────────────────
-- Audit Log Table
-- ─────────────────────────────────────────────────────
CREATE TABLE audit_log (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id  INT,
    action          VARCHAR(100),
    performed_by    VARCHAR(50),
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);

-- ─────────────────────────────────────────────────────
-- Default Admin User
-- Username: admin
-- Password: admin123
-- ─────────────────────────────────────────────────────
INSERT INTO users (username, email, password, role)
VALUES (
    'admin',
    'admin@fraudshield.com',
    '$2b$12$KIX8GWKHUlPBpBt/M7L7puR0BQYXG6VL5Nz6OcPu9MODzaR3Ae8Ky',
    'admin'
);

-- ─────────────────────────────────────────────────────
-- Fraud Summary View
-- ─────────────────────────────────────────────────────
CREATE VIEW fraud_summary AS
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS total_transactions,
    SUM(is_fraud) AS fraud_count,
    ROUND(SUM(is_fraud)/COUNT(*)*100, 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN is_fraud=1 THEN amount ELSE 0 END), 2) AS fraud_amount
FROM transactions
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- ─────────────────────────────────────────────────────
-- Verify Setup
-- ─────────────────────────────────────────────────────
SHOW TABLES;
SELECT 'FraudShield Database Ready ✅' AS status;