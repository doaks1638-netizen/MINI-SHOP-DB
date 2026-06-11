from enum import Enum


class UserRole(str, Enum):
    admin = "admin"  # can deactive user, but not create role admin
    user = "user"
    creator = "creator"  # can change role admin
