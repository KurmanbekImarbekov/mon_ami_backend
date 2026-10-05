from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "customer"


class UserLogin(BaseModel):
    username: str
    password: str