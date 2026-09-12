# InvoiceFlow

A backend API for managing clients, projects, and invoices.

## Features

* User registration and authentication
* JWT-based authentication
* Client management
* Project management
* Invoice management
* Dashboard with business statistics
* PostgreSQL database
* SQLAlchemy ORM
* Alembic database migrations
* FastAPI automatic API documentation

## Tech Stack

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Psycopg
* Alembic
* JWT
* Pydantic
* Uvicorn

## API

The API provides endpoints for:

* Authentication
* Clients
* Projects
* Invoices
* Dashboard statistics

Interactive API documentation is available through Swagger UI at:

`/docs`

## Project Structure

```text
InvoiceFlow/
├── alembic/
│   └── versions/
├── app/
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   └── models.py
├── tests/
│   └── test_auth.py
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── README.md
```

## Database

InvoiceFlow uses PostgreSQL as its database and SQLAlchemy as the ORM.

Database schema changes are managed with Alembic migrations.

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/Birdseye-lab/InvoiceFlow.git
cd InvoiceFlow
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file:

```env
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/invoiceflow
```

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start the server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Swagger documentation:

`http://127.0.0.1:8000/docs`

## Authentication

InvoiceFlow uses JWT bearer authentication.

Users can register and log in through the API. Protected endpoints require a valid access token.

## Example Workflow

1. Register a user
2. Log in and receive a JWT token
3. Create a client
4. Create a project for the client
5. Create invoices for the project
6. View dashboard statistics

## Status

The project is currently under active development.

## Author

**Birdseye Lab**

GitHub: https://github.com/Birdseye-lab
