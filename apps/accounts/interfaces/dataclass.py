from libs import dataclasses
from uuid import uuid4
from enum import Enum


class UserType(str, Enum):
    ORDINARY = 'ordinary'
    INTERNAL = 'internal_app'
    ADMIN = 'admin'

class CreateUserRequest(dataclasses.BaseModel):
    uid: dataclasses.UUIDField
    username: str
    mobile: str
    password: dataclasses.PasswordField


class UpdateUserRequest(dataclasses.BaseModel):
    uid: dataclasses.UUIDField
    username: str | None = None
    mobile: str | None = None
    password: dataclasses.PasswordField | None = None


class User(dataclasses.BaseModel):
    uid: dataclasses.UUIDField
    username: str | None = None
    mobile: str | None = None
    user_type: UserType | None = UserType.ORDINARY
    created_at: int | None = None
    modified_at: int | None = None
    

class GetUserRequest(dataclasses.BaseModel):
    uid: dataclasses.UUIDField
    username: str | None = None
    mobile: str | None = None
    password: dataclasses.PasswordField | None = None


class AccessMetadata(dataclasses.BaseModel):
    ip: dataclasses.IPField
    user_agent: str


class Session(dataclasses.BaseModel):
    session_uid: dataclasses.UUIDField
    user_uid: dataclasses.UUIDField
    token: str | None = None
    access_metadata: AccessMetadata | None = None
    created_at: int | None = None
    expires_at: int | None = None
    terminated_at: int | None = None
    last_activity_at: int | None = None
    is_authenticated: bool = True  # for django compatibility
    user: User | None = None

    @classmethod
    def for_internal_app(cls, uid):
        return cls(
            session_uid=str(uuid4()),
            user_uid=uid,
            user=User(
                uid=uid,
                is_identified=True,
                full_name=uid.replace('_', ' '),
                user_type=UserType.INTERNAL
            )
        )


class AuthenticateRequest(dataclasses.BaseModel):
    token: str
    access_metadata: AccessMetadata


class CreateSessionRequest(dataclasses.BaseModel):
    session_uid: dataclasses.UUIDField
    mobile: str
    password: str
    access_metadata: AccessMetadata


class CreateAdminUserRequest(dataclasses.BaseModel):
    mobile: str
    password: dataclasses.PasswordField
