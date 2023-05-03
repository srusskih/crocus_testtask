# API router for permissions CRUD operations.
from functools import partial
from typing import List, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, exc
from app.api import deps
from app.schemas import user as user_schemas
from app.schemas import permissions as schemas

router = APIRouter()


@router.get("/",
            dependencies=[Depends(partial(deps.has_permissions, ["roles:read"]))],
            response_model=List[schemas.Role])
def read_roles(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100
) -> Any:
    roles = crud.role.get_multi(db, skip=skip, limit=limit)
    return roles


@router.post("/",
             dependencies=[Depends(partial(deps.has_permissions, ["roles:write"]))],
             response_model=schemas.Role)
def create_roles(
        *,
        db: Session = Depends(deps.get_db),
        new_role: schemas.RoleCreate,
        _current_user: user_schemas.User = Depends(deps.get_current_active_user)
) -> Any:
    role = crud.role.create(db=db, obj_in=new_role)
    return role


@router.get("/{role_id}",
            dependencies=[Depends(partial(deps.has_permissions, ["roles:read"]))],
            response_model=schemas.Role)
def read_role_by_id(
        *,
        db: Session = Depends(deps.get_db),
        role_id: int
) -> Any:
    role = crud.role.get(db, id=role_id)
    if not role:
        raise exc.NotFound(message="Role not found")
    return role


@router.delete("/{role_id}",
               dependencies=[Depends(partial(deps.has_permissions, ["roles:write"]))],
               response_model=schemas.Role)
def delete_role_by_id(
        *,
        db: Session = Depends(deps.get_db),
        role_id: int
) -> Any:
    role = crud.role.remove(db, id=role_id)
    return schemas.Role(id=role.id, name=role.name, permissions=role.permissions).dict()
