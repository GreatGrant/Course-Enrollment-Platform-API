"""Tests for bonus features: pagination, soft deletes, audit logs, and rate limiting."""

from tests.conftest import auth_headers


def _admin(client):
    client.post(
        "/auth/register",
        json={"name": "Admin", "email": "admin@test.com", "password": "StrongPass123", "role": "admin"},
    )
    token = client.post("/auth/login", json={"email": "admin@test.com", "password": "StrongPass123"}).json()["access_token"]
    return auth_headers(token)


def _student(client, email="student@test.com"):
    client.post(
        "/auth/register",
        json={"name": "Student", "email": email, "password": "StrongPass123", "role": "student"},
    )
    token = client.post("/auth/login", json={"email": email, "password": "StrongPass123"}).json()["access_token"]
    return auth_headers(token)


# Pagination


def test_course_list_pagination(client):
    ah = _admin(client)
    for i in range(5):
        client.post("/courses", headers=ah, json={"title": f"C{i}", "code": f"PG{i:03d}", "capacity": 10, "is_active": True})

    # First page
    r1 = client.get("/courses?skip=0&limit=2")
    d1 = r1.json()
    assert d1["total"] == 5
    assert len(d1["items"]) == 2
    assert d1["skip"] == 0
    assert d1["limit"] == 2

    # Second page
    r2 = client.get("/courses?skip=2&limit=2")
    d2 = r2.json()
    assert len(d2["items"]) == 2

    # Third page (remaining)
    r3 = client.get("/courses?skip=4&limit=2")
    d3 = r3.json()
    assert len(d3["items"]) == 1


def test_admin_enrollment_pagination(client):
    ah = _admin(client)
    course_id = client.post("/courses", headers=ah, json={"title": "Bulk", "code": "BLK100", "capacity": 10, "is_active": True}).json()["id"]

    for i in range(3):
        sh = _student(client, email=f"s{i}@test.com")
        client.post(f"/enrollments/{course_id}", headers=sh)

    r = client.get("/admin/enrollments?skip=0&limit=2", headers=ah)
    d = r.json()
    assert d["total"] == 3
    assert len(d["items"]) == 2


# Soft Delete


def test_soft_delete_hides_course(client):
    ah = _admin(client)
    course_id = client.post("/courses", headers=ah, json={"title": "ToDelete", "code": "DEL100", "capacity": 5, "is_active": True}).json()["id"]

    # Visible before delete
    assert client.get(f"/courses/{course_id}").status_code == 200

    # Soft delete
    assert client.delete(f"/courses/{course_id}", headers=ah).status_code == 204

    # Gone from public view
    assert client.get(f"/courses/{course_id}").status_code == 404

    # Gone from listing
    listing = client.get("/courses").json()
    codes = [c["code"] for c in listing["items"]]
    assert "DEL100" not in codes


def test_soft_deleted_course_code_cannot_be_reused(client):
    """After soft-deleting a course, its code is still reserved (unique constraint intact)."""
    ah = _admin(client)
    client.post("/courses", headers=ah, json={"title": "Original", "code": "REUSE1", "capacity": 5, "is_active": True})
    # The code is stored uppercased; soft-delete it
    courses_list = client.get("/courses").json()["items"]
    cid = [c for c in courses_list if c["code"] == "REUSE1"][0]["id"]
    client.delete(f"/courses/{cid}", headers=ah)

    # Attempting to create with the same code should fail with a clean 400 Bad Request
    res = client.post("/courses", headers=ah, json={"title": "Another", "code": "REUSE1", "capacity": 5, "is_active": True})
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"].lower()

    # Soft-deleted course is not returned by get_by_id.
    assert client.get(f"/courses/{cid}").status_code == 404


# Audit Logs


def test_audit_logs_recorded_for_enrollment_lifecycle(client):
    ah = _admin(client)
    sh = _student(client)
    course_id = client.post("/courses", headers=ah, json={"title": "Audit", "code": "AUD100", "capacity": 5, "is_active": True}).json()["id"]

    # Enroll → audit log
    client.post(f"/enrollments/{course_id}", headers=sh)

    logs = client.get("/admin/audit-logs", headers=ah).json()
    assert logs["total"] == 1
    assert logs["items"][0]["action"] == "ENROLL"

    # Deregister → audit log
    client.delete(f"/enrollments/{course_id}", headers=sh)

    logs = client.get("/admin/audit-logs", headers=ah).json()
    assert logs["total"] == 2
    actions = [l["action"] for l in logs["items"]]
    assert "DEREGISTER" in actions


def test_audit_log_for_admin_remove(client):
    ah = _admin(client)
    sh = _student(client)
    course_id = client.post("/courses", headers=ah, json={"title": "AuditRemove", "code": "AUD200", "capacity": 5, "is_active": True}).json()["id"]
    client.post(f"/enrollments/{course_id}", headers=sh)

    student_id = client.get("/users/me", headers=sh).json()["id"]
    client.delete(f"/admin/courses/{course_id}/enrollments/{student_id}", headers=ah)

    logs = client.get("/admin/audit-logs", headers=ah).json()
    admin_remove_logs = [l for l in logs["items"] if l["action"] == "ADMIN_REMOVE"]
    assert len(admin_remove_logs) == 1
    assert admin_remove_logs[0]["course_id"] == course_id
    assert admin_remove_logs[0]["user_id"] == student_id


def test_audit_logs_require_admin(client):
    _admin(client)
    sh = _student(client)
    r = client.get("/admin/audit-logs", headers=sh)
    assert r.status_code == 403


# Rate Limiting


def test_rate_limit_on_register(client):
    """After 5 rapid registrations, the 6th should be rate-limited (429)."""
    from app.core.rate_limit import limiter

    limiter.enabled = True
    limiter.reset()

    for i in range(5):
        client.post(
            "/auth/register",
            json={"name": f"User{i}", "email": f"rl{i}@test.com", "password": "StrongPass123", "role": "student"},
        )

    response = client.post(
        "/auth/register",
        json={"name": "User6", "email": "rl6@test.com", "password": "StrongPass123", "role": "student"},
    )
    assert response.status_code == 429

    limiter.enabled = False


def test_rate_limit_on_login(client):
    """After 5 rapid login attempts, the 6th should be rate-limited (429)."""
    from app.core.rate_limit import limiter

    limiter.enabled = True
    limiter.reset()

    client.post(
        "/auth/register",
        json={"name": "LoginTest", "email": "loginrl@test.com", "password": "StrongPass123", "role": "student"},
    )
    for i in range(5):
        client.post("/auth/login", json={"email": "loginrl@test.com", "password": "StrongPass123"})

    response = client.post("/auth/login", json={"email": "loginrl@test.com", "password": "StrongPass123"})
    assert response.status_code == 429

    limiter.enabled = False
