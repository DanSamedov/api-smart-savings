## App Setup Guide

### Requirements

- **Python 3.9+**
- **Docker** (installed & running)
- **PostgreSQL** (client, CLI, pgAdmin recommended)
- **Make** (for running Makefile commands)

---

### Setup Steps

1. **Clone the Repository**

```bash
   git clone https://github.com/heisdanielade/api-smart-savings.git
   cd api-smart-savings
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure Environment Variables**

- Copy `.env.example` → `.env` (created by you)
- Create a PostgreSQL database (e.g., `smartsave`)
- Update `.env` with your **database credentials**
- Set one or more test emails under:

```bash
TEST_EMAIL_ACCOUNTS=email1@example.com,email2@example.com
```

- These accounts are used by a **startup script** that seeds test data (e.g., test user accounts).
- Update other values as provided privately by the project manager: ([@heisdanielade](https://github.com/heisdanielade))

4. **Run App Commands**

```bash
make build      # Start app using Docker
make down       # Stop app
make tests      # Run tests
```

More helpful commands are provided in `Makefile` in the project's root directory.

5. **Verification**
   Once the app starts, verify it’s running by visiting:
   **_http://localhost:3195_**
