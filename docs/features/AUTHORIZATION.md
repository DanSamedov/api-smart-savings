# Authorization & Role-Based Access Control (RBAC)

SmartSave implements a robust **Role-Based Access Control (RBAC)** system to ensure that users have exactly the permissions they need—and nothing more. This follows the **Principle of Least Privilege (PoLP)**.

---

## User Roles

The system defines three primary roles, each with increasing levels of authority:

### 1. `USER`

- **Scope**: Personal data and authorized group data.
- **Permissions**:
  - Manage personal profile and wallet.
  - Create and participate in individual and group savings.
  - Request personal GDPR data reports.
  - Delete own account.

### 2. `ADMIN`

- **Scope**: System monitoring and basic management.
- **Permissions**:
  - View non-sensitive application metrics (transaction counts, total users).
  - List all users in the system (basic details only).
  - View group details for auditing purposes.
- **Restrictions**: Cannot view or modify user wallet balances, private transactions, or GDPR sensitive data.

### 3. `SUPER_ADMIN`

- **Scope**: Full system administration.
- **Permissions**:
  - **All ADMIN permissions**.
  - Update user roles (e.g., promoting a USER to ADMIN).
  - Enable/Disable user accounts.
  - Manage system-wide configurations.
- **Restrictions**: Even Super Admins **cannot modify or delete** finalized financial transactions or direct wallet balances, ensuring financial integrity and auditability.

---

## Implementation Details

### 1. Dependency Injection (FastAPI)

Authorization is enforced using FastAPI's `Depends` mechanism. Custom dependencies like `get_current_admin_user` or `get_current_super_admin_user` are used as guards on sensitive endpoints.

```python
@router.get("/app-metrics")
async def get_app_metrics(
    service: RBACService = Depends(get_rbac_service),
    _: User = Depends(get_current_admin_user) # Authorization Guard
):
    ...
```

### 2. Data Immutability

A key security feature of SmartSave is the **immutability of financial data**:

- **Wallets**: Once created, a wallet cannot be deleted by any user or administrator through the standard API.
- **Transactions**: Transactions are "append-only". Once a transaction (deposit, withdrawal, contribution) is completed, it cannot be modified or deleted. This ensures a reliable audit trail.

### 3. Group Ownership & Permissions

Within the **Savings Groups** feature:

- **Group Admin**: Can manage members (add/remove), update group goals, and approve withdrawals.
- **Group Member**: Can contribute funds and view group progress.
- Members who violate group rules are subject to a **7-day ban** from rejoining, enforced at the service layer.

---

## Financial Integrity

Permissions are structured to prevent "Insider Threats":

- No endpoint allows for the arbitrary modification of a user's wallet balance.
- All balance changes must be backed by a verified transaction record.

---

## Scope Summary

This system demonstrates:

- **Granular Control**: Fine-tuned permissions that balance user privacy with administrative needs.
- **Defensive Programming**: Protecting critical financial data through immutability and strict role checks.
- **Code Maintainability**: Using reusable FastAPI dependencies for clean, declarative authorization logic.
