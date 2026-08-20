from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

NY_TIMEZONE = ZoneInfo("America/New_York")


def now_ny() -> datetime:
    return datetime.now(NY_TIMEZONE)

def localize_ptid(group: pd.DataFrame) -> pd.DataFrame:
    group = group.copy()

    timestamps = pd.to_datetime(
        group["Time Stamp"],
        format="%m/%d/%Y %H:%M:%S",
    )

    group["Time Stamp"] = timestamps.dt.tz_localize(
        "America/New_York",
        ambiguous="infer",
        nonexistent="raise",
    )

    return group