from dataclasses import dataclass
from typing import Optional


@dataclass
class Page:

    page: int

    text: str


@dataclass
class Chunk:

    id: str

    document: str

    text: str

    start_char: int

    end_char: int

    start_page: int

    end_page: int


    