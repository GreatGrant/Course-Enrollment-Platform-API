# Progress

- Scaffolded the FastAPI project structure.
- Added JWT auth, RBAC, SQLAlchemy models, repositories, and services.
- Added Alembic migration files and test scaffolding.
- Fixed the inactive-user test to use the current database session path.
- Stabilized test DB fixture to isolate each test with a fresh in-memory database.
- Fixed Alembic runtime path setup so migrations import the app package correctly.
- Updated test database engine to use `StaticPool` for consistent in-memory SQLite behavior.
- Switched password hashing from bcrypt to `pbkdf2_sha256` for Python 3.14 compatibility.
- Completed environment setup, installed dependencies, ran migrations, and executed tests.
- Final status: 10 tests passed.
- Updated README setup steps with exact Windows PowerShell commands used in this environment.