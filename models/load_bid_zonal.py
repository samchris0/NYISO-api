from extensions import db

class LoadBidZonalModel(db.Model):
    timestamp = db.Column(db.DateTime, primary_key=True)
    ptid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    energy_bid_load = db.Column(db.Float, nullable=True)
    bilateral_load = db.Column(db.Float, nullable=True)
    price_cap_load = db.Column(db.Float, nullable=True)
    virtual_load = db.Column(db.Float, nullable=True)
    virtual_supply = db.Column(db.Float, nullable=True)