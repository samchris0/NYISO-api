from models.historical_rtc_generator import HistoricalRTCGeneratorModel  # import your model class
from extensions import db

db.session.query(HistoricalRTCGeneratorModel).delete()
db.session.commit()