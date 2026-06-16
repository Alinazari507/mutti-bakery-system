from enum import Enum

class RoleType(Enum):
    ADMIN = "Mutti"
    MANAGER = "Manager"
    BAKER = "Baker"

class User:
    def __init__(self, username: str, role: RoleType):
        self.username = username
        self.role = role

    def can_approve_recipe(self) -> bool:
        return self.role == RoleType.ADMIN

    def can_scale(self) -> bool:
        return True

    def can_audit_log(self) -> bool:
        return self.role in [RoleType.ADMIN, RoleType.MANAGER]