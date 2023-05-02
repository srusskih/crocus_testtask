from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.crud.base import CRUDBase
from app.models import permissions as models
from app.schemas import permissions as schemas


class RoleAlreadyExists(Exception):
    message = "Role with this name already exists"


class CRUDRole(CRUDBase[models.Role, schemas.RoleCreate, schemas.Role]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[models.Role]:
        return db.query(self.model).filter(self.model.name == name).first()

    def create(self, db: Session, *, obj_in: schemas.RoleCreate) -> models.Role:
        try:
            return super().create(db, obj_in=obj_in)
        except IntegrityError as e:
            raise RoleAlreadyExists from e


class CRUDBinding(CRUDBase[models.Bindings, schemas.Binding, schemas.Binding]):

    def find_for_user(self, db: Session, *, user_id: int) -> List[models.Bindings]:
        return (
            db
            .query(self.model)
            .options(joinedload(self.model.role, innerjoin=True))
            .filter(self.model.user_id == user_id).all())


role = CRUDRole(models.Role)
user_role_binding = CRUDBinding(models.Bindings)