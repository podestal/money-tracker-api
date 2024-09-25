# Money Tracker API

This API is a personal finance management tool that allows users to track their income, expenses, and balances across different categories. Users can create transactions, assign them to categories, and the system will update their balance accordingly. 

## Features

- **User Authentication** (via JWT using Djoser)
- **Create and Manage Categories** for organizing income and expenses
- **Track Balances** for each user
- **Create, Update, Delete Transactions**, affecting user balance
- **Date-based Transaction Queries** (e.g., retrieve transactions for a specific month)

## Models

### Category

Represents a user-defined category to organize transactions. Each user can create their own categories for income or expenses.

| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField | Name of the category (max length 255) |
| `user` | ForeignKey | Foreign key relation to `AUTH_USER_MODEL` |

### Balance

Represents the current balance of a user, automatically updated when a transaction is created, updated, or deleted.

| Field | Type | Description |
|-------|------|-------------|
| `amount` | DecimalField | The current balance of the user (10 digits, 2 decimal places) |
| `user` | ForeignKey | Foreign key relation to `AUTH_USER_MODEL` |

### Transaction

Represents an income or expense transaction for a user, which is linked to a category.

| Field | Type | Description |
|-------|------|-------------|
| `transaction_type` | CharField | Type of transaction (`IN` for income, `OUT` for expenses) |
| `amount` | DecimalField | Amount of the transaction |
| `created_at` | DateField | Date the transaction was created |
| `updated_at` | DateTimeField | Date and time the transaction was last updated |
| `description` | TextField | Optional description for the transaction |
| `user` | ForeignKey | Foreign key relation to `AUTH_USER_MODEL` |
| `category` | ForeignKey | Foreign key relation to `Category` |

## Serializers

### CategorySerializer

Serializes `Category` model, allowing users to create and retrieve categories.

- **Fields**: `id`, `name`

### BalanceSerializer

Serializes `Balance` model, allowing users to retrieve their current balance.

- **Fields**: `id`, `amount`

### TransactionSerializer

Serializes `Transaction` model, allowing users to create and retrieve transactions.

- **Fields**: `id`, `transaction_type`, `amount`, `created_at`, `updated_at`, `description`, `category`

## Views

### CategoryViewSet

Handles CRUD operations for user-defined categories.

- **Authentication**: Users must be authenticated.
- **Permissions**: Only the authenticated user or superuser can access categories.

### BalanceViewSet

Handles balance retrieval for users.

- **Authentication**: Users must be authenticated.
- **Permissions**: Only the authenticated user can access their balance.

#### Custom Actions

- `GET /balance/me/` - Retrieve or create the current balance for the authenticated user.

### TransactionViewSet

Handles CRUD operations for transactions and updates the user's balance automatically.

- **Authentication**: Users must be authenticated.
- **Permissions**: Only the authenticated user or superuser can access transactions.

#### Query Parameters

- **`created_at`**: Filter transactions by the created date (in `YYYY-MM-DD` format) and retrieve transactions for a specific month.

## Endpoints

- **`/api/categories/`**: Category CRUD operations.
- **`/api/balances/`**: Retrieve or update balances.
- **`/api/balances/me/`**: Retrieve the current user’s balance.
- **`/api/transactions/`**: Transaction CRUD operations.

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/moneytracker.git
   cd moneytracker
