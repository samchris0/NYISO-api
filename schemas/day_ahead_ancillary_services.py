import datetime

from marshmallow import Schema, fields, validates_schema, ValidationError, RAISE

from utils.fields import FlexibleDateTimeField


class DayAheadAncillaryQuery(Schema):
    start = FlexibleDateTimeField(required=True)
    
    end = FlexibleDateTimeField(required=True)

    @validates_schema
    def start_after(self, data, **kwargs):
        if data['start'] < datetime.datetime(1999, 11, 18, 0, 0):
             raise ValidationError('Data not available for this range. Please select a start time at or greater than November 18, 1999 00:00')

    @validates_schema
    def end_before(self, data, **kwargs):
        if data['end'] > datetime.datetime.now():
             raise ValidationError('Data not available for this end point')

    @validates_schema
    def start_less_than_end(self, data, **kwargs):
        if data['start'] > data['end']:
             raise ValidationError('Start date must be less than or equal to end date')
        
    @validates_schema
    def less_than_thirty_one_days(self, data, **kwargs):
        delta = data['end'] - data['start']
        if abs(delta.days) > 31:
             raise ValidationError('Individual queries must be less than 31 days.')

class DayAheadAncillaryValidation(Schema):
    timestamp = fields.DateTime(required=True)
    name = fields.String(required=True)
    ptid = fields.Integer()
    spinning_reserve_10min = fields.Float()
    non_sync_reserve_10min = fields.Float()
    operating_reserve_30min = fields.Float()
    regulation_capacity = fields.Float()