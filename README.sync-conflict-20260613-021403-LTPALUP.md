# 🛒 Mini Shop DB

<p align="left">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E" alt="Vite" />
</p>

Современное веб-приложение для управления небольшим магазином. Проект состоит из быстрого API на **FastAPI** и современного интерфейса на **React (Vite)**.

## 🚀 Быстрый старт

### 1 Запуск Backend (FastAPI)
Убедитесь, что у вас установлен Python 3.12+ и настроены переменные окружения.

```bash
# Запуск сервера
uvicorn app.routes.app:app --reload
```

API будет доступно по адресу: http://localhost:8000

### 2 Запуск Frontend (React + Vite)

Убедитесь, что у вас установлен Node.js.

cd frontend
npm install
npm run dev

Интерфейс будет доступен по адресу: http://localhost:5173

## 🛠️ Стек технологий

• Backend: Python 3.12, FastAPI, SQLAlchemy, Alembic, AsyncPG, JWT-авторизация
• Frontend: React 19, Vite, React Router DOM
• База данных: PostgreSQL
• Менеджер пакетов: uv (backend) / npm (frontend)
