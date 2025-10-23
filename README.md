# SmartSave Backend

---

## App Setup Guide

### Requirements

- **Python 3.9+**
- **Docker** installed and running
- **PostgreSQL** installed (client, CLI, and pgAdmin recommended)

### Setup Steps

1. **Clone the repository**

```bash
git clone https://github.com/heisdanielade/api-savings-app.git
cd api-savings-app

```

2. **Create and activate a virtual environment**

```bash
python -m venv venv
venv\Scripts\activate        # On Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

- Copy `.env.example` -> `.env`
- Fill in the required values provided privately by the project manager ([@heisdanielade](https://github.com/heisdanielade))

5. **Run the app**

```bash
docker-compose up --build
```

Verify app is running by hitting **_http://localhost:3195_**
