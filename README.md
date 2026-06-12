# 🛒 Mini Shop DB

A lightweight and fast e-commerce backend API built with **FastAPI** and **SQLAlchemy** (Async).

## 🚀 Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (asyncpg)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Package Manager**: [uv](https://github.com/astral-sh/uv)

## 📦 Features

- **Users**: Balance management, profile updates.
- **Products & Categories**: Catalog management, inventory tracking.
- **Cart**: Add/remove items, manage quantities.
- **Orders**: Secure checkout, automatic balance deduction, and inventory synchronization.

## 🛠️ Getting Started

### 1. Installation

Ensure you have `uv` installed, then install the dependencies:

```bash
uv sync
```

### 2. Environment Variables

Create a `.env` file in the root directory and configure your database connection:

```env
DB_URL="postgresql+asyncpg://user:password@localhost:5432/minishop"
```

### 3. Database Migrations

Apply the latest database migrations using Alembic:

```bash
uv run alembic upgrade head
```

### 4. Running the Application

Start the development server:

```bash
uv run fastapi dev app/main.py
```
*The API will be available at `http://127.0.0.1:8000`.*
*Swagger UI documentation will be available at `http://127.0.0.1:8000/docs`.*

## 📂 Project Structure

```text
.
├── alembic/        # Database migrations
├── app/
│   ├── models/     # SQLAlchemy ORM models
│   ├── schemas/    # Pydantic DTOs for validation
│   ├── routes/     # FastAPI endpoints
│   ├── services/   # Business logic layer
│   ├── database.py # DB connection & session
│   └── main.py     # FastAPI application entry point
```

## Start Command 

Back: uvicorn app.routes.app:app --reload
Front: cd frontend && npm run dev