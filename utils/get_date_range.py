import datetime

def get_date_range(start,end):
    """
        Return a set of dates containing all dates (YYYY MM DD) between the start and end point (inclusive)

        Parameters:
            start (datetime): Start of query range
            end (datetime: End of query range

        Returns:
            daterange (set, datetimes): all dates between start and end
    """

    daterange = set()

    end_date = end.date()
    current = start.date()
    while current <= end_date:
        daterange.add(current)
        current = current+datetime.timedelta(days=1)
    
    return daterange