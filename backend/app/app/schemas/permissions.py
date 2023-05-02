from typing import List

from pydantic import BaseModel


class RoleCreate(BaseModel):
    """Schema for creating a role"""
    name: str
    permissions: List[str]

    class Config:
        orm_mode = True


class RoleUpdate(BaseModel):
    """Schema to read the role(s)"""
    id : int
    name: str
    permissions: List[str]

    class Config:
        orm_mode = True


class Binding(BaseModel):
    """Schema for binding a role to a user"""
    role_id: int
    user_id: int

    class Config:
        orm_mode = True
