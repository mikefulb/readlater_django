from datetime import datetime, timedelta, timezone
from django.template import Library
register = Library()

# @register.filter
# def nice_timesince(value):
#     """
#     Return a nice string for the time since 'value'.
#
#     For a time delta this routine will return the largest non-zero value of the time delta and truncate the rest.
#
#     Example usage in template:
#
#     {{ my_datetime|nice_timesince }}
#
#     """
#     timed = timedelta(value)
#     print('timed = ', timed)
#
#     new_value = value.replace(hour=0, minute=0, second=0, microsecond=0)
#     print('new_value = ', new_value)
#     return new_value


@register.filter
def nice_timesince(value, utc_offset=0):
    """
    Return a nice string for the time since 'value'.

    For a time delta this routine will return the largest non-zero value of the time delta and truncate the rest.

    Example usage in template:

    {{ my_datetime|nice_timesince }}

    Note: Assumes time value is for UTC time zone.  Use utc_offset to specify an offset from UTC.

    """

    # only do something if datetime was passed in else just return value
    if not isinstance(value, datetime):
        return value

    dt = datetime.now(timezone(timedelta(hours=utc_offset))) - value
    secs = dt.total_seconds()

    # want to return largest time unit which is non-zero
    tunits = {
        'year': 365.25 * 24 * 3600,
        'month': 30 * 24 * 3600,
        'week': 7 * 24 * 3600,
        'day': 24 * 3600,
        'hour': 3600,
        'minute': 60,
        'second': 1
    }

    for u, s in tunits.items():
        sdiv = secs / s
        if sdiv > 1:
            ustr = u if sdiv < 2 else u + 's'
            return f'{int(sdiv)} {ustr} ago'
    else:
        return '0 seconds ago'
