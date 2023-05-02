from typing import Optional, List
from sqlalchemy.sql.expression import Select
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models import permissions as models
from app.schemas import permissions as schemas


class CRUDRole(CRUDBase[models.Role, schemas.RoleCreate, schemas.RoleUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[models.Role]:
        return db.query(self.model).filter(self.model.name == name).first()


class CRUDBinding(CRUDBase[models.Bindings, schemas.Binding, schemas.Binding]):

    def find_for_user(self, db: Session, *, user_id: int) -> List[models.Bindings]:
        return (
            db
            .query(self.model)
            .options(joinedload(self.model.role, innerjoin=True))
            .filter(self.model.user_id == user_id).all())


role = CRUDRole(models.Role)
user_role_binding = CRUDBinding(models.Bindings)