# Authentication System

The SmartSave Authentication System is designed with security, reliability, and user experience at its core. It follows industry standards to ensure that user data is protected while providing a seamless onboarding and login process.

## Overview

SmartSave uses a combination of **Email-based OTP (One-Time Password)** for verification and **JWT (JSON Web Tokens)** for stateless session management.

---

## Features

### 1. Secure Registration & Verification

- **Email Validation**: Users register with a valid email and a strong password.
- **OTP Verification**: Upon registration, a 6-digit secure code is generated and sent to the user's email.
- **Expiration Logic**: Verification codes are time-bound (e.g., 10 minutes) to prevent brute-force attacks.
- **Onboarding**: Only verified users can access the application features, ensuring a high-quality user base.

### 2. JWT-Based Authentication

- **Stateless Sessions**: The system uses JWTs, eliminating the need for server-side session storage and enabling better scalability.
- **Secure Handling**: Tokens are issued upon successful login and must be included in the `Authorization: Bearer <token>` header for all protected requests.
- **Token Versioning**: Implements a `token_version` on the User model. This allows for immediate **global logout** by incrementing the version, which invalidates all previously issued tokens for that user.

### 3. Account Security & Protection

- **Password Hashing**: Passwords are never stored in plain text. We use robust hashing algorithms (SHA256) via `hashlib`, `bcrypt` and `Passlib`.
- **Failed Login Protection**: To prevent brute-force attacks, the system tracks failed login attempts.
- **Account Locking**: If a user exceeds the maximum allowed failed attempts (e.g., 5), the account is automatically locked, and the user is notified via email with instructions for unlocking (usually through a password reset).
- **Login Notifications**: Users receive an email alert whenever a new login is detected, including the IP address and approximate location.

### 4. Password Recovery

- **Safe Reset Flow**: Users can request a password reset if they forget their credentials.
- **Signed Tokens**: A secure, short-lived signed token is emailed to the user, ensuring that only the owner of the email account can reset the password.

---

## Technical Flow

### Registration Flow

1. `POST /v1/auth/register` → Validate input → Create `User` (unverified) → Generate OTP → Send Email.
2. `POST /v1/auth/verify-email` → Validate OTP → Mark User as `verified` → Create initial `Wallet`.

### Login Flow

1. `POST /v1/auth/login` → Verify credentials → Check if account is locked/verified.
2. If successful: Issues JWT → Updates `last_login_at` → Sends Login Notification.
3. If failed: Increments `failed_login_attempts` → Locks account if threshold reached.

---

## Security Best Practices Implemented

- **Input Sanitization**: All inputs are validated using Pydantic schemas.
- **CORS Protection**: Restricted to trusted domains.
- **Secure Headers**: The API uses standard security headers to protect against common web vulnerabilities.
- **Log Anonymization**: Sensitive data like IPs are hashed in logs to comply with GDPR.

---

## Scope Summary

This system demonstrates a deep understanding of:

- **Backend Security**: Handling sensitive credentials and preventing common attacks (Brute-force, Session Hijacking).
- **Scalable Architecture**: Using JWTs and stateless authentication.
- **User Experience**: Providing clear feedback and proactive security notifications.
