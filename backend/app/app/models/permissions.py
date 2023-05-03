from sqlalchemy import Column, ForeignKey, Integer, String, ARRAY
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Role(Base):
    """
    Roles is a collection of permissions that can be assigned on different Users via `Bindings`.
    """
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    permissions = Column(ARRAY(String))


class Bindings(Base):
    """
    Bindings is a table that binds Users to Roles.

    User can have only one UNIQUE role, but can have multiple roles
    """
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("role.id", ondelete="CASCADE"), primary_key=True)
    role = relationship("Role")
    user = relationship("User")