# 💰 SmartSave - EU/Poland GDPR-Compliant Smart Savings App  

![API Version](https://img.shields.io/badge/API%20version-v1.0.0-blue.svg)
[![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![Pydantic](https://img.shields.io/badge/Pydantic-E92063?logo=Pydantic&logoColor=white)](#) 
[![Pytest](https://img.shields.io/badge/Pytest-fff?logo=pytest&logoColor=000)](#)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff)](#)
[![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?logo=postgresql&logoColor=white)](#)
[![Redis](https://img.shields.io/badge/Redis-%23DD0031.svg?logo=redis&logoColor=white)](#)
[![Bash](https://img.shields.io/badge/Bash-4EAA25?logo=gnubash&logoColor=fff)](#)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)](#)

## Overview
**SmartSave** is a GDPR-compliant smart savings application designed for users in the EU, focusing on transparency, collaboration, and security.  
It combines traditional savings with AI-powered financial insights via the **SaveBuddy AI assistant**, allowing users to manage personal and group savings easily, while keeping their data private and secure.  

## Contributors

| Developer | GitHub Username | Responsibilities |
|------------|-----------------|------------------|
| Daniel Adediran | [@heisdanielade](https://github.com/heisdanielade) | Core backend & DevOps — repo management, authentication, user profiles, wallets, group savings, GDPR, notifications, and CI/CD |
| Danylo Samedov | [@DanSamedov](https://github.com/DanSamedov) | Core backend — authentication, user profile, wallets, transactions, group savings, tests, and SaveBuddy AI |
| Artem Ruzhevych | [@ArtemRuzhevych](https://github.com/ArtemRuzhevych) | AI & Backend integrations — SaveBuddy AI, notifications, GDPR, SaveBuddy AI, and testing |

## Table of Contents
  
1. [Features](#features)  
2. [Architecture](#architecture)  
3. [Authentication & Authorization](#authentication--authorization)  
4. [GDPR Compliance](#gdpr-compliance)  
5. [Core Savings](#core-savings)  
6. [Technologies & Design Decisions](#technologies--design-decisions)  
7. [Screenshots](#screenshots)  
8. [Future Improvements](#future-improvements)  
9. [Closing Note](#closing-note)

---

## Features

- Individual and group savings management  
- AI savings assistant (**SaveBuddy**) for automation, requires user consent  
- GDPR-compliant data handling and user privacy management  
- Email-based OTP verification and secure login (JWT & OAuth) 
- Detailed requests logging with hashed IPs  
- Rate limiting, and background email notifications  
- CI/CD integration for automated deployments  
- Redis caching and PostgreSQL indexing for performance  
- Modular and scalable monorepo architecture  

---

## Architecture

### Monorepo & Modular Design
SmartSave uses a **modular architecture** within a **monorepo** setup.  
Each feature lives in its own module under the `modules/` directory, designed for separation of concerns and ease of scaling.

**Modules:**
- `auth` — authentication and authorization logic  
- `gdpr` — GDPR compliance and user data management  
- `user` — user profile and preferences  
- `wallet` — wallet creation and balance management  
- `savings` — individual and group savings  
- `notifications` — email-based user notifications  
- `shared` — reusable schemas and utilities

Each module contains:
```yaml
  repository.py # Database access layer
  models.py # Database models (except Auth module)
  schemas.py # Pydantic schemas
  service.py # Business logic
  helpers.py # Utility functions (optional)
```

### API & Infrastructure Highlights
- **Versioning:** `/v1/...` URL structure for all endpoints  
- **Docs:** Swagger & ReDoc available at `/v1/docs` (protected with Basic Auth)  
- **Rate Limiting:** `Per-minute/hour` restrictions per IP  
- **Redis:** Used for `caching` and fast data retrieval  
- **Logging:** Structured `JSON logs` per request, with hashed IP addresses  
- **Makefile:** Common commands for Docker, Alembic, and Pytest  
- **Scripts:** Dev and prod startup scripts in `scripts/`  
- **Database:** PostgreSQL + Alembic for `DB migrations`  
- **CI/CD:** GitHub Actions workflows (`ci.yml`, `cd.yml`)  
- **Environment:** `.env.example` provided for configuration variables  

**Backend System Flow:**  
```bash
  Middleware → Router → Service → Repository → Database
```
---

## Authentication & Authorization

1. User registers with **email** and **password**.  
2. A **6-digit OTP** is sent to the user’s email for verification.  
3. Once verified, `user.is_verified` is set to `True`.  
4. On successful login, a **JWT** is issued and used for all authenticated requests.  
5. Failed logins increment `user.failed_login_attempts`; exceeding the limit locks the account.  
6. Locked accounts trigger a **notification email** to the user.  
7. Roles are defined as:
   - **USER:** Full access to own data only  
   - **ADMIN:** Limited create/read access except GDPR/user/wallet data  
   - **SUPER_ADMIN:** Full CRUD access (excluding wallet/transactions modification)  

Wallets and transactions are **immutable** - they cannot be modified or deleted once created.

---

## GDPR Compliance

SmartSave was built around the **three core GDPR principles**:
1. **Right to Access Data**  
2. **Right to Modify Data**  
3. **Right to Delete Data**

### Key Implementations
- IP addresses are stored as **irreversible hashes** in logs.  
- Users can **request a data report**, delivered as a **password-protected PDF** via email.  
- Data modification is allowed through the app or via support requests.  
- Account deletions are **soft-deleted** for 14 days before anonymization.  
- **Anonymization Process:**
  - All PII replaced with random values.
  - User can no longer log in.
  - Maintains referential integrity for financial auditing.
- Logs older than **30 days** are auto-deleted.
- GDPR requests are logged in a dedicated `GDPRRequest` table.  
- After two years, even the anonymized GDPR requests are removed.

---

## Core Savings

### Individual Savings
- Each goal (e.g., *“Buy a bicycle”*) is a single independent saving entry.
- Funds are allocated from the user’s wallet.
- `user.locked_amount` tracks funds currently in use for savings/goals.

### Group Savings
- Groups have **2–7 members** and one or two admins.  
- Each group focuses on **one shared goal**.  
- Contributions and withdrawals appear as **chat-like transactions**.  
- Admins can enable approval for fund withdrawals.  
- Users violating group rules (e.g., unauthorized withdrawals) are **banned** from rejoining for 7 days.  
- Group balances are **derived from members’ wallets** — groups have no separate wallets.  
- Groups trigger automatic notifications for:
  - Added/removed members  
  - Contributions  
  - Target reached (50% or 100%)  

### Wallet System
- Each verified user automatically gets **one wallet**.  
- Wallet fields:
  - `total_balance`
  - `locked_amount`
  - Computed `available_balance = total_balance - locked_amount`  
- Base app currency is **EUR**, but users can select from **4 additional currencies** for frontend display.  
- Exchange rates are fetched from an external API and cached in the DB.

---

## Technologies & Design Decisions

| Technology | Purpose | Design Relation |
|-------------|----------|-----------------|
| **FastAPI** | High-performance backend & auto-generated docs | Enables clear dependency injection and modular design |
| **Pydantic** | Data validation and serialization | Supports DRY and type-safe schema sharing |
| **SQLModel + SQLAlchemy** | ORMs for PostgreSQL | Enforces consistent data access layer (Repository pattern) |
| **Alembic** | Database migrations | Streamlined schema versioning |
| **Slow-api** | Rate-limiting | For security and simplified implementation |
| **Redis** | Caching | Optimizes performance and scalability |
| **Docker** | Containerization | Simplifies setup and deployment |
| **Pytest** | Automated testing | Ensures reliability and regression safety |
| **GitHub Actions** | CI/CD pipeline | Automates testing and deployment |

### Design Principles in Action
- **SOLID:** Dependency Injection in routers promotes modular and testable code.  
- **DRY:** Shared helpers and reusable service methods minimize duplication.  
- **Separation of Concerns:** Clear flow: *Middleware → Router → Service → Repository*.  
- **Extensibility:** Notification service follows the **ABC pattern**, allowing easy integration of SMS or push services in the future.

---

## Screenshots

### API Endpoints (Swagger)
![Swagger Screenshot](docs/images/swagger_endpoints.png)

### Frontend Interface
![Frontend Screenshot 1](docs/images/frontend_home.png)  
![Frontend Screenshot 2](docs/images/frontend_groups.png)

### Email Templates
![Email Template Screenshot 1](docs/images/wallet_notification.png)  
![Email Template Screenshot 2](docs/images/group_notification.png)

---

## Future Improvements

- Introduce **referral system** for user growth.  
- Split modules into **dedicated microservices** for better scalability.  
- Integrate **real banking APIs** for live savings and transactions.  
- Add **SMSNotificationService** and **push notifications**.  
- Expand **SaveBuddy AI** to provide personalized financial recommendations.

---

## Closing Note

SmartSave was initially designed as a final-year project by 3 students from the `University of Zielona Gora - Computer Science & Econometrics` but advanced to a production-grade system. It's not just a financial tool but a **trustworthy digital companion** for responsible saving.  
Built with transparency, collaboration, and user privacy at its core; this project is a foundation for modern, ethical financial technology.

**Thank you for checking out SmartSave! 💚**
