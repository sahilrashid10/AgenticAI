from pydantic import BaseModel, EmailStr


class Customer(BaseModel):
    name: str
    email: str
    company: str