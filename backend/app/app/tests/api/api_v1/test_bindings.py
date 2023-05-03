import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.config import settings
from app.tests.utils import user as user_utils


@pytest.fixture(scope="function")
def with_clean_roles_data(db: Session) -> None:
    """Clean roles table before and after each test."""
    db.query(models.permissions.Bindings).delete()
    db.query(models.Role).delete()
    yield
    db.query(models.permissions.Bindings).delete()
    db.query(models.Role).delete()


def test_superuser_can_read_bindings(
        client: TestClient,
        superuser_token_headers: dict,
        db: Session,
        with_clean_roles_data
):
    user = user_utils.create_random_user(db)
    user_role = user_utils.bind_role_with_permissions(db, user, ["roles:read"])

    response = client.get(
        f"{settings.API_V1_STR}/permissions/bindings/",
        headers=superuser_token_headers
    )
    assert response.status_code == 200

    assert response.json() == [schemas.permissions.DetailedUserRoleBinding(user=user, role=user_role).dict()]


def test_user_can_read_bindings_with_proper_permissions(
        client: TestClient,
        db: Session,
        with_clean_roles_data
):
    user = user_utils.create_random_user(db)
    user_role = user_utils.bind_role_with_permissions(db, user, ["roles:read"])

    response = client.get(
        f"{settings.API_V1_STR}/permissions/bindings/",
        headers=user_utils.authentication_token_from_email(client=client, email=user.email, db=db)
    )
    assert response.status_code == 200

    assert response.json() == [schemas.permissions.DetailedUserRoleBinding(user=user, role=user_role).dict()]


def test_user_unable_to_read_bindings_without_proper_permissions(
        client: TestClient,
        db: Session,
        with_clean_roles_data
):
    user = user_utils.create_random_user(db)
    user_utils.bind_role_with_permissions(db, user, ["roles:write"])

    response = client.get(
        f"{settings.API_V1_STR}/permissions/bindings/",
        headers=user_utils.authentication_token_from_email(client=client, email=user.email, db=db)
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions"}


def test_superuser_can_create_bindings(
        client: TestClient,
        superuser_token_headers: dict,
        db: Session,
        with_clean_roles_data
):
    user = user_utils.create_random_user(db)
    role = user_utils.create_random_role(db)

    response = client.post(
        f"{settings.API_V1_STR}/permissions/bindings/",
        headers=superuser_token_headers,
        json={"user_id": user.id, "role_id": role.id}
    )
    assert response.status_code == 200

    assert response.json() == schemas.permissions.DetailedUserRoleBinding(user=user, role=role).dict()


def test_user_can_create_bindings_with_proper_permissions(
        client: TestClient,
        db: Session,
        with_clean_roles_data
):
    user = user_utils.create_random_user(db)
    role = user_utils.create_random_role(db)
    user_utils.bind_role_with_permissions(db, user, ["roles:write"])

    response = client.post(
        f"{settings.API_V1_STR}/permissions/bindings/",
        headers=user_utils.authentication_token_from_email(client=client, email=user.email, db=db),
        json={"user_id": user.id, "role_id": role.id}
    )
    assert response.status_code == 200

    assert response.json() == schemas.permissions.DetailedUserRoleBinding(user=user, role=role).dict()


def test_user_unable_to_create_bindings_without_proper_permissions(
        client: TestClient,
        db: Session,
        with_clean_roles_data
):
    user = user_utils.create_random_user(db)
    user_utils.bind_role_with_permissions(db, user, ["roles:read"])

    role_to_bind = user_utils.create_random_role(db)

    response = client.post(
        f"{settings.API_V1_STR}/permissions/bindings/",
        headers=user_utils.authentication_token_from_email(client=client, email=user.email, db=db),
        json={"user_id": user.id, "role_id": role_to_bind.id}
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions"}


def test_user_unable_to_create_same_binding_twice(
        client: TestClient,
        db: Session,
        superuser_token_headers: dict,
        with_clean_roles_data
):
    user = user_utils.create_random_user(db)
    user_role = user_utils.bind_role_with_permissions(db, user, ["roles:read"])

    # bind role to user one more time
    response = client.post(
        f"{settings.API_V1_STR}/permissions/bindings/",
        headers=superuser_token_headers,
        json={"user_id": user.id,
              "role_id": user_role.id}
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Binding already exists"}


def test_superuser_can_delete_bindings(
        client: TestClient,
        superuser_token_headers: dict,
        db: Session,
        with_clean_roles_data
):
    user = user_utils.create_random_user(db)
    user_role_to_remove = user_utils.bind_role_with_permissions(db, user, ["roles:read"])

    response = client.delete(
        f"{settings.API_V1_STR}/permissions/bindings/",
        headers=superuser_token_headers,
        json={"user_id": user.id,
              "role_id": user_role_to_remove.id}
    )

    assert response.status_code == 200
    assert response.json() == schemas.permissions.Binding(user_id=user.id, role_id=user_role_to_remove.id).dict()


def test_user_can_delete_bindings_with_proper_permissions(
        client: TestClient,
        db: Session,
        with_clean_roles_data
):
    user = user_utils.create_random_user(db)
    user_role_to_remove = user_utils.bind_role_with_permissions(db, user, ["roles:write"])

    response = client.delete(
        f"{settings.API_V1_STR}/permissions/bindings/",
        headers=user_utils.authentication_token_from_email(client=client, email=user.email, db=db),
        json={"user_id": user.id,
              "role_id": user_role_to_remove.id}
    )

    assert response.status_code == 200
    assert response.json() == schemas.permissions.Binding(user_id=user.id, role_id=user_role_to_remove.id).dict()


def test_user_unable_to_delete_bindings_without_proper_permissions(
        client: TestClient,
        db: Session,
        with_clean_roles_data
):
    user = user_utils.create_random_user(db)
    user_role_to_remove = user_utils.bind_role_with_permissions(db, user, ["roles:read"])

    response = client.delete(
        f"{settings.API_V1_STR}/permissions/bindings/",
        headers=user_utils.authentication_token_from_email(client=client, email=user.email, db=db),
        json={"user_id": user.id,
              "role_id": user_role_to_remove.id}
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions"}


def test_user_unable_to_delete_bindings_if_not_exists(
        client: TestClient,
        db: Session,
        superuser_token_headers: dict,
        with_clean_roles_data
):
    response = client.delete(
        f"{settings.API_V1_STR}/permissions/bindings/",
        headers=superuser_token_headers,
        json={"user_id": 0, "role_id": 0}  # non existing in ids
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Binding not found"}


def test_superuser_can_get_bindings_by_user_id(
        client: TestClient,
        db: Session,
        superuser_token_headers: dict,
        with_clean_roles_data
):
    user = user_utils.create_random_user(db)
    user_role = user_utils.bind_role_with_permissions(db, user, ["roles:read"])

    response = client.get(
        f"{settings.API_V1_STR}/permissions/bindings/for_user/{user.id}",
        headers=superuser_token_headers,
    )

    assert response.status_code == 200
    assert response.json() == [schemas.permissions.DetailedUserRoleBinding(user=user, role=user_role).dict()]


def test_user_can_get_bindings_by_user_id_with_proper_permissions(
        client: TestClient,
        db: Session,
        with_clean_roles_data
):
    user = user_utils.create_random_user(db)
    user_role = user_utils.bind_role_with_permissions(db, user, ["roles:read"])

    response = client.get(
        f"{settings.API_V1_STR}/permissions/bindings/for_user/{user.id}",
        headers=user_utils.authentication_token_from_email(client=client, email=user.email, db=db),
    )

    assert response.status_code == 200
    assert response.json() == [schemas.permissions.DetailedUserRoleBinding(user=user, role=user_role).dict()]


def test_user_unable_to_get_bindings_by_user_id_without_proper_permissions(
        client: TestClient,
        db: Session,
        with_clean_roles_data
):
    user = user_utils.create_random_user(db)
    user_utils.bind_role_with_permissions(db, user, ["roles:write"])

    response = client.get(
        f"{settings.API_V1_STR}/permissions/bindings/for_user/{user.id}",
        headers=user_utils.authentication_token_from_email(client=client, email=user.email, db=db),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions"}
