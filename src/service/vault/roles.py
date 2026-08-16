from enum import IntEnum


class Role(IntEnum):
    USER = 0
    MODERATOR = 1
    ADMIN = 2
    OWNER = 3
    ROOT = 4
