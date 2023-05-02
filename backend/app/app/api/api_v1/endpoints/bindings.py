# API router for Permission Bindings CRUD operations
from functools import partial
from typing import List, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas import permissions as schemas

router = APIRouter()


@router.get("/",
            dependencies=[Depends(partial(deps.has_permissions, ["roles:read"]))],
            response_model=List[schemas.DetailedUserRoleBinding])
def read_bindings(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100
) -> Any:
    bindings = crud.user_role_binding.get_detailed_multi(db, skip=skip, limit=limit)
    return [schemas.DetailedUserRoleBinding.from_orm(binding)
            for binding in bindings]


@router.post("/",
             dependencies=[Depends(partial(deps.has_permissions, ["roles:write"]))],
             response_model=schemas.DetailedUserRoleBinding)
def create_binding(
        *,
        db: Session = Depends(deps.get_db),
        binding_in: schemas.Binding
) -> Any:
    binding = crud.user_role_binding.create(db, obj_in=binding_in)
    return schemas.DetailedUserRoleBinding.from_orm(binding)


@router.delete("/",
               dependencies=[Depends(partial(deps.has_permissions, ["roles:write"]))],
               response_model=schemas.Binding)
def delete_binding(
        *,
        db: Session = Depends(deps.get_db),
        binding_in: schemas.Binding
) -> Any:
    deleted_binding = crud.user_role_binding.remove(db, binding_in=binding_in)
    return schemas.Binding.from_orm(deleted_binding)


@router.get("/for_user/{user_id}",
            dependencies=[Depends(partial(deps.has_permissions, ["roles:read"]))],
            response_model=List[schemas.DetailedUserRoleBinding])
def read_bindings_for_user(
        *,
        db: Session = Depends(deps.get_db),
        user_id: int
) -> Any:
    bindings = crud.user_role_binding.get_detailed_multi_for_user(db, user_id=user_id)
    return [schemas.DetailedUserRoleBinding.from_orm(binding)
            for binding in bindings]
