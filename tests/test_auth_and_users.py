from tests.conftest import auth_headers


def register(client, name: str, email: str, password: str, role: str):
    return client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password, "role": role},
    )


def login(client, email: str, password: str):
    return client.post("/auth/login", json={"email": email, "password": password})


def test_register_login_and_profile(client):
    response = register(client, "Ada Student", "ada@example.com", "StrongPass123", "student")
    assert response.status_code == 201
    payload = response.json()
    assert payload["email"] == "ada@example.com"
    assert payload["role"] == "student"

    login_response = login(client, "ada@example.com", "StrongPass123")
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = auth_headers(token)

    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "ada@example.com"

    profile_response = client.get("/users/me", headers=headers)
    assert profile_response.status_code == 200
    assert profile_response.json()["name"] == "Ada Student"


def test_duplicate_email_and_invalid_role(client):
    register(client, "Admin User", "admin@example.com", "StrongPass123", "admin")
    duplicate = register(client, "Another Admin", "admin@example.com", "StrongPass123", "admin")
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Email already registered"

    invalid_role = client.post(
        "/auth/register",
        json={"name": "Bad Role", "email": "bad@example.com", "password": "StrongPass123", "role": "guest"},
    )
    assert invalid_role.status_code == 422


def test_inactive_user_cannot_authenticate(client, db_session):
    register(client, "Inactive User", "inactive@example.com", "StrongPass123", "student")
    from app.models.user import User

    user = db_session.query(User).filter(User.email == "inactive@example.com").one()
    user.is_active = False
    db_session.commit()

    response = login(client, "inactive@example.com", "StrongPass123")
    assert response.status_code == 403
    assert response.json()["detail"] == "Inactive user cannot authenticate"