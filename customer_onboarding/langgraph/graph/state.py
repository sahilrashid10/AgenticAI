from typing import TypedDict

# By defining your state with a TypedDict, you are creating a strict blueprint.
#  You are telling Python, "Hey, this dictionary is "
# "only allowed to have these exact keys, and the values must be these exact types."
from models.customer import Customer
class CustomerState(TypedDict):
    customer: Customer
    valid: bool
    exists: bool
    saved: bool
    welcome_email: str
    task_list: str
    error: str