import pytest

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud
from app.schemas.permissions import RoleCreate, Binding
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_role(db):
    role_in = RoleCreate(name=random_lower_string(), permissions=[])
    role = crud.role.create(db=db, obj_in=role_in)
    return role


@pytest.mark.parametrize("permissions",
                         [[],
                          [""],
                          ["item:read"],
                          ["item:read", "item:write"],
                          ])
def test_create_role(db: Session, permissions) -> None:
    name = random_lower_string()
    role_in = RoleCreate(name=name,
                         permissions=permissions)
    role = crud.role.create(db=db, obj_in=role_in)
    assert role.name == name
    assert role.permissions == permissions


# tests update role with permissions
@pytest.mark.parametrize("permissions",
                            [[],
                                [""],
                                ["item:read"],
                                ["item:read", "item:write"],
                                ])
def test_update_role(db: Session, permissions) -> None:
    name = random_lower_string()
    role_in = RoleCreate(name=name,
                         permissions=permissions)
    role = crud.role.create(db=db, obj_in=role_in)

    new_name = random_lower_string()
    role_in.name = new_name
    new_permissions = ["users:read"]
    role_in.permissions = new_permissions
    updated_role = crud.role.update(db=db, db_obj=role, obj_in=role_in)
    assert updated_role.name == new_name
    assert updated_role.permissions == new_permissions


def test_get_role_by_name(db: Session) -> None:
    role = create_random_role(db)
    stored_role = crud.role.get_by_name(db=db, name=role.name)
    assert stored_role
    assert role.id == stored_role.id
    assert role.name == stored_role.name
    assert role.permissions == stored_role.permissions


def test_bind_roles_to_user(db: Session) -> None:
    item_manager_role = create_random_role(db)
    user_manager_role = create_random_role(db)

    user = create_random_user(db)

    crud.user_role_binding.create(db=db, obj_in=Binding(user_id=user.id,
                                                        role_id=item_manager_role.id))
    crud.user_role_binding.create(db=db, obj_in=Binding(user_id=user.id,
                                                        role_id=user_manager_role.id))

    roles = {b.role for b in crud.user_role_binding.find_for_user(db=db, user_id=user.id)}
    assert roles == {item_manager_role, user_manager_role}


def test_unable_to_bind_same_role_twice_on_the_user(db: Session) -> None:
    role = create_random_role(db)
    user = create_random_user(db)

    binding_in = Binding(user_id=user.id, role_id=role.id)
    crud.user_role_binding.create(db=db, obj_in=binding_in)

    with pytest.raises(IntegrityError):
        crud.user_role_binding.create(db=db, obj_in=binding_in)
