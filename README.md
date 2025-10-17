# HR Document Management System API

A secure and robust backend service for managing employee documents, built with FastAPI. This system provides role-based access control, secure authentication with JWT, and a versioning system for all uploaded documents.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Setup and Installation](#setup-and-installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication)
  - [Document Management](#document-management)

---

## Features

- **Secure User Authentication**: JWT-based authentication for user registration and login.
- **Role-Based Access Control (RBAC)**: Distinct roles ('Employee', 'HR Manager', 'Admin') with different permissions.
- **Document Upload**: Secure endpoint for HR and Admin roles to upload documents for employees.
- **File Versioning**: Automatically creates a new version of a document if a file with the same name is uploaded for the same employee, preserving all historical copies.
- **Secure Document Retrieval**: Endpoints to list and download documents, ensuring employees can only access their own files while privileged roles can access all.
- **Asynchronous Database Operations**: Built with `async` and `await` using `motor` for high-performance, non-blocking database interactions.
- **Modern Data Validation**: Utilizes Pydantic for robust data validation and serialization.

## Project Structure

The project follows a clean, scalable architecture with a clear separation of concerns.

```
HR_docs_management/
├── app/
│   ├── api/
│   │   ├── auth.py         # Handles user registration, login, and security dependencies
│   │   └── documents.py    # Handles all document-related API endpoints
│   ├── auth/
│   │   ├── jwt.py          # JWT creation and decoding logic
│   │   └── password.py     # Password hashing and verification (bcrypt)
│   ├── core/
│   │   ├── document.py     # Core business logic for document versioning
│   │   └── validator.py    # Custom validators (e.g., for ObjectId)
│   ├── db/
│   │   └── database.py     # MongoDB connection and collection setup
│   ├── models/
│   │   ├── document.py     # Pydantic model for Document and DocumentVersion
│   │   └── user.py         # Pydantic models for User, UserCreate, etc.
│   └── main.py             # Main FastAPI application instance and router setup
├── uploads/                # Directory where uploaded files are stored
├── .env                    # Environment variables 
├── pyproject.toml          # Project dependencies
└── README.md               # This file
```

## Technology Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [MongoDB](https://www.mongodb.com/) (interacted with via `motor`)
- **Authentication**: JWT Tokens (`python-jose`)
- **Password Hashing**: `bcrypt`
- **Data Validation**: [Pydantic](https://docs.pydantic.dev/)
- **Environment Management**: `python-dotenv` & `pydantic-settings`
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/)

## Setup and Installation

1.  **Clone the repository:**
    ```
    git clone <your-repository-url>
    cd HR_docs_management
    ```

2.  **Create a virtual environment and install dependencies:**
    This project uses `uv` for package management.
    ```
    # Create the virtual environment
    python -m venv .venv
    # Activate it
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    # Install dependencies
    uv pip install -r requirements.txt # Or create a requirements.txt first
    ```

## Configuration

1.  **Create a `.env` file** in the root directory of the project.
2.  **Add the following environment variables** to the `.env` file, replacing the placeholder values with your actual credentials:

    ```
    # MongoDB Connection
    MONGODB_URI="mongodb+srv://<username>:<password>@<your-cluster-url>/?retryWrites=true&w=majority"
    DATABASE_NAME="hr_dms"

    # JWT Settings
    JWT_SECRET_KEY="your-super-secret-key-that-is-long-and-random"
    JWT_ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

## Running the Application

Once the dependencies are installed and the `.env` file is configured, run the application using Uvicorn:

```
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Interactive documentation (Swagger UI) can be accessed at `http://127.0.0.1:8000/docs`.

## API Endpoints

### Authentication

- **`POST /register`**
  - Registers a new user.
  - **Body**: `{ "username": "...", "email": "...", "password": "...", "role": "Employee" }`

- **`POST /login`**
  - Authenticates a user and returns a JWT access token.
  - **Body (form-data)**: `username` and `password`.

### Document Management

*All document endpoints require a valid JWT Bearer token in the `Authorization` header.*

- **`POST /documents/upload`**
  - Uploads a document for a specific employee. **Requires HR/Admin role.**
  - **Query Parameters**: `employee_id` (string), `document_type` (string).
  - **Body (form-data)**: `file` (the file to upload).

- **`GET /documents/my-documents`**
  - Retrieves a list of all documents belonging to the currently logged-in user.

- **`GET /documents/user/{employee_id}`**
  - Retrieves a list of all documents for a specific employee. **Requires HR/Admin role.**

- **`GET /documents/download/{doc_id}/version/{version_num}`**
  - Downloads a specific version of a document. Requires ownership or HR/Admin role.
