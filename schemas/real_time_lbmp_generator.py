import datetime

from marshmallow import Schema, fields, validates_schema, ValidationError, RAISE

from utils.fields import FlexibleDateTimeField

class RealTimeLBMPGeneratorQuery(Schema):
    start = FlexibleDateTimeField(required=True)
    
    end = FlexibleDateTimeField(required=True)

    ptid = fields.List(fields.Int(), required=False)

    @validates_schema
    def start_after(self, data, **kwargs):
        if data['start'] < datetime.datetime(2007, 12, 1, 0, 0):
             raise ValidationError('Data not available for this range. Please select a start time at or after than December 1, 2007, 00:05')

    @validates_schema
    def end_before(self, data, **kwargs):
        if data['end'] > datetime.now():
             raise ValidationError('Data not available for this end point')

    @validates_schema
    def start_less_than_end(self, data, **kwargs):
        if data['start'] > data['end']:
             raise ValidationError('Start date must be less than or equal to end date')

    @validates_schema
    def start_five_minute(self, data, **kwargs):
        if data['start'].minute%5 != 0:
             raise ValidationError('Queries in this date range start every 5 minutes, ex. HH:00,05,10,15')

    @validates_schema
    def end_five_minute(self, data, **kwargs):
        if data['end'].minute%5 != 0:
             raise ValidationError('Queries in this date range end every 5 minutes, ex. HH:00,05,10,15')

    @validates_schema
    def less_than_thirty_one_days(self, data, **kwargs):
        delta = data['end'] - data['start']
        if abs(delta.days) > 31:
             raise ValidationError('Individual queries must be less than 31 days.')

class RealTimeLBMPGeneratorValidation(Schema):
    timestamp = fields.DateTime(required=True)
    name = fields.String()
    ptid = fields.Integer()
    lbmp = fields.Float()
    marginal_cost_losses = fields.Float()
    marginal_cost_congestion = fields.Float()