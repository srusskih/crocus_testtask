from typing import List, TypeVar

from pydantic import BaseModel

Permissions = List[str]


class RoleCreate(BaseModel):
    """Schema for creating a role"""
    name: str
    permissions: Permissions

    class Config:
        orm_mode = True


class Role(BaseModel):
    """Schema to read the role(s)"""
    id : int
    name: str
    permissions: Permissions

    class Config:
        orm_mode = True


class Binding(BaseModel):
    """Schema for binding a role to a user"""
    role_id: int
    user_id: int

    class Config:
        orm_mode = True
