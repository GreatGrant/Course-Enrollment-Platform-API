from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.rate_limit import limiter
from app.routers import admin, auth, courses, enrollments, users

app = FastAPI(title="Course Enrollment Platform API", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(admin.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Course Enrollment Platform API"}