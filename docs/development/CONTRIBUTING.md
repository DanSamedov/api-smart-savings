# Contributing Guidelines

Please follow these guidelines to keep our development process clean, consistent, and efficient.

## Branching Strategy

- **Never push directly to** `main`
- Each contributor must **create a personal or feature-specific branch** from the latest `main`

- **Branch naming convention**

```bash
feature/<short-description>     -> for new features
fix/<short-description>         -> for bug fixes
```

Examples:

```bash
feature/add-user-auth
fix/email-validation-bug
```

## Syncing with Main

Before you start coding or pushing:

1. **Pull the latest changes** from `main`:

```bash
git checkout main
git pull origin main
```

2. **Rebase your branch** to avoid merge conflicts:

```bash
git checkout <your-branch>
git fetch origin main
git rebase origin/main
```

## Commit Message Style

Use **clear and descriptive** commit messages with the following prefixes:

| Type      | Description                            |
| --------- | -------------------------------------- |
| feat:     | New feature added                      |
| fix:      | Bug fix                                |
| update:   | Improvement or refactor (non-breaking) |
| chore:    | Routine or build-related changes       |
| refactor: | Code overhaul, file modifications      |
| test:     | Adding or modifying tests              |

Examples:

```bash
feat: added JWT authentication middleware
fix: correct database connection string
update: changed reset password endpoint
test: added test for verify email endpoint
```

---

## Caching Guidelines

This section provides guidelines for naming cache keys, TTL, and general caching best practices for our FastAPI app with Redis.

---

### 1. Cache Key Naming

- **Use clear, descriptive keys** that indicate the resource and scope.
- **Use a colon `:` as a separator** for hierarchy and readability.
- **Include unique identifiers** for user-specific or entity-specific data.

#### Recommended Patterns

| Resource                  | Key Pattern                           | Example                              |
|----------------------------|--------------------------------------|--------------------------------------|
| Current authenticated user | `user_current:{email}`                | `user_current:john@example.com`      |
| Wallet transactions        | `wallet_transactions:{user_id}`       | `wallet_transactions:42`             |
| Any other entity           | `{entity}:{id}`                        | `notification:123`                   |
| Lists/collections          | `{entity}_list:{filter}`              | `users_list:active`                  |

**Tips:**

- Always include user ID/email for user-specific data.
- Avoid very long keys; use readable identifiers.

---

### 2. TTL (Time-to-Live)

- Default TTL: `300` seconds (5 minutes) unless otherwise needed.
- Shorter TTL for highly dynamic data.
- Longer TTL for mostly static data.

```python
CACHE_TTL = 300  # Default TTL in seconds
```

## Code Review & Pull Requests

- Always **open a Pull Request (PR)** to merge into `main`
- Assign at least **one reviewer** from the team
- Ensure:
  - The app runs without errors.
  - Tests (if available) pass.
  - No sensitive data (like `.env` values) is committed.
- Use **draft PRs** if your work is still in progress

## Project Structure

- Follow the folder structure conventions already in place.
- Add a comment on the first line of every python file, indicating the directory i.e.,

```bash
# app/modules/auth/service.py
```

- Keep consistent naming ( `snake_case` for Python)
- Avoid pushing unnecessary files; ensure `.gitignore` is up-to-date.

## Environment Setup

- Use the provided `.env.example` example to create your `.env` file
- Don't commit `.env` or any secrets
- If you add new environment variables, **update** `.env.example` and notify the team
- Run formatters/linters before commiting:

```bash
# check formatting
black --check .

# fix formatting
black .

# check import sorting
isort --check-only .

# fix import sorting
isort .
```

OR use the Make commands in `Makefile`:

```bash
# Build Docker containers
make build

# Run tests & code formatting
make all
```

## Communication

- Use GitHub issues for bugs, ideas, or tasks.
- Discuss major design changes before implementation.
- Keep commit history clean; rebase and squash where needed.
