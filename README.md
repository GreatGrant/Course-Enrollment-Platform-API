# Course Enrollment Platform API

FastAPI REST API for managing users, courses, and enrollments with JWT authentication, role-based access control, and a relational database.

## Features

- User registration and login with secure password hashing
- JWT authentication
- Student and admin roles with access control
- Public course browsing
- Course enrollment rules with capacity and duplicate checks
- Admin oversight endpoints for enrollment management
- SQLAlchemy models and Alembic migrations
- Automated pytest coverage

### Bonus Features

- **Pagination & filtering** – All list endpoints return paginated responses with `skip`, `limit`, `total`, and `items`. Use `?skip=0&limit=10` query parameters.
- **Soft deletes** – Courses are soft-deleted (marked with a `deleted_at` timestamp) rather than permanently removed. Soft-deleted courses are excluded from all queries.
- **Audit logs** – Every enrollment lifecycle event (ENROLL, DEREGISTER, ADMIN_REMOVE) is recorded with timestamps and actor tracking. Admins can view the audit trail via `GET /admin/audit-logs`.
- **Rate limiting** – The `/auth/register` and `/auth/login` endpoints are rate-limited to 5 requests per minute per IP address using slowapi.

## Tech Stack

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL (default) or SQLite for local development via `DATABASE_URL`
- Pytest
- slowapi (rate limiting)

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/GreatGrant/Course-Enrollment-Platform-API.git
   cd course-enrollment-platform-api
   ```

2. Create and activate a virtual environment.

   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   *If script execution is blocked on Windows:*
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

   **Linux / macOS:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and update the values if needed:

   **Windows (PowerShell):**
   ```powershell
   Copy-Item .env.example .env
   ```

   **Linux / macOS / Git Bash:**
   ```bash
   cp .env.example .env
   ```

   Set a strong `SECRET_KEY` before running the app.

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the API:
   ```bash
   uvicorn app.main:app --reload
   ```

## Running Tests

```powershell
pytest
```

## API Summary

### Authentication
- `POST /auth/register` – Register a new user (rate-limited: 5/min)
- `POST /auth/login` – Log in and receive a JWT (rate-limited: 5/min)
- `GET /auth/me` – Get current user profile

### Users
- `GET /users/me` – Get current user profile

### Courses (Public)
- `GET /courses?skip=0&limit=100` – List active courses (paginated)
- `GET /courses/{course_id}` – Get a course by ID

### Courses (Admin Only)
- `POST /courses` – Create a course
- `PUT /courses/{course_id}` – Update course details
- `PATCH /courses/{course_id}/status` – Activate/deactivate a course
- `DELETE /courses/{course_id}` – Soft-delete a course

### Enrollments (Student)
- `POST /enrollments/{course_id}` – Enroll in a course
- `DELETE /enrollments/{course_id}` – Deregister from a course

### Admin Oversight
- `GET /admin/enrollments?skip=0&limit=100` – View all enrollments (paginated)
- `GET /admin/courses/{course_id}/enrollments?skip=0&limit=100` – View course enrollments (paginated)
- `DELETE /admin/courses/{course_id}/enrollments/{user_id}` – Remove a student from a course
- `GET /admin/audit-logs?skip=0&limit=100` – View enrollment audit trail (paginated)

## Notes

- Admin-only endpoints require a Bearer token for a user with the `admin` role.
- Students can enroll in active courses only, once per course, and only while seats remain.
- Inactive users cannot authenticate.
- Deleted courses are soft-deleted and excluded from all API responses.
- All enrollment actions are recorded in the audit log with actor tracking.