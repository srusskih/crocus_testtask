import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User
from app.tests.utils.user import (create_superuser,
                                  create_random_user,
                                  bind_role_with_permissions)


def test_super_user_has_permissions(db: Session):
    user: User = create_superuser(db)
    assert deps.has_permissions(["roles:read"], db, user)


def test_user_without_roles_does_not_have_permissions(db: Session):
    user: User = create_random_user(db)
    with pytest.raises(HTTPException) as e:
        deps.has_permissions(["roles:read"], db, user)

        assert e.value.status_code == 403


def test_user_with_required_permission_has_permissions(db: Session):
    user: User = create_random_user(db)
    bind_role_with_permissions(db, user, ["roles:read", "roles:write"])

    assert deps.has_permissions(["roles:read"], db, user)


def test_user_without_required_permissions_not_have_permissions(db: Session):
    user: User = create_random_user(db)
    bind_role_with_permissions(db, user, ["roles:write"])

    with pytest.raises(HTTPException) as e:
        deps.has_permissions(["roles:read"], db, user)
        assert e.value.status_code == 403
