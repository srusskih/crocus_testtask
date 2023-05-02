from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, ARRAY, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Role(Base):
    """
    Roles is a collection of permissions that can be assigned on different Users via `Bindings`.
    """
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, index=True)
    permissions = Column(ARRAY(String))


class Bindings(Base):
    """
    Bindings is a table that binds Users to Roles.

    User can have only one UNIQUE role, but can have multiple roles
    """
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("role.id"), primary_key=True)