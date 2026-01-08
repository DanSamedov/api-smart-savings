# 🇪🇺 GDPR Compliance & Data Privacy

SmartSave is built with a **Privacy-by-Design** philosophy. We prioritize the protection of our users' personal data and strictly adhere to the General Data Protection Regulation (GDPR).

---

## Core GDPR Principles

The system is architected to support the three fundamental rights of users in the EU:

### 1. Right to Access (Art. 15 GDPR)

Users have full transparency regarding what data is stored about them.

- **Data Export**: Users can request a complete report of their data via the dashboard.
- **Secure Delivery**: The report is generated as a **password-protected PDF** in a background task and sent via email.
- **Snapshot Logic**: The report includes profile details, wallet status, transaction history, and a record of previous GDPR requests.

### 2. Right to Rectification (Art. 16 GDPR)

Users can easily update their personal information (name, currency preferences, password) directly through the application settings.

### 3. Right to Erasure / "Right to be Forgotten" (Art. 17 GDPR)

We provide a clear path for users to delete their accounts while maintaining the financial integrity required for auditing.

- **Soft Deletion**: Accounts are initially marked as `is_deleted`. This allows a "cooling-off" period (default 365 days) where a user can recover their account by logging in.
- **Anonymization**: After the retention period, the system performs an anonymization process:
  - Personally Identifiable Information (PII) like names and emails are replaced with randomized strings.
  - The link between the human user and the wallet is severed, but the transaction history remains for aggregate financial reporting (with no PII attached).

---

## Advanced Privacy Features

### Log Anonymization

To prevent tracking user behavior through server logs, we implement **IP Address Hashing**:

- Real IP addresses are never stored in our logs.
- Instead, we store an **irreversible cryptographic hash** of the IP. This allows us to track unique visitors and detect potential attacks (e.g., rate-limiting) without compromising the user's anonymity according to GDPR standards.

### Data Minimization & Retention

- **Automatic Cleanup**: Logs and temporary data (like GDPR request records) are automatically purged after defined periods (e.g., 30 days for logs, 2 years for GDPR request metadata).
- **Purpose Limitation**: We only collect data essential for the operation of the savings platform.

### Secure AI Processing

The **SaveBuddy AI** assistant only processes user data after explicit **consent** is granted. Users can withdraw this consent at any time, which immediately halts all AI-related data processing for that account.

---

## Technical Implementation

- **Background Workers**: Heavy tasks like PDF generation are handled by background tasks to ensure API responsiveness.
- **Encryption at REST**: Sensitive snapshots and database fields are encrypted to ensure data remains secure even if storage is compromised.
- **Audit Logs**: Every GDPR request is logged in a dedicated table for compliance tracking.

---

## Scope Summary

This demonstrates:

- **Ethical Engineering**: A commitment to user privacy and legal compliance.
- **Complex Data Lifecycles**: Handling the balance between "Right to be Forgotten" and financial data retention requirements.
- **Regulatory Knowledge**: Translating abstract legal requirements (GDPR) into concrete technical features.
