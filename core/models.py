from dataclasses import dataclass
from typing import Optional
import time
import uuid

@dataclass
class Entry:
    id: str
    service: str
    login: str
    password: str
    url: Optional[str]
    category_id: str
    note: str
    created_at: float
    updated_at: float

    @staticmethod
    def create(service, login, password, category_id, url="", note=""):
        now = time.time()
        return Entry(
            id=str(uuid.uuid4()),
            service=service,
            login=login,
            password=password,
            url=url,
            category_id=category_id,
            note=note,
            created_at=now,
            updated_at=now
        )
