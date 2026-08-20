def test_register_and_create_task_flow(client):
    register_response = client.post(
        "/api/users/register",
        json={
            "username": "flowuser",
            "email": "flowuser@example.com",
            "password": "secret123",
            "full_name": "Flow User",
        },
    )
    assert register_response.status_code == 201
    user = register_response.json()
    assert user["username"] == "flowuser"

    login_response = client.post(
        "/api/users/login",
        data={"username": "flowuser", "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token

    project_response = client.post(
        "/api/projects/",
        json={"name": "Flow Project", "owner_id": user["id"]},
    )
    assert project_response.status_code == 200
    project = project_response.json()

    task_response = client.post(
        "/api/tasks/",
        json={"title": "Flow Task", "project_id": project["id"]},
    )
    assert task_response.status_code == 200
    task = task_response.json()
    assert task["title"] == "Flow Task"
    assert task["project_id"] == project["id"]
    assert task["comments"] == []

    duplicate_response = client.post(
        "/api/users/register",
        json={
            "username": "flowuser",
            "email": "other@example.com",
            "password": "secret123",
        },
    )
    assert duplicate_response.status_code == 400
