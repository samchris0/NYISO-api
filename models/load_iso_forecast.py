from extensions import db

class LoadISOForecastModel(db.Model):
    timestamp = db.Column(db.DateTime, primary_key=True)
    name = db.Column(db.String, primary_key=True)
    load = db.Column(db.String, nullable=True)