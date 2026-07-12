# MINI SHOP DB

Full-stack e-commerce platform with integrated payment system and comprehensive product management.

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python%203.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-000000?style=flat-square&logo=pytest&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)
![React](https://img.shields.io/badge/React%2019-282C34?style=flat-square&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-black?style=flat-square)

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy 2.0, AsyncPG, Python 3.12 |
| Frontend | React 19, Vite, React Router |
| Database | PostgreSQL with Full Text Search |
| Deployment | Docker, Docker Compose, Nginx |
| Authentication | Google OAuth 2.0, JWT |
| Payments | Yookassa (ЮКасса) |

## Key Features

- OAuth 2.0 authentication with Google integration
- Payment processing with Yookassa
- Full-text search for product catalog
- Shopping cart and order management
- Product media management
- Inventory tracking
- Real-time payment status monitoring

## Quick Start

### Requirements

- Docker 20.10+
- Docker Compose 1.29+
- Git

### Installation

```bash
git clone https://github.com/doaks1638-netizen/MINI-SHOP-DB.git --depth 1
cd MINI-SHOP-DB
```
⬇
```bash
mv .env.example .env
vim .env
```
⬇
```bash
docker compose up -d --build
```

## Project Structure

```
MINI-SHOP-DB/
├── app/                # Backend API
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic validation
│   ├── routes/        # API endpoints
│   ├── services/      # Business logic
│   └── media/         # Media handling
├── frontend/           # React application
├── alembic/           # Database migrations
├── nginx/             # Nginx configuration
└── docker-compose.yml # Container orchestration
```

## For Developers

- After modifying the code, you can run the tests using this command:
- !!! INFO I strongly advise against altering the logic or adding volumes for the test data; instead, use the `-v` flag to avoid errors related to database creation and deletion.

Testing uses the `.env.test` file which is checked into the repository with dummy data.

```bash
sudo docker compose --env-file .env.test -f docker-compose.test.yml up --build --abort-on-container-exit; sudo docker compose -f docker-compose.test.yml down -v
```

- To change the test execution parameters, modify `docker-compose.test.yml` -> `web` -> `command`:

## License

MIT
