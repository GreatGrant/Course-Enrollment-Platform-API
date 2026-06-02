from tests.conftest import auth_headers


def setup_admin_and_student(client):
    client.post(
        "/auth/register",
        json={"name": "Admin", "email": "admin@example.com", "password": "StrongPass123", "role": "admin"},
    )
    admin_token = client.post("/auth/login", json={"email": "admin@example.com", "password": "StrongPass123"}).json()["access_token"]
    client.post(
        "/auth/register",
        json={"name": "Student", "email": "student@example.com", "password": "StrongPass123", "role": "student"},
    )
    student_token = client.post("/auth/login", json={"email": "student@example.com", "password": "StrongPass123"}).json()["access_token"]
    return auth_headers(admin_token), auth_headers(student_token)


def test_admin_can_view_and_remove_enrollments(client):
    admin_headers, student_headers = setup_admin_and_student(client)
    course_id = client.post(
        "/courses",
        headers=admin_headers,
        json={"title": "Admin Oversight", "code": "ADM101", "capacity": 2, "is_active": True},
    ).json()["id"]

    client.post(f"/enrollments/{course_id}", headers=student_headers)

    all_enrollments = client.get("/admin/enrollments", headers=admin_headers)
    assert all_enrollments.status_code == 200
    data = all_enrollments.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1

    course_enrollments = client.get(f"/admin/courses/{course_id}/enrollments", headers=admin_headers)
    assert course_enrollments.status_code == 200
    course_data = course_enrollments.json()
    assert course_data["total"] == 1
    assert len(course_data["items"]) == 1

    student_id = client.get("/users/me", headers=student_headers).json()["id"]
    remove_response = client.delete(f"/admin/courses/{course_id}/enrollments/{student_id}", headers=admin_headers)
    assert remove_response.status_code == 204

    empty_after_remove = client.get(f"/admin/courses/{course_id}/enrollments", headers=admin_headers)
    assert empty_after_remove.json()["items"] == []


def test_admin_routes_require_admin(client):
    _, student_headers = setup_admin_and_student(client)
    forbidden = client.get("/admin/enrollments", headers=student_headers)
    assert forbidden.status_code == 403