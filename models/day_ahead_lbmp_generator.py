from extensions import db

class DayAheadLBMPGeneratorModel(db.Model):
    timestamp = db.Column(db.DateTime, primary_key=True)
    ptid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    lbmp = db.Column(db.Float, nullable = True)
    marginal_cost_losses = db.Column(db.Float, nullable=True)
    marginal_cost_congestion = db.Column(db.Float, nullable=True)
