from datetime import datetime, timezone
from typing import Union, Optional

def to_datetime(value: Union[str, datetime]) -> datetime:
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value

def calculate_remaining_seconds(created_at: datetime, deadline: Optional[datetime]) -> float:
    if not deadline:
        return 0.0

    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    return (deadline - now).total_seconds()
