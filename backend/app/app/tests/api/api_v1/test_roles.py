import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, crud, schemas
from app.core.config import settings
from app.tests.utils import utils, user as user_utils


@pytest.fixture(scope="function")
def with_clean_roles_table(db: Session) -> None:
    """Clean roles table before and after each test."""
    db.query(models.Role).delete()
    yield
    db.query(models.Role).delete()


def test_superuser_can_read_roles(
        client: TestClient,
        superuser_token_headers: dict,
        db: Session,
        with_clean_roles_table
):
    role = user_utils.create_random_role(db)

    response = client.get(
        f"{settings.API_V1_STR}/permissions/roles",
        headers=superuser_token_headers
    )
    assert response.status_code == 200

    assert response.json() == [schemas.Role.from_orm(role).dict()]


def test_user_can_read_roles_with_proper_permissions(
        client: TestClient,
        db: Session,
        with_clean_roles_table
):
    user = user_utils.create_random_user(db)
    role = user_utils.bind_role_with_permissions(db, user, ["roles:read"])
    not_the_user_role = user_utils.create_random_role(db)

    response = client.get(
        f"{settings.API_V1_STR}/permissions/roles",
        headers=user_utils.authentication_token_from_email(client=client, email=user.email, db=db)
    )

    assert response.status_code == 200
    assert response.json() == [schemas.Role.from_orm(role).dict(), schemas.Role.from_orm(not_the_user_role).dict()]


def test_user_unable_to_read_roles_without_proper_permissions(
        client: TestClient,
        db: Session,
        with_clean_roles_table
):
    user = user_utils.create_random_user(db)
    user_utils.bind_role_with_permissions(db, user, ["roles:write"])

    response = client.get(
        f"{settings.API_V1_STR}/permissions/roles",
        headers=user_utils.authentication_token_from_email(client=client, email=user.email, db=db)
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions"}


def test_superuser_can_create_new_role(
        client: TestClient,
        superuser_token_headers: dict,
        db: Session
):
    role_data = {"name": utils.random_lower_string(), "permissions": ["roles:read"]}

    response = client.post(
        f"{settings.API_V1_STR}/permissions/roles/",
        headers=superuser_token_headers,
        json=role_data
    )

    stored_role = crud.role.get_by_name(db, name=role_data["name"])
    stored_role.permissions = role_data["permissions"]

    assert response.status_code == 200
    assert response.json() == schemas.Role.from_orm(stored_role).dict()


def test_user_can_create_new_role_with_proper_permissions(
        client: TestClient,
        superuser_token_headers: dict,
        db: Session
):
    user = user_utils.create_random_user(db)
    user_utils.bind_role_with_permissions(db, user, ["roles:write"])

    role_data = {"name": utils.random_email(), "permissions": ["roles:read"]}

    response = client.post(
        f"{settings.API_V1_STR}/permissions/roles/",
        headers=user_utils.authentication_token_from_email(client=client, email=user.email, db=db),
        json=role_data
    )

    stored_role = crud.role.get_by_name(db, name=role_data["name"])
    stored_role.permissions = role_data["permissions"]

    assert response.status_code == 200
    assert response.json() == schemas.Role.from_orm(stored_role).dict()


def test_user_unable_to_create_new_role_without_proper_permissions(
        client: TestClient,
        superuser_token_headers: dict,
        db: Session
):
    user = user_utils.create_random_user(db)
    user_utils.bind_role_with_permissions(db, user, ["roles:read"])

    role_data = {"name": utils.random_email(), "permissions": ["roles:read"]}

    response = client.post(
        f"{settings.API_V1_STR}/permissions/roles/",
        headers=user_utils.authentication_token_from_email(client=client, email=user.email, db=db),
        json=role_data
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions"}


def test_user_unable_to_create_new_role_with_the_same_name(
        client: TestClient,
        superuser_token_headers: dict,
        db: Session
):
    role = user_utils.create_random_role(db)

    role_data = {"name": role.name, "permissions": ["roles:read"]}

    response = client.post(
        f"{settings.API_V1_STR}/permissions/roles/",
        headers=superuser_token_headers,
        json=role_data
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Role with this name already exists"}


def test_superuser_can_get_role_by_id(
        client: TestClient,
        superuser_token_headers: dict,
        db: Session
):
    role = user_utils.create_random_role(db)

    response = client.get(
        f"{settings.API_V1_STR}/permissions/roles/{role.id}/",
        headers=superuser_token_headers
    )

    assert response.status_code == 200
    assert response.json() == schemas.Role.from_orm(role).dict()


def test_user_can_get_role_by_id_with_proper_permissions(
        client: TestClient,
        db: Session
):
    user = user_utils.create_random_user(db)
    role = user_utils.bind_role_with_permissions(db, user, ["roles:read"])

    response = client.get(
        f"{settings.API_V1_STR}/permissions/roles/{role.id}/",
        headers=user_utils.authentication_token_from_email(client=client, email=user.email, db=db)
    )

    assert response.status_code == 200
    assert response.json() == schemas.Role.from_orm(role).dict()


def test_user_unable_to_get_role_by_id_without_proper_permissions(
        client: TestClient,
        db: Session
):
    user = user_utils.create_random_user(db)
    role = user_utils.bind_role_with_permissions(db, user, ["roles:write"])

    response = client.get(
        f"{settings.API_V1_STR}/permissions/roles/{role.id}/",
        headers=user_utils.authentication_token_from_email(client=client, email=user.email, db=db)
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions"}


def test_superuser_can_delete_role(
        client: TestClient,
        superuser_token_headers: dict,
        db: Session
):
    role = user_utils.create_random_role(db)

    response = client.delete(
        f"{settings.API_V1_STR}/permissions/roles/{role.id}",
        headers=superuser_token_headers
    )

    assert response.status_code == 200
    assert response.json() == schemas.Role(id=role.id,
                                           name=role.name,
                                           permissions=role.permissions).dict()


def test_user_unable_to_delete_non_existing_role(
        client: TestClient,
        superuser_token_headers: dict,
        db: Session
):
    response = client.delete(
        f"{settings.API_V1_STR}/permissions/roles/0",
        headers=superuser_token_headers
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Role not found"}


def test_user_can_delete_role_with_proper_permissions(
        client: TestClient,
        db: Session
):
    user = user_utils.create_random_user(db)
    role = user_utils.bind_role_with_permissions(db, user, ["roles:write"])

    # we need to pre-generate expected response,
    # because role will be deleted, and we won't be able to get it from the Session
    expected_data = schemas.Role.from_orm(role).dict()

    response = client.delete(
        f"{settings.API_V1_STR}/permissions/roles/{role.id}",
        headers=user_utils.authentication_token_from_email(client=client, email=user.email, db=db)
    )

    assert response.status_code == 200
    assert response.json() == expected_data


def test_user_unable_to_delete_role_without_proper_permissions(
        client: TestClient,
        db: Session
):
    user = user_utils.create_random_user(db)
    role = user_utils.bind_role_with_permissions(db, user, ["roles:read"])

    response = client.delete(
        f"{settings.API_V1_STR}/permissions/roles/{role.id}",
        headers=user_utils.authentication_token_from_email(client=client, email=user.email, db=db)
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions"}