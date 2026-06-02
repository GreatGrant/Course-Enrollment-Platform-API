from tests.conftest import auth_headers


def create_admin(client):
    client.post(
        "/auth/register",
        json={"name": "Admin", "email": "admin@example.com", "password": "StrongPass123", "role": "admin"},
    )
    token = client.post("/auth/login", json={"email": "admin@example.com", "password": "StrongPass123"}).json()["access_token"]
    return auth_headers(token)


def create_student(client, email: str = "student@example.com"):
    client.post(
        "/auth/register",
        json={"name": "Student", "email": email, "password": "StrongPass123", "role": "student"},
    )
    token = client.post("/auth/login", json={"email": email, "password": "StrongPass123"}).json()["access_token"]
    return auth_headers(token)


def create_course(client, admin_headers, *, capacity: int = 1, is_active: bool = True, code: str = "ENR101"):
    response = client.post(
        "/courses",
        headers=admin_headers,
        json={"title": "Enrollment Basics", "code": code, "capacity": capacity, "is_active": is_active},
    )
    return response.json()["id"]


def test_student_enroll_and_deregister(client):
    admin_headers = create_admin(client)
    student_headers = create_student(client)
    course_id = create_course(client, admin_headers, capacity=2, code="ENR201")

    enroll_response = client.post(f"/enrollments/{course_id}", headers=student_headers)
    assert enroll_response.status_code == 201
    assert enroll_response.json()["course_id"] == course_id

    duplicate = client.post(f"/enrollments/{course_id}", headers=student_headers)
    assert duplicate.status_code == 400

    deregister_response = client.delete(f"/enrollments/{course_id}", headers=student_headers)
    assert deregister_response.status_code == 204


def test_enrollment_rules(client):
    admin_headers = create_admin(client)
    student_headers = create_student(client, email="student2@example.com")
    inactive_course_id = create_course(client, admin_headers, capacity=1, is_active=False, code="ENR202")
    full_course_id = create_course(client, admin_headers, capacity=1, is_active=True, code="ENR203")

    inactive_response = client.post(f"/enrollments/{inactive_course_id}", headers=student_headers)
    assert inactive_response.status_code == 400
    assert inactive_response.json()["detail"] == "Course is inactive"

    first_enroll = client.post(f"/enrollments/{full_course_id}", headers=student_headers)
    assert first_enroll.status_code == 201

    second_student_headers = create_student(client, email="student3@example.com")
    full_response = client.post(f"/enrollments/{full_course_id}", headers=second_student_headers)
    assert full_response.status_code == 400
    assert full_response.json()["detail"] == "Course is full"