# HR Document Management System API

A secure and robust backend service for managing employee documents, built with FastAPI. This system provides role-based access control, secure authentication with JWT, and an industry-standard versioning system with check-in/check-out functionality to prevent data conflicts.

## Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Setup and Installation](#setup-and-installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Future Work: RAG Integration](#future-work-rag-integration)

---

## Features

-   **Secure User Authentication**: JWT-based authentication for user registration and login.
-   **Role-Based Access Control (RBAC)**: Distinct roles ('Employee', 'HR Manager', 'Admin') with granular permissions.
-   **Robust Document Versioning**: Implements the Document Versioning Pattern by maintaining a master record for the latest version and storing all historical versions in a separate collection for a complete audit trail.
-   **Conflict Prevention with Check-In/Check-Out**: A pessimistic locking mechanism ensures that only one user can edit a document at a time, preventing data loss from conflicting updates.
-   **Secure and Controlled Document Lifecycle**: Endpoints for uploading, downloading, listing, and versioning documents, with strict adherence to user permissions.
-   **Asynchronous & High-Performance**: Built with `async`/`await` and `motor` for non-blocking database operations, ensuring high concurrency.
-   **Modern Data Validation**: Utilizes Pydantic for robust, type-safe data validation and serialization.

## System Architecture

The versioning system is designed for efficiency and data integrity:
1.  **`documents` Collection**: This collection stores only the *latest metadata* for each master document (e.g., `latest_version`, `is_checked_out`). It is optimized for fast queries to find current documents.
2.  **`document_versions` Collection**: This collection acts as an immutable log, storing a full copy of every version ever uploaded. This provides a complete, auditable history of changes.

## Project Structure

The project is organized into a modular structure to separate concerns, making it easier to maintain and scale.

```
HR_docs_management/
├── app/                      # Main application source code
│   ├── main.py             # FastAPI app entry point and router inclusion
│   ├── config.py           # Centralized application configuration (from .env)
│   │
│   ├── api/                # API layer: Endpoints and routing
│   │   ├── auth.py         # Authentication endpoints (/register, /login) & security dependencies
│   │   └── documents.py    # All document management endpoints
│   │
│   ├── auth/               # Authentication helpers and utilities
│   │   ├── jwt.py          # Logic for creating and decoding JWTs
│   │   └── password.py     # Password hashing and verification logic
│   │
│   ├── core/               # Core business logic of the application
│   │   ├── document.py     # Handles versioning, check-in/check-out, and file operations
│   │   └── validator.py    # Reusable data validation functions (e.g., ObjectId)
│   │
│   ├── db/                 # Database connection and setup
│   │   └── database.py     # Motor client setup and collection definitions
│   │
│   └── models/             # Pydantic data models for validation and serialization
│       ├── document.py     # `Document` and `DocumentVersion` models
│       └── user.py         # `User`, `UserCreate`, and `UserInDB` models
│
├── documents/                # Sample documents for testing uploads
│   ├── agreement.txt
│   ├── contract.txt
│   └── ...
│
├── uploads/                  # Storage for user-uploaded files (Git-ignored)
│
├── .env                      # Environment variables (Git-ignored)
├── .gitignore                # Specifies files and directories to be ignored by Git
├── pyproject.toml            # Project metadata and dependencies (replaces requirements.txt)
└── README.md                 # This documentation file
```

## Technology Stack

-   **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/)
-   **Database**: [MongoDB](https://www.mongodb.com/) (with `motor` for async operations)
-   **Authentication**: JWT Tokens (`python-jose`), OAuth2
-   **Password Hashing**: `bcrypt`
-   **Data Validation**: [Pydantic](https://docs.pydantic.dev/)
-   **Environment Management**: `python-dotenv` & `pydantic-settings`
-   **ASGI Server**: [Uvicorn](https://www.uvicorn.org/)

## Setup and Installation

1.  **Clone the repository:**
    ```
    git clone <your-repository-url>
    cd HR_docs_management
    ```

2.  **Create a virtual environment and install dependencies:**
    ```
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    ```

## Configuration

1.  Create a `.env` file in the root directory.
2.  Add the following environment variables, replacing the placeholders:

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

Run the application using Uvicorn:
The API will be available at `http://127.0.0.1:8000`. Interactive documentation (Swagger UI) can be accessed at `http://127.0.0.1:8000/docs`.

## API Endpoints

### Authentication

-   **`POST /register`**: Registers a new user.
-   **`POST /login`**: Authenticates a user and returns a JWT access token.

### Document Management

*All document endpoints require a valid JWT Bearer token in the `Authorization` header.*

-   **`POST /documents/upload`**
    -   Uploads a **new** document. Creates version 1 of a master document.
    -   **Important**: This endpoint is blocked if the document already exists to enforce the check-in/check-out workflow.
    -   **Requires**: HR/Admin role.

-   **`GET /documents/my-documents`**
    -   Retrieves a list of all documents belonging to the currently logged-in user.

-   **`GET /documents/user/{employee_id}`**
    -   Retrieves a list of all documents for a specific employee. **Requires**: HR/Admin role.

-   **`GET /documents/{doc_id}/versions`**
    -   Lists the complete version history for a specific master document.

-   **`POST /documents/{doc_id}/checkout`**
    -   Locks a document for editing, preventing others from making changes.

-   **`POST /documents/{doc_id}/checkin`**
    -   Uploads a new version of a document that is currently checked out by the user, then releases the lock.

-   **`GET /documents/download/{doc_id}/version/{version_num}`**
    -   Downloads a specific version of a document. Requires ownership or HR/Admin role.

---

## Future Work: RAG Integration

A planned enhancement is to integrate a **Retrieval-Augmented Generation (RAG)** system to enable a "chat with your documents" feature.