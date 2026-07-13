from dataclasses import dataclass, asdict


@dataclass
class Customer:
    customer_id: str
    name: str
    email: str
    status: str = "new"

    def to_dict(self) -> dict:
        return asdict(self)
