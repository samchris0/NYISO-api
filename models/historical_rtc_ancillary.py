from extensions import db

class HistoricalRTCAncillaryModel(db.Model):
    timestamp = db.Column(db.DateTime, primary_key=True)
    name = db.Column(db.String, primary_key=True)
    ptid = db.Column(db.Integer, nullable=True)
    spinning_reserve_10min = db.Column(db.Float, nullable=True)
    non_sync_reserve_10min = db.Column(db.Float, nullable=True)
    operating_reserve_30min = db.Column(db.Float, nullable=True)
    regulation_capacity = db.Column(db.Float, nullable=True)
    regulation_movement = db.Column(db.Float, nullable=True)
