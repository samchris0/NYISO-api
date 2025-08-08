from extensions import db

class LoadRealTimeIntegratedModel(db.Model):
    timestamp = db.Column(db.DateTime, primary_key=True)
    name = db.Column(db.String, primary_key=True)
    ptid = db.Column(db.Integer, nullable=True)
    integrated_load = db.Column(db.String, nullable=True)