from extensions import db

class LoadRealTimeActualModel(db.Model):
    timestamp = db.Column(db.DateTime, primary_key=True)
    name = db.Column(db.String, primary_key=True)
    ptid = db.Column(db.Integer, nullable=True)
    load = db.Column(db.String, nullable=True)