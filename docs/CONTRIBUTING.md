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
git rebase main
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
- Keep consistent naming ( `snake_case` for Python)
- Avoid pushing unnecessary files; ensure `.gitignore` is up-to-date.

## Environment Setup

- Use the provided `.env.example` example to create your `.env` file
- Don't commit `.env` or any secrets
- If you add new environment variables, **update** `.env.example` and notify the team
- Run formatters/linters before commiting:

```bash
black .
```

## Communication

- Use GitHub issues for bugs, ideas, or tasks.
- Discuss major design changes before implementation.
- Keep commit history clean; rebase and squash where needed.
