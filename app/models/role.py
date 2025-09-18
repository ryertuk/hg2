# app/models/role.py
from sqlalchemy import Column, Integer, String, Text
from app.models.base import BaseModel
import json

class Role(BaseModel):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    permissions = Column(Text, nullable=False, default='{}')  # JSON string

    def __init__(self, name, permissions=None):
        self.name = name
        self.permissions = json.dumps(permissions or {})

    def has_permission(self, perm: str) -> bool:
        perms = json.loads(self.permissions)
        return perms.get(perm, False)

    def __repr__(self):
        return f"<Role {self.name}>"