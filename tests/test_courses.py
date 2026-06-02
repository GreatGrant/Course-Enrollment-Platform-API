from tests.conftest import auth_headers


def register_admin_and_login(client):
    client.post(
        "/auth/register",
        json={"name": "Admin", "email": "admin@example.com", "password": "StrongPass123", "role": "admin"},
    )
    token = client.post("/auth/login", json={"email": "admin@example.com", "password": "StrongPass123"}).json()["access_token"]
    return auth_headers(token)


def register_student_and_login(client):
    client.post(
        "/auth/register",
        json={"name": "Student", "email": "student@example.com", "password": "StrongPass123", "role": "student"},
    )
    token = client.post("/auth/login", json={"email": "student@example.com", "password": "StrongPass123"}).json()["access_token"]
    return auth_headers(token)


def test_public_course_listing_and_detail(client):
    admin_headers = register_admin_and_login(client)
    create_response = client.post(
        "/courses",
        headers=admin_headers,
        json={"title": "FastAPI", "code": "API101", "capacity": 2, "is_active": True},
    )
    assert create_response.status_code == 201
    course_id = create_response.json()["id"]

    list_response = client.get("/courses")
    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 1
    assert data["items"][0]["code"] == "API101"

    detail_response = client.get(f"/courses/{course_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["title"] == "FastAPI"


def test_get_course_not_found_and_inactive(client):
    not_found = client.get("/courses/9999")
    assert not_found.status_code == 404

    admin_headers = register_admin_and_login(client)
    create_response = client.post(
        "/courses",
        headers=admin_headers,
        json={"title": "Hidden", "code": "HID101", "capacity": 5, "is_active": False},
    )
    inactive_id = create_response.json()["id"]

    inactive_response = client.get(f"/courses/{inactive_id}")
    assert inactive_response.status_code == 404
    assert inactive_response.json()["detail"] == "Course not found"


def test_admin_course_crud_and_status_toggle(client):
    admin_headers = register_admin_and_login(client)
    create_response = client.post(
        "/courses",
        headers=admin_headers,
        json={"title": "Databases", "code": "DB201", "capacity": 3, "is_active": True},
    )
    course_id = create_response.json()["id"]

    update_response = client.put(
        f"/courses/{course_id}",
        headers=admin_headers,
        json={"title": "Relational Databases", "capacity": 4},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Relational Databases"
    assert update_response.json()["capacity"] == 4

    status_response = client.patch(
        f"/courses/{course_id}/status",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert status_response.status_code == 200
    assert status_response.json()["is_active"] is False

    delete_response = client.delete(f"/courses/{course_id}", headers=admin_headers)
    assert delete_response.status_code == 204


def test_course_validation_and_permissions(client):
    admin_headers = register_admin_and_login(client)
    student_headers = register_student_and_login(client)

    bad_capacity = client.post(
        "/courses",
        headers=admin_headers,
        json={"title": "Bad", "code": "BAD1", "capacity": 0, "is_active": True},
    )
    assert bad_capacity.status_code == 422

    create_response = client.post(
        "/courses",
        headers=admin_headers,
        json={"title": "Security", "code": "SEC101", "capacity": 2, "is_active": True},
    )
    assert create_response.status_code == 201

    duplicate_code = client.post(
        "/courses",
        headers=admin_headers,
        json={"title": "Duplicate", "code": "SEC101", "capacity": 2, "is_active": True},
    )
    assert duplicate_code.status_code == 400

    forbidden = client.post(
        "/courses",
        headers=student_headers,
        json={"title": "Student Course", "code": "STU101", "capacity": 2, "is_active": True},
    )
    assert forbidden.status_code == 403