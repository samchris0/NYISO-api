from marshmallow import fields, ValidationError
from datetime import datetime

from nyiso_api.utils.time import NY_TIMEZONE

class FlexibleDateTimeField(fields.DateTime):
    def _deserialize(self, value, attr, data, **kwargs):
        parsed = super()._deserialize(value, attr, data, **kwargs)

        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValidationError(
                "Datetime must include a UTC offset, for example "
                "2026-08-26T14:30:00-04:00."
            )

        return parsed.astimezone(NY_TIMEZONE)
