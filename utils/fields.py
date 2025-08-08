from marshmallow import fields, ValidationError
from datetime import datetime

class FlexibleDateTimeField(fields.DateTime):
    def _deserialize(self, value, attr, data, **kwargs):
        formats = ["%Y-%m-%d %H", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"]
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise ValidationError("Invalid datetime format. Expected one of: YYYY MM DD HH[:MM[:SS]]")