# Core Savings & Wallet System

SmartSave provides a flexible and secure ecosystem for managing both individual financial goals and collaborative group savings.

## Overview

The system is built on a foundation of **Wallet-based transactions**. Every user has a virtual wallet that tracks their balances and serves as the source of funds for all savings activities.

---

## Individual Savings

Individual savings goals enable users to set aside funds for specific purposes (e.g., "Holiday Fund", "New Car").

- **Independent Entries**: Each goal is tracked separately with its own target and progress.
- **Fund Locking**: When funds are allocated to a goal, they are moved to a `locked_amount` state in the user's wallet. This prevents the same funds from being spent or double-counted.
- **Progress Tracking**: Real-time updates on how close the user is to their target.

---

## Group Savings (Squads)

"Squads" allow 2–7 members to save together towards a shared objective.

### Key Features

- **Shared Goals**: One common target for the entire group.
- **Collaborative Flow**: Contributions and withdrawals appear in a real-time, chat-like transaction history.
- **Admin Governance**: Groups can have up to two admins who manage membership and can enforce withdrawal approvals.
- **Dynamic Balances**: Group balances are **derived** from the contributions of its members' individual wallets. The group itself does not hold a separate bank account, ensuring transparency and linkability to user wallets.

### Rule Enforcement

- **Anti-Abuse Logic**: Users who violate group trust (e.g., unauthorized withdrawals or disruptive behavior) can be banned by admins for 7 days.
- **Milestone Notifications**: Automated alerts are sent when the group reaches 50% and 100% of its target.

---

## The Wallet System

The wallet is the central hub for all financial data in SmartSave.

### Balance Types

- **Total Balance**: The absolute sum of all funds associated with the account.
- **Locked Amount**: Funds currently committed to individual or group saving goals.
- **Available Balance**: The spending power of the user (`Total - Locked`).

### Multi-Currency Support

While the base system operates in **EUR**, users can view their balances in several major currencies (USD, PLN, GBP). Exchange rates are fetched from external financial APIs and cached for efficiency.

---

## Scope Summary

This system demonstrates:

- **Complex Data Modeling**: Managing relationships between wallets, goals, and multi-tenant groups.
- **Concurrency & Integrity**: Ensure that fund locking and unlocking are atomic operations.
- **Social Engineering**: Implementing governance and reputation systems (bans, approvals) for collaborative features.
