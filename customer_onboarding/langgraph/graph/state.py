from typing_extensions import TypedDict


class CustomerState(TypedDict, total=False):
    name: str
    email: str
    company: str
    onboarding_result: str
    welcome_email: str
    task_list: str
