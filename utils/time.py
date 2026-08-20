from datetime import datetime
from zoneinfo import ZoneInfo

NY_TIMEZONE = ZoneInfo("America/New_York")


def now_ny() -> datetime:
    return datetime.now(NY_TIMEZONE)