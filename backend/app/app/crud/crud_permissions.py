from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, NoResultFound

from app.crud.base import CRUDBase
from app import exc
from app.models import permissions as models
from app.schemas import permissions as schemas


class CRUDRole(CRUDBase[models.Role, schemas.RoleCreate, schemas.Role]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[models.Role]:
        return db.query(self.model).filter(self.model.name == name).first()

    def create(self, db: Session, *, obj_in: schemas.RoleCreate) -> models.Role:
        try:
            return super().create(db, obj_in=obj_in)
        except IntegrityError as e:
            raise exc.Conflict("Role with this name already exists") from e

    def remove(self, db: Session, *, id: int) -> models.Role:
        try:
            obj = db.query(self.model).filter(self.model.id == id).one()
        except NoResultFound as e:
            raise exc.NotFound("Role not found") from e
        db.delete(obj)
        db.commit()
        return obj


class CRUDBinding(CRUDBase[models.Bindings, schemas.Binding, schemas.Binding]):

    def create(self, db: Session, *, obj_in: schemas.Binding) -> models.Bindings:
        try:
            return super().create(db, obj_in=obj_in)
        except IntegrityError as e:
            raise exc.Conflict("Binding already exists") from e

    def find_for_user(self, db: Session, *, user_id: int) -> List[models.Bindings]:
        return (
            db
            .query(self.model)
            .options(joinedload(self.model.role, innerjoin=True))
            .filter(self.model.user_id == user_id).all())

    def get_detailed_multi_for_user(self, db: Session, *, user_id: int) -> List[models.Bindings]:
        return (
            db
            .query(self.model)
            .options(joinedload(self.model.user, innerjoin=True))
            .options(joinedload(self.model.role, innerjoin=True))
            .filter(self.model.user_id == user_id)
            .all())

    def get_detailed_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[models.Bindings]:
        bindings = (
            db
            .query(self.model)
            .options(joinedload(self.model.role, innerjoin=True))
            .options(joinedload(self.model.user, innerjoin=True))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return bindings

    def remove(self, db: Session, *, binding_in: schemas.Binding) -> None:
        try:
            b = db.query(self.model).filter(
                self.model.user_id == binding_in.user_id,
                self.model.role_id == binding_in.role_id
            ).one()
        except NoResultFound as e:
            raise exc.NotFound(message="Binding not found") from e
        db.delete(b)
        db.commit()
        return b


role = CRUDRole(models.Role)
user_role_binding = CRUDBinding(models.Bindings)
