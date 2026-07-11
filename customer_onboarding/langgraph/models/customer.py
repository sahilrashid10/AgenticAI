from pydantic import BaseModel, EmailStr


class Customer(BaseModel):
    name: str
    email: EmailStr
    company: str
